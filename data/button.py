import time

class Button:

	STATE_UP = "STATE_UP"
	STATE_DOWN = "STATE_DOWN"

	def __init__(self, pin_id, pin, short_press_time_ms=200, long_press_time_ms=3000):
		self.pin_id = pin_id
		self.pin = pin
		self.last_update = 0
		self.init_time_ms = time.ticks_ms()
		self.state = (Button.STATE_UP, self.init_time_ms)
		self.prev_state = (None, self.init_time_ms)
		self.short_press_time_ms = short_press_time_ms
		self.long_press_time_ms = long_press_time_ms
		self.short_press_listeners = []
		self.long_press_listeners = []


	def update(self):
		self.state[2] += 0 - self.last_update


	def get_pin(self):
		return (self.pin_id, self.pin)


	def get_state(self):
		return self.state


	def get_prev_state(self):
		return self.prev_state


	def pressed(self):
		if self.state[0] == Button.STATE_UP:
			self.prev_state = self.state
			self.state = (Button.STATE_DOWN, time.ticks_ms())


	def released(self):
		if self.state[0] == Button.STATE_DOWN:
			self.prev_state = self.state
			self.state = (Button.STATE_UP, time.ticks_ms())
			if self.state[1] - self.prev_state[1] >= self.long_press_time_ms:
				for listener in self.long_press_listeners:
					listener()
			else:
				for listener in self.short_press_listeners:
					listener()


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