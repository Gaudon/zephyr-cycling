import utime
import bluetooth

from service_manager import service_locator
from services.config_service import ConfigService
from services.network_service import WirelessService, BluetoothService
from services.display_service import DisplayService
from services.light_service import LightService
from services.input_service import InputService


def main():
    ############################
    # Configuration
    ############################
    service_locator.register(ConfigService())
    
    ############################
    # Service Initialization
    ############################
    
    # Output
    service_locator.register(DisplayService())
    service_locator.register(LightService())
    
    # Networking
    service_locator.register(WirelessService())
    service_locator.register(BluetoothService())
    
    # Input
    service_locator.register(InputService())


if __name__ == "__main__":
    main()