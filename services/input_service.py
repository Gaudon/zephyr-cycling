import machine
import asyncio

from service_manager import service_locator
from services.config_service import ConfigService
from services.base_service import BaseService
from data.button import Button


class InputService(BaseService):

    BTN_CALLBACK_SHORT_PRESS = "BTN_CALLBACK_SHORT_PRESS"
    BTN_CALLBACK_LONG_PRESS = "BTN_CALLBACK_LONG_PRESS"

    def __init__(self, operation_mode, thread_sleep_time_ms):
        BaseService.__init__(self, operation_mode, thread_sleep_time_ms)
        self.config_service = service_locator.get(ConfigService)
        self.long_press_duration_ms = 3000
        self.buttons = []
        self.buttons.append(
            Button(
                self.config_service.get("BTN_BLUETOOTH_SYNC_PIN"), 
                machine.Pin(int(self.config_service.get("BTN_BLUETOOTH_SYNC_PIN")), machine.Pin.IN), 
                200, 
                3000
            )
        )
        self.button_hold_count = 0.0

    
    async def start(self):
        if self.config_service.get_operation_mode() == ConfigService.OP_MODE_PRIMARY:
            await asyncio.gather(
                self.check_inputs()
            )
        
    
    def register_callback(self, pin, function_handler, button_callback_type):
        for btn in self.buttons:
            if btn.get_pin()[0] == pin:
                if button_callback_type == InputService.BTN_CALLBACK_SHORT_PRESS:
                    btn.register_short_press_callback(function_handler)
                elif button_callback_type == InputService.BTN_CALLBACK_LONG_PRESS:
                    btn.register_long_press_callback(function_handler)



    async def check_inputs(self):
        while True:
            await asyncio.sleep_ms(self.thread_sleep_time_ms)
            for btn in self.buttons:
                if btn.get_pin()[1].value() == 1:
                    # Button is being held
                    self.button_hold_count += self.thread_sleep_time_ms
                else:
                    if self.button_hold_count >= self.long_press_duration_ms:
                        print("Button Was Held For {0}ms".format(self.button_hold_count))
                    elif self.button_hold_count != 0:
                        print("Button Was Pressed")
                    self.button_hold_count = 0.0