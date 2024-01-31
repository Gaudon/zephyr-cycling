import machine
import asyncio

from service_manager import service_locator

class InputService:
    def __init__(self):
        self.buttons = []
        
        for i in range(0, 4):
            self.buttons.append(machine.Pin(i, machine.Pin.IN))
            print("Button Registered: PIN [{}]".format(i))
        
        asyncio.run(self.check_inputs())

    async def check_inputs(self):
        while True:
            if self.buttons[0].value() == 1:
                print("Button Pressed: [1]")
            if self.buttons[1].value() == 1:
                print("Button Pressed: [2]")
            if self.buttons[2].value() == 1:
                print("Button Pressed: [3]")
            if self.buttons[3].value() == 1:
                print("Button Pressed: [4]")
                machine.reset()
            await asyncio.sleep_ms(200)
