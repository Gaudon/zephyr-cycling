import machine
import asyncio

from machine import UART
from services.service_manager import service_locator
from services.config_service import ConfigService
from services.input_service import InputService
from services.base_service import BaseService


class UartTransmitService(BaseService):
    
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
        self.uart_id = int(self.config_service.get(UartTransmitService.CONFIG_UART_ID))
        self.uart_mode_primary = (operation_mode == ConfigService._OP_MODE_PRIMARY)
        self.tx_pin = machine.Pin(int(self.config_service.get(UartTransmitService.CONFIG_UART_TX_PIN)), machine.Pin.OUT)
        self.rx_pin = machine.Pin(int(self.config_service.get(UartTransmitService.CONFIG_UART_RX_PIN)), machine.Pin.IN)
        self.buffer_size = int(self.config_service.get(UartTransmitService.CONFIG_UART_BUFFER_SIZE))
        self.baud_rate = int(self.config_service.get(UartTransmitService.CONFIG_UART_BAUD_RATE))

        # Uart
        self.uart = UART(
            self.uart_id, 
            baudrate = self.baud_rate, 
            tx = int(self.config_service.get(UartTransmitService.CONFIG_UART_TX_PIN)),
            rx = int(self.config_service.get(UartTransmitService.CONFIG_UART_RX_PIN)),
            txbuf = 1024,
            rxbuf = 1024,
            timeout_char = 100
        )
        self.uart.init(self.baud_rate, bits = self.buffer_size)

        # Data
        self.data = None


    async def start(self):       
        await asyncio.gather(
            self.run()
        )


    def update_data(self, data):
        self.data = data


    async def transmit_heart_rate_data(self):
        if self.data is not None:
            #print("[UartTransmitService] : Sending Data - {0}".format(self.data))
            self.uart.write(self.data)
            self.data = None
    

    async def run(self):
        while True:    
            await self.transmit_heart_rate_data()
            await asyncio.sleep(self.thread_sleep_time)