import asyncio
import time

from machine import Pin
from data.relay import Relay
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
        self.last_relay_change = time.ticks_ms()


    async def start(self):
        await self.register_callbacks()

        for i in range(1, 9):
            self.relays.append(
                Relay(
                    i,
                    int(self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)),
                    Pin(int(self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i))),
                    Relay._STATE_OFF,
                    None,
                    False
                )
            )

        coroutines = []
        for relay in self.relays:
            coroutines.append(relay.update())
        
        await asyncio.gather(
            self.run(),
            *coroutines
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
            if self.mode == FanService.__MODE_HEARTRATE:
                target_relay = self.get_relay_for_heartrate()
                current_relay = self.get_current_relay()

                if current_relay is not None and target_relay is not None:
                    if target_relay.pin_id is not current_relay.pin_id:
                        if (target_relay.heart_rate_threshold < current_relay.heart_rate_threshold) and (time.ticks_ms() - self.last_relay_change >= 15000):
                            self.enable_relay(target_relay)

            await asyncio.sleep(self.thread_sleep_time)
    

    def enable_relay(self, relay):
        # Disable all other relays
        for relay in self.relays:
            relay.state = Relay._STATE_OFF

        # Enable the target relay
        relay.state = Relay._STATE_ON
        self.last_relay_change = time.ticks_ms()
        

    def on_heart_rate_received(self, data):
        self.heart_rate_value = data[1]


    def on_manual_mode_button_short_press(self):
        if self.mode == FanService.__MODE_MANUAL:
            for current_relay in self.relays:
                if current_relay.state == Relay._STATE_ON:
                    next_relay = self.find_next_enabled_relay(current_relay)

                    if next_relay is not current_relay:
                        self.enable_relay(next_relay)

        elif self.mode == FanService.__MODE_HEARTRATE:
            # Reserved for future functionality.
            pass


    def on_manual_mode_button_long_press(self):
        if self.mode == FanService.__MODE_HEARTRATE:
            self.mode = FanService.__MODE_MANUAL
        else:
            self.mode = FanService.__MODE_HEARTRATE

    
    def update_user_config(self, user_config):
        for relay_config in user_config.get_relay_config():
            for relay in self.relays:
                if int(relay_config[0]) == relay.index_id:
                    relay.enabled = bool(relay_config[1])
                    relay.heart_rate_threshold = int(relay_config[2])
                    break
                    

    def filter_active(self, relay):
        return relay.enabled
    

    def get_current_relay(self):
        for relay in self.relays:
            if relay.enabled and relay.state == Relay._STATE_ON:
                return relay
            

    def get_relay_for_heartrate(self):
        target_relay = None
        for relay in self.relays:
            if relay.enabled:
                if target_relay is None or self.heart_rate_value >= relay.heart_rate_threshold:
                    target_relay = relay
        
        return target_relay


    def find_next_enabled_relay(self, current_relay):
        # Find the index of the current relay
        current_index = self.relays.index(current_relay)

        # Search for the next enabled relay
        for i in range(1, len(self.relays)):
            next_index = (current_index + i) % len(self.relays)
            next_relay = self.relays[next_index]
            if next_relay.enabled:
                return next_relay

        # If no next enabled relay found, return the current relay
        return current_relay