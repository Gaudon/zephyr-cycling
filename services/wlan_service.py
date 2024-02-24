import network
import socket
import asyncio 
import utils.files as files
import json

from services.service_manager import service_locator
from services.display_service import DisplayService
from services.light_service import LightService
from services.config_service import ConfigService
from services.base_service import BaseService
from data.user_config import UserConfig
from lib.microdot import Microdot, send_file, Request


app = Microdot()

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

        # Start the web server
        app.run(port=80, debug=True)
        

    @app.route('/', methods=['GET', 'POST'])
    async def root(request):
        if request.method == 'GET':
            return files.read_file_as_string("../web/configuration.html"), 200, {'Content-Type': 'text/html'}
        elif request.method == 'POST':
            # Process the form data
            form_data = []
            user_config = UserConfig()
            for i in range(1, 8):
                user_config.add_fan_mode(
                    request.form.get("en{0}".format(i)), 
                    request.form.get("hr{0}".format(i))
                )

            with open('..\\config\\user.json', 'w') as file:
                file.write(json.dumps(user_config))
                file.close()
    

    @app.route('resources/<path:path>', methods=['GET'])
    async def resources(request, path):
        if '..' in path:
            return 'Not found', 404
        return send_file('../web/resources/' + path, max_age=86400)