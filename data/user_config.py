import logging

class UserConfig:

    def __init__(self, json_data=None):
        self.relay_settings = []
        self.wifi_settings = {}

        if json_data:
            # Wireless Network Configuration
            self.wifi_settings['ssid'] = json_data['wifi_settings']['ssid']
            self.wifi_settings['password'] = json_data['wifi_settings']['password']

            # Fan Mode / Relay Configuration
            for config_data in json_data['relay_settings']:
                self.relay_settings.append((int(config_data[0]), bool(config_data[1]), int(config_data[2])))

            logging.debug("[UserConfig] : Loaded Config - {0} - {1}".format(self.wifi_settings['ssid'], self.relay_settings))


    def add_fan_mode(self, relay_number: int, status: bool, heart_rate: int):
        for config_num in self.relay_settings:
            if config_num[0] == relay_number:
                return
        self.relay_settings.append((relay_number, status, heart_rate))
    

    def get_relay_config(self, enabled_only: bool=False):
        if enabled_only:
            enabled_relay_config = []
            for config in self.relay_settings:
                if config[1]:
                    enabled_relay_config.append(config)
            return enabled_relay_config
        else:
            return self.relay_settings
        

    def set_wifi_info(self, ssid: str, password: str):
        self.wifi_settings['ssid'] = ssid
        self.wifi_settings['password'] = password
        

    def get_wifi_info(self):
        return (self.wifi_settings['ssid'], self.wifi_settings['password'])


    def __repr__(self) -> str:
        return "Wifi Config: {0} - Relay Config: {2}".format(self.wifi_settings, self.relay_settings)