import aioble
import bluetooth
import asyncio
import random

from micropython import const

from service_manager import service_locator
from services.config_service import ConfigService
from services.uart_service import UartService
from services.base_service import BaseService


class BluetoothTransmitService(BaseService):

    _STATE_IDLE = "IDLE"
    _STATE_PAIRED = "PAIRED"
    _STATE_BROADCASTING = "BROADCASTING"
    
    # Must be multiple of 0.625ms
    BLUETOOTH_ADVERTISING_INTERVAL = 120_000

    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        
        self.__state = BluetoothTransmitService._STATE_IDLE
        self.data = None

        # Services
        self.config_service = service_locator.get(ConfigService)
        self.uart_service = service_locator.get(UartService)
        self.connection = None
        
        # Bluetooth
        self.ble = bluetooth.BLE()
        self.ble.active(True)

        # Configuration
        self._SVC_DEVICE_INFO = bluetooth.UUID(0x180A)
        self._UUID_HEART_RATE_SERVICE = bluetooth.UUID(0x180D)
        self._UUID_HEART_RATE_SENSOR = bluetooth.UUID(0x037F)
        self._UUID_GENERIC_HEART_RATE_SENSOR = bluetooth.UUID(0x0340)
        self._CHAR_HEART_RATE_MEASUREMENT = bluetooth.UUID(0x2A37)
        self._CHAR_MANUFACTURER_NAME_STR = bluetooth.UUID(0x2A29)
        self._CHAR_MODEL_NUMBER_STR = bluetooth.UUID(0x2A24)
        self._CHAR_SERIAL_NUMBER_STR = bluetooth.UUID(0x2A25)
        self._CHAR_FIRMWARE_REV_STR = bluetooth.UUID(0x2A26)
        self._CHAR_HARDWARE_REV_STR = bluetooth.UUID(0x2A27)
    
        # Device Info
        self.svc_device_info = aioble.Service(self._SVC_DEVICE_INFO)        
        aioble.Characteristic(self.svc_device_info, self._CHAR_MANUFACTURER_NAME_STR, read=True, initial='Zephyr HRM')
        aioble.Characteristic(self.svc_device_info, self._CHAR_MODEL_NUMBER_STR, read=True, initial='ZF-0001')
        aioble.Characteristic(self.svc_device_info, self._CHAR_SERIAL_NUMBER_STR, read=True, initial='G-ZF-982987')
        aioble.Characteristic(self.svc_device_info, self._CHAR_FIRMWARE_REV_STR, read=True, initial='0.0.1')
        aioble.Characteristic(self.svc_device_info, self._CHAR_HARDWARE_REV_STR, read=True, initial='0.0.1')

        # Heart Rate
        self.svc_heart_rate = aioble.Service(self._UUID_HEART_RATE_SERVICE)
        self.char_heart_rate_measurement = aioble.Characteristic(self.svc_heart_rate, self._CHAR_HEART_RATE_MEASUREMENT, notify=True)

        # Register Callbacks
        self.uart_service.register_callback(UartService.CALLBACK_RX, self.on_data_received)

        # Register Services
        aioble.register_services(self.svc_device_info, self.svc_heart_rate)

        
    async def start(self):
        await asyncio.gather(
            self.run(),
            self.connected()
        )


    async def broadcasting(self):
        while True:
            async with await aioble.advertise(
                BluetoothTransmitService.BLUETOOTH_ADVERTISING_INTERVAL,
                name="Zephyr HRM",
                services=[self._UUID_HEART_RATE_SERVICE, self._UUID_HEART_RATE_SENSOR, self._UUID_GENERIC_HEART_RATE_SENSOR],
                appearance=0x037F,
            ) as connection:
                print("[BluetoothTransmitService] : Accepted Connection - Device ({0})".format(connection.device))
                self.connection = connection
                await connection.disconnected()
            await asyncio.sleep(random.uniform(0.01, 0.1))

    
    def set_state(self, state):
        print("[BluetoothTransmitService] : State Changed - {0}".format(state))
        self.__state = state


    async def idle(self):
        await asyncio.sleep(self.thread_sleep_time)
        self.set_state(BluetoothTransmitService._STATE_BROADCASTING)


    def on_data_received(self, data):
        print("[BluetoothTransmitService] : Data Received - {0}".format(data))
        self.data = data


    async def paired(self):
        await asyncio.sleep(self.thread_sleep_time)


    async def connected(self):
        while True:
            if self.connection is not None and self.data is not None:
                print("[BluetoothTransmitService] : Notifying Data - {0}".format(self.data))
                self.char_heart_rate_measurement.notify(self.connection, self.data)
                    
            await asyncio.sleep(self.thread_sleep_time)


    async def run(self):
        while True:
            if self.__state == BluetoothTransmitService._STATE_IDLE:
                # Idle state should transition to broadcasting afer a period of inactivity.
                await self.idle()
            elif self.__state == BluetoothTransmitService._STATE_BROADCASTING:
                # Wait for a connection request
                await self.broadcasting()
            elif self.__state == BluetoothTransmitService._STATE_PAIRED:
                # Ensure connection still exists and do nothing
                await self.paired()

            await asyncio.sleep(self.thread_sleep_time)