import machine
import asyncio

from service_manager import service_locator
from services.config_service import ConfigService
from services.base_service import BaseService

class LightService(BaseService):

    def __init__(self):
        self.config_service = service_locator.get(ConfigService)
        self.led_power_pin = machine.Pin(int(self.config_service.get(ConfigService.LED_POWER_PIN)), machine.Pin.OUT)
        self.led_bluetooth_pin = machine.Pin(int(self.config_service.get(ConfigService.LED_BLUETOOTH_PIN)), machine.Pin.OUT)
        self.led_bluetooth_blinking = False
        self.set_led_power(False)
        self.set_led_bluetooth(False)
    

    async def start(self):
        pass
            
    
    def set_led_power(self, enabled):
        if enabled:
            self.led_power_pin.on()
        else:
            self.led_power_pin.off()
    

    def set_led_bluetooth(self, enabled):
        if enabled:
            self.led_bluetooth_pin.on()
        else:
            self.led_bluetooth_pin.off()

    
    async def led_bluetooth_blink(self, blinking=True, blink_rate_ms=500):
        self.led_bluetooth_blinking = blinking
        self.set_led_bluetooth(blinking)

        while self.led_bluetooth_blinking:
            await asyncio.sleep_ms(blink_rate_ms)
            if self.led_bluetooth_blinking.value() == 1:
                self.set_led_bluetooth(False)
            else:
                self.set_led_bluetooth(True)