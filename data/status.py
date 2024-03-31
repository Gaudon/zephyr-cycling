import asyncio
import logging


class Status:

    mode: str
    hrm_connected: bool
    hrm_value: int

    def __init__(self, mode: str, hrm_connected: bool, hrm_value: int):
        self.mode = mode
        self.hrm_connected = hrm_connected
        self.hrm_value = hrm_value

    def __repr__(self) -> str:
        return "[Status] : mode({0}) hr_connected({1}) hr_value({2})".format(self.mode, self.hrm_connected, self.hrm_value)