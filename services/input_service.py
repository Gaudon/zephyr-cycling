import machine
import asyncio
import time

from services.service_manager import service_locator
from services.config_service import ConfigService
from services.base_service import BaseService
from data.button import Button


class InputService(BaseService):

    _BTN_CALLBACK_SHORT_PRESS = "BTN_CALLBACK_SHORT_PRESS"
    _BTN_CALLBACK_LONG_PRESS = "BTN_CALLBACK_LONG_PRESS"

    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.config_service = service_locator.get(ConfigService)
        self.long_press_duration_ms = 3000
        self.buttons = []
        if self.operation_mode == ConfigService._OP_MODE_PRIMARY:
            # Add Bluetooth Button
            self.buttons.append(
                Button(
                    int(self.config_service.get(ConfigService._BTN_BLUETOOTH_SYNC_PIN)), 
                    machine.Pin(int(self.config_service.get(ConfigService._BTN_BLUETOOTH_SYNC_PIN)), machine.Pin.IN), 
                    200, 
                    3000
                )
            )

            # Add Manual Mode Operation Button
            self.buttons.append(
                Button(
                    int(self.config_service.get(ConfigService._BTN_MANUAL_MODE_PIN)), 
                    machine.Pin(int(self.config_service.get(ConfigService._BTN_MANUAL_MODE_PIN)), machine.Pin.IN), 
                    200, 
                    3000
                )
            )

    
    async def start(self):
        if self.config_service.get_operation_mode() == ConfigService._OP_MODE_PRIMARY:
            coroutines = []
            for button in self.buttons:
                coroutines.append(button.update())
            
            await asyncio.gather(*coroutines)
        
    
    def register_callback(self, pin_id, function_handler, button_callback_type):
        for btn in self.buttons:
            if int(btn.pin_id) == int(pin_id):
                if button_callback_type == InputService._BTN_CALLBACK_SHORT_PRESS:
                    btn.register_short_press_callback(function_handler)
                elif button_callback_type == InputService._BTN_CALLBACK_LONG_PRESS:
                    btn.register_long_press_callback(function_handler)