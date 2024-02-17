import utime
import aioble
import bluetooth
import asyncio
import micropython

from micropython import const

from service_manager import service_locator
from services.light_service import LightService
from services.config_service import ConfigService
from services.uart_service import UartService
from services.input_service import InputService
from services.base_service import BaseService


class BluetoothService(BaseService):
    
    # Input/Output 
    _IO_CAPABILITY_NO_INPUT_OUTPUT = const(3)
    
    # IRQ Events
    _IRQ_SCAN_RESULT = const(5)
    _IRQ_SCAN_DONE = const(6)
    _IRQ_PERIPHERAL_CONNECT = const(7)
    _IRQ_PERIPHERAL_DISCONNECT = const(8)
    
    
    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.configure()
        self.uart_service = service_locator.get(UartService)
        self.input_service = service_locator.get(InputService)
        self.config_service = service_locator.get(ConfigService)
        self.light_service = service_locator.get(LightService)
        self.connection = None
        self.scan_ready = False
        self.nearby_hrms = []
        self.data = None
        self.scanning = False
        self.reconnect_interval = 10
        
        # Device Info
        self.svc_device_info = aioble.Service(self._SVC_DEVICE_INFO)        
        aioble.Characteristic(self.svc_device_info, self._CHAR_MANUFACTURER_NAME_STR, read=True, initial='Pico Fan')
        aioble.Characteristic(self.svc_device_info, self._CHAR_MODEL_NUMBER_STR, read=True, initial='PF-0001')
        aioble.Characteristic(self.svc_device_info, self._CHAR_SERIAL_NUMBER_STR, read=True, initial='G-PF-982987')
        aioble.Characteristic(self.svc_device_info, self._CHAR_FIRMWARE_REV_STR, read=True, initial='0.0.1')
        aioble.Characteristic(self.svc_device_info, self._CHAR_HARDWARE_REV_STR, read=True, initial='0.0.1')
        
        # Heart Rate
        self.svc_heart_rate = aioble.Service(self._SVC_HEART_RATE)
        aioble.Characteristic(self.svc_heart_rate, self._CHAR_HEART_RATE_MEASUREMENT, read=True)
        
        # Register Services
        aioble.register_services(self.svc_device_info, self.svc_heart_rate)

        
    def on_bluetooth_btn_short_press(self):
        self.scan_ready = True


    def on_bluetooth_btn_long_press(self):
        self.scan_ready = True

        
    async def start(self):
        # Register Button Callbacks
        self.input_service.register_callback(
            self.config_service.get(ConfigService.BTN_BLUETOOTH_SYNC_PIN),
            self.on_bluetooth_btn_short_press, 
            InputService.BTN_CALLBACK_SHORT_PRESS
        )

        self.input_service.register_callback(
            self.config_service.get(ConfigService.BTN_BLUETOOTH_SYNC_PIN),
            self.on_bluetooth_btn_long_press, 
            InputService.BTN_CALLBACK_LONG_PRESS
        )

        await asyncio.gather(
            self.get_data(),
            self.scan(),
            self.update_bluetooth_led()
        )

    
    def configure(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self._SVC_DEVICE_INFO = bluetooth.UUID(0x180A)
        self._SVC_HEART_RATE = bluetooth.UUID(0x180D)
        self._CHAR_HEART_RATE_MEASUREMENT = bluetooth.UUID(0x2A37)
        self._CHAR_MANUFACTURER_NAME_STR = bluetooth.UUID(0x2A29)
        self._CHAR_MODEL_NUMBER_STR = bluetooth.UUID(0x2A24)
        self._CHAR_SERIAL_NUMBER_STR = bluetooth.UUID(0x2A25)
        self._CHAR_FIRMWARE_REV_STR = bluetooth.UUID(0x2A26)
        self._CHAR_HARDWARE_REV_STR = bluetooth.UUID(0x2A27)
    
    
    async def get_data(self):
        hrm_service = None
        hrm_char = None
        self.hrm_subscribed = False
        
        while True:            
            if self.connection is not None:
                try:
                    if hrm_service is None:
                        hrm_service = await self.connection.service(self._SVC_HEART_RATE)
                        print("Service : {}".format(hrm_service.uuid))
                   
                    if hrm_char is None:
                        hrm_char = await hrm_service.characteristic(self._CHAR_HEART_RATE_MEASUREMENT)
                        print("Characteristic : {}".format(hrm_char.uuid))
                     
                    if self.hrm_subscribed is False: 
                        await hrm_char.subscribe(notify=True)
                        self.hrm_subscribed = True
                   
                    # HRM Specificiation States Heart Rate Measurements Must Be Notified (Not Read)
                    data = await hrm_char.notified()
                    flag_data = data[0]
                    self.data = data[1]
                   
                    self.uart_service.transmit_heart_rate_data(data)

                    print("HRM Data Received - {} bpm".format(self.data))
                except Exception as e:
                    print(type(e).__name__)
                    print("[BluetoothService][Exception] - {}".format(e))
                    self.connection = None
                    self.data = None
            await asyncio.sleep(1)
                                
    
    def get_bits(self, byte, start_bit, num_bits):
        mask = (1 << num_bits) - 1
        mask = mask << start_bit
        result = (byte & mask) >> start_bit
        return result


    async def disconnect(self):
        if self.connection is not None:
            await self.connection.disconnect()


    async def connect_next(self):
        if self.connection is not None:
            for device_data in self.nearby_hrms:
                if device_data[1] is not self.connection.device:
                    await self.connect(device_data[1])


    async def connect(self, device):
        await self.disconnect()
        try:
            self.connection = await device.connect(timeout_ms=10000)
        except asyncio.TimeoutError:
            print('[BluetoothService][TIMEOUT] - Could not connect to device.')


    def stop_scanning(self):
        self.scanning = False
        self.scan_ready = False


    async def update_bluetooth_led(self):
        while True:
            if not self.scanning:
                if self.connection is not None:
                    self.light_service.set_led_bluetooth(True)
                else:
                    self.light_service.set_led_bluetooth_blink_status(False)
                    self.light_service.set_led_bluetooth(False)
            else:
                self.light_service.set_led_bluetooth_blink_status(True)

            await asyncio.sleep(self.thread_sleep_time)


    async def scan(self):
        while True:
            if not self.scanning and self.scan_ready:
                print("[BluetoothService] - Scanning")
                self.scanning = True
                self.scan_ready = False
                await self.disconnect()
                self.nearby_hrms.clear()
                
                async with aioble.scan(10000, 1280000, 11250, True) as scanner:
                    async for result in scanner:
                        if result.connectable:
                            device_services = result.services()
                            if self._SVC_HEART_RATE in device_services:
                                self.nearby_hrms.append((result.name, result.device))
                
                self.stop_scanning()
                if(len(self.nearby_hrms) == 0):
                    print('[BluetoothService] - No heart rate monitor found.')
                else:
                    await self.connect(result.device)

            await asyncio.sleep(self.thread_sleep_time)