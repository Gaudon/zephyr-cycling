class HeartRateCommand:

    COMMAND_HEART_RATE = "HeartRateCommand"

    def __init__(self, command_type, payload):
        self.command_type = HeartRateCommand.COMMAND_HEART_RATE
        self.payload = payload


    def get_command_type(self):
        return self.command_type
    

    def get_payload(self):
        return self.payload