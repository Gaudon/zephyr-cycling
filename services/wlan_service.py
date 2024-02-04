import network

class WirelessService:
    def __init__(self):
        self.display_service = service_locator.get(DisplayService)
        self.light_service = service_locator.get(LightService)
        self.config_service = service_locator.get(ConfigService)
        self.wlan = network.WLAN(network.STA_IF)        
        
    
    async def start(self):
        self.wlan.active(False)
        self.wlan.deinit()
    
    
    def connect(self, ssid, password):   
        if not self.wlan.isconnected():
            self.wlan.connect(ssid, password)
            
            while not self.wlan.isconnected():
                utime.sleep(3)
                
        self.light_service.set_wlan(True)
    
    
    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()
            self.light_service.set_wlan(False)


    def toggle(self):
        if self.wlan.isconnected():
            self.disconnect()
        else:
            self.connect(self.config_service.get('NETWORK_SSID'), self.config_service.get('NETWORK_PASSWORD'))