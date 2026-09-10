import os
import json
import re
import unicodedata
from flask_login import UserMixin

ROLE_DISPLAY_NAMES = {
    "admin": "Quản trị viên hệ thống",
    "operations": "Quản lý vận hành",
    "finance": "Tài chính & Lễ tân",
    "coordinator": "Điều phối lịch trình",
    "activity_manager": "Quản lý hoạt động",
    "sales_staff": "Nhân viên bán hàng & dịch vụ",
    "passenger": "Hành khách",
}

class User(UserMixin):
    def __init__(self, id, username, password, full_name, role, role_name=None, status="Active", passenger_id=None):
        self.id = str(id)
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role
        self.role_name = role_name or ROLE_DISPLAY_NAMES.get(role, role)
        self.status = status
        # ID của bản ghi Passenger THẬT trên backend/Supabase (chỉ có ý nghĩa
        # với role='passenger'). None nghĩa là tài khoản này chưa liên kết
        # với 1 hành khách thật nào (sẽ tự tạo/gán khi cần).
        self.passenger_id = passenger_id

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return self.status == "Active"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "role": self.role,
            "role_name": self.role_name,
            "status": self.status,
            "passenger_id": self.passenger_id,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            username=data["username"],
            password=data["password"],
            full_name=data["full_name"],
            role=data["role"],
            role_name=data.get("role_name"),
            status=data.get("status", "Active"),
            passenger_id=data.get("passenger_id"),
        )


DATA_FILE = os.path.join(os.path.dirname(__file__), "users_data.json")

# Danh sách 5 thành viên nhóm chuẩn hóa theo yêu cầu
DEFAULT_USERS = [
    {
        "id": "1",
        "username": "nguyenchihai",
        "password": "123456",
        "full_name": "Nguyễn Chí Hải",
        "role": "admin",
        "role_name": "Quản trị viên hệ thống",
        "status": "Active"
    },
    {
        "id": "2",
        "username": "nguyenhoangphat",
        "password": "123456",
        "full_name": "Nguyễn Hoàng Phát",
        "role": "operations",
        "role_name": "Quản lý vận hành",
        "status": "Active"
    },
    {
        "id": "3",
        "username": "nguyenthithi",
        "password": "123456",
        "full_name": "Nguyễn Thị Thi",
        "role": "finance",
        "role_name": "Tài chính & Lễ tân",
        "status": "Active"
    },
    {
        "id": "4",
        "username": "nguyentronghai",
        "password": "123456",
        "full_name": "Nguyễn Trọng Hải",
        "role": "coordinator",
        "role_name": "Điều phối lịch trình",
        "status": "Active"
    },
    {
        "id": "5",
        "username": "ledinhquy",
        "password": "123456",
        "full_name": "Lê Đình Quý",
        "role": "activity_manager",
        "role_name": "Quản lý hoạt động",
        "status": "Active"
    },
    {
        "id": "6",
        "username": "posstaff",
        "password": "123456",
        "full_name": "Nhân viên POS Demo",
        "role": "sales_staff",
        "role_name": "Nhân viên bán hàng & dịch vụ",
        "status": "Active"
    },
    {
        "id": "7",
        "username": "passenger",
        "password": "123456",
        "full_name": "Hành khách Demo",
        "role": "passenger",
        "role_name": "Hành khách",
        "status": "Active"
    }
]

def _load_users():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {item["id"]: User.from_dict(item) for item in data}
        except Exception:
            pass
    # Khởi tạo mặc định nếu chưa có file
    users_map = {item["id"]: User.from_dict(item) for item in DEFAULT_USERS}
    _save_users(users_map)
    return users_map

def _save_users(users_map):
    data = [user.to_dict() for user in users_map.values()]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users_db = _load_users()

