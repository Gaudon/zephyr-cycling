import utime
import aioble
import bluetooth
import asyncio
import micropython
import random
import json

from micropython import const

from service_manager import service_locator
from services.config_service import ConfigService
from services.base_service import BaseService


class BluetoothTransmitService(BaseService):

    _STATE_IDLE = "IDLE"
    _STATE_PAIRED = "PAIRED"
    _STATE_BROADCASTING = "BROADCASTING"
    

    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        
        self.state = BluetoothTransmitService._STATE_IDLE

        # Services
        self.config_service = service_locator.get(ConfigService)
        self.connection = None
        
        # Bluetooth
        self.ble = bluetooth.BLE()
        self.ble.active(True)

        # Configuration
        self._SVC_DEVICE_INFO = bluetooth.UUID(0x180A)
        self._UUID_HEART_RATE_SERVICE = bluetooth.UUID(0x180D)
        self._CHAR_HEART_RATE_MEASUREMENT = bluetooth.UUID(0x2A37)
        self._CHAR_MANUFACTURER_NAME_STR = bluetooth.UUID(0x2A29)
        self._CHAR_MODEL_NUMBER_STR = bluetooth.UUID(0x2A24)
        self._CHAR_SERIAL_NUMBER_STR = bluetooth.UUID(0x2A25)
        self._CHAR_FIRMWARE_REV_STR = bluetooth.UUID(0x2A26)
        self._CHAR_HARDWARE_REV_STR = bluetooth.UUID(0x2A27)
    
        self.supported_services = [self._UUID_HEART_RATE_SERVICE]

        # Device Info
        self.svc_device_info = aioble.Service(self._SVC_DEVICE_INFO)        
        aioble.Characteristic(self.svc_device_info, self._CHAR_MANUFACTURER_NAME_STR, read=True, initial='Pico HRM')
        aioble.Characteristic(self.svc_device_info, self._CHAR_MODEL_NUMBER_STR, read=True, initial='PF-0001')
        aioble.Characteristic(self.svc_device_info, self._CHAR_SERIAL_NUMBER_STR, read=True, initial='G-PF-982987')
        aioble.Characteristic(self.svc_device_info, self._CHAR_FIRMWARE_REV_STR, read=True, initial='0.0.1')
        aioble.Characteristic(self.svc_device_info, self._CHAR_HARDWARE_REV_STR, read=True, initial='0.0.1')

        
    async def start(self):
        await asyncio.gather(
            self.run()
        )


    async def broadcasting(self):
        await asyncio.sleep(self.thread_sleep_time)

    
    async def idle(self):
        await asyncio.sleep(self.thread_sleep_time)


    async def paired(self):
        await asyncio.sleep(self.thread_sleep_time)


    async def run(self):
        while True:
            if self.state == BluetoothTransmitService._STATE_IDLE:
                # Idle state should transition to broadcasting afer a period of inactivity.
                await self.idle()
            elif self.state == BluetoothTransmitService._STATE_BROADCASTING:
                # Wait for a connection request
                await self.broadcasting()
            elif self.state == BluetoothTransmitService._STATE_PAIRED:
                # Ensure connection still exists and do nothing
                await self.paired()

            await asyncio.sleep(self.thread_sleep_time)