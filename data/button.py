import time
import asyncio

from machine import Pin

class Button:

	pin_id: int
	pin: Pin
	last_update: int
	init_time_ms: int
	state: tuple
	prev_state: tuple
	short_press_time_ms: int
	long_press_time_ms: int

	STATE_UP = "STATE_UP"
	STATE_DOWN = "STATE_DOWN"

	def __init__(self, pin_id: int, pin: Pin, short_press_time_ms: int=200, long_press_time_ms: int=3000):
		self.pin_id = pin_id
		self.pin = pin
		self.last_update = 0
		self.init_time_ms = time.ticks_ms()
		self.state = (Button.STATE_UP, self.init_time_ms)
		self.prev_state = (Button.STATE_UP, self.init_time_ms)
		self.short_press_time_ms = short_press_time_ms
		self.long_press_time_ms = long_press_time_ms
		self.short_press_listeners = []
		self.long_press_listeners = []


	async def update(self):
		while True:
			if self.pin.value() == 1:
				if self.state[0] == Button.STATE_UP:
					self.prev_state = self.state
					self.state = (Button.STATE_DOWN, time.ticks_ms())
			else:
				if self.state[0] == Button.STATE_DOWN:
					self.prev_state = self.state
					self.state = (Button.STATE_UP, time.ticks_ms())
					if self.state[1] - self.prev_state[1] >= self.long_press_time_ms:
						for listener in self.long_press_listeners:
							listener()
					else:
						for listener in self.short_press_listeners:
							listener()
			await asyncio.sleep(0.005)


	def register_short_press_callback(self, callback):
		self.short_press_listeners.append(callback)


	def register_long_press_callback(self, callback):
		self.long_press_listeners.append(callback)