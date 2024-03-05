import asyncio
import logging

from machine import Pin


class Relay:

    index: int
    pin_id: int
    pin: Pin
    state: str
    heart_rate_threshold: int
    enabled: bool

    _STATE_ON = "ON"
    _STATE_OFF = "OFF"


    def __init__(self, index: int, pin_id: int, pin: Pin, state: str, heart_rate_threshold: int, enabled: bool):
        self.index = index
        self.pin_id = pin_id
        self.pin = pin
        self.state = state
        self.heart_rate_threshold = heart_rate_threshold
        self.enabled = enabled
        logging.debug("[Relay] : Initialized - {0}".format(self))
    
    
    async def update(self, sleep_time_ms: int=150):
        while True:
            if self.state == Relay._STATE_OFF:
                if self.pin.value() == 1:
                    self.pin.off()
                await asyncio.sleep(sleep_time_ms/1000)
            elif self.state == Relay._STATE_ON:
                if self.pin.value() == 0:
                    logging.debug("[Relay] : Enabled - PinID [{0}] Index [{1}]".format(self.pin_id, self.index))
                    self.pin.on()
                await asyncio.sleep(sleep_time_ms/1000)
            else:
                # Unknown State
                if self.pin.value() == 1:
                    self.pin.off()
                await asyncio.sleep(sleep_time_ms/1000)


    def __repr__(self) -> str:
        return "[Relay] : index({0}) pin({1}) state({2}) enabled({3}) target({4})".format(self.index, self.pin_id, self.state, self.enabled, self.heart_rate_threshold)