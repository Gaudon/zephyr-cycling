import asyncio
import logging
import gc
import sys

from services.service_manager import service_locator
from services.config_service import ConfigService
from services.user_service import UserService
from services.wlan_service import WirelessService
from services.bluetooth_receive_service import BluetoothReceiveService
from services.bluetooth_transmit_service import BluetoothTransmitService
from services.light_service import LightService
from services.input_service import InputService
from services.uart_receive_service import UartReceiveService
from services.uart_transmit_service import UartTransmitService
from services.fan_service import FanService


async def main():
    ############################
    # Configuration
    ############################
    service_locator.register(ConfigService())
    operation_mode = service_locator.get(ConfigService).get_operation_mode()

    logging.basicConfig(level=logging.DEBUG)
    logging.debug("[SYSTEM] : Version - {0}".format(sys.version))

    ############################
    # Service Initialization
    ############################
    
    # Common Services
    service_locator.register(InputService(operation_mode, 0.05))

    if operation_mode == ConfigService._OP_MODE_PRIMARY:
        service_locator.register(UserService(operation_mode, 0.5))
        service_locator.register(LightService(operation_mode, 0.5))
        service_locator.register(WirelessService(operation_mode, 0.5))
        service_locator.register(BluetoothReceiveService(operation_mode, 0.5))
        service_locator.register(UartTransmitService(operation_mode, 0.05))
        service_locator.register(FanService(operation_mode, 0.5))
    else:
        service_locator.register(UartReceiveService(operation_mode, 0.05))
        service_locator.register(BluetoothTransmitService(operation_mode, 0.5))

    logging.info("[SYSTEM] : Initialized - Mode [{0}]".format(operation_mode))

    # Start Services
    coroutines = []
    for service in service_locator.get_services():
        coroutines.append(service.start())

    coroutines.append(cleanup())

    # Start Web Server
    if operation_mode == ConfigService._OP_MODE_PRIMARY:
        gc.collect()
        from web import server
        coroutines.append(server.app.start_server(port=80, debug=True))

    await asyncio.gather(*coroutines)


async def cleanup():
    __last_memory_value = 0
    while True:
        gc.collect()
        if int(gc.mem_alloc() / gc.mem_free() * 100) != __last_memory_value:
            __last_memory_value = int(gc.mem_alloc() / gc.mem_free() * 100)
            logging.debug(f"[SYSTEM] : Memory - {gc.mem_alloc()} of {gc.mem_free()} bytes used ({__last_memory_value}%).")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())