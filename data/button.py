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

	_STATE_UP = "STATE_UP"
	_STATE_DOWN = "STATE_DOWN"

	def __init__(self, pin_id: int, pin: Pin, short_press_time_ms: int=200, long_press_time_ms: int=3000, between_presses_time_ms: int=1000):
		self.pin_id = pin_id
		self.pin = pin
		self.last_update = time.ticks_ms()
		self.init_time_ms = time.ticks_ms()
		self.__state = (Button._STATE_UP, self.init_time_ms)
		self.__prev_state = (Button._STATE_UP, self.init_time_ms)
		self.short_press_time_ms = short_press_time_ms
		self.long_press_time_ms = long_press_time_ms
		self.between_presses_time_ms = between_presses_time_ms
		self.short_press_listeners = []
		self.long_press_listeners = []


	async def update(self):
		while True:
			if time.ticks_ms() - self.last_update >= self.between_presses_time_ms:
				if self.pin.value() == 1:
					if self.__state[0] == Button._STATE_UP:
						self.set_state(Button._STATE_DOWN)
				else:
					if self.__state[0] == Button._STATE_DOWN:
						self.set_state(Button._STATE_UP)
						if self.__state[1] - self.__prev_state[1] >= self.long_press_time_ms:
							for listener in self.long_press_listeners:
								listener()
						else:
							for listener in self.short_press_listeners:
								listener()
			await asyncio.sleep(0.01)


	def set_state(self, state):
		self.__prev_state = self.__state
		self.__state = (state, time.ticks_ms())
		self.last_update = time.ticks_ms()


	def register_short_press_callback(self, callback):
		self.short_press_listeners.append(callback)


	def register_long_press_callback(self, callback):
		self.long_press_listeners.append(callback)