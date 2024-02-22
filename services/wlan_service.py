import network
import socket
import asyncio 
import files


from service_manager import service_locator
from services.display_service import DisplayService
from services.light_service import LightService
from services.config_service import ConfigService
from services.base_service import BaseService


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
        
        
        await asyncio.gather(
            self.run() 
        )


    async def connected(self):
        if self.ap_if.active:
            if self.socket is None:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind(('', 80))
                self.socket.listen(5)
            else:
                try:
                    connection, addr = self.socket.accept()
                    print("Connection Accepted: {0}".format(addr))
                    request = connection.recv(1024)
                    response = files.read_file_as_string("../web/configuration.html")
                    connection.send("HTTP/1.0 200 OK\r\n")
                    connection.send("Content-Type: text/html\r\n\r\n")
                    connection.send(response)
                    connection.close()
                except OSError as e:
                    connection.close()
                    print("[WlanService] : Exception - {0}".format(e))

    async def run(self):
        while True:
            await self.connected()