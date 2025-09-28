import asyncio
import logging


class BluetoothStatus:
    def __init__(self, state: str = "Unknown", device_name: str = "None", device_list: list = None):
        self.state = state
        self.device_name = device_name
        self.device_list = device_list if device_list is not None else []

    def to_dict(self):
        return {
            "state": self.state,
            "device_name": self.device_name,
            "device_list": [
                {"name": name, "address": addr, "address_type": addr_type} for (name, addr, addr_type) in self.device_list
            ]
        }


class WlanStatus:
    def __init__(self, state: str = "Unknown", network_name: str = "None"):
        self.state = state
        self.network_name = network_name
    
    
    def to_dict(self):
        return {
            "state": self.state,
            "network_name": self.network_name
        }


class Status:
    def __init__(self, mode: str, ble_status: BluetoothStatus, wlan_status: WlanStatus):
        self._mode = mode
        self.ble_status = ble_status
        self.wlan_status = wlan_status

    def __repr__(self) -> str:
        return "[Status] : mode({}) ble(state={}, device={}) wlan(state={}, network={})".format(
            self._mode,
            self.ble_status.state, self.ble_status.device_name,
            self.wlan_status.state, self.wlan_status.network_name
        )