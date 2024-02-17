from machine import Pin, I2C
from services.base_service import BaseService


class FanService(BaseService):
    
    STATE_OFF = 0
    STATE_LOW_POWER = 1
    STATE_NORMAL_POWER = 2
    STATE_HIGH_POWER = 3
    
    def __init__(self):
        self.state = FanService.STATE_OFF


    async def start(self):
        pass