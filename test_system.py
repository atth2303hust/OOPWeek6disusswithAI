"""
/****************/
Mã sinh viên: [DIEN_MSSV]
Họ tên: [DIEN_HO_TEN]
/****************/
Kiểm thử dữ liệu, kế thừa, ngoại lệ và tính nhất quán nghiệp vụ.
"""

from datetime import date, datetime
from decimal import Decimal
import unittest

from src.borrowers import Lecturer, TeachingAssistant
from src.borrowing import BorrowingSlip, BorrowItem
from src.classroom import ClassRoom
from src.devices import (
    DeviceStatus, ProjectorRemote, AirConditionerRemote, WirelessMicrophone,
)
from src.exceptions import (
    BorrowLimitExceededException, DeviceAlreadyReturnedException,
    DeviceNotInSlipException, DeviceUnavailableException, DuplicateDeviceException,
    InvalidBorrowPeriodException, InvalidReturnDateException,
    InvalidDeviceStateException,
)
from src.maintenance import MaintenanceContract


class SystemTests(unittest.TestCase):
    """Mỗi test độc lập, không tác động qua trạng thái global."""

    def setUp(self) -> None:
        self.when = datetime(2026, 10, 1, 8)
        self.teacher = Lecturer('GV01', 'Teacher A')
        self.ta = TeachingAssistant('TA01', 'Assistant B')
        self.projector = ProjectorRemote('P01', 'Remote', 2020, '1000000')
        self.mic = WirelessMicrophone('M01', 'Wireless Microphone', 2024, '1500000')
        self.ac = AirConditionerRemote('A01', 'Aircon remote', 2019, '600000')
        self.slip = BorrowingSlip('S01', self.teacher, 'P301', self.when)

    def test_01_valid_devices(self):
        self.assertEqual(self.projector.status, DeviceStatus.AVAILABLE)

    def test_02_empty_device_id_rejected(self):
        with self.assertRaises(ValueError):
            ProjectorRemote(' ', 'ABC', 2020, 100)

    def test_03_nonpositive_price_rejected(self):
        with self.assertRaises(ValueError):
            WirelessMicrophone('M02', 'abc', 2021, 0)

    def test_04_future_year_rejected(self):
        with self.assertRaises(ValueError):
            ProjectorRemote('P03', 'ABC', 9999, 100)

    def test_05_read_only_device_id(self):
        with self.assertRaises(AttributeError):
            self.projector.device_id = 'P04'

    def test_06_lecturer_limit(self):
        self.assertEqual(self.teacher.get_maximum_devices(), 3)

    def test_07_assistant_limit(self):
        self.assertEqual(self.ta.get_maximum_devices(), 2)

    def test_08_polymorphic_maintenance(self):
        room = ClassRoom('P1', 'A', 40)
        for dev in (self.projector, self.mic, self.ac):
            room.add_device(dev)
        self.assertEqual(room.calculate_annual_maintenance_cost(), Decimal('224000'))

    def test_09_classroom_duplicate_rejected(self):
        room = ClassRoom('P1', 'A', 30)
        room.add_device(self.ac)
        with self.assertRaises(ValueError):
            room.add_device(self.ac)
        self.assertEqual(len(room.devices), 1)

    def test_10_classroom_null_rejected(self):
        with self.assertRaises(ValueError):
            ClassRoom('P1', 'A', 30).add_device(None)

    def test_11_room_find_remove(self):
        room = ClassRoom('P1', 'A', 30)
        room.add_device(self.ac)
        self.assertIs(room.find_device('A01'), self.ac)
        self.assertTrue(room.remove_device('A01'))
        self.assertFalse(room.remove_device('A01'))
        self.assertIsNone(room.find_device('A01'))

    def test_12_maintenance_age_and_status(self):
        self.ac.send_to_maintenance()
        room = ClassRoom('P1', 'A', 30)
        room.add_device(self.projector)  # 2026 - 2020 > 5
        room.add_device(self.ac)
        room.add_device(self.mic)
        self.assertEqual({d.device_id for d in room.get_devices_requiring_maintenance(date(2026, 10, 1))},
                         {'P01', 'A01'})

    def test_13_borrow_success(self):
        self.slip.add_device(self.mic, 1, 1, 2)
        self.assertEqual(self.mic.status, DeviceStatus.BORROWED)
        self.assertEqual(len(self.slip.items), 1)

    def test_14_mic_three_days_rejected_unchanged(self):
        with self.assertRaises(InvalidBorrowPeriodException):
            self.slip.add_device(self.mic, 3)
        self.assertEqual(self.mic.status, DeviceStatus.AVAILABLE)
        self.assertEqual(len(self.slip.items), 0)

    def test_15_duplicate_rejected_unchanged(self):
        self.slip.add_device(self.mic, 1)
        with self.assertRaises(DuplicateDeviceException):
            self.slip.add_device(self.mic, 1)
        self.assertEqual(len(self.slip.items), 1)
        self.assertEqual(self.mic.status, DeviceStatus.BORROWED)

    def test_16_device_under_maintenance_rejected(self):
        self.ac.send_to_maintenance()
        with self.assertRaises(DeviceUnavailableException):
            self.slip.add_device(self.ac, 1)
        self.assertEqual(self.ac.status, DeviceStatus.UNDER_MAINTENANCE)
        self.assertEqual(len(self.slip.items), 0)

    def test_17_assistant_third_device_rejected(self):
        slip = BorrowingSlip('S02', self.ta, 'P301', self.when)
        slip.add_device(self.mic, 1)
        slip.add_device(self.projector, 1)
        with self.assertRaises(BorrowLimitExceededException):
            slip.add_device(self.ac, 1)
        self.assertEqual(self.ac.status, DeviceStatus.AVAILABLE)
        self.assertEqual(len(slip.items), 2)

    def test_18_null_device_rejected(self):
        with self.assertRaises(ValueError):
            self.slip.add_device(None, 1)

    def test_19_invalid_period_order_rejected_unchanged(self):
        with self.assertRaises(InvalidBorrowPeriodException):
            self.slip.add_device(self.mic, 1, 4, 2)
        self.assertEqual(self.mic.status, DeviceStatus.AVAILABLE)

    def test_20_invalid_period_limit_rejected(self):
        with self.assertRaises(InvalidBorrowPeriodException):
            self.slip.add_device(self.mic, 1, 1, 5)
        self.assertEqual(len(self.slip.items), 0)

    def test_21_return_on_time(self):
        self.slip.add_device(self.projector, 2)
        fee = self.slip.return_device('P01', datetime(2026, 10, 3, 8))
        self.assertEqual(fee, Decimal('0'))
        self.assertEqual(self.projector.status, DeviceStatus.AVAILABLE)

    def test_22_return_two_days_late(self):
        self.slip.add_device(self.mic, 1)
        fee = self.slip.return_device('M01', datetime(2026, 10, 4, 8))
        self.assertEqual(fee, Decimal('40000'))
        self.assertEqual(self.slip.calculate_total_late_fee(), Decimal('40000'))

    def test_23_return_missing_device(self):
        with self.assertRaises(DeviceNotInSlipException):
            self.slip.return_device('UNKNOWN', datetime(2026, 10, 3))

    def test_24_return_twice(self):
        self.slip.add_device(self.mic, 1)
        self.slip.return_device('M01', datetime(2026, 10, 2, 8))
        with self.assertRaises(DeviceAlreadyReturnedException):
            self.slip.return_device('M01', datetime(2026, 10, 3, 8))
        self.assertEqual(self.slip.items[0].returned_date, datetime(2026, 10, 2, 8))

    def test_25_return_before_borrowed_date_rejected_unchanged(self):
        self.slip.add_device(self.projector, 2)
        with self.assertRaises(InvalidReturnDateException):
            self.slip.return_device('P01', datetime(2026, 9, 30, 8))
        self.assertEqual(self.projector.status, DeviceStatus.BORROWED)
        self.assertFalse(self.slip.items[0].is_returned)

    def test_26_unreturned_and_overdue(self):
        self.slip.add_device(self.projector, 2)
        self.assertEqual(len(self.slip.get_unreturned_items()), 1)
        self.assertEqual(len(self.slip.get_overdue_items(datetime(2026, 10, 5))), 1)
        self.assertEqual(self.slip.calculate_total_late_fee(datetime(2026, 10, 5)),
                         Decimal('40000'))

    def test_27_items_read_only_collection(self):
        self.slip.add_device(self.mic, 1)
        with self.assertRaises(AttributeError):
            self.slip.items.append('bad')

    def test_28_invalid_state_transition(self):
        with self.assertRaises(InvalidDeviceStateException):
            self.projector.mark_as_available()

    def test_29_maintenance_contract(self):
        contract = MaintenanceContract('HD01', 'Supplier', self.ac,
                                       date(2026, 1, 1), date(2026, 12, 31), 180000)
        self.assertTrue(contract.is_active(date(2026, 10, 13)))
        self.assertFalse(contract.is_active(date(2027, 1, 1)))

    def test_30_invalid_maintenance_contract(self):
        with self.assertRaises(ValueError):
            MaintenanceContract('HD01', 'Supplier', self.ac,
                                date(2026, 12, 31), date(2026, 1, 1), 180000)

    def test_31_microphone_maintenance_formula(self):
        self.assertEqual(self.mic.calculate_annual_maintenance_cost(), Decimal('150000'))

    def test_32_try_failed_return_doesnt_mutate(self):
        self.slip.add_device(self.projector, 2)
        original_count = len(self.slip.items)
        try:
            self.slip.return_device('P01', datetime(2026, 9, 30))
        except InvalidReturnDateException:
            pass
        self.assertEqual(len(self.slip.items), original_count)
        self.assertIsNone(self.slip.items[0].returned_date)
        self.assertEqual(self.projector.status, DeviceStatus.BORROWED)

    def test_33_borrowitem_null_rejected(self):
        with self.assertRaises(ValueError):
            BorrowItem(None, self.when, 1)

    def test_34_return_wrong_date_type_rejected(self):
        self.slip.add_device(self.projector, 1)
        with self.assertRaises(InvalidReturnDateException):
            self.slip.return_device('P01', '2026-10-02')
        self.assertFalse(self.slip.items[0].is_returned)

    def test_35_initial_return_date_null(self):
        self.slip.add_device(self.mic, 1)
        self.assertIsNone(self.slip.items[0].returned_date)


if __name__ == '__main__':
    unittest.main()
