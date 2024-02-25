from machine import Pin, I2C

from services.service_manager import service_locator
from services.base_service import BaseService
from services.config_service import ConfigService


class FanService(BaseService):

    
    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.config_service = service_locator.get(ConfigService)
        self.fan_settings = []
        

    async def start(self):
        print("ran")
        for i in range(1, 9):
            self.fan_settings.append((i, self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)))
        
        print(self.fan_settings)