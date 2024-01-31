import utime
import aioble
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
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
    
    async def start(self):
        pass
    
    
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
            

class BluetoothService:
    
    # Input/Output 
    _IO_CAPABILITY_NO_INPUT_OUTPUT = const(3)
    
    # IRQ Events
    _IRQ_SCAN_RESULT = const(5)
    _IRQ_PERIPHERAL_CONNECT = const(7)
    _IRQ_PERIPHERAL_DISCONNECT = const(8)
    
    
    def __init__(self):
        self.configure()
        self.BLE_UUID_HR = bluetooth.UUID(0x180D)
        self.display_service = service_locator.get(DisplayService)
        self.paired_device = None
        self.devices = []
        
    
    async def start(self):
        pass
#         await asyncio.gather(
#             #self.scan()
#             self.scan_devices()
#         )
    
    
    def configure(self):
        self.bt = bluetooth.BLE()
        self.bt.active(True)
        self.bt.config(gap_name='Smart Fan')
        self.bt.irq(self.bluetooth_event_handler)
    
    
    def bluetooth_event_handler(self, event, data):
        if event == _IRQ_PERIPHERAL_CONNECT:
            print("[BluetoothService] - Device Connected")
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            self.paired_device = None
            print("[BluetoothService] - Device Connected")
    
    
    async def scan(self):
        while True:
            await asyncio.sleep(5)
            print('[BluetoothService][SEARCH] - Scanning For Heart Rate Monitor(s)')
            async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner:
                async for result in scanner:
                    print(result, result.name(), result.rssi, result.services())
                    
                    
#                 async for result in scanner:
#                     print(result)
#                     device_name = result.name()
#                     device_services = result.services()
#                     if device_name is not None and device_name is not "":
#                         if self.BLE_UUID_HR in device_services:
#                             if device_name not in self.devices:
#                                 self.devices.append(device_name)
#                 print('No Results Found')
#                 if len(self.devices) == 0:
#                     print('[BluetoothService][SLEEP] - No Heart Rate Monitor Found')
#                 else:
#                     for item in self.devices:
#                         self.display_service.clear()
#                         self.display_service.print(item, self.devices.index(item))