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
    "sales_staff": "Nhân viên bán hàng & dịch vụ",
    "passenger": "Hành khách",
}

class User(UserMixin):
    def __init__(self, id, username, password, full_name, role, role_name=None, status="Active", passenger_id=None, password_hash=None):
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
        # Mật khẩu đã băm - chỉ có với tài khoản xác thực qua Supabase
        # (bảng auth_users), tài khoản local vẫn dùng self.password thường.
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

SUPABASE_ROLE_MAP = {
    "ADMIN": "admin",
    "OPERATIONS_MANAGER": "operations",
    "FINANCE": "finance",
    "ITINERARY_STAFF": "coordinator",
    "ACTIVITY_STAFF": "activity_manager",
    "SALES_STAFF": "sales_staff",
    "PASSENGER": "passenger",
}


def _supabase_users():
    """Lấy danh sách user THẬT từ bảng auth_users/auth_roles/auth_user_roles
    trên Supabase (nếu đã cấu hình SUPABASE_URL/SUPABASE_KEY) - áp dụng cho
    TẤT CẢ role, bao gồm cả sales_staff/passenger (đã chuyển hẳn sang
    Supabase, không còn phụ thuộc users_data.json local nữa).

    QUAN TRỌNG: hàm này chạy ở MỌI request (qua load_user của Flask-Login),
    nên toàn bộ xử lý dữ liệu phải nằm trong try/except - nếu Supabase trả
    về dữ liệu bất thường (sai schema, bảng trống, lỗi cấu trúc...) thì
    phải rơi về {} an toàn, không được để crash lan ra ngoài (sẽ sập toàn
    bộ Frontend vì mọi trang đều gọi current_user)."""
    try:
        client = get_supabase_client()
    except Exception as e:
        print(f"[_supabase_users] Không kết nối được Supabase: {e}")
        return {}

    try:
        users = client.table("auth_users").select(
            "id, username, email, password_hash, full_name, status, passenger_id"
        ).execute().data or []
        roles = client.table("auth_roles").select("id, name").execute().data or []
        user_roles = client.table("auth_user_roles").select("user_id, role_id").execute().data or []

        role_names = {
            str(role["id"]): role["name"]
            for role in roles
            if isinstance(role, dict) and "id" in role and "name" in role
        }
        roles_by_user = {}
        for user_role in user_roles:
            if not isinstance(user_role, dict):
                continue
            role_name = role_names.get(str(user_role.get("role_id")))
            if role_name:
                roles_by_user[str(user_role.get("user_id"))] = role_name

        result = {}
        for row in users:
            if not isinstance(row, dict) or "id" not in row or "username" not in row:
                continue
            role_name = roles_by_user.get(str(row["id"]), "")
            role = SUPABASE_ROLE_MAP.get(role_name, role_name.lower() if role_name else "")
            username = row["username"]
            result[str(row["id"])] = User(
                id=row["id"],
                username=username,
                password="",
                full_name=row.get("full_name") or username,
                role=role,
                role_name=ROLE_DISPLAY_NAMES.get(role, role_name or role),
                status=row.get("status", "Active"),
                passenger_id=row.get("passenger_id"),
                password_hash=row.get("password_hash"),
            )
        return result
    except Exception as e:
        print(f"[_supabase_users] Lỗi xử lý dữ liệu Supabase: {type(e).__name__}: {e}")
        return {}


def authenticate(username, password):
    """Xác thực đăng nhập tài khoản. Ưu tiên kiểm tra Supabase auth_users
    (nếu đã cấu hình) trước, nếu không tìm thấy/không cấu hình thì rơi về
    kho local (bao gồm cả tài khoản sales_staff/passenger)."""
    global users_db
    if is_supabase_configured():
        supabase_db = _supabase_users()
        if supabase_db:
            for user in supabase_db.values():
                if user.username == username.strip().lower() and user.password_hash and check_password_hash(user.password_hash, password):
                    return user
    users_db = _load_users()  # Luôn đồng bộ dữ liệu mới nhất
    for user in users_db.values():
        if user.username == username.strip().lower() and user.password == password:
            return user
    return None

def get_user_by_id(user_id):
    global users_db
    if is_supabase_configured():
        supabase_db = _supabase_users()
        if str(user_id) in supabase_db:
            return supabase_db[str(user_id)]
    users_db = _load_users()
    return users_db.get(str(user_id))

