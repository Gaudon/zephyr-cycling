import aioble
import aioble.device
import bluetooth
import asyncio
import logging

from micropython import const

from services.service_manager import service_locator
from services.light_service import LightService
from services.config_service import ConfigService
from services.input_service import InputService
from services.base_service import BaseService
from services.user_service import UserService

from data.led import Led
from data.status import BluetoothStatus


class BluetoothReceiveService(BaseService):
       
    _STATE_IDLE = "IDLE"
    _STATE_SCANNING = "SCANNING"
    _STATE_CONNECTING = "CONNECTING"
    _STATE_CONNECTED = "CONNECTED"

    _EVENT_HEART_RATE_RECEIVED = "HEART_RATE_RECEIVED"

    def __init__(self, thread_sleep_time):
        BaseService.__init__(self, thread_sleep_time)

        self.__state = BluetoothReceiveService._STATE_IDLE
        self.__status = BluetoothStatus(self.__state, "None")
        self.connection = None
        self.heart_rate_device_name = None
        self.heart_rate_device_addr = None
        self.heart_rate_device_addr_type = None
        self.heart_rate_device_list = []
        self.heart_rate_service = None
        self.heart_rate_characteristic = None
        self.heart_rate_subscription = False
        self.heart_rate_data = None
        self.listeners = []

        # Services
        self.input_service = service_locator.get(InputService)
        self.config_service = service_locator.get(ConfigService)
        self.light_service = service_locator.get(LightService)
        self.user_service = service_locator.get(UserService)
        
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
    
        #self.supported_services = [self._UUID_HEART_RATE_SERVICE, self._UUID_CYCLING_SPEED_AND_CADENCE]
        self.supported_services = [self._UUID_HEART_RATE_SERVICE]

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
            InputService._BTN_CALLBACK_SHORT_PRESS
        )

        self.input_service.register_callback(
            self.config_service.get(ConfigService._BTN_BLUETOOTH_SYNC_PIN),
            self.on_bluetooth_btn_long_press, 
            InputService._BTN_CALLBACK_LONG_PRESS
        )

        coroutines = [self.run(), self.update_bluetooth_led(), self.update_status()]
        await asyncio.gather(*coroutines, return_exceptions=True)


    def set_state(self, state):
        if not self.__state == state and self.can_change_state(self.__state, state):
            logging.info("[BluetoothReceiveService] : [StateChangeEvent] - {0} -> {1}".format(self.__state, state))
            self.__state = state


    def get_status(self):
        return self.__status
    

    async def update_status(self):
        while True:
            self.__status.state = self.__state
            self.__status.device_name = "" if self.heart_rate_device_name is None else self.heart_rate_device_name
            self.__status.device_list = self.heart_rate_device_list
            await asyncio.sleep(self.thread_sleep_time)
    

    def can_change_state(self, current_state, next_state) -> bool:
        if current_state == self._STATE_IDLE:
            if next_state in [self._STATE_SCANNING, self._STATE_CONNECTING]:
                return True
            else:
                return False
        elif current_state == self._STATE_SCANNING:
            if next_state in [self._STATE_CONNECTING, self._STATE_IDLE]:
                return True
            else:
                return False
        elif current_state == self._STATE_CONNECTING:
            if next_state in [self._STATE_CONNECTED, self._STATE_IDLE]:
                return True
            else:
                return False
        elif current_state == self._STATE_CONNECTED:
            if next_state in [self._STATE_IDLE]:
                return True
            else:
                return False
        else:
            return False


    def isconnected(self):
        return self.__state == BluetoothReceiveService._STATE_CONNECTED


    def register_callback(self, event, function_handler):
        self.listeners.append((event, function_handler))
        

    async def disconnect(self):
        if self.connection is not None:
            await self.connection.disconnect()
            await aioble.device.DeviceConnection.disconnect(self.connection)
            self.connection = None
        
        self.heart_rate_device_name = None
        self.heart_rate_device_addr = None
        self.heart_rate_device_addr_type = None
        self.heart_rate_service = None
        self.heart_rate_characteristic = None
        self.heart_rate_subscription = False
        self.heart_rate_data = None
        
        logging.info("[BluetoothReceiveService] : Disconnected...")
        self.set_state(BluetoothReceiveService._STATE_IDLE)

        
    async def run(self):
        while True:
            if self.__state == BluetoothReceiveService._STATE_IDLE:
                if self.heart_rate_device_addr and self.heart_rate_device_addr_type:
                    self.set_state(BluetoothReceiveService._STATE_CONNECTING)
            elif self.__state in [BluetoothReceiveService._STATE_SCANNING]:
                await self.scanning()
            elif self.__state == BluetoothReceiveService._STATE_CONNECTING:
                await self.connecting()
            elif self.__state == BluetoothReceiveService._STATE_CONNECTED:
                await self.connected()

            await asyncio.sleep(self.thread_sleep_time)


    async def scanning(self):
        logging.info("[BluetoothReceiveService] : Scanning for devices...")
        try:
            async with aioble.scan(20000, 1280000, 11250, True) as scanner:
                async for result in scanner:
                    logging.info("[BluetoothReceiveService] : Device Found - [{0}] - {1}".format(result, str(result.services())))
                    if any(service in result.services() for service in self.supported_services):
                        logging.info("[BluetoothReceiveService] : Supported Device Found - {0}[{1}]".format(result.name(), result.device.addr_hex()))
                        device_entry = (result.name(), result.device.addr_hex(), result.device.addr_type)
                        if device_entry not in self.heart_rate_device_list:
                            self.heart_rate_device_list.append(device_entry)
        except Exception as e:
            logging.error("[BluetoothReceiveService] : Exception - {0}".format(e))

        if(self.heart_rate_device_list.count == 0):
            logging.info("[BluetoothReceiveService] : No Connection - Heart rate monitor not found.")
            
        self.set_state(BluetoothReceiveService._STATE_IDLE)

            
    async def update_bluetooth_led(self):
        while True:
            if self.__state == BluetoothReceiveService._STATE_SCANNING or self.__state == BluetoothReceiveService._STATE_CONNECTING:
                self.light_service.set_led_state(LightService._LED_BLUETOOTH, Led._STATE_BLINKING)
            elif self.__state == BluetoothReceiveService._STATE_CONNECTED:
                self.light_service.set_led_state(LightService._LED_BLUETOOTH, Led._STATE_ON)
            else:
                self.light_service.set_led_state(LightService._LED_BLUETOOTH, Led._STATE_OFF)
            
            await asyncio.sleep(self.thread_sleep_time)


    def connect(self, address: str, address_type: str):
        logging.info("[BluetoothReceiveService] : Connecting to Device - {0}".format(address))
        self.heart_rate_device_addr = address
        self.heart_rate_device_addr_type = int(address_type)
        self.set_state(BluetoothReceiveService._STATE_CONNECTING)


    async def connecting(self):
        try:
            if not self.connection and self.heart_rate_device_addr and self.heart_rate_device_addr_type:
                try:
                    logging.info("[BluetoothReceiveService] : Connecting to Device - {0}".format(self.heart_rate_device_addr))
                    self.connection = await aioble.Device(self.heart_rate_device_addr_type, self.heart_rate_device_addr).connect(timeout_ms=10000)
                except asyncio.TimeoutError:
                    logging.info("[BluetoothReceiveService] : Connection Timeout - Could not connect to device.")
                    self.set_state(BluetoothReceiveService._STATE_IDLE)
                
            if not self.heart_rate_service and self.connection:
                self.heart_rate_service = await self.connection.service(self._UUID_HEART_RATE_SERVICE)
            
            if not self.heart_rate_characteristic and self.heart_rate_service:
                self.heart_rate_characteristic = await self.heart_rate_service.characteristic(self._CHAR_HEART_RATE_MEASUREMENT)
                
            if not self.heart_rate_subscription and self.heart_rate_characteristic: 
                await self.heart_rate_characteristic.subscribe(notify=True)

            # Save the connected device information
            self.set_state(BluetoothReceiveService._STATE_CONNECTED)
        except Exception as e:
            logging.error("[BluetoothReceiveService] : Exception - {0}".format(e))
            await self.disconnect()


    async def connected(self):      
        try:
            # Find and set the device name for the connected address
            if(self.heart_rate_device_name == None and self.heart_rate_device_addr):
                for entry in self.heart_rate_device_list:
                    if len(entry) >= 2 and entry[1] == self.heart_rate_device_addr:
                        self.heart_rate_device_name = entry[0]
                        break

            if self.heart_rate_characteristic is not None:
                self.heart_rate_data = await self.heart_rate_characteristic.notified(timeout_ms=5000)
                logging.debug("[BluetoothReceiveService] : Heart Rate Received - Raw[{0}] - Value[{1}]".format(self.heart_rate_data, bytes(self.heart_rate_data)[1]))
                for listener in self.listeners:
                    if listener[0] == self._EVENT_HEART_RATE_RECEIVED:
                        listener[1](bytes(self.heart_rate_data))

            await asyncio.sleep(self.thread_sleep_time)
        except Exception as e:
            logging.debug("[BluetoothReceiveService] : Device Disconnected - {0}".format(e))
            await self.disconnect()
