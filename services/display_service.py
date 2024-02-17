from machine import Pin, I2C
from lib import ssd1306

class DisplayService:
    def __init__(self):
        self.i2c = I2C(1, sda=Pin(26), scl=Pin(27))
        self.display = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.screen_height = 32
        self.screen_width = 128
        self.line_height = 8


    async def start(self):
        self.clear()
        self.display.show()


    def print_header(self):
        self.display.text("Pico Fan v0.1", 0, 0)


    def print(self, text):
        self.clear()
        self.display.text(text, 0, 2 * self.line_height)
        self.display.show()


    def clear(self):
        self.display.fill(0)
        self.print_header()