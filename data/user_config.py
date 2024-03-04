import logging

class UserConfig:

    wifi_password: str

    def __init__(self, json_data=None):
        self.relay_config = []
        self.wifi_password = ""

        if json_data is not None:
            self.wifi_password = json_data['wifi_password']
            for config_data in json_data['fan_config']:
                self.relay_config.append((int(config_data[0]), bool(config_data[1]), int(config_data[2])))
            logging.debug("[UserConfig] : Loaded Config - {0}".format(self.relay_config))


    def add_fan_mode(self, relay_number: int, status: bool, heart_rate: int):
        for config_num in self.relay_config:
            if config_num[0] == relay_number:
                return
        self.relay_config.append((relay_number, status, heart_rate))
    

    def get_relay_config(self, enabled_only: bool=False):
        if enabled_only:
            enabled_relay_config = []
            for config in self.relay_config:
                if config[1]:
                    enabled_relay_config.append(config)
            return enabled_relay_config
        else:
            return self.relay_config
        

    def __repr__(self) -> str:
        return "Wifi Password: {0} - Relay Config: {1}".format(self.wifi_password, self.relay_config)