def slugify_username(full_name):
    """
    Chuyển họ và tên tiếng Việt thành username viết thường liền không dấu.
    Ví dụ: 'Trần Văn An' -> 'tranvanan'
    """
    if not full_name:
        return ""
    # Chuyển ký tự đ/Đ trước vì NFD chuẩn Unicode không tách đ thành d + dấu
    s = full_name.replace("đ", "d").replace("Đ", "d")
    # Phân rã dấu Unicode (NFD)
    s = unicodedata.normalize("NFD", s)
    # Loại bỏ các ký tự dấu
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    # Chuyển thành chữ thường và chỉ giữ lại chữ cái/số
    s = re.sub(r"[^a-zA-Z0-9]", "", s).lower()
    return s

def authenticate(username, password):
    """Xác thực đăng nhập tài khoản."""
    global users_db
    users_db = _load_users()  # Luôn đồng bộ dữ liệu mới nhất
    for user in users_db.values():
        if user.username == username.strip().lower() and user.password == password:
            return user
    return None

def get_user_by_id(user_id):
    global users_db
    users_db = _load_users()
    return users_db.get(str(user_id))

def get_all_users():
    global users_db
    users_db = _load_users()
    return list(users_db.values())

def add_user(full_name, role, custom_username=None, password="123456"):
    """Thêm người dùng mới và tự động sinh username."""
    global users_db
    users_db = _load_users()

    base_username = custom_username.strip().lower() if custom_username else slugify_username(full_name)
    if not base_username:
        base_username = "user"

    # Xử lý tránh trùng lặp username
    username = base_username
    existing_usernames = {u.username for u in users_db.values()}
    counter = 1
    while username in existing_usernames:
        username = f"{base_username}{counter}"
        counter += 1

    # Tạo ID tự tăng
    numeric_ids = [int(u.id) for u in users_db.values() if u.id.isdigit()]
    next_id = str(max(numeric_ids) + 1) if numeric_ids else "1"

    new_user = User(
        id=next_id,
        username=username,
        password=password,
        full_name=full_name.strip(),
        role=role,
        role_name=ROLE_DISPLAY_NAMES.get(role, role),
        status="Active"
    )

    users_db[next_id] = new_user
    _save_users(users_db)
    return new_user

def toggle_user_status(user_id):
    """Bật / tắt trạng thái hoạt động của người dùng (Active / Inactive)."""
    global users_db
    users_db = _load_users()
    user = users_db.get(str(user_id))
    if user:
        user.status = "Inactive" if user.status == "Active" else "Active"
        _save_users(users_db)
        return user
    return None


def username_exists(username):
    global users_db
    users_db = _load_users()
    username = (username or "").strip().lower()
    return any(u.username == username for u in users_db.values())


def register_passenger_user(username, password, full_name, passenger_id):
    """Tạo tài khoản đăng nhập mới cho Hành khách tự đăng ký (UC: Đăng ký
    tài khoản), liên kết với 1 bản ghi Passenger thật (passenger_id) đã
    được tạo trước đó trên backend/Supabase."""
    global users_db
    users_db = _load_users()

    numeric_ids = [int(u.id) for u in users_db.values() if u.id.isdigit()]
    next_id = str(max(numeric_ids) + 1) if numeric_ids else "1"

    new_user = User(
        id=next_id,
        username=username.strip().lower(),
        password=password,
        full_name=full_name.strip(),
        role="passenger",
        role_name=ROLE_DISPLAY_NAMES.get("passenger"),
        status="Active",
        passenger_id=passenger_id,
    )
    users_db[next_id] = new_user
    _save_users(users_db)
    return new_user


def update_password(user_id, new_password):
    global users_db
    users_db = _load_users()
    user = users_db.get(str(user_id))
    if not user:
        return None
    user.password = new_password
    _save_users(users_db)
    return user


def set_passenger_id(user_id, passenger_id):
    """Gán passenger_id cho tài khoản chưa liên kết (dùng để tự vá cho các
    tài khoản demo cũ được tạo trước khi có cơ chế liên kết này)."""
    global users_db
    users_db = _load_users()
    user = users_db.get(str(user_id))
    if not user:
        return None
    user.passenger_id = passenger_id
    _save_users(users_db)
    return user
