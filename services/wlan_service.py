import network
import utils.files as files
import asyncio
import logging

from services.service_manager import service_locator
from services.light_service import LightService
from services.base_service import BaseService
from services.user_service import UserService
from data.user_config import UserConfig


class WirelessService(BaseService):
    
    _STATE_DISCONNECTED = "DISCONNECTED"
    _STATE_CONNECTED = "CONNECTED"


    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.light_service = service_locator.get(LightService)
        self.user_service = service_locator.get(UserService)

        network.hostname('zephyr')
        network.WLAN(network.AP_IF).active(False)
        network.WLAN(network.STA_IF).active(False)

        self.interface_access_point = network.WLAN(network.AP_IF)
        self.interface_station = network.WLAN(network.STA_IF)

        self.__state = WirelessService._STATE_DISCONNECTED


    async def start(self):
        (self.ssid, self.password) = self.user_service.get_user_config().get_wifi_info()
        while True:
            if self.ssid:
                # Station Mode
                if not self.interface_station.active():
                    logging.debug("[WLanService] : Activating Station Interface")
                    network.WLAN(network.STA_IF).active(True)
                    await asyncio.sleep(3)
                
                if not self.interface_station.isconnected():
                    self.__state = WirelessService._STATE_DISCONNECTED
                    logging.debug("[WLanService] : Connecting to wireless network.")
                    self.interface_station.connect(self.ssid, self.password)
                else:
                    if self.__state == WirelessService._STATE_DISCONNECTED:
                        self.__state = WirelessService._STATE_CONNECTED
                        logging.debug("[WLanService] : Wireless Connected. {0}".format(self.interface_station.ifconfig()))         
            else:
                # Access Point Mode
                if not self.interface_access_point.active():
                    logging.debug("[WLanService] : Activating Access Point Interface")
                    self.interface_access_point.config(essid='Zephyr Wifi', password='Zephyr123', channel=11)
                    self.interface_access_point.active(True)
            await asyncio.sleep(self.thread_sleep_time)