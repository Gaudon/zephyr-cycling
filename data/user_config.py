class UserConfig:

    def __init__(self, json_data=None):
        self.fan_config = []
        self.wifi_password = None

        if json_data is not None:
            self.wifi_password = json_data['wifi_password']
            # TODO(Gaudon) : Implement
            self.fan_config = []


    def add_fan_mode(self, relay_number, status, heart_rate):
        for config_num in self.fan_config:
            if config_num[0] == relay_number:
                return
        self.fan_config.append((relay_number, status, heart_rate))
    

    def get_fan_config(self, enabled_only=False):
        if enabled_only:
            enabled_fan_config = []
            for config in self.fan_config:
                if config[1]:
                    enabled_fan_config.append(config)
            return enabled_fan_config
        else:
            return self.fan_config