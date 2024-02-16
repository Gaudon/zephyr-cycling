import uos
import bluetooth


class ConfigService():
    
    OP_MODE_PRIMARY = "PRIMARY"
    OP_MODE_SECONDARY = "SECONDARY"
    CONFIG_OPERATION_MODE = "OPERATION_MODE"
    
    # PIN DEFINITIONS
    BTN_BLUETOOTH_SYNC_PIN = "BTN_BLUETOOTH_SYNC_PIN"
    LED_POWER_PIN = "LED_POWER_PIN"
    LED_BLUETOOTH_PIN = "LED_BLUETOOTH_PIN"

    
    def __init__(self):
        self.config_file_name = 'config.txt'
        self.data = {}
        self.operation_mode = ConfigService.OP_MODE_PRIMARY

        if not self.file_exists(self.config_file_name):
            self.create_config_file()
        return self.load_config_file()
    
    
    async def start(self):
        self.operation_mode = self.get(ConfigService.CONFIG_OPERATION_MODE)
    
    
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
        with open(self.config_file_name, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    self.data[key.strip()] = value.strip()


    def get(self, item):
        for key, value in self.data.items():
            if key == item:
                return value       