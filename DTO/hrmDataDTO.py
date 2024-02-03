class HeartRateDataDTO:
    def __init__(self):
        self.data = None
        self.value = 0
        self.measurement_format = None
        self.sensor_contact_support = False
        self.sensor_contact_detected = False

    
    def update_values(self, data):
        self.data = data
        self.measurement_format = get_measurement_format()
        self.sensor_contact_support = get_sensor_contact_support()
        self.sensor_contact_detected = get_sensor_contact_detected()
        self.value = get_measurement_value()

    
    def get_measurement_format(self):