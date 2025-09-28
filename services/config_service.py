import uos
import json

from utils import files
from data.user_config import UserConfig


class ConfigService():
    
    # PIN DEFINITIONS
    _BTN_BLUETOOTH_SYNC_PIN = "BTN_BLUETOOTH_SYNC_PIN"
    _BTN_MANUAL_MODE_PIN = "BTN_MANUAL_MODE_PIN"
    _BTN_SYSTEM_RESET_PIN = "BTN_SYSTEM_RESET_PIN"
    _LED_MANUAL_FAN_PIN = "LED_MANUAL_FAN_PIN"
    _LED_POWER_PIN = "LED_POWER_PIN"
    _LED_BLUETOOTH_PIN = "LED_BLUETOOTH_PIN"
    _LED_WIFI_PIN = "LED_WIFI_PIN"
    _RELAY_PIN_PREFIX = "RELAY_PIN_"

    
    def __init__(self):
        self.config_file_name = 'config.txt'
        self.data = {}
        self.load_config()
    
    
    async def start(self):
        pass
    

    def file_exists(self, filename):
        try:
            # Try to get file information
            uos.stat(filename)
            return True
        except OSError:
            # File does not exist or there was an error accessing it
            return False
            

    def load_config(self):
        with open("config/{0}".format(self.config_file_name), 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    self.data[key.strip()] = value.strip()


    def get(self, item, index=None):
        for key, value in self.data.items():
            if index is not None:
                if "{0}{1}".format(item, index) == key:
                    return value
            elif key == item:
                return value       