# LAB W06 - Hệ thống quản lý thiết bị và phiếu mượn

Bài thực hành Python 3.10+ chuyển thể từ `lab w06.pdf` (đề có ví dụ chữ ký lớp C#), giữ các khái niệm OOP và quy tắc nghiệp vụ. Không cần cài gói ngoài.

## Cách chạy

```bash
python main.py
python -m unittest discover -s tests -v
```

## Cấu trúc

- `src/devices.py`: `DeviceStatus`, `Device`, `TeachingDevice`, ba loại thiết bị.
- `src/borrowers.py`: interface `IBorrower`, `Lecturer`, `TeachingAssistant`.
- `src/classroom.py`: kết tập `ClassRoom`, tính bảo trì bằng đa hình.
- `src/borrowing.py`: `BorrowItem`, `BorrowingSlip`, mượn/trả an toàn.
- `src/exceptions.py`: hệ phân cấp ngoại lệ riêng.
- `src/maintenance.py`: mở rộng `MaintenanceContract`.
- `tests/test_system.py`: các tình huống kiểm thử.
- `docs/So_do_lop.png`, `docs/So_do_lop.dot`: UML/Graphviz.
- `docs/AI_USAGE_LOG.md`: khung ghi nhận trao đổi và tự phản biện.

## Quy ước và quyết định thiết kế

1. Python dùng `Enum`, `ABC`, `@abstractmethod` tương ứng enum, abstract class, interface ở ví dụ C# trong đề. Hàm công khai theo `snake_case` của PEP 8 thay cho `PascalCase` trong ví dụ C#.
2. PDF có hai danh sách trạng thái ở các mục khác nhau. Hệ thống thống nhất thành `Available`, `Borrowed`, `UnderMaintenance`, `Retired`.
3. Đề chưa quy định giới hạn ngày cho điều khiển máy chiếu và điều hòa; bản demo chọn 5 và 2 ngày. Giới hạn micro = 1 ngày đúng tình huống 11.2. Giới hạn tiết trong ví dụ demo lần lượt 6, 8, 4 tiết (quy ước bổ sung).
4. Đề không ấn định mức phạt trễ. Bản demo chọn **20.000 VND/ngày lịch/thiết bị**. `calculate_total_late_fee(as_of)` cộng phí các món đã trả và khoản tạm tính cho món còn nợ đến ngày `as_of`.
5. Mỗi thiết bị chỉ được thêm một lần trên một phiếu, kể cả khi đã trả. Giới hạn 2/3 thiết bị đếm *tất cả các dòng* trên phiếu.
6. `MaintenanceContract` là lớp bổ sung có chủ đích: tiêu đề đề bài nhắc hợp đồng bảo trì nhưng thân đề chưa đưa đặc tả cụ thể.
7. Đây là mô phỏng trong bộ nhớ, không dùng database, giao diện hay xác thực. Không xử lý truy cập đồng thời nhiều tiến trình; khi triển khai thực tế cần transaction và khóa ở DB.

## Bảo đảm nhất quán

`BorrowingSlip.add_device()` kiểm tra tất cả điều kiện và tạo `BorrowItem` trước, rồi mới chuyển trạng thái và append. `return_device()` xác thực phiếu/ngày trả trước khi ghi trả và đổi trạng thái. Các kiểm thử xác minh tình huống lỗi không làm thay đổi phiếu/thiết bị.

## Thông tin nộp bài / GitHub

- Họ và tên: `[DIEN_HO_TEN]`
- MSSV: `[DIEN_MSSV]`
- Repository URL: `[DIEN_GITHUB_URL_SAU_KHI_PUSH]`

**Không được coi mẫu là bằng chứng đã tự làm/commit.** Quy trình bài tập yêu cầu bạn tự làm và commit phần của bạn *trước* khi sử dụng AI. Phần này phải tự bổ sung bằng lịch sử thật của repository; không được điền commit giả. Xem `docs/AI_USAGE_LOG.md`.

Lệnh git để tải bài lên repository mà bạn tạo:

```bash
git init
git add .
git commit -m "Add Lab W06 OOP implementation and tests"
git branch -M main
git remote add origin https://github.com/<USERNAME>/<REPOSITORY>.git
git push -u origin main
```

Chỉ sử dụng lệnh `git remote add ...` sau khi thay `<USERNAME>/<REPOSITORY>` bằng repository thật. Git commit của mã AI **không thay thế** commit phần tự làm trước AI mà giảng viên yêu cầu.
