"""
/****************/
Mã sinh viên: [DIEN_MSSV]
Họ tên: [DIEN_HO_TEN]
/****************/
ClassRoom kết tập danh sách Device.
"""

from __future__ import annotations
from datetime import date
from decimal import Decimal
from .devices import Device, DeviceStatus


class ClassRoom:
    """Thiết bị tồn tại độc lập với phòng học (aggregation)."""

    def __init__(self, room_id: str, room_name: str, capacity: int) -> None:
        if not isinstance(room_id, str) or not room_id.strip():
            raise ValueError('Mã phòng không hợp lệ.')
        if not isinstance(room_name, str) or not room_name.strip():
            raise ValueError('Tên phòng không hợp lệ.')
        if type(capacity) is not int or capacity <= 0:
            raise ValueError('Sức chứa phải dương.')
        self.room_id = room_id.strip()
        self.room_name = room_name.strip()
        self.capacity = capacity
        self._devices: dict[str, Device] = {}

    @property
    def devices(self) -> tuple[Device, ...]:
        return tuple(self._devices.values())

    def add_device(self, device: Device) -> None:
        if device is None or not isinstance(device, Device):
            raise ValueError('Thiết bị phải là một đối tượng Device, không được null.')
        if device.device_id in self._devices:
            raise ValueError(f'Mã thiết bị {device.device_id} đã nằm trong phòng.')
        self._devices[device.device_id] = device

    def remove_device(self, device_id: str) -> bool:
        return self._devices.pop(device_id, None) is not None

    def find_device(self, device_id: str) -> Device | None:
        return self._devices.get(device_id)

    def calculate_annual_maintenance_cost(self) -> Decimal:
        # ĐA HÌNH: gọi cùng một method trên lớp cha, không cần if/switch theo loại.
        return sum((device.calculate_annual_maintenance_cost()
                    for device in self._devices.values()), Decimal('0'))

    def get_devices_requiring_maintenance(self, today: date | None = None) -> list[Device]:
        today = today or date.today()
        return [
            device for device in self._devices.values()
            if device.status is DeviceStatus.UNDER_MAINTENANCE
            or today.year - device.introduced_year > 5
        ]
