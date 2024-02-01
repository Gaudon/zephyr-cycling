import utime
import aioble
import bluetooth
import asyncio
import network
import micropython

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
    _IRQ_SCAN_DONE = const(6)
    _IRQ_PERIPHERAL_CONNECT = const(7)
    _IRQ_PERIPHERAL_DISCONNECT = const(8)
    
    
    def __init__(self):
        self.configure()
        self.BLE_UUID_HR = bluetooth.UUID(0x180D)
        self.display_service = service_locator.get(DisplayService)
        self.paired_device = None
        self.devices = []
        
    
    async def start(self):
        await asyncio.gather(
            #self.scan()
            self.aio_scan()
        )
    
    
    def configure(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.config(gap_name='Smart Fan')
        #self.ble.irq(self.bluetooth_event_handler)
    
    
    def bluetooth_event_handler(self, event, data):
        if event == _IRQ_PERIPHERAL_CONNECT:
            print("[BluetoothService] - Device Connected")
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            self.paired_device = None
            print("[BluetoothService] - Device Connected")
        elif event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            print(adv_data)
        elif event == _IRQ_SCAN_DONE:
            print("[BluetoothService] - Scan Done")
    
    
    async def aio_scan(self):
        while self.paired_device == None:
            async with aioble.scan(5000, 1280000, 11250, True) as scanner:
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
            await asyncio.sleep(5)
    
    async def scan(self):
        while True:
            print('[BluetoothService][SEARCH] - Scanning For Heart Rate Monitor(s)')
            self.ble.gap_scan(5000, 1280000, 11250, True)
            await asyncio.sleep(5)