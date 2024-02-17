class Command:

    COMMAND_TYPE_HEART_RATE = "CMD_HR"

    def __init__(self, command_type, payload):
        self.command_type = command_type
        self.payload = payload


    def get_command_type(self):
        return self.command_type
    

    def get_payload(self):
        return self.payload