import utime
import aioble
import bluetooth
import asyncio
import micropython

from micropython import const

from service_manager import service_locator
from services.display_service import DisplayService
from services.light_service import LightService
from services.config_service import ConfigService
from services.uart_service import UartService


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
        self.display_service = service_locator.get(DisplayService)
        self.uart_service = service_locator.get(UartService)
        self.connection = None
        self.connected_device_name = ""
        self.data = None
        self.sleep_duration = 5
        self.reconnect_interval = 10
        
        # Device Info
        self.svc_device_info = aioble.Service(self._SVC_DEVICE_INFO)        
        aioble.Characteristic(self.svc_device_info, self._CHAR_MANUFACTURER_NAME_STR, read=True, initial='Pico Fan')
        aioble.Characteristic(self.svc_device_info, self._CHAR_MODEL_NUMBER_STR, read=True, initial='PF-0001')
        aioble.Characteristic(self.svc_device_info, self._CHAR_SERIAL_NUMBER_STR, read=True, initial='G-PF-982987')
        aioble.Characteristic(self.svc_device_info, self._CHAR_FIRMWARE_REV_STR, read=True, initial='0.0.1')
        aioble.Characteristic(self.svc_device_info, self._CHAR_HARDWARE_REV_STR, read=True, initial='0.0.1')
        
        # Heart Rate
        self.svc_heart_rate = aioble.Service(self._SVC_HEART_RATE)
        aioble.Characteristic(self.svc_heart_rate, self._CHAR_HEART_RATE_MEASUREMENT, read=True)
        
        # Register Services
        aioble.register_services(self.svc_device_info, self.svc_heart_rate)
        
        
    async def start(self):
        await asyncio.gather(
            self.scan(),
            self.get_data()
        )

    
    def configure(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self._SVC_DEVICE_INFO = bluetooth.UUID(0x180A)
        self._SVC_HEART_RATE = bluetooth.UUID(0x180D)
        self._CHAR_HEART_RATE_MEASUREMENT = bluetooth.UUID(0x2A37)
        self._CHAR_MANUFACTURER_NAME_STR = bluetooth.UUID(0x2A29)
        self._CHAR_MODEL_NUMBER_STR = bluetooth.UUID(0x2A24)
        self._CHAR_SERIAL_NUMBER_STR = bluetooth.UUID(0x2A25)
        self._CHAR_FIRMWARE_REV_STR = bluetooth.UUID(0x2A26)
        self._CHAR_HARDWARE_REV_STR = bluetooth.UUID(0x2A27)
    
    
    async def get_data(self):
        hrm_service = None
        hrm_char = None
        self.hrm_subscribed = False
        
        while True:
            # Update the display screen
            self.update_display()
            
            if self.connection is not None:
                try:
                   if hrm_service is None:
                       hrm_service = await self.connection.service(self._SVC_HEART_RATE)
                       print("Service : {}".format(hrm_service.uuid))
                   
                   if hrm_char is None:
                       hrm_char = await hrm_service.characteristic(self._CHAR_HEART_RATE_MEASUREMENT)
                       print("Characteristic : {}".format(hrm_char.uuid))
                     
                   if self.hrm_subscribed is False: 
                       await hrm_char.subscribe(notify=True)
                       self.hrm_subscribed = True
                   
                   # HRM Specificiation States Heart Rate Measurements Must Be Notified (Not Read)
                   data = await hrm_char.notified()
                   flag_data = data[0]
                   self.data = data[1]
                   
                   print("HRM Data Received - {} bpm".format(self.data))
                except Exception as e:
                    print(type(e).__name__)
                    print("[BluetoothService][Exception] - {}".format(e))
                    self.connection = None
                    self.data = None
            await asyncio.sleep(1)
                            
    
    def update_display(self):
        if self.connected_device_name is "" or self.connected_device_name is None:
            self.display_service.print("No Device")
        else:
            if self.data is not None:
                self.display_service.print("{} [{}]".format(str(self.data), self.connected_device_name))
            else:
                self.display_service.print("0")
    
    
    def get_bits(self, byte, start_bit, num_bits):
        mask = (1 << num_bits) - 1
        mask = mask << start_bit
        result = (byte & mask) >> start_bit
        return result


    async def scan(self):
        while True:
            if self.connection == None:
                async with aioble.scan(5000, 1280000, 11250, True) as scanner:
                    async for result in scanner:
                        self.connected_device_name = result.name()
                        device_services = result.services()

                        if self._SVC_HEART_RATE in device_services:
                            try:
                                self.connection = await result.device.connect(timeout_ms=10000)
                            except asyncio.TimeoutError:
                                print('[BluetoothService][TIMEOUT] - Could not connect to device.')
              
                print('[BluetoothService][SLEEP]({}) - No heart rate monitor found.'.format(self.sleep_duration))
                await asyncio.sleep(self.sleep_duration)
            await asyncio.sleep(self.reconnect_interval)
