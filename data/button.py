class Button:

	def __init__(self, pin_id, pin, short_press_time_ms=200, long_press_time_ms=3000):
		self.pin_id = pin_id
		self.pin = pin
		self.short_press_time_ms = short_press_time_ms
		self.long_press_time_ms = long_press_time_ms
		self.short_press_listeners = []
		self.long_press_listeners = []


	def get_pin(self):
		return (self.pin_id, self.pin)


	def register_short_press_callback(self, callback):
		self.short_press_listeners.append(callback)


	def register_long_press_callback(self, callback):
		self.long_press_listeners.append(callback)


	def short_press(self):
		for listener in short_press_listeners:
			listener()


	def long_press(self):
		for listener in long_press_listeners:
			listener()