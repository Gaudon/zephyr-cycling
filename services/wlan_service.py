import network
import socket
import asyncio 
import files


from service_manager import service_locator
from services.display_service import DisplayService
from services.light_service import LightService
from services.config_service import ConfigService
from services.base_service import BaseService

from microdot import Microdot


class WirelessService(BaseService):
    
    _STATE_DISCONNECTED = "DISCONNECTED"
    _STATE_CONNECTED = "CONNECTED"


    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.light_service = service_locator.get(LightService)
        self.config_service = service_locator.get(ConfigService)

        # Wireless Interfaces
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        self.socket = None
        self.__state = WirelessService._STATE_DISCONNECTED
        
        self.ssid = self.config_service.get(ConfigService._WLAN_NETWORK_SSID)
        self.password = self.config_service.get(ConfigService._WLAN_NETWORK_PASSWORD)


    async def start(self):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        self.sta_if.active(True)

        await asyncio.gather(
            self.run() 
        )


    async def connected(self):
        if self.socket is None:
            self.address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(self.address)
            self.socket.listen(5)
        else:
            try:
                client, addr = self.socket.accept()
                request = client.recv(1024)
                response = files.read_file_as_string("index.html")
                client.send("HTTP/1.0 200 OK\r\n")
                client.send("Content-Type: text/html\r\n\r\n")
                client.send(response)
                client.close()
            except OSError as e:
                client.close()
                print("[WlanService] : Exception - {0}".format(e))


    async def disconnected(self):
        self.sta_if.connect(
            self.ssid,
            self.password
        )

        if self.sta_if.isconnected():
            print("[WlanService] : Wireless Network Connected - {0} [{1}]".format(self.ssid, self.sta_if.ifconfig()[0]))
            self.__state = WirelessService._STATE_CONNECTED
        print("[WlanService] : Wireless Not Connected - Retrying...")


    async def run(self):
        while True:
            if self.__state == WirelessService._STATE_CONNECTED:
                await self.connected()
            elif self.__state == WirelessService._STATE_DISCONNECTED:
                await self.disconnected()
            await asyncio.sleep(self.thread_sleep_time)