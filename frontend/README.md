# Cruise Activity & Service Management System - Web Admin Frontend

## Hướng dẫn sử dụng

### 1. Cấu trúc thư mục

```
frontend_webadmin/
├── app.py                 # Entry point chính
├── config.py              # Cấu hình
├── requirements.txt       # Thư viện cần thiết
├── blueprints/
│   ├── auth.py            # Login / Logout
│   └── admin.py           # Các trang Admin
├── templates/
│   ├── layouts/
│   │   └── base.html      # Layout chung
│   ├── auth/
│   │   └── login.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── itinerary.html
│   │   ├── activities.html
│   │   ├── excursions.html
│   │   ├── passengers.html
│   │   ├── finance.html
│   │   ├── users.html
│   │   └── settings.html
│   └── components/
│       ├── sidebar.html
│       └── navbar.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

### 2. Cách chạy (trong VS Code)

```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt (Windows)
.venv\Scripts\activate

# Cài thư viện
pip install -r requirements.txt

# Chạy
python app.py
```

Truy cập: http://localhost:5000

### 3. Tài khoản demo (tạm thời)

| Role              | Username     | Password   |
|-------------------|--------------|------------|
| Admin             | admin        | admin123   |
| Operations        | operations   | ops123     |
| Finance           | finance      | fin123     |
| Coordinator       | coordinator  | coord123   |

> Hiện tại đang dùng mock data. Sau này sẽ kết nối với API backend thật.
