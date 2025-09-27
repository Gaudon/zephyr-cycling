import machine
import asyncio

from services.service_manager import service_locator
from services.config_service import ConfigService
from services.base_service import BaseService
from data.led import Led

class LightService(BaseService):

    _LED_POWER = "POWER"
    _LED_BLUETOOTH = "BLUETOOTH"
    _LED_FAN_MODE = "FAN_MODE"
    _LED_WIFI = "WIFI"

    def __init__(self, thread_sleep_time):
        BaseService.__init__(self, thread_sleep_time)
        self.leds = []

        # Services
        self.config_service = service_locator.get(ConfigService)        
        

    async def start(self):
        self.leds.append(
            Led(
                self.config_service.get(ConfigService._LED_POWER_PIN), 
                machine.Pin(int(self.config_service.get(ConfigService._LED_POWER_PIN)), machine.Pin.OUT),
                Led._STATE_OFF
            )
        )

        self.leds.append(
            Led(
                self.config_service.get(ConfigService._LED_BLUETOOTH_PIN), 
                machine.Pin(int(self.config_service.get(ConfigService._LED_BLUETOOTH_PIN)), machine.Pin.OUT),
                Led._STATE_OFF,
                250
            )
        )

        self.leds.append(
            Led(
                self.config_service.get(ConfigService._LED_MANUAL_FAN_PIN), 
                machine.Pin(int(self.config_service.get(ConfigService._LED_MANUAL_FAN_PIN)), machine.Pin.OUT),
                Led._STATE_OFF
            )
        )

        self.leds.append(
            Led(
                self.config_service.get(ConfigService._LED_WIFI_PIN), 
                machine.Pin(int(self.config_service.get(ConfigService._LED_WIFI_PIN)), machine.Pin.OUT),
                Led._STATE_OFF
            )
        )
        
        coroutines = []

        for led in self.leds:
            coroutines.append(led.update())

        await asyncio.gather(*coroutines)
               

    def set_led_state(self, led, state):
        for l in self.leds:
            target_pin_id = None
            if led == LightService._LED_BLUETOOTH:
                target_pin_id = self.config_service.get(ConfigService._LED_BLUETOOTH_PIN)
            elif led == LightService._LED_POWER:
                target_pin_id = self.config_service.get(ConfigService._LED_POWER_PIN)
            elif led == LightService._LED_FAN_MODE:
                target_pin_id = self.config_service.get(ConfigService._LED_MANUAL_FAN_PIN)
            elif led == LightService._LED_WIFI:
                target_pin_id = self.config_service.get(ConfigService._LED_WIFI_PIN)

            if target_pin_id is not None and l.pin_id == target_pin_id:
                l.state = state
                break