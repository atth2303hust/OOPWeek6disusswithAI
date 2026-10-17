"""
/****************/
Mã sinh viên: [DIEN_MSSV]
Họ tên: [DIEN_HO_TEN]
/****************/
Các ngoại lệ nghiệp vụ mượn/trả thiết bị.
"""

from __future__ import annotations


class BorrowingException(Exception):
    """Lớp cha cho mọi lỗi phát sinh trong nghiệp vụ mượn/trả."""


class DeviceUnavailableException(BorrowingException):
    """Thiết bị không ở trạng thái cho mượn."""

    def __init__(self, device_id: str, current_status: object):
        self.device_id = device_id
        self.current_status = current_status
        super().__init__(f"Thiết bị {device_id} không khả dụng ({current_status}).")


class BorrowLimitExceededException(BorrowingException):
    """Người mượn đã đạt số thiết bị tối đa trên một phiếu."""

    def __init__(self, borrower_id: str, maximum_devices: int):
        self.borrower_id = borrower_id
        self.maximum_devices = maximum_devices
        super().__init__(
            f"Người mượn {borrower_id} chỉ được mượn tối đa "
            f"{maximum_devices} thiết bị/phiếu."
        )


class InvalidBorrowPeriodException(BorrowingException):
    """Thời hạn mượn hoặc khoảng tiết mượn không hợp lệ."""

    def __init__(self, device_id: str, requested: int, maximum: int, unit: str = 'ngày'):
        self.device_id = device_id
        self.requested = requested
        self.maximum = maximum
        self.unit = unit
        super().__init__(
            f"Thời hạn của {device_id}: yêu cầu {requested} {unit}; "
            f"giới hạn {maximum} {unit} và giá trị phải dương."
        )


class DuplicateDeviceException(BorrowingException):
    """Một thiết bị đã xuất hiện trong chính phiếu mượn đó."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        super().__init__(f"Thiết bị {device_id} đã nằm trong phiếu mượn.")


class DeviceNotInSlipException(BorrowingException):
    """Yêu cầu trả thiết bị không thuộc phiếu."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        super().__init__(f"Không tìm thấy thiết bị {device_id} trong phiếu.")


class DeviceAlreadyReturnedException(BorrowingException):
    """Không được trả một thiết bị hai lần."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        super().__init__(f"Thiết bị {device_id} đã được trả trước đó.")


class InvalidReturnDateException(BorrowingException):
    """Ngày trả trước ngày mượn hoặc không có kiểu ngày hợp lệ."""


class InvalidDeviceStateException(BorrowingException):
    """Chuyển trạng thái thiết bị không hợp lệ."""
