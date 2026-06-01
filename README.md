# Hệ Thống Quản Lý Khách Sạn (Hotel Management System)

Ứng dụng desktop quản lý khách sạn đa chi nhánh với giao diện PyQt6, phân quyền 4 vai trò, hỗ trợ đầy đủ quy trình đặt phòng - nhận/trả phòng - thanh toán.

## Tính năng

- **Đăng nhập & Phân quyền**: 4 vai trò — Admin, Lễ tân, Buồng phòng, Bếp trưởng
- **Quản lý đặt phòng**: Tạo/sửa/hủy đặt phòng, nhận/trả phòng, tự động hủy đặt phòng quá hạn
- **Quản lý khách hàng**: Thêm/sửa/tìm kiếm khách hàng theo CCCD, số điện thoại, xem lịch sử đặt phòng
- **Sơ đồ phòng trực quan**: Hiển thị trạng thái phòng theo mã màu, check-in/out ngay trên sơ đồ
- **Biểu đồ Gantt**: Trực quan hóa lịch đặt phòng theo thời gian, hỗ trợ hover tooltip
- **Đặt dịch vụ & món ăn**: Order dịch vụ, gọi món theo bữa (sáng/trưa/tối) cho từng phòng
- **Hóa đơn PDF**: Xem trước hóa đơn, xuất PDF (ReportLab) kèm VAT 8%, hỗ trợ tiếng Việt
- **Thống kê doanh thu**: Biểu đồ cột doanh thu ngày/tháng, biểu đồ tròn tỷ lệ lấp đầy, top khách hàng
- **Quản lý nhân viên**: CRUD tài khoản, vô hiệu hóa, đổi mật khẩu
- **Quản lý chi nhánh**: Hỗ trợ nhiều khách sạn, nhân viên gắn với chi nhánh
- **Quản lý thực đơn & dịch vụ**: CRUD món ăn/dịch vụ, kiểm soát tồn kho, phân loại theo bữa
- **Dọn dẹp phòng**: Cập nhật trạng thái vệ sinh, tự động set "Dirty" khi trả phòng

## Kiến trúc

Ứng dụng tổ chức theo mô hình **3-layer**:

```
┌──────────────────────────────┐
│  Views (PyQt6)               │  Giao diện người dùng
│  ├── admin/                  │  4 role riêng biệt
│  ├── receptionist/           │  Mỗi role chia feature
│  ├── housekeeping/           │  thành thư mục con
│  └── chef/                   │
├──────────────────────────────┤
│  Services                    │  Logic nghiệp vụ
│  ├── booking_service.py      │  Validation, tính tiền,
│  └── invoice_service.py      │  sinh PDF, check-in/out
├──────────────────────────────┤
│  Models (SQL thuần)          │  Truy xuất dữ liệu
│  └── *_model.py              │  CRUD, thống kê
├──────────────────────────────┤
│  Database / Utils            │  Schema, seed, config,
│                              │  bảo mật, hằng số
└──────────────────────────────┘
```

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.10+ |
| Giao diện | PyQt6 |
| Cơ sở dữ liệu | SQLite3 (sqlite3.Row) |
| Xuất PDF | ReportLab |
| Biểu đồ | Matplotlib, NumPy, Pandas |
| Bảo mật | SHA-256 + Salt (16-byte) |
| Kiểm thử | pytest + unittest.mock |

## Cài đặt

```bash
# 1. Di chuyển vào thư mục dự án
cd D:\hotel_management

# 2. Tạo môi trường ảo (khuyến nghị)
python -m venv venv
venv\Scripts\activate

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Chạy ứng dụng (tự động tạo DB & seed data)
python main.py
```

## Tài khoản mặc định

Tất cả tài khoản có mật khẩu: `123456`

| Tài khoản | Vai trò | Chi nhánh |
|---|---|---|
| `admin` | Admin | Tất cả |
| `letan1` | Lễ tân | Grand Palace Hotel (TP.HCM) |
| `letan2` | Lễ tân | Ocean View Resort (Đà Nẵng) |
| `buongphong1` | Buồng phòng | Grand Palace Hotel |
| `buongphong2` | Buồng phòng | Ocean View Resort |
| `beptruong1` | Bếp trưởng | Grand Palace Hotel |

## Cấu trúc thư mục

