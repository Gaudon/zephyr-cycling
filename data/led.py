import asyncio

class Led:

    _STATE_ON = "ON"
    _STATE_OFF = "OFF"
    _STATE_BLINKING = "BLINKING"


    def __init__(self, pin_id, pin, state, blink_time_ms=500):
        self.pin_id = pin_id
        self.pin = pin
        self.state = state
        self.blink_time_ms = blink_time_ms


    def get_pin(self):
        return (self.pin_id, self.pin)


    def set_state(self, state):
        self.state = state


    def get_state(self):
        return self.state
    

    async def update(self, sleep_time_ms=1000):
        while True:
            if self.state == Led._STATE_OFF:
                self.pin.on()
                await asyncio.sleep(sleep_time_ms/1000)
            elif self.state == Led._STATE_ON:
                self.pin.off() # Active Low
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