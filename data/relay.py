import asyncio

class Relay:

    _STATE_ON = "ON"
    _STATE_OFF = "OFF"

    def __init__(self, index, pin_id, pin, state, heart_rate_threshold, enabled):
        self.index = index
        self.pin_id = pin_id
        self.pin = pin
        self.state = state
        self.heart_rate_threshold = heart_rate_threshold
        self.enabled = enabled
    
    
    async def update(self, sleep_time_ms=100):
        while True:
            if self.state == Relay._STATE_OFF:
                if self.pin.value() == 1:
                    self.pin.off()
                await asyncio.sleep(sleep_time_ms/1000)
            elif self.state == Relay._STATE_ON:
                if self.pin.value() == 0:
                    self.pin.on()
                await asyncio.sleep(sleep_time_ms/1000)
            else:
                # Unknown State
                if self.pin.value() == 1:
                    self.pin.off()
                await asyncio.sleep(sleep_time_ms/1000)