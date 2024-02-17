import network

from service_manager import service_locator
from services.display_service import DisplayService
from services.light_service import LightService
from services.config_service import ConfigService
from services.base_service import BaseService


class WirelessService(BaseService):
    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.light_service = service_locator.get(LightService)
        self.config_service = service_locator.get(ConfigService)
        self.wlan = network.WLAN(network.STA_IF)        
        self.wlan.active(False)
        self.wlan.deinit()
    

    async def start(self):
        pass