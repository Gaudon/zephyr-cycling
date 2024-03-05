import asyncio
from machine import Pin


class Led:

    pin_id: int
    pin: Pin
    state: str
    blink_time_ms: int
    active_low: bool

    _STATE_ON = "ON"
    _STATE_OFF = "OFF"
    _STATE_BLINKING = "BLINKING"
        

    def __init__(self, pin_id: int, pin: Pin, state: str, blink_time_ms: int=500, active_low: bool=False):
        self.pin_id = pin_id
        self.pin = pin
        self.state = state
        self.active_low = active_low
        self.blink_time_ms = blink_time_ms


    async def update(self, sleep_time_ms: int=250):
        while True:
            if self.state == Led._STATE_OFF:
                self.pin.on() if self.active_low else self.pin.off()
                await asyncio.sleep(sleep_time_ms/1000)
            elif self.state == Led._STATE_ON:
                self.pin.off() if self.active_low else self.pin.on()
                await asyncio.sleep(sleep_time_ms/1000)
            elif self.state == Led._STATE_BLINKING:
                if self.pin.value() == 0:
                    self.pin.on()
                else:
                    self.pin.off()
                await asyncio.sleep(self.blink_time_ms/1000)
            else:
                # Unknown State
                await asyncio.sleep(sleep_time_ms/1000)