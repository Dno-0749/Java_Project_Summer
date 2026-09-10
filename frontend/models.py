import os
import json
import re
import unicodedata
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from supabase_client import get_supabase_client, is_supabase_configured

ROLE_DISPLAY_NAMES = {
    "admin": "Quản trị viên hệ thống",
    "operations": "Quản lý vận hành",
    "finance": "Tài chính & Lễ tân",
    "coordinator": "Điều phối lịch trình",
    "activity_manager": "Quản lý hoạt động",
}

class User(UserMixin):
    def __init__(self, id, username, password, full_name, role, role_name=None, status="Active", password_hash=None):
        self.id = str(id)
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role
        self.role_name = role_name or ROLE_DISPLAY_NAMES.get(role, role)
        self.status = status
        self.password_hash = password_hash

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
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            username=data["username"],
            password=data.get("password", ""),
            full_name=data["full_name"],
            role=data["role"],
            role_name=data.get("role_name"),
            status=data.get("status", "Active"),
        )

    @classmethod
    def from_api(cls, data):
        return cls.from_dict(data)


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

SUPABASE_ROLE_MAP = {
    "ADMIN": "admin",
    "OPERATIONS_MANAGER": "operations",
    "FINANCE": "finance",
    "ITINERARY_STAFF": "coordinator",
    "ACTIVITY_STAFF": "activity_manager",
}


def _supabase_users():
    try:
        client = get_supabase_client()
        users = client.table("auth_users").select("id, username, email, password_hash").execute().data or []
        roles = client.table("auth_roles").select("id, name").execute().data or []
        user_roles = client.table("auth_user_roles").select("user_id, role_id").execute().data or []
    except Exception:
        return {}
    role_names = {str(role["id"]): role["name"] for role in roles}
    roles_by_user = {}
    for user_role in user_roles:
        role_name = role_names.get(str(user_role["role_id"]))
        if role_name:
            roles_by_user[str(user_role["user_id"])] = role_name

    result = {}
    for row in users:
        role_name = roles_by_user.get(str(row["id"]), "")
        role = SUPABASE_ROLE_MAP.get(role_name, role_name.lower())
        username = row["username"]
        result[str(row["id"])] = User(
            id=row["id"],
            username=username,
            password="",
            full_name=username,
            role=role,
            role_name=ROLE_DISPLAY_NAMES.get(role, role_name or role),
            password_hash=row["password_hash"],
        )
    return result

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
    if is_supabase_configured():
        users_db = _supabase_users()
        if users_db:
            for user in users_db.values():
                if user.username == username.strip().lower() and check_password_hash(user.password_hash, password):
                    return user
            return None
    users_db = _load_users()  # Luôn đồng bộ dữ liệu mới nhất
    for user in users_db.values():
        if user.username == username.strip().lower() and user.password == password:
            return user
    return None

def get_user_by_id(user_id):
    global users_db
    if is_supabase_configured():
        users_db = _supabase_users()
        if users_db:
            return users_db.get(str(user_id))
    users_db = _load_users()
    return users_db.get(str(user_id))

def get_all_users():
    global users_db
    if is_supabase_configured():
        users_db = _supabase_users()
        if users_db:
            return list(users_db.values())
    users_db = _load_users()
    return list(users_db.values())

def add_user(full_name, role, custom_username=None, password="123456"):
    """Thêm người dùng mới và tự động sinh username."""
    global users_db
    if is_supabase_configured():
        client = get_supabase_client()
        remote_users = _supabase_users()
        base_username = custom_username.strip().lower() if custom_username else slugify_username(full_name)
        username = base_username or "user"
        existing_usernames = {user.username for user in remote_users.values()}
        counter = 1
        while username in existing_usernames:
            username = f"{base_username}{counter}"
            counter += 1
        inserted = client.table("auth_users").insert({
            "username": username,
            "email": f"{username}@local.invalid",
            "password_hash": generate_password_hash(password),
        }).execute().data[0]
        role_name = next((name for name, code in SUPABASE_ROLE_MAP.items() if code == role), role.upper())
        role_rows = client.table("auth_roles").select("id").eq("name", role_name).execute().data
        if role_rows:
            client.table("auth_user_roles").insert({"user_id": inserted["id"], "role_id": role_rows[0]["id"]}).execute()
        users_db = _supabase_users()
        return users_db.get(str(inserted["id"]))
    users_db = _load_users()
    return _add_local_user(full_name, role, custom_username, password)


def _add_local_user(full_name, role, custom_username=None, password="123456"):
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
    if is_supabase_configured():
        return None
    users_db = _load_users()
    user = users_db.get(str(user_id))
    if user:
        user.status = "Inactive" if user.status == "Active" else "Active"
        _save_users(users_db)
        return user
    return None


def delete_user(user_id):
    global users_db
    users_db = _load_users()
    user = users_db.pop(str(user_id), None)
    if user is None:
        return None
    _save_users(users_db)
    return user
