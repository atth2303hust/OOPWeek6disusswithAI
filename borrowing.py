"""
/****************/
Mã sinh viên: [DIEN_MSSV]
Họ tên: [DIEN_HO_TEN]
/****************/
Nghiệp vụ mượn/trả với validation trước khi biến đổi trạng thái.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from decimal import Decimal
from .borrowers import IBorrower
from .devices import DeviceStatus, TeachingDevice
from .exceptions import (
    BorrowLimitExceededException, DeviceAlreadyReturnedException,
    DeviceNotInSlipException, DeviceUnavailableException,
    DuplicateDeviceException, InvalidBorrowPeriodException,
    InvalidReturnDateException,
)

# QUY ƯỚC BỔ SUNG: đề bài không đưa ra đơn giá phạt trễ.
LATE_FEE_PER_DAY = Decimal('20000')


class BorrowItem:
    """Một thiết bị trên phiếu, chứa hạn mượn và lịch sử trả."""

    def __init__(
        self, device: TeachingDevice, borrowed_date: datetime,
        borrow_days: int, from_period: int = 1, to_period: int = 1,
    ) -> None:
        if device is None or not isinstance(device, TeachingDevice):
            raise ValueError('Device không hợp lệ hoặc null.')
        if not isinstance(borrowed_date, datetime):
            raise ValueError('BorrowedDate phải là datetime.')
        if type(borrow_days) is not int or not (1 <= borrow_days <= device.max_borrow_days):
            raise InvalidBorrowPeriodException(
                device.device_id, borrow_days, device.max_borrow_days
            )
        if type(from_period) is not int or type(to_period) is not int:
            raise ValueError('Số tiết phải là số nguyên.')
        count = to_period - from_period + 1
        if from_period < 1 or to_period > 12 or count < 1 or count > device.max_borrow_periods:
            raise InvalidBorrowPeriodException(
                device.device_id, count, device.max_borrow_periods, 'tiết'
            )
        self._device = device
        self._borrowed_date = borrowed_date
        self._borrow_days = borrow_days
        self._due_date = borrowed_date + timedelta(days=borrow_days)
        self._from_period = from_period
        self._to_period = to_period
        self._returned_date: datetime | None = None

    @property
    def device(self) -> TeachingDevice:
        return self._device

    @property
    def borrowed_date(self) -> datetime:
        return self._borrowed_date

    @property
    def due_date(self) -> datetime:
        return self._due_date

    @property
    def from_period(self) -> int:
        return self._from_period

    @property
    def to_period(self) -> int:
        return self._to_period

    @property
    def returned_date(self) -> datetime | None:
        return self._returned_date

    @property
    def is_returned(self) -> bool:
        return self._returned_date is not None

    def validate_return(self, returned_date: datetime) -> None:
        if self.is_returned:
            raise DeviceAlreadyReturnedException(self.device.device_id)
        if not isinstance(returned_date, datetime) or returned_date < self.borrowed_date:
            raise InvalidReturnDateException('Ngày trả không được trước ngày mượn.')

    def return_item(self, returned_date: datetime) -> None:
        """Lưu ngày trả; BorowingSlip chịu trách nhiệm cập nhật Device."""
        self.validate_return(returned_date)
        self._returned_date = returned_date

    def calculate_late_fee(self, as_of: datetime | None = None) -> Decimal:
        """Tính theo ngày lịch, phần ngày không tính thành một ngày trễ."""
        checked_date = self.returned_date or as_of
        if checked_date is None:
            return Decimal('0')
        days = max(0, (checked_date.date() - self.due_date.date()).days)
        return LATE_FEE_PER_DAY * days


class BorrowingSlip:
    """Phiếu hợp thành BorrowItem; tham chiếu IBorrower và TeachingDevice."""

    def __init__(
        self, slip_id: str, borrower: IBorrower,
        teaching_room: str, borrowed_date: datetime,
    ) -> None:
        if not isinstance(slip_id, str) or not slip_id.strip():
            raise ValueError('SlipId không hợp lệ.')
        if borrower is None or not isinstance(borrower, IBorrower):
            raise ValueError('Borrower phải cài đặt IBorrower.')
        if not isinstance(teaching_room, str) or not teaching_room.strip():
            raise ValueError('TeachingRoom không hợp lệ.')
        if not isinstance(borrowed_date, datetime):
            raise ValueError('BorrowedDate không hợp lệ.')
        self.slip_id = slip_id.strip()
        self.borrower = borrower
        self.teaching_room = teaching_room.strip()
        self.borrowed_date = borrowed_date
        self._items: list[BorrowItem] = []

    @property
    def items(self) -> tuple[BorrowItem, ...]:
        # Read-only về cấu trúc: bên ngoài không thể append hoặc remove.
        return tuple(self._items)

    def add_device(
        self, device: TeachingDevice, borrow_days: int,
        from_period: int = 1, to_period: int = 1,
    ) -> None:
        """Kiểm tra TẤT CẢ điều kiện trước khi đổi Device/Items."""
        if device is None or not isinstance(device, TeachingDevice):
            raise ValueError('TeachingDevice không hợp lệ hoặc null.')
        if type(borrow_days) is not int or not 1 <= borrow_days <= device.max_borrow_days:
            raise InvalidBorrowPeriodException(
                device.device_id, borrow_days, device.max_borrow_days
            )
        if any(item.device.device_id == device.device_id for item in self._items):
            raise DuplicateDeviceException(device.device_id)
        maximum = self.borrower.get_maximum_devices()
        if len(self._items) >= maximum:
            raise BorrowLimitExceededException(self.borrower.borrower_id, maximum)
        if device.status is not DeviceStatus.AVAILABLE:
            raise DeviceUnavailableException(device.device_id, device.status.value)

        # Constructor cũng kiểm tra số tiết; không có tác dụng phụ.
        item = BorrowItem(device, self.borrowed_date, borrow_days, from_period, to_period)
        # Bước này có thể phát sinh ngoại lệ khi một thao tác khác đã mượn thiết bị;
        # khi đó item vẫn chưa được thêm vào phiếu.
        device.mark_as_borrowed()
        self._items.append(item)

    def return_device(self, device_id: str, returned_date: datetime) -> Decimal:
        if not isinstance(device_id, str) or not device_id.strip():
            raise ValueError('DeviceId không được rỗng.')
        item = next((i for i in self._items if i.device.device_id == device_id), None)
        if item is None:
            raise DeviceNotInSlipException(device_id)
        # Thẩm định trước khi sửa trạng thái; hạn chế lỗi nửa chừng.
        item.validate_return(returned_date)
        item.device.mark_as_available()
        item.return_item(returned_date)
        return item.calculate_late_fee()

    def calculate_total_late_fee(self, as_of: datetime | None = None) -> Decimal:
        return sum((item.calculate_late_fee(as_of) for item in self._items), Decimal('0'))

    def get_overdue_items(self, as_of: datetime) -> list[BorrowItem]:
        return [i for i in self._items if not i.is_returned and as_of > i.due_date]

    def get_unreturned_items(self) -> list[BorrowItem]:
        return [i for i in self._items if not i.is_returned]
