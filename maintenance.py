"""
/****************/
Mã sinh viên: [DIEN_MSSV]
Họ tên: [DIEN_HO_TEN]
/****************/
Mở rộng có giải thích: hợp đồng bảo trì (tiêu đề đề bài, chưa có đặc tả lớp).
"""

from __future__ import annotations
from datetime import date
from decimal import Decimal
from .devices import Device


class MaintenanceContract:
    """Một hợp đồng dịch vụ gắn với thiết bị; không sở hữu thiết bị."""

    def __init__(
        self, contract_id: str, supplier: str, device: Device,
        start_date: date, end_date: date, annual_fee: Decimal | int | str,
    ) -> None:
        if not isinstance(contract_id, str) or not contract_id.strip():
            raise ValueError('Mã hợp đồng không được rỗng.')
        if not isinstance(supplier, str) or not supplier.strip():
            raise ValueError('Đơn vị cung cấp không hợp lệ.')
        if not isinstance(device, Device):
            raise ValueError('Thiết bị hợp đồng không hợp lệ.')
        if (not isinstance(start_date, date) or not isinstance(end_date, date)
                or end_date < start_date):
            raise ValueError('Khoảng thời gian hợp đồng không hợp lệ.')
        try:
            fee = Decimal(str(annual_fee))
        except Exception as error:
            raise ValueError('Phí hợp đồng không hợp lệ.') from error
        if not fee.is_finite() or fee <= 0:
            raise ValueError('Phí hợp đồng phải lớn hơn 0.')
        self.contract_id = contract_id.strip()
        self.supplier = supplier.strip()
        self.device = device
        self.start_date = start_date
        self.end_date = end_date
        self.annual_fee = fee

    def is_active(self, on_date: date) -> bool:
        return self.start_date <= on_date <= self.end_date
