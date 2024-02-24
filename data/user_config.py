class UserConfig:

    def __init__(self):
        self.fan_config = []
        self.wifi_password = None


    def add_fan_mode(self, relay_number, heart_rate):
        for mode in self.fan_config:
            if mode[0] == relay_number:
                return
        self.fan_config.append((relay_number, heart_rate))

    
    def get_fan_config(self):
        return self.fan_config