import utime
import bluetooth
import asyncio
import aioble
import time

from service_manager import service_locator
from services.config_service import ConfigService
from services.wlan_service import WirelessService
from services.bluetooth_receive_service import BluetoothReceiveService
from services.bluetooth_transmit_service import BluetoothTransmitService
from services.light_service import LightService
from services.input_service import InputService
from services.uart_service import UartService


async def main():
    ############################
    # Configuration
    ############################
    service_locator.register(ConfigService())
    operation_mode = service_locator.get(ConfigService).get_operation_mode()

    ############################
    # Service Initialization
    ############################
    
    # Input
    service_locator.register(InputService(operation_mode, 0.05))
    
    # Output
    service_locator.register(LightService(operation_mode, 0.05))
    
    # Networking
    service_locator.register(WirelessService(operation_mode, 1))
    service_locator.register(UartService(operation_mode, 0.05))
    service_locator.register(BluetoothReceiveService(operation_mode, 1))
    service_locator.register(BluetoothTransmitService(operation_mode, 1))

    print("[SYSTEM] : Initialized - Mode [{0}]".format(operation_mode))

    # Start Services
    coroutines = []
    for service in service_locator.get_services():
        coroutines.append(service.start())
    
    await asyncio.gather(*coroutines)

        
if __name__ == "__main__":
    asyncio.run(main())
