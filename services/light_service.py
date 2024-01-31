import machine
import asyncio

class LightService:
    def __init__(self):
        self.led_power_pin = machine.Pin(16, machine.Pin.OUT)
        self.led_wlan_pin = machine.Pin(17, machine.Pin.OUT)
        self.set_power(False)
    
    
    async def start(self):
        await asyncio.gather(
            self.toggle()
        )
            
    
    def set_power(self, enabled):
        if enabled:
            self.led_power_pin.on()
        else:
            self.led_power_pin.off()
    
    
    async def toggle(self):
        while True:
            await asyncio.sleep(1)
            if self.led_power_pin.value() == 1:
                self.set_power(False)
            else:
                self.set_power(True)
            
         
    def set_wlan(self, enabled):
        if enabled:
            self.led_wlan_pin.on()
        else:
            self.led_wlan_pin.off()