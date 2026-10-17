"""
/****************/
Mã sinh viên: [DIEN_MSSV]
Họ tên: [DIEN_HO_TEN]
/****************/
Interface IBorrower, giảng viên và trợ giảng.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


class IBorrower(ABC):
    """Hợp đồng trừu tượng để BorrowingSlip không phụ thuộc kiểu người mượn."""

    def __init__(self, borrower_id: str, full_name: str) -> None:
        if not isinstance(borrower_id, str) or not borrower_id.strip():
            raise ValueError('Mã người mượn không hợp lệ.')
        if not isinstance(full_name, str) or not full_name.strip():
            raise ValueError('Họ tên người mượn không hợp lệ.')
        self._borrower_id = borrower_id.strip()
        self._full_name = full_name.strip()

    @property
    def borrower_id(self) -> str:
        return self._borrower_id

    @property
    def full_name(self) -> str:
        return self._full_name

    @abstractmethod
    def get_maximum_devices(self) -> int:
        """Số thiết bị tối đa được mượn trên một phiếu."""


class Lecturer(IBorrower):
    """Giảng viên: tối đa 3 thiết bị."""

    def get_maximum_devices(self) -> int:
        return 3


class TeachingAssistant(IBorrower):
    """Trợ giảng: tối đa 2 thiết bị."""

    def get_maximum_devices(self) -> int:
        return 2
