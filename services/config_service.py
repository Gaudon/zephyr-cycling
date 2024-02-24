import uos

from utils import files


class ConfigService():
    
    _OP_MODE_PRIMARY = "PRIMARY"
    _OP_MODE_SECONDARY = "SECONDARY"
    _CONFIG_OPERATION_MODE = "OPERATION_MODE"
    
    # NETWORKING
    _WLAN_NETWORK_SSID = "WLAN_NETWORK_SSID"
    _WLAN_NETWORK_PASSWORD = "WLAN_NETWORK_PASSWORD"

    # PIN DEFINITIONS
    _BTN_BLUETOOTH_SYNC_PIN = "BTN_BLUETOOTH_SYNC_PIN"
    _LED_POWER_PIN = "LED_POWER_PIN"
    _LED_BLUETOOTH_PIN = "LED_BLUETOOTH_PIN"

    
    def __init__(self):
        self.config_file_name = 'config.txt'
        self.data = {}
        self.load_config_file()
        self.operation_mode = self.get(ConfigService._CONFIG_OPERATION_MODE)
    
    
    async def start(self):
        pass
    
    
    def get_operation_mode(self):
        return self.operation_mode


    def file_exists(self, filename):
        try:
            # Try to get file information
            uos.stat(filename)
            return True
        except OSError:
            # File does not exist or there was an error accessing it
            return False
            

    def load_config_file(self):
        with open("config/{0}".format(self.config_file_name), 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    self.data[key.strip()] = value.strip()


    def get(self, item):
        for key, value in self.data.items():
            if key == item:
                return value       