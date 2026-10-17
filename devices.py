"""
/****************/
Mã sinh viên: [DIEN_MSSV]
Họ tên: [DIEN_HO_TEN]
/****************/
Abstract Device, TeachingDevice và ba kiểu thiết bị kế thừa.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from enum import Enum

from .exceptions import DeviceUnavailableException, InvalidDeviceStateException


class DeviceStatus(str, Enum):
    """Gộp các trạng thái xuất hiện ở hai phần của đề bài."""

    AVAILABLE = 'Available'
    BORROWED = 'Borrowed'
    UNDER_MAINTENANCE = 'UnderMaintenance'
    RETIRED = 'Retired'


class Device(ABC):
    """Lớp trừu tượng: quản lý dữ liệu và hợp đồng tính bảo trì."""

    def __init__(
        self, device_id: str, name: str, introduced_year: int,
        purchase_price: Decimal | int | str,
        status: DeviceStatus = DeviceStatus.AVAILABLE,
    ) -> None:
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError('Mã thiết bị không được rỗng.')
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Tên thiết bị không được rỗng.')
        if (type(introduced_year) is not int or introduced_year < 1
                or introduced_year > date.today().year):
            raise ValueError('Năm sử dụng phải hợp lệ và không vượt năm hiện tại.')
        try:
            price = Decimal(str(purchase_price))
        except Exception as error:
            raise ValueError('Giá mua phải là một số hợp lệ.') from error
        if not price.is_finite() or price <= 0:
            raise ValueError('Giá mua phải lớn hơn 0.')
        if not isinstance(status, DeviceStatus):
            raise ValueError('Trạng thái thiết bị không hợp lệ.')

        self._device_id = device_id.strip()  # Read-only qua property.
        self._name = name.strip()
        self._introduced_year = introduced_year
        self._purchase_price = price
        self._status = status

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def introduced_year(self) -> int:
        return self._introduced_year

    @property
    def purchase_price(self) -> Decimal:
        return self._purchase_price

    @property
    def status(self) -> DeviceStatus:
        return self._status

    def mark_as_borrowed(self) -> None:
        """Chỉ thiết bị Available được chuyển sang Borrowed."""
        if self._status is not DeviceStatus.AVAILABLE:
            raise DeviceUnavailableException(self.device_id, self._status.value)
        self._status = DeviceStatus.BORROWED

    def mark_as_available(self) -> None:
        """Chỉ hoàn trả từ Borrowed về Available."""
        if self._status is not DeviceStatus.BORROWED:
            raise InvalidDeviceStateException(
                f'Không thể trả {self.device_id} khi trạng thái là {self._status.value}.'
            )
        self._status = DeviceStatus.AVAILABLE

    def send_to_maintenance(self) -> None:
        """Không bảo trì thiết bị đang được mượn hoặc đã thanh lý."""
        if self._status is not DeviceStatus.AVAILABLE:
            raise InvalidDeviceStateException(
                f'Không thể bảo trì {self.device_id} ({self._status.value}).'
            )
        self._status = DeviceStatus.UNDER_MAINTENANCE

    def finish_maintenance(self) -> None:
        if self._status is not DeviceStatus.UNDER_MAINTENANCE:
            raise InvalidDeviceStateException('Thiết bị không ở trạng thái bảo trì.')
        self._status = DeviceStatus.AVAILABLE

    @abstractmethod
    def calculate_annual_maintenance_cost(self) -> Decimal:
        """Đa hình: mỗi loại thiết bị có công thức riêng."""

    def __str__(self) -> str:
        return (
            f'{self.__class__.__name__}(id={self.device_id}, tên={self.name}, '
            f'năm={self.introduced_year}, trạng thái={self.status.value})'
        )


class TeachingDevice(Device, ABC):
    """Thiết bị giảng dạy hỗ trợ giới hạn ngày và số tiết mượn."""

    max_borrow_days: int
    max_borrow_periods: int


class ProjectorRemote(TeachingDevice):
    """Điều khiển máy chiếu: tối đa 5 ngày, 6 tiết; bảo trì 5% giá."""

    max_borrow_days = 5
    max_borrow_periods = 6

    def calculate_annual_maintenance_cost(self) -> Decimal:
        return (self.purchase_price * Decimal('0.05')).quantize(Decimal('1'))


class AirConditionerRemote(TeachingDevice):
    """Điều khiển điều hòa: tối đa 2 ngày, 8 tiết; bảo trì 4% giá."""

    max_borrow_days = 2
    max_borrow_periods = 8

    def calculate_annual_maintenance_cost(self) -> Decimal:
        return (self.purchase_price * Decimal('0.04')).quantize(Decimal('1'))


class WirelessMicrophone(TeachingDevice):
    """Micro không dây: tối đa 1 ngày, 4 tiết; bảo trì 10% giá."""

    max_borrow_days = 1
    max_borrow_periods = 4

    def calculate_annual_maintenance_cost(self) -> Decimal:
        return (self.purchase_price * Decimal('0.10')).quantize(Decimal('1'))
