import utime
#import aioble
import bluetooth
import asyncio
import network

from micropython import const

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
    
    # Input/Output 
    _IO_CAPABILITY_NO_INPUT_OUTPUT = const(3)
    
    # IRQ Events
    _IRQ_SCAN_RESULT = const(5)
    _IRQ_PERIPHERAL_CONNECT = const(7)
    _IRQ_PERIPHERAL_DISCONNECT = const(8)
    
    
    def __init__(self):
        self.bt = bluetooth.BLE
        self.configure()
        self.bt.active(True)
        self.BLE_UUID_HR = bluetooth.UUID(0x180D)
        self.display_service = service_locator.get(DisplayService)
        self.paired_device = None
        asyncio.run(self.scan())
    
    
    def configure(self):
        self.bt.config(gap_name='Smart Fan')
        self.bt.irq(handler=self.bluetooth_event_handler)
    
    
    def bluetooth_event_handler(self, event, data):
        if event == _IRQ_SCAN_RESULT:
            print("[BluetoothService] - Device Detected - {}".format(data))
        elif event == _IRQ_PERIPHERAL_CONNECT:
            print("[BluetoothService] - Device Connected")
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            self.paired_device = None
            print("[BluetoothService] - Device Connected")
    
    
    async def scan(self, interval=10):
        self.devices = []
        
        while self.paired_device == None:
            print('[BluetoothService][SEARCH] - Scanning For Heart Rate Monitor(s)')
            async with aioble.scan(interval * 1000, interval_us=30000, window_us=30000, active=True) as scanner:
                async for result in scanner:
                    device_name = result.name()
                    device_services = result.services()
                    if device_name is not None and device_name is not "":
                        if self.BLE_UUID_HR in device_services:
                            if device_name not in self.devices:
                                self.devices.append(device_name)
           
                if len(self.devices) == 0:
                    print('[BluetoothService][SLEEP] - No Heart Rate Monitor Found')
                else:
                    for item in self.devices:
                        self.display_service.clear()
                        self.display_service.print(item, self.devices.index(item))
                        
            await asyncio.sleep(10)  
