import network
import utils.files as files
import asyncio
import logging

from services.service_manager import service_locator
from services.light_service import LightService
from services.base_service import BaseService
from services.user_service import UserService

from data.led import Led
from data.status import WlanStatus


class WirelessService(BaseService):
    
    _STATE_DISCONNECTED = "DISCONNECTED"
    _STATE_CONNECTED = "CONNECTED"
    _STATE_CONNECTING = "CONNECTING"
    

    def __init__(self, thread_sleep_time):
        BaseService.__init__(self, thread_sleep_time)
        self.__host_name = "zephyr"
        self.light_service = service_locator.get(LightService)
        self.user_service = service_locator.get(UserService)

        network.hostname(self.__host_name)
        network.WLAN(network.AP_IF).active(False)
        network.WLAN(network.STA_IF).active(False)

        self.interface_access_point = network.WLAN(network.AP_IF)
        self.interface_station = network.WLAN(network.STA_IF)

        self.__state = WirelessService._STATE_DISCONNECTED
        self.__status = WlanStatus(self.__state, "None")


    async def start(self):
        (self.ssid, self.password) = self.user_service.get_user_config().get_wifi_info()
        coroutines = [self.run(), self.update_wifi_led(), self.update_status()]
        await asyncio.gather(*coroutines, return_exceptions=True)
        

    def get_status(self):
        return self.__status
    

    async def update_status(self):
        while True:
            self.__status.state = self.__state
            if self.interface_station.isconnected():
                self.__status.network_name = self.ssid
            else:
                self.__status.network_name = "None"
            await asyncio.sleep(self.thread_sleep_time)

        
    async def update_wifi_led(self):
        while True:
            if self.__state == WirelessService._STATE_CONNECTING:
                self.light_service.set_led_state(LightService._LED_WIFI, Led._STATE_BLINKING)
            elif self.__state == WirelessService._STATE_CONNECTED:
                self.light_service.set_led_state(LightService._LED_WIFI, Led._STATE_ON)
            else:
                self.light_service.set_led_state(LightService._LED_WIFI, Led._STATE_OFF)
            
            await asyncio.sleep(self.thread_sleep_time)


    async def run(self):
        while True:
            if self.ssid:
                # Station Mode
                if not self.interface_station.active():
                    logging.debug("[WLanService] : Activating Station Interface")
                    network.WLAN(network.STA_IF).active(True)
                    await asyncio.sleep(3)

                if not self.interface_station.isconnected():
                    self.__state = WirelessService._STATE_DISCONNECTED
                    logging.info("[WLanService] : Connecting to wireless network.")
                    logging.info("[WLanService] : SSID: {0}, Password: {1}".format(self.ssid, self.password))
                    self.interface_station.disconnect()
                    self.interface_station.connect(self.ssid, self.password, channel=12)
                    self.__state = WirelessService._STATE_CONNECTING
                    await asyncio.sleep(15)
                else:
                    if self.__state == WirelessService._STATE_DISCONNECTED or self.__state == WirelessService._STATE_CONNECTING:
                        self.__state = WirelessService._STATE_CONNECTED
                        logging.info("[WLanService] : Wireless Connected. {0}".format(self.interface_station.ifconfig()))  
                        logging.info("[WLanService] : Visit http://{0}/ in your browser to access options.".format(self.__host_name))
            else:
                # Access Point Mode
                if not self.interface_access_point.active():
                    logging.debug("[WLanService] : Activating Access Point Interface")
                    self.interface_access_point.config(essid='Zephyr Wifi', password='Zephyr123', channel=11)
                    self.interface_access_point.active(True)
            await asyncio.sleep(self.thread_sleep_time)