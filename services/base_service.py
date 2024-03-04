import logging

from services.config_service import ConfigService

class BaseService:

	operation_mode: str
	thread_sleep_time: float

	def __init__(self, operation_mode: str, thread_sleep_time: float=1):
		self.operation_mode = operation_mode
		self.thread_sleep_time = thread_sleep_time


	def get_operation_mode(self):
		return self.operation_mode


	def is_primary_op_mode(self):
		return self.operation_mode == ConfigService._OP_MODE_PRIMARY


	def is_secondary_op_mode(self):
		return self.operation_mode == ConfigService._OP_MODE_SECONDARY