import machine
import asyncio
import json

from machine import UART, Pin
from data.heart_rate_command import HeartRateCommand
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

    CALLBACK_RX = "RX"
    CALLBACK_TX = "TX"


    def __init__(self, operation_mode, thread_sleep_time):
        BaseService.__init__(self, operation_mode, thread_sleep_time)
        
        #  Services
        self.config_service = service_locator.get(ConfigService)
        self.input_service = service_locator.get(InputService)

        # Configuration
        self.uart_id = int(self.config_service.get(UartService.CONFIG_UART_ID))
        self.uart_mode_primary = (operation_mode == ConfigService._OP_MODE_PRIMARY)
        self.tx_pin = machine.Pin(int(self.config_service.get(UartService.CONFIG_UART_TX_PIN)), machine.Pin.OUT)
        self.rx_pin = machine.Pin(int(self.config_service.get(UartService.CONFIG_UART_RX_PIN)), machine.Pin.IN)
        self.buffer_size = int(self.config_service.get(UartService.CONFIG_UART_BUFFER_SIZE))
        self.baud_rate = int(self.config_service.get(UartService.CONFIG_UART_BAUD_RATE))
        self.data_rec = bytearray()

        # Uart
        self.uart = UART(
            self.uart_id, 
            baudrate = self.baud_rate, 
            tx = int(self.config_service.get(UartService.CONFIG_UART_TX_PIN)),
            rx = int(self.config_service.get(UartService.CONFIG_UART_RX_PIN)),
            txbuf = 1024,
            rxbuf = 1024,
            timeout_char = 100
        )
        self.uart.init(self.baud_rate, bits = self.buffer_size)

        # Listeners
        self.listeners = []


    async def start(self):       
        await asyncio.gather(
            self.run()
        )


    def update_data(self, data):
        self.data_rec = data
        print("[UartService] : Data Updated - {0}".format(data))


    def register_callback(self, type, function_handler):
        self.listeners.append(
            (type, function_handler)
        )


    async def transmit_heart_rate_data(self):
        if self.data_rec is not None:
            self.uart.write(self.data_rec)
            self.data_rec = None
    
    
    async def receive_heart_rate_data(self):
        while self.uart.any() > 0:
            self.data_rec = self.uart.read()
        
        if self.data_rec is not None:
            try:
                heart_rate_value = json.loads(self.data_rec.decode('utf-8'))['payload']
                print("[UartService] : Data Received - {1}".format(self.data_rec))
                
                for listener in self.listeners:
                    if listener[0] == UartService.CALLBACK_RX:
                        listener[1](self.data_rec)
                
                self.data_rec = None
            except:
                pass


    async def run(self):
        while True:    
            if self.uart_mode_primary:
                await self.transmit_heart_rate_data()
            else:
                await self.receive_heart_rate_data()

            await asyncio.sleep(self.thread_sleep_time)