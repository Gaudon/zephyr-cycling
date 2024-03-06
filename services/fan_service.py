import asyncio
import time
import logging

from machine import Pin
from data.relay import Relay
from data.led import Led
from services.service_manager import service_locator
from services.base_service import BaseService
from services.config_service import ConfigService
from services.user_service import UserService
from services.input_service import InputService
from services.light_service import LightService
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
        self.light_service = service_locator.get(LightService)
        self.mode = FanService.__MODE_HEARTRATE
        self.heart_rate_value = (0, time.ticks_ms())
        self.relays = []
        self.last_relay_change = time.ticks_ms()
        self.last_relay_update = time.ticks_ms()
        self.time_in_lower_hr_zone = 0


    async def start(self):
        for i in range(1, 9):
            self.relays.append(
                Relay(
                    i,
                    int(self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)),
                    Pin(int(self.config_service.get(ConfigService._RELAY_PIN_PREFIX, i)), mode=Pin.OUT),
                    Relay._STATE_OFF,
                    0,
                    False
                )
            )

        await self.register_callbacks()

        coroutines = []
        coroutines.append(self.run())
        coroutines.append(self.check_for_stale_data())
        for relay in self.relays:
            coroutines.append(relay.update())

        await asyncio.gather(*coroutines)


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
                
                if target_relay is not None:
                    if current_relay is None:
                        self.enable_relay(target_relay)
                    else:
                        if target_relay.pin_id is not current_relay.pin_id:
                            if target_relay.heart_rate_threshold < current_relay.heart_rate_threshold: 
                                if self.time_in_lower_hr_zone >= 15000:
                                    self.enable_relay(target_relay)
                                else:

                                if time.ticks_ms() - self.last_relay_change >= 15000:
                                    self.enable_relay(target_relay)
                            else:
                                self.enable_relay(target_relay)
                        else:
                            # if the target relay is the currently active one, reset the internal counter.
                            self.time_in_lower_hr_zone = 0
            
            self.last_relay_update = time.ticks_ms()
            await asyncio.sleep(self.thread_sleep_time)
    

    async def check_for_stale_data(self):
        max_hrt = 0

        while True:
            if self.heart_rate_value[1] is not 0:
                # Stale heart rate data detected
                if time.ticks_ms() - self.heart_rate_value[1] >= 30000:
                    for r in self.relays:
                        if r.enabled:
                            if r.heart_rate_threshold >= max_hrt or max_hrt == 0:
                                max_hrt = r.heart_rate_threshold
            
                self.heart_rate_value = (int(0.75 * max_hrt), 0)
            await asyncio.sleep(self.thread_sleep_time)


    def disable_all_relays(self):
        # Disable all other relays
        for r in self.relays:
            r.state = Relay._STATE_OFF


    def enable_relay(self, relay):
        # Disable all other relays
        self.disable_all_relays()

        # Enable the target relay
        relay.state = Relay._STATE_ON
        self.last_relay_change = time.ticks_ms()
        self.time_in_lower_hr_zone = 0
        

    def on_heart_rate_received(self, data):
        self.heart_rate_value = (data[1], time.ticks_ms())


    def on_manual_mode_button_short_press(self):
        if self.mode == FanService.__MODE_MANUAL:
            relay_on = False
            for current_relay in self.relays:
                if current_relay.state == Relay._STATE_ON:
                    relay_on = True
                    next_relay = self.find_next_enabled_relay(current_relay)

                    if next_relay is None:
                        self.disable_all_relays()
                        return
                    elif next_relay.pin_id is not current_relay.pin_id:
                        self.enable_relay(next_relay)
                        break

            # No relays are active, enable the first.
            if not relay_on:
                self.enable_relay(self.relays[0])

        elif self.mode == FanService.__MODE_HEARTRATE:
            # Reserved for future functionality.
            pass


    def on_manual_mode_button_long_press(self):
        if self.mode == FanService.__MODE_HEARTRATE:
            self.change_fan_mode(FanService.__MODE_MANUAL)
        else:
            self.change_fan_mode(FanService.__MODE_HEARTRATE)
        

    def change_fan_mode(self, mode):
        self.mode = mode

        # Disable all relays
        for r in self.relays:
            r.state = Relay._STATE_OFF

        self.light_service.set_led_state(
            LightService._LED_FAN_MODE, 
            Led._STATE_OFF if (mode == FanService.__MODE_HEARTRATE) else Led._STATE_ON
        )
        logging.debug("[FanService] : Mode Changed - {0}".format(self.mode))


    def update_user_config(self, user_config):
        relays_configured = []
        for relay in self.relays:
            for relay_config in user_config.get_relay_config():
                if int(relay_config[0]) == int(relay.index) and relay.index not in relays_configured:
                    relay.enabled = bool(relay_config[1])
                    relay.heart_rate_threshold = int(relay_config[2])
                    relays_configured.append(relay.index)
                    logging.debug("[FanService] : Relay Updated - {0}".format(relay))
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
                if self.heart_rate_value[0] >= relay.heart_rate_threshold:
                    target_relay = relay
        
        if target_relay is not None:
            logging.debug("[FanService] : Target Relay ({0}) HRT ({1}) HR ({2})".format(target_relay.pin_id, target_relay.heart_rate_threshold, self.heart_rate_value[0]))

        return target_relay


    def find_next_enabled_relay(self, current_relay):
        # Find the index of the current relay
        current_index = self.relays.index(current_relay)

        # Search for the next enabled relay
        for i in range(1, len(self.relays)):
            next_index = (current_index + i) % len(self.relays)
            next_relay = self.relays[next_index]
            if next_relay.enabled:
                if self.relays.index(next_relay) > current_index:
                    return next_relay
                else:
                    return None

        # If no next enabled relay found, return the current relay
        return current_relay