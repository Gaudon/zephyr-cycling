import machine
import asyncio

from services.network_service import WirelessService, BluetoothService
from service_manager import service_locator

class InputService:
    def __init__(self):
        self.btn_wlan_toggle = machine.Pin(14, machine.Pin.IN)
        self.btn_ble_scan = machine.Pin(15, machine.Pin.IN)
        self.wireless_service = service_locator.get(WirelessService)
        self.bluetooth_service = service_locator.get(BluetoothService)
        asyncio.run(self.check_inputs())

    async def check_inputs(self):
        while True:
            if self.btn_wlan_toggle.value() == 1:
                self.wireless_service.toggle()
            if self.btn_ble_scan.value() == 1:
                asyncio.run(self.bluetooth_service.scan())
            await asyncio.sleep_ms(200)
