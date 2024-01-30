from machine import Pin, I2C
import ssd1306

class DisplayService:
    def __init__(self):
        self.i2c = I2C(1, sda=Pin(26), scl=Pin(27))
        self.display = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        self.display.text("Gaudon Fan", 0, 0)
        self.display.show()

    def print(self, text, line):
        self.display.text(text, 0, line * 16)
        self.display.show()          

    def clear(self):
        self.display.fill(0)
        self.display.show()
