import utime
import bluetooth
import asyncio

from service_manager import service_locator
from services.config_service import ConfigService
from services.network_service import WirelessService, BluetoothService
from services.display_service import DisplayService
from services.light_service import LightService
from services.input_service import InputService
   

async def test2():
    while True:
        print("Test 2")
        await asyncio.sleep(2)


async def main():
    ############################
    # Configuration
    ############################
    #service_locator.register(ConfigService())
    
    ############################
    # Service Initialization
    ############################
    
    # Input
    service_locator.register(InputService())
    
    # Output
    #service_locator.register(DisplayService())
    service_locator.register(LightService())
    
    # Networking
    #service_locator.register(WirelessService())
    #service_locator.register(BluetoothService())
    
    # Start Services
    coroutines = []
    for service in service_locator.get_services():
        coroutines.append(service.start())
    
    await asyncio.gather(*coroutines)

        
if __name__ == "__main__":
    asyncio.run(main())
