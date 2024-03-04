import json
import asyncio
import logging

from services.base_service import BaseService
from data.user_config import UserConfig


class UserService(BaseService):
    
    
    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        self.config_file_name = 'user.json'
        self.user_config = None
        self.user_config_update_listeners = []
        self.update_user_config()

    
    async def start(self):
        await asyncio.gather(
            self.run()
        )
    

    async def run(self):
        while True:
            await asyncio.sleep(self.thread_sleep_time)


    def get_user_config(self):
        if self.user_config is None:
            self.update_user_config()
        return self.user_config


    def register_callback(self, function_handler):
        self.user_config_update_listeners.append(function_handler)
        function_handler(self.user_config)


    def update_user_config(self):
        with open("/config/user.json", "r") as file:
            json_data = json.load(file)
            self.user_config = UserConfig(json_data)
            file.close()

        for listener in self.user_config_update_listeners:
            listener(self.user_config)