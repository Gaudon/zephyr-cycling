import asyncio
import json

from machine import Pin, I2C
from data.user_config import UserConfig
from services.service_manager import service_locator
from services.base_service import BaseService
from services.config_service import ConfigService
from services.input_service import InputService
from services.bluetooth_receive_service import BluetoothReceiveService


class FanService(BaseService):

    __MODE_HEARTRATE = "MODE_HEARTRATE"
    __MODE_MANUAL = "MODE_MANUAL"

    _STATE_CURRENT = None
    _STATE_PREV = None

    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.config_service = service_locator.get(ConfigService)
        self.bluetooth_receive_service = service_locator.get(BluetoothReceiveService)
        self.input_service = service_locator.get(InputService)
        self.mode = FanService.__MODE_HEARTRATE
        self.heart_rate_value = 0
        self.fan_config = []


    async def start(self):
        await self.register_callbacks()

        for i in range(1, 9):
            self.fan_config.append((i, Pin(int(self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)))))
        
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
        
    
    async def run(self):
        # TODO(Gaudon) : Implement
        # Compare current heart rate values to user settings and relay indexes
        await asyncio.sleep(self.thread_sleep_time)
    

    def enable_relay(self, relay_pin):
        # Disable all other relays
        for config in self.fan_config:
            config[1].off()

        # Enable the target relay
        for config in self.fan_config:
            if config[0] == relay_pin:
                config[1].on()
        

    def on_heart_rate_received(self, data):
        self.heart_rate_value = data[1]


    def on_manual_mode_button_short_press(self):
        if self.mode == FanService.__MODE_MANUAL:
            pass


    def on_manual_mode_button_long_press(self):
        if self.mode == FanService.__MODE_HEARTRATE:
            self.mode = FanService.__MODE_MANUAL
        else:
            self.mode = FanService.__MODE_HEARTRATE