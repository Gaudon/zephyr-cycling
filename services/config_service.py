import uos

class ConfigService:
    
    config_file_name = 'config.txt'
    data = {}
    
    def __init__(self):
        if not self.file_exists(self.config_file_name):
            self.create_config_file()
        return self.load_config_file()
        
    
    def file_exists(self, filename):
        try:
            # Try to get file information
            uos.stat(filename)
            return True
        except OSError:
            # File does not exist or there was an error accessing it
            return False


    def create_config_file(self):
        with open(config_file_name, 'w') as file:
            # Write data to the file
            file.write('# NETWORKING\n')
            file.write('NETWORK_SSID=\n')
            file.write('NETWORK_PASSWORD=\n')
            file.write('# PROFILE\n')
            file.write('MAX_HEARTRATE=\n')
            

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