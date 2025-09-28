import logging

from services.config_service import ConfigService

class BaseService:

	thread_sleep_time: float

	def __init__(self, thread_sleep_time: float=1):
		self.thread_sleep_time = thread_sleep_time