import machine
import asyncio

from service_manager import service_locator
from services.config_service import ConfigService
from services.base_service import BaseService

class LightService(BaseService):

    _LED_STATE_ON = "ON"
    _LED_STATE_OFF = "OFF"
    _LED_STATE_BLINKING = "BLINKING"

    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        
        # Services
        self.config_service = service_locator.get(ConfigService)
        
        # Lights
        self.led_power = (
            self.config_service.get(ConfigService._LED_POWER_PIN),
            machine.Pin(int(self.config_service.get(ConfigService._LED_POWER_PIN)), machine.Pin.OUT),
            LightService._LED_STATE_OFF
        )
        
        self.led_bluetooth = (
            self.config_service.get(ConfigService._LED_BLUETOOTH_PIN),
            machine.Pin(int(self.config_service.get(ConfigService._LED_BLUETOOTH_PIN)), machine.Pin.OUT),
            LightService._LED_STATE_OFF
        )


    async def start(self):
        await asyncio.gather(
            self.update_led_bluetooth()
        )
               

    def set_led_bluetooth_state(self, state):
        self.led_bluetooth = (
            self.led_bluetooth[0],
            self.led_bluetooth[1],
            state
        )


    async def update_led_bluetooth(self, blink_rate_ms=500):
        while True:
            if self.led_bluetooth[2] == LightService._LED_STATE_OFF:
                self.led_bluetooth[1].on()
                await asyncio.sleep(self.thread_sleep_time)
            elif self.led_bluetooth[2] == LightService._LED_STATE_ON:
                self.led_bluetooth[1].off() # Active Low
                await asyncio.sleep(self.thread_sleep_time)
            elif self.led_bluetooth[2] == LightService._LED_STATE_BLINKING:
                if self.led_bluetooth[1].value() == 0:
                    self.led_bluetooth[1].on()
                else:
                    self.led_bluetooth[1].off()
                await asyncio.sleep(blink_rate_ms/1000)

            