def get_all_users():
    global users_db
    users_db = _load_users()
    result = list(users_db.values())
    if is_supabase_configured():
        supabase_db = _supabase_users()
        # Gộp thêm user Supabase (nếu có) vào cùng danh sách hiển thị,
        # không loại bỏ tài khoản local (sales_staff/passenger demo)
        result.extend(supabase_db.values())
    return result

def add_user(full_name, role, custom_username=None, password="123456"):
    """Thêm người dùng mới và tự động sinh username.
    Nếu Supabase đã cấu hình -> tạo trên Supabase (bảng auth_users thật),
    áp dụng cho MỌI role (kể cả sales_staff). Nếu chưa cấu hình Supabase
    -> tạo local như cũ (users_data.json).
    """
    global users_db
    role_is_supabase_managed = role in SUPABASE_ROLE_MAP.values()

    if is_supabase_configured() and role_is_supabase_managed:
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
        if not role_rows:
            role_rows = [client.table("auth_roles").insert(
                {"name": role_name, "description": ROLE_DISPLAY_NAMES.get(role, role_name)}
            ).execute().data[0]]
        client.table("auth_user_roles").insert({"user_id": inserted["id"], "role_id": role_rows[0]["id"]}).execute()
        return _supabase_users().get(str(inserted["id"]))

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
    """Bật / tắt trạng thái hoạt động của người dùng (Active / Inactive).
    Chỉ áp dụng cho tài khoản local - Supabase auth_users hiện chưa có cột
    trạng thái tương ứng trong boilerplate gốc."""
    global users_db
    users_db = _load_users()
    user = users_db.get(str(user_id))
    if user:
        user.status = "Inactive" if user.status == "Active" else "Active"
        _save_users(users_db)
        return user
    if is_supabase_configured():
        return None
    return None


def delete_user(user_id):
    """Xóa hẳn tài khoản (chỉ áp dụng tài khoản local, ví dụ sales_staff/
    passenger tạo thủ công qua Admin - không xóa tài khoản Supabase từ đây
    để tránh xóa nhầm dữ liệu auth_users thật)."""
    global users_db
    users_db = _load_users()
    user = users_db.pop(str(user_id), None)
    if user is None:
        return None
    _save_users(users_db)
    return user


def username_exists(username):
    username = (username or "").strip().lower()
    if is_supabase_configured():
        if any(u.username == username for u in _supabase_users().values()):
            return True
    global users_db
    users_db = _load_users()
    return any(u.username == username for u in users_db.values())


def register_passenger_user(username, password, full_name, passenger_id):
    """Tạo tài khoản đăng nhập mới cho Hành khách tự đăng ký (UC: Đăng ký
    tài khoản), liên kết với 1 bản ghi Passenger thật (passenger_id) đã
    được tạo trước đó trên backend/Supabase.
    Nếu Supabase đã cấu hình -> ghi thẳng vào auth_users (role PASSENGER),
    kèm cột passenger_id để liên kết. Nếu chưa cấu hình -> tạo local như cũ."""
    username = username.strip().lower()

    if is_supabase_configured():
        client = get_supabase_client()
        inserted = client.table("auth_users").insert({
            "username": username,
            "email": f"{username}@local.invalid",
            "password_hash": generate_password_hash(password),
            "full_name": full_name.strip(),
            "status": "Active",
            "passenger_id": passenger_id,
        }).execute().data[0]
        role_rows = client.table("auth_roles").select("id").eq("name", "PASSENGER").execute().data
        if not role_rows:
            role_rows = [client.table("auth_roles").insert(
                {"name": "PASSENGER", "description": "Hành khách"}
            ).execute().data[0]]
        client.table("auth_user_roles").insert(
            {"user_id": inserted["id"], "role_id": role_rows[0]["id"]}
        ).execute()
        return _supabase_users().get(str(inserted["id"]))

    global users_db
    users_db = _load_users()

    numeric_ids = [int(u.id) for u in users_db.values() if u.id.isdigit()]
    next_id = str(max(numeric_ids) + 1) if numeric_ids else "1"

    new_user = User(
        id=next_id,
        username=username,
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
    if is_supabase_configured():
        client = get_supabase_client()
        result = client.table("auth_users").update(
            {"password_hash": generate_password_hash(new_password)}
        ).eq("id", user_id).execute()
        if result.data:
            return _supabase_users().get(str(user_id))

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
