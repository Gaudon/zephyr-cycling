from services.config_service import ConfigService

class BaseService:

	def __init__(self, operation_mode, thread_sleep_time=1):
		self.operation_mode = operation_mode
		self.thread_sleep_time = thread_sleep_time


	def get_operation_mode(self):
		return self.operation_mode


	def is_primary_op_mode(self):
		return self.operation_mode == ConfigService._OP_MODE_PRIMARY


	def is_secondary_op_mode(self):
		return self.operation_mode == ConfigService._OP_MODE_SECONDARY