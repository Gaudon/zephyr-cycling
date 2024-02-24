from machine import Pin, I2C

from services.service_manager import service_locator
from services.base_service import BaseService
from services.config_service import ConfigService


class FanService(BaseService):

    
    def __init__(self):
        self.config_service = service_locator.get(ConfigService)
        
        for i in range(1, 9):
            self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)

    async def start(self):
        pass