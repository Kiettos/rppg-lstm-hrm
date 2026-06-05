# PsyTrack — Employee Psychology Analytics Dashboard

## Giới thiệu
Web dashboard cho Admin/CEO xem phân tích tâm lý nhân viên dựa trên dữ liệu rPPG (nhịp tim) và YOLO+LSTM (biểu cảm).

## Yêu cầu hệ thống
- Python 3.8+
- pip

## Cài đặt & Chạy

### Bước 1: Cài thư viện
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy server
```bash
python app.py
```

### Bước 3: Mở trình duyệt
Truy cập: http://localhost:5000

---

## Tài khoản demo

| Tài khoản | Mật khẩu  | Quyền     |
|-----------|-----------|-----------|
| admin     | admin123  | Admin     |
| ceo       | ceo123    | CEO       |
| hr        | hr123     | HR Manager|

---

## Chức năng
1. **Đăng nhập** — Xác thực Admin/CEO/HR
2. **Dashboard** — Biểu đồ stress theo giờ, phân bố biểu cảm, so sánh phòng ban, cảnh báo
3. **Chi tiết & Lọc** — Lọc theo phòng ban / nhân viên / ngày, bảng dữ liệu phân trang, xuất CSV

## Tích hợp API thực tế
Trong `app.py`, thay hàm `generate_mock_data()` bằng lời gọi API thực từ server xử lý AI:
```python
import requests
def get_real_data(date_str, dept=None, emp_id=None):
    resp = requests.get('http://your-leader-server/api/data', params={...})
    return resp.json()
```

## Cấu trúc thư mục
```
psytrack/
├── app.py              # Flask backend
├── requirements.txt    # Thư viện Python
├── README.md           # Hướng dẫn này
└── templates/
    ├── base.html       # Layout chung
    ├── login.html      # Trang đăng nhập
    ├── dashboard.html  # Dashboard tổng quan
    └── detail.html     # Chi tiết & Lọc
```
