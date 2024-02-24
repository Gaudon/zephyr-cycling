import network
import utils.files as files
import json

from services.service_manager import service_locator
from services.display_service import DisplayService
from services.light_service import LightService
from services.config_service import ConfigService
from services.base_service import BaseService
from data.user_config import UserConfig


class WirelessService(BaseService):
    
    _STATE_DISCONNECTED = "DISCONNECTED"
    _STATE_CONNECTED = "CONNECTED"


    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.light_service = service_locator.get(LightService)
        self.config_service = service_locator.get(ConfigService)
        

        # Wireless Access Point
        self.ap_if = network.WLAN(network.AP_IF)
        self.socket = None
        self.__state = WirelessService._STATE_DISCONNECTED
        
        self.ssid = self.config_service.get(ConfigService._WLAN_NETWORK_SSID)
        self.password = self.config_service.get(ConfigService._WLAN_NETWORK_PASSWORD)


    async def start(self):
        self.ap_if = network.WLAN(network.AP_IF)

        network.WLAN(network.STA_IF).active(False)

        # Access Point Mode
        self.ap_if.config(essid='Zephyr Wifi', password='Zephyr123', channel=11)
        self.ap_if.active(True)