import machine
import asyncio
import json

from machine import UART, Pin
from data.command import Command
from service_manager import service_locator
from services.config_service import ConfigService
from services.input_service import InputService
from services.base_service import BaseService


class UartService(BaseService):
    
    CONFIG_UART_ID = "UART_ID"
    CONFIG_UART_MODE_PRIMARY = "UART_MODE"
    CONFIG_UART_TX_PIN = "UART_TX_PIN"
    CONFIG_UART_RX_PIN = "UART_RX_PIN"
    CONFIG_UART_BUFFER_SIZE = "UART_BUFFER_SIZE"
    CONFIG_UART_BAUD_RATE = "UART_BAUD_RATE"


    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        
        #  Services
        self.config_service = service_locator.get(ConfigService)
        self.input_service = service_locator.get(InputService)

        # Configuration
        self.uart_id = int(self.config_service.get(UartService.CONFIG_UART_ID))
        self.uart_mode_primary = bool(self.config_service.get(UartService.CONFIG_UART_MODE_PRIMARY))
        self.tx_pin = machine.Pin(int(self.config_service.get(UartService.CONFIG_UART_TX_PIN)), machine.Pin.OUT)
        self.rx_pin = machine.Pin(int(self.config_service.get(UartService.CONFIG_UART_RX_PIN)), machine.Pin.IN)
        self.buffer_size = int(self.config_service.get(UartService.CONFIG_UART_BUFFER_SIZE))
        self.baud_rate = int(self.config_service.get(UartService.CONFIG_UART_BAUD_RATE))
        self.data_rec = [self.buffer_size]

        # Uart
        self.uart = UART(self.uart_id, self.baud_rate)
        self.uart.init(self.baud_rate, bits = self.buffer_size, parity = None, stop = 1)

        # Data
        self.command = None


    async def start(self):       
        await asyncio.gather(
            self.run()
        )


    def update_data(self, command_data: Command):
        self.command = command_data


    async def transmit_heart_rate_data(self):
        if self.command is not None:
            self.uart.write(bytearray(json.dumps(self.command).encode()))
            self.command = None
    
    
    async def receive_heart_rate_data(self):
        self.data_rec = self.uart.read()
        if self.data_rec is not None:
            print(self.data_rec)
            self.data_rec = None
            #print(json.loads(self.data_rec.decode()))

    
    async def run(self):
        while True:    
            if self.uart_mode_primary:
                await self.transmit_heart_rate_data()
            else:
                await self.receive_heart_rate_data()

            await asyncio.sleep(self.thread_sleep_time)