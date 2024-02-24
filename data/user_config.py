class UserConfig:

    def __init__(self):
        self.fan_config = []
        self.wifi_password = None


    def add_fan_mode(self, relay_number, status, heart_rate):
        for config_num in self.fan_config:
            if config_num[0] == relay_number:
                return
        self.fan_config.append((relay_number, status, heart_rate))

    
    def get_fan_config(self):
        return self.fan_config