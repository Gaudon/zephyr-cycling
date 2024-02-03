from machine import Pin, I2C
import ssd1306

class DisplayService:
    def __init__(self):
        self.i2c = I2C(1, sda=Pin(26), scl=Pin(27))
        self.display = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.display.text("Pico Fan!", 0, 0)
        self.display.show()
        self.line_height = 8


    async def start(self):
        pass


    def print(self, text, line):
        self.clear(line)
        self.display.text(text, 0, line * self.line_height)
        self.display.show()          


    def clear(self, line=None):
        if line is None:   
            self.display.fill(0)
            self.display.show()
        else:
            self.display.fill_rect(0, line * self.line_height, 0, line * self.line_height + self.line_height, 0)
