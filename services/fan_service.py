import asyncio
import json

from machine import Pin, I2C
from data.user_config import UserConfig
from services.service_manager import service_locator
from services.base_service import BaseService
from services.config_service import ConfigService
from services.bluetooth_receive_service import BluetoothReceiveService


class FanService(BaseService):

    _STATE_CURRENT = None
    _STATE_PREV = None

    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.config_service = service_locator.get(ConfigService)
        self.bluetooth_receive_service = service_locator.get(BluetoothReceiveService)
        self.heart_rate_value = 0
        self.fan_config = []


    async def start(self):
        self.bluetooth_receive_service.register_callback(BluetoothReceiveService._EVENT_HEART_RATE_RECEIVED, self.on_heart_rate_received)
        for i in range(1, 9):
            self.fan_config.append((i, Pin(int(self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)))))
        
        # Initialize the user configuration settings
        with open("../config/user.json", "r") as file:
            json_data = json.load(file)
            self.user_config.update_from_json(json_data)
            file.close()
        
        await asyncio.gather(
            self.run()
        )

    
    async def run(self):
        # TODO(Gaudon) : Implement
        # Compare current heart rate values to user settings and relay indexes
        await asyncio.sleep(self.thread_sleep_time)
    

    def enable_relay(self, relay_pin):
        # Disable all other relays
        for config in self.fan_config:
            config[1].off()

        # Enable the target relay
        for config in self.fan_config:
            if config[0] == relay_pin:
                config[1].on()


    def update_user_config(self, user_config):
        self.user_config = user_config
        

    def on_heart_rate_received(self, data):
        self.heart_rate_value = data[1]