import os

from supabase import Client, create_client
from werkzeug.security import check_password_hash


ROLE_MAP = {
    "ADMIN": ("admin", "Quản trị viên hệ thống"),
    "OPERATIONS_MANAGER": ("operations", "Quản lý vận hành"),
    "FINANCE": ("finance", "Tài chính & Lễ tân"),
    "ITINERARY_STAFF": ("coordinator", "Điều phối lịch trình"),
    "ACTIVITY_STAFF": ("activity_manager", "Quản lý hoạt động"),
}


def _client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    return create_client(url, key)


def authenticate(username: str, password: str):
    client = _client()
    users = client.table("auth_users").select(
        "id, username, password_hash, status"
    ).eq("username", username.strip().lower()).limit(1).execute().data or []
    if not users:
        return None

    user = users[0]
    if user.get("status", "Active") != "Active":
        return None
    if not check_password_hash(user["password_hash"], password):
        return None

    links = client.table("auth_user_roles").select("role_id").eq("user_id", user["id"]).limit(1).execute().data or []
    role_name = ""
    if links:
        roles = client.table("auth_roles").select("name").eq("id", links[0]["role_id"]).limit(1).execute().data or []
        role_name = roles[0]["name"] if roles else ""

    role, display_name = ROLE_MAP.get(role_name, (role_name.lower(), role_name or "User"))
    return {
        "id": str(user["id"]),
        "username": user["username"],
        "full_name": user["username"],
        "role": role,
        "role_name": display_name,
        "status": user.get("status", "Active"),
    }


def delete_user(user_id: str) -> bool:
    client = _client()
    result = client.table("auth_users").delete().eq("id", user_id).select("id").execute()
    return bool(result.data)


def list_users():
    client = _client()
    users = client.table("auth_users").select(
        "id, username, status"
    ).order("id").execute().data or []
    roles = client.table("auth_roles").select("id, name").execute().data or []
    links = client.table("auth_user_roles").select("user_id, role_id").execute().data or []
    role_names = {str(role["id"]): role["name"] for role in roles}
    roles_by_user = {
        str(link["user_id"]): role_names.get(str(link["role_id"]), "")
        for link in links
    }
    result = []
    for user in users:
        role_name = roles_by_user.get(str(user["id"]), "")
        role, display_name = ROLE_MAP.get(role_name, (role_name.lower(), role_name or "User"))
        result.append({
            "id": str(user["id"]),
            "username": user["username"],
            "full_name": user["username"],
            "role": role,
            "role_name": display_name,
            "status": user.get("status", "Active"),
        })
    return result
