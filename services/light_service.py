import machine
import asyncio

from service_manager import service_locator
from services.config_service import ConfigService
from services.base_service import BaseService

class LightService(BaseService):

    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.config_service = service_locator.get(ConfigService)
        self.led_power_pin = machine.Pin(int(self.config_service.get(ConfigService.LED_POWER_PIN)), machine.Pin.OUT)
        self.led_bluetooth_pin = machine.Pin(int(self.config_service.get(ConfigService.LED_BLUETOOTH_PIN)), machine.Pin.OUT)
        self.led_bluetooth_blinking = False
        self.set_led_power(False)
        self.set_led_bluetooth(False)


    async def start(self):
        await asyncio.gather(
            self.update_bluetooth_led()
        )
            
    
    def set_led_power(self, enabled):
        if enabled:
            self.led_power_pin.on()
        else:
            self.led_power_pin.off()
    

    def set_led_bluetooth(self, enabled):
        self.led_bluetooth_blinking = False
        if not enabled:
            self.led_bluetooth_pin.on()
        else:
            self.led_bluetooth_pin.off()


    def set_led_bluetooth_blink_status(self, enabled):
        self.led_bluetooth_blinking = enabled


    async def update_bluetooth_led(self, blink_rate_ms=100):
        while True:
            if self.led_bluetooth_blinking:
                await asyncio.sleep(blink_rate_ms/1000)
                if self.led_bluetooth_pin.value() == 0:
                    self.set_led_bluetooth(False)
                else:
                    self.set_led_bluetooth(True)
            else:
                await asyncio.sleep(self.thread_sleep_time)