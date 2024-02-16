class BaseService:

	def __init__(self, operation_mode, thread_sleep_time_ms=1000):
		self.operation_mode = operation_mode
		self.thread_sleep_time_ms = thread_sleep_time_ms

	def get_operation_mode(self):
		return self.operation_mode


	def is_primary_op_mode(self):
		return self.operation_mode == ConfigService.OP_MODE_PRIMARY


	def is_secondary_op_mode(self):
		return self.operation_mode == ConfigService.OP_MODE_SECONDARY