import machine
import asyncio

from machine import UART, Pin
from service_manager import service_locator
from services.config_service import ConfigService
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


    async def start(self):
        await asyncio.gather(
            self.run()
        )
        
    
    def transmit_heart_rate_data(self, data):
        if self.uart_mode_primary:
            print("Transmitting Heart Rate Data")
            
    
    async def run(self):
        while True:    
            await asyncio.sleep(self.thread_sleep_time)