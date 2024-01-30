import machine

class LightService:
    def __init__(self):
        # Define the onboard LED pins
        self.led_power_pin = machine.Pin(16, machine.Pin.OUT)
        self.led_wlan_pin = machine.Pin(17, machine.Pin.OUT)
        self.set_power(True)
    
    def set_power(self, enabled):
        if enabled:
            self.led_power_pin.on()
        else:
            self.led_power_pin.off()
        
    def set_wlan(self, enabled):
        if enabled:
            self.led_wlan_pin.on()
        else:
            self.led_wlan_pin.off()