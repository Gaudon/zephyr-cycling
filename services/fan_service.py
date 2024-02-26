import asyncio
import json

from machine import Pin, I2C
from data.user_config import UserConfig
from services.service_manager import service_locator
from services.base_service import BaseService
from services.config_service import ConfigService
from services.bluetooth_receive_service import BluetoothReceiveService


class FanService(BaseService):


    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.config_service = service_locator.get(ConfigService)
        self.bluetooth_receive_service = service_locator.get(BluetoothReceiveService)
        self.heart_rate_value = 0
        self.fan_config = []
        self.user_config = UserConfig()


    async def start(self):
        self.bluetooth_receive_service.register_callback(BluetoothReceiveService._EVENT_HEART_RATE_RECEIVED, self.on_heart_rate_received)
        for i in range(1, 9):
            self.fan_config.append((i, Pin(int(self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)))))
        
        await asyncio.gather(
            self.run(),
            self.update_user_heart_rate_settings()
        )

    
    async def run(self):
        await asyncio.sleep(self.thread_sleep_time)
    

    async def update_user_heart_rate_settings(self):
        json_data = None
        with open("../config/user.json", "r") as file:
            json_data = json.load(file)
            file.close()
        
        if json_data is not None:
            self.user_config.update_from_json(json_data)
        
        await asyncio.sleep(120)
        

    def on_heart_rate_received(self, data):
        self.heart_rate_value = data[1]