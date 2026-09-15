# OpsPulse - Operations Control Center

Web application focused on cruise operations: live operational metrics and passenger check-in monitoring.

## Hướng dẫn sử dụng

### 1. Cấu trúc thư mục

```
frontend_new/
├── app.py                 # Entry point chính
├── config.py              # Cấu hình
├── requirements.txt       # Thư viện cần thiết
├── blueprints/
│   ├── auth.py            # Login / Logout
│   └── operations.py      # Dashboard và giám sát check-in
├── templates/
│   ├── layouts/
│   │   └── base.html      # Layout chung
│   ├── auth/
│   │   └── login.html
│   ├── operations/
│   │   ├── dashboard.html
│   │   └── checkins.html
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

### 3. Tài khoản Operations demo

| Role              | Username     | Password   |
|-------------------|--------------|------------|
| Operations        | nguyenhoangphat | 123456 |

> Dashboard sử dụng dữ liệu Supabase nếu khả dụng và tự động dùng dữ liệu demo khi chưa cấu hình kết nối.
