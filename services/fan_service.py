import asyncio
import json
import time

from machine import Pin, I2C
from data.user_config import UserConfig
from services.service_manager import service_locator
from services.base_service import BaseService
from services.config_service import ConfigService
from services.user_service import UserService
from services.input_service import InputService
from services.bluetooth_receive_service import BluetoothReceiveService


class FanService(BaseService):

    __MODE_HEARTRATE = "MODE_HEARTRATE"
    __MODE_MANUAL = "MODE_MANUAL"


    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.config_service = service_locator.get(ConfigService)
        self.bluetooth_receive_service = service_locator.get(BluetoothReceiveService)
        self.input_service = service_locator.get(InputService)
        self.user_service = service_locator.get(UserService)
        self.mode = FanService.__MODE_HEARTRATE
        self.heart_rate_value = 0
        self.relays = []
        self.active_relays = []
        self.last_relay_change = time.ticks_ms()
        self.user_config = None


    async def start(self):
        await self.register_callbacks()

        for i in range(1, 9):
            self.relays.append((i, Pin(int(self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)))))
        
        await asyncio.gather(
            self.run()
        )


    async def register_callbacks(self):
        self.bluetooth_receive_service.register_callback(
            BluetoothReceiveService._EVENT_HEART_RATE_RECEIVED, 
            self.on_heart_rate_received
        )

        self.input_service.register_callback(
            self.config_service.get(ConfigService._BTN_MANUAL_MODE_PIN), 
            self.on_manual_mode_button_short_press, 
            InputService._BTN_CALLBACK_SHORT_PRESS
        )

        self.input_service.register_callback(
            self.config_service.get(ConfigService._BTN_MANUAL_MODE_PIN), 
            self.on_manual_mode_button_long_press, 
            InputService._BTN_CALLBACK_LONG_PRESS
        )

        self.user_service.register_callback(self.update_user_config)
        
    
    async def run(self):
        while True:
            # TODO(Gaudon) : Implement
            # Compare current heart rate values to user settings and relay indexes
            await asyncio.sleep(self.thread_sleep_time)
    

    def enable_relay(self, relay_pin):
        # Disable all other relays
        for relay in self.relays:
            relay[1].off()

        # Enable the target relay
        for relay in self.relays:
            if relay[0] == relay_pin:
                relay[1].on()
        

    def on_heart_rate_received(self, data):
        self.heart_rate_value = data[1]


    def on_manual_mode_button_short_press(self):
        if self.mode == FanService.__MODE_MANUAL:
            for i in range(0, len(self.active_relays)):
                # Find the active relay
                if self.relays[i][1].value() == 1:
                    # Disable the current active relay
                    self.relays[i][1].off()

                    # Enable the next relay
                    if i == (len(self.active_relays) - 1):
                        self.relays[int(self.active_relays[0][0]) - 1][1].on()
                    else:
                        self.relays[int(self.active_relays[i+1][0] - 1)][1].on()
                    break
        elif self.mode == FanService.__MODE_HEARTRATE:
            # We probably don't want any functionality here.
            pass


    def on_manual_mode_button_long_press(self):
        if self.mode == FanService.__MODE_HEARTRATE:
            self.mode = FanService.__MODE_MANUAL
        else:
            self.mode = FanService.__MODE_HEARTRATE

    
    def update_user_config(self, user_config):
        self.user_config = user_config
        self.active_relays = self.user_config.get_fan_config(True)