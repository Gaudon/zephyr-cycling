import utime
import aioble
import uasyncio as asyncio
import bluetooth
import network

from service_manager import service_locator
from services.display_service import DisplayService
from services.light_service import LightService
from services.config_service import ConfigService


class WirelessService:
    def __init__(self):
        self.display_service = service_locator.get(DisplayService)
        self.light_service = service_locator.get(LightService)
        self.config_service = service_locator.get(ConfigService)
        
    def connect(self, ssid, password):
        wlan = network.WLAN(network.STA_IF)
    
        if not wlan.isconnected():
            self.display_service.clear()
            self.display_service.print('Scan Wifi...', 0)
            wlan.active(True)
            wlan.connect(ssid, password)
            
            while not wlan.isconnected():
                utime.sleep(3)

        self.light_service.set_wlan(True)
        self.display_service.clear()
        self.display_service.print(ssid, 0)
        self.display_service.print(wlan.ifconfig()[0], 1)
    
    def disconnect(self, wlan):
        if wlan.isconnected():
            wlan.disconnect()
            self.display_service.clear()
            self.display_service.print('WiFi Off', 0)
            self.light_service.set_wlan(False)

    def toggle(self):
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():
            self.disconnect(wlan)
        else:
            self.connect(self.config_service.get('NETWORK_SSID'), self.config_service.get('NETWORK_PASSWORD'))
            

class BluetoothService:
    def __init__(self):
        self.bt = bluetooth.BLE()
        self.bt.active(True)
        self.BLE_UUID_HR = bluetooth.UUID(0x180D)
        self.display_service = service_locator.get(DisplayService)

    async def scan(self, duration=10):
        self.devices = []
        self.display_service.clear()
        self.display_service.print('BLE Scanning...', 0)
        
        async with aioble.scan(duration * 1000, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                device_name = result.name()
                device_services = result.services()
                if device_name is not None and device_name is not "":
                    if self.BLE_UUID_HR in device_services:
                        if device_name not in self.devices:
                            devices.append(result.name())
    
        self.display_service.clear()
        if len(self.devices) == 0:
            self.display_service.print('No HRM Found', 0)
        for item in self.devices:
            self.display_service.print(item, self.devices.index(item))