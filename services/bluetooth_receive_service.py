import utime
import aioble
import bluetooth
import asyncio
import micropython
import random
import json

from micropython import const

from service_manager import service_locator
from services.light_service import LightService
from services.config_service import ConfigService
from services.uart_service import UartService
from services.input_service import InputService
from services.base_service import BaseService
from data.heart_rate_command import HeartRateCommand


class BluetoothReceiveService(BaseService):
       
    _STATE_IDLE = "IDLE"
    _STATE_SCANNING = "SCANNING"
    _STATE_SCAN_STARTED = "SCAN_STARTED"
    _STATE_CONNECTING = "CONNECTING"
    _STATE_CONNECTED = "CONNECTED"

    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)

        self.__state = BluetoothReceiveService._STATE_IDLE
        self.connection = None
        self.nearby_heart_rate_services = []
        self.heart_rate_service = None
        self.heart_rate_characteristic = None
        self.heart_rate_subscription = False
        self.heart_rate_data = None
        self.banned_device_names = ['Zephyr HRM']
        self.command = HeartRateCommand(HeartRateCommand.COMMAND_HEART_RATE, None)

        # Services
        self.uart_service = service_locator.get(UartService)
        self.input_service = service_locator.get(InputService)
        self.config_service = service_locator.get(ConfigService)
        self.light_service = service_locator.get(LightService)
        
        # Bluetooth
        self.ble = bluetooth.BLE()
        self.ble.active(True)

        # Configuration
        self._SVC_DEVICE_INFO = bluetooth.UUID(0x180A)
        self._UUID_HEART_RATE_SERVICE = bluetooth.UUID(0x180D)
        self._UUID_CYCLING_SPEED_AND_CADENCE = bluetooth.UUID(0x1816)
        self._CHAR_HEART_RATE_MEASUREMENT = bluetooth.UUID(0x2A37)
        self._CHAR_MANUFACTURER_NAME_STR = bluetooth.UUID(0x2A29)

        self._CHAR_MODEL_NUMBER_STR = bluetooth.UUID(0x2A24)
        self._CHAR_SERIAL_NUMBER_STR = bluetooth.UUID(0x2A25)
        self._CHAR_FIRMWARE_REV_STR = bluetooth.UUID(0x2A26)
        self._CHAR_HARDWARE_REV_STR = bluetooth.UUID(0x2A27)
    
        self.supported_services = [self._UUID_HEART_RATE_SERVICE, self._UUID_CYCLING_SPEED_AND_CADENCE]

        # Device Info
        self.svc_device_info = aioble.Service(self._SVC_DEVICE_INFO)        
        aioble.Characteristic(self.svc_device_info, self._CHAR_MANUFACTURER_NAME_STR, read=True, initial='Zephyr Fan')
        aioble.Characteristic(self.svc_device_info, self._CHAR_MODEL_NUMBER_STR, read=True, initial='ZF-0001')
        aioble.Characteristic(self.svc_device_info, self._CHAR_SERIAL_NUMBER_STR, read=True, initial='G-ZF-982987')
        aioble.Characteristic(self.svc_device_info, self._CHAR_FIRMWARE_REV_STR, read=True, initial='0.0.1')
        aioble.Characteristic(self.svc_device_info, self._CHAR_HARDWARE_REV_STR, read=True, initial='0.0.1')
        
        # Heart Rate
        self.svc_heart_rate = aioble.Service(self._UUID_HEART_RATE_SERVICE)
        aioble.Characteristic(self.svc_heart_rate, self._CHAR_HEART_RATE_MEASUREMENT, read=True)
        
        # Register Services
        aioble.register_services(self.svc_device_info, self.svc_heart_rate)

        
    def on_bluetooth_btn_short_press(self):
        if self.__state == BluetoothReceiveService._STATE_IDLE:
            self.set_state(BluetoothReceiveService._STATE_SCANNING)


    def on_bluetooth_btn_long_press(self):
        if self.__state == BluetoothReceiveService._STATE_IDLE:
            self.set_state(BluetoothReceiveService._STATE_SCANNING)

        
    async def start(self):
        # Register Button Callbacks
        self.input_service.register_callback(
            self.config_service.get(ConfigService._BTN_BLUETOOTH_SYNC_PIN),
            self.on_bluetooth_btn_short_press, 
            InputService.BTN_CALLBACK_SHORT_PRESS
        )

        self.input_service.register_callback(
            self.config_service.get(ConfigService._BTN_BLUETOOTH_SYNC_PIN),
            self.on_bluetooth_btn_long_press, 
            InputService.BTN_CALLBACK_LONG_PRESS
        )

        await asyncio.gather(
            self.run()
            #self.update_bluetooth_led()
        )

    def set_state(self, state):
        print("[BluetoothReceiveService] : State Changed - {0}".format(state))
        self.__state = state


    async def disconnect(self):
        if self.connection is not None:
            await self.connection.disconnect()
            self.set_state(BluetoothReceiveService._STATE_IDLE)

        
    async def run(self):
        while True:
            if self.__state == BluetoothReceiveService._STATE_IDLE:
                await asyncio.sleep(self.thread_sleep_time)
            elif self.__state in [BluetoothReceiveService._STATE_SCANNING, BluetoothReceiveService._STATE_SCAN_STARTED]:
                await self.scanning()
            elif self.__state == BluetoothReceiveService._STATE_CONNECTING:
                await self.connecting()
            elif self.__state == BluetoothReceiveService._STATE_CONNECTED:
                await self.connected()

            await asyncio.sleep(self.thread_sleep_time)


    async def scanning(self):
        if not self.__state == BluetoothReceiveService._STATE_SCAN_STARTED:
            async with aioble.scan(10000, 1280000, 11250, True) as scanner:
                async for result in scanner:
                    if any(service in result.services() for service in self.supported_services):
                        # Do not pair with the transmission chip
                        if result.name() not in self.banned_device_names:
                            self.nearby_heart_rate_services.append((result.name(), result.device))

        self.set_state(BluetoothReceiveService._STATE_SCAN_STARTED)

        if(len(self.nearby_heart_rate_services) == 0):
            print('[BluetoothReceiveService] : No Connection - Heart rate monitor not found.')
            self.set_state(BluetoothReceiveService._STATE_IDLE)
        else:
            try:
                self.connection = await self.nearby_heart_rate_services[0][1].connect(timeout_ms=10000)
                self.set_state(BluetoothReceiveService._STATE_CONNECTING)
            except asyncio.TimeoutError:
                print('[BluetoothReceiveService] : Connection Timeout - Could not connect to device.')
                self.set_state(BluetoothReceiveService._STATE_IDLE)
            

    async def update_bluetooth_led(self):
        while True:
            if self.__state == BluetoothReceiveService._STATE_SCANNING:
                self.light_service.set_led_bluetooth_state(LightService._LED_STATE_BLINKING)
            elif self.__state == BluetoothReceiveService._STATE_CONNECTED:
                self.light_service.set_led_bluetooth_state(LightService._LED_STATE_ON)
            else:
                self.light_service.set_led_bluetooth_state(LightService._LED_STATE_OFF)
            
            await asyncio.sleep(self.thread_sleep_time)


    async def connecting(self):
        try:
            if self.heart_rate_service is None:
                self.heart_rate_service = await self.connection.service(self._UUID_HEART_RATE_SERVICE) # type: ignore
            
            if self.heart_rate_characteristic is None:
                self.heart_rate_characteristic = await self.heart_rate_service.characteristic(self._CHAR_HEART_RATE_MEASUREMENT)
                
            if self.heart_rate_subscription is False: 
                await self.heart_rate_characteristic.subscribe(notify=True)

            self.set_state(BluetoothReceiveService._STATE_CONNECTED)
        except Exception as e:
                print(type(e).__name__)
                print("[BluetoothReceiveService] : Exception - {0}".format(e))
                await self.disconnect()


    async def connected(self):      
        # HRM Specification States Heart Rate Measurements Cannot be Read Directly
        if self.heart_rate_characteristic is not None:
            self.heart_rate_data = await self.heart_rate_characteristic.notified()
            print("[BluetoothReceiveService] : Data Received - {} bpm".format(self.heart_rate_data[1]))
            self.command.payload = self.heart_rate_data[1]
            self.uart_service.update_data(str(json.dumps(self.command.__dict__)))
            await asyncio.sleep(self.thread_sleep_time)