```
hotel_management/
├── main.py                         # Điểm vào ứng dụng
│
├── database/                       # Khởi tạo CSDL
│   ├── connection.py               # Connection factory (sqlite3.Row)
│   ├── schema.py                   # CREATE TABLE statements
│   ├── seed_data.py                # Seed mẫu
│   └── init_db.py                  # Orchestrator khởi tạo
│
├── models/                         # Tầng truy xuất dữ liệu
│   ├── base_model.py               # get_conn() dùng chung
│   ├── user_model.py               # Users + authentication
│   ├── hotel_model.py              # Chi nhánh khách sạn
│   ├── room_model.py               # Phòng & loại phòng
│   ├── customer_model.py           # Khách hàng + search
│   ├── booking_model.py            # Đặt phòng, check-in/out
│   ├── invoice_model.py            # Hóa đơn + thống kê doanh thu
│   ├── menu_model.py               # Thực đơn + gọi món
│   └── service_model.py            # Dịch vụ + tồn kho
│
├── services/                       # Tầng nghiệp vụ
│   ├── booking_service.py          # Validation, check-in/out, tính tiền
│   ├── invoice_service.py          # Sinh hóa đơn PDF
│   ├── invoice_fonts.py            # Đăng ký font đa nền tảng
│   ├── invoice_styles.py           # Paragraph styles
│   └── invoice_tables.py           # Table builder cho PDF
│
├── views/                          # Tầng giao diện (PyQt6)
│   ├── login_window.py             # Màn hình đăng nhập
│   │
│   ├── widgets/                    # Component dùng chung
│   │   ├── sidebar.py              # Sidebar điều hướng
│   │   ├── room_card.py            # Card phòng (màu theo trạng thái)
│   │   ├── gantt_canvas.py         # Gantt chart tự vẽ (QPainter)
│   │   └── gantt_chart_widget.py   # Gantt container + controls
│   │
│   ├── admin/
│   │   ├── admin_window.py         # Cửa sổ chính Admin
│   │   ├── staff/
│   │   │   ├── staff_tab.py        # Quản lý nhân viên
│   │   │   └── user_dialog.py      # Dialog thêm/sửa user
│   │   ├── branch/
│   │   │   ├── branch_tab.py       # Quản lý chi nhánh
│   │   │   └── hotel_dialog.py     # Dialog thêm/sửa khách sạn
│   │   ├── rooms/
│   │   │   ├── rooms_tab.py        # Quản lý phòng & loại phòng
│   │   │   ├── rooms_ui.py         # Layout UI rooms tab
│   │   │   ├── rooms_presenter.py  # Presenter rooms tab
│   │   │   └── room_dialogs.py     # Dialog thêm/sửa phòng
│   │   └── statistics/
│   │       ├── statistics_tab.py   # Thống kê + biểu đồ
│   │       └── statistics_charts.py # Vẽ biểu đồ
│   │
│   ├── receptionist/
│   │   ├── receptionist_window.py  # Cửa sổ chính Lễ tân
│   │   ├── booking/
│   │   │   ├── booking_tab.py      # Danh sách đặt phòng
│   │   │   ├── booking_dialog.py   # Dialog tạo/sửa đặt phòng
│   │   │   ├── booking_dialog_ui.py# Layout UI booking dialog
│   │   │   └── room_switch_dialog.py# Dialog đổi phòng giữa chừng
│   │   ├── customer/
│   │   │   ├── customer_tab.py     # Danh sách khách hàng
│   │   │   └── customer_dialog.py  # Dialog thêm/sửa khách
│   │   ├── rooms/
│   │   │   ├── rooms_tab.py        # Sơ đồ phòng + check-in/out
│   │   │   └── room_action_dialog.py # Dialog hành động phòng
│   │   ├── service/
│   │   │   ├── service_tab.py      # Dịch vụ & gọi món
│   │   │   ├── service_helpers.py  # Helper table/cell
│   │   │   └── service_dialogs.py  # Dialog thêm dịch vụ
│   │   ├── invoice/
│   │   │   ├── invoice_tab.py      # Hóa đơn + xuất PDF
│   │   │   ├── invoice_ui.py       # Layout UI invoice
│   │   │   ├── invoice_helpers.py  # Helper UI invoice
│   │   │   └── invoice_presenter.py# Presenter invoice
│   │   └── gantt/
│   │       └── gantt_tab.py        # Biểu đồ Gantt
│   │
│   ├── housekeeping/
│   │   ├── housekeeping_window.py  # Cửa sổ chính Buồng phòng
│   │   └── housekeeping_tab.py     # Grid phòng + toggle sạch/bẩn
│   │
│   └── chef/
│       ├── chef_window.py          # Cửa sổ chính Bếp trưởng
│       ├── menu/
│       │   ├── menu_tab.py         # Quản lý thực đơn
│       │   └── menu_item_dialog.py # Dialog thêm/sửa món
│       └── order/
│           ├── order_tab.py        # Nhận order món ăn
│           └── order_panels.py     # Panel UI order
│
├── utils/                          # Tiện ích & cấu hình
│   ├── config.py                   # Hằng số (status, màu, VAT, role...)
│   └── security.py                 # Hash/verify mật khẩu
│
├── resources/                      # Tài nguyên tĩnh
│   ├── style.qss                   # 847 dòng QSS (2 theme)
│   └── images/
│       └── login_background.jpg    # Ảnh nền đăng nhập
│
├── tests/                          # Kiểm thử (59 tests)
│   ├── conftest.py                 # Fixtures (temp DB, patch)
│   ├── test_config.py              # Hằng số config
│   ├── test_imports.py             # Import tất cả module
│   ├── test_security.py            # Hash/verify password
│   ├── test_models.py              # CRUD models (temp DB)
│   └── test_services.py            # Business logic + validation
│
├── requirements.txt                # Thư viện phụ thuộc
└── README.md                       # Tài liệu dự án
```

## Cơ sở dữ liệu

11 bảng quan hệ: `Hotels`, `Roles`, `Users`, `RoomTypes`, `Rooms`, `Customers`, `Bookings`, `Services`, `BookingServices`, `MealTypes`, `MenuItems`, `BookingMeals`, `Invoices`.

Trạng thái được lưu dưới dạng chuỗi:
- **Phòng**: `Available`, `Occupied`, `Reserved`
- **Vệ sinh**: `Clean`, `Dirty`
- **Đặt phòng**: `Reserved`, `Checked-in`, `Checked-out`, `Cancelled`
- **Thanh toán**: `Unpaid`, `Paid`

## Chạy kiểm thử

```bash
# Cài đặt pytest nếu chưa có
pip install pytest

# Chạy toàn bộ test suite (59 tests)
pytest -v

# Chạy test theo module
pytest tests/test_security.py -v
pytest tests/test_models.py -v
pytest tests/test_services.py -v
```

## Giấy phép

Dự án được phát triển cho mục đích học tập và quản lý khách sạn.
```

