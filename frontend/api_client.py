"""
API Client - lớp bọc gọi HTTP request tới Backend Flask (Clean Architecture)
đang chạy tại config.API_BASE_URL (mặc định http://localhost:9999).

Mọi hàm ở đây trả về (data, error):
  - Nếu thành công: (dict/list dữ liệu, None)
  - Nếu lỗi (backend trả lỗi HOẶC không kết nối được): (None, "thông báo lỗi")
Cách trả về theo tuple giúp code gọi phía blueprint dễ xử lý flash message
mà không cần try/except lặp lại ở khắp nơi.
"""
import requests
from flask import session
from config import Config

BASE_URL = Config.API_BASE_URL
TIMEOUT = 5  # giây - tránh treo giao diện quá lâu nếu backend không phản hồi


def _request(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
    headers = dict(kwargs.pop("headers", {}) or {})
    token = session.get("access_token")
    if token:
        headers.setdefault("Authorization", f"Bearer {token}")
    if headers:
        kwargs["headers"] = headers
    try:
        resp = requests.request(method, url, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        return None, "Không kết nối được tới Backend API. Kiểm tra lại server Flask (port 9999) đã chạy chưa."
    except requests.exceptions.Timeout:
        return None, "Backend API phản hồi quá chậm (timeout)."

    if resp.status_code >= 400:
        try:
            err = resp.json().get("error") or resp.json().get("message") or resp.text
        except Exception:
            err = resp.text
        return None, err

    if resp.status_code == 204 or not resp.content:
        return {}, None

    try:
        return resp.json(), None
    except Exception:
        return None, "Backend trả về dữ liệu không hợp lệ (không phải JSON)."


# ==================== AUTHENTICATION ====================
def login(username, password):
    """Authenticate against the backend and return its canonical user/token."""
    return _request("POST", "/auth/login", json={
        "username": username,
        "password": password,
    })


def get_current_user():
    return _request("GET", "/auth/me")


# ==================== ITINERARY ====================
def list_cruises():
    return _request("GET", "/cruises")


def get_cruise(cruise_id):
    return _request("GET", f"/cruises/{cruise_id}")


def create_cruise(data):
    return _request("POST", "/cruises", json=data)


def list_ports():
    return _request("GET", "/ports")


def list_cruise_days(cruise_id):
    return _request("GET", f"/cruises/{cruise_id}/days")


def create_cruise_day(cruise_id, data):
    return _request("POST", f"/cruises/{cruise_id}/days", json=data)


def update_cruise_day(day_id, data):
    return _request("PUT", f"/cruise-days/{day_id}", json=data)


def create_port(data):
    return _request("POST", "/ports", json=data)


def list_bookings():
    return _request("GET", "/bookings")


def create_booking(data):
    return _request("POST", "/bookings", json=data)


def update_booking(booking_id, data):
    return _request("PUT", f"/bookings/{booking_id}", json=data)


def update_booking_status(booking_id, status):
    return _request("PATCH", f"/bookings/{booking_id}/status", json={"status": status})


def delete_booking(booking_id):
    return _request("DELETE", f"/bookings/{booking_id}")


# ==================== PASSENGER ====================
def list_passengers(cruise_id):
    return _request("GET", f"/cruises/{cruise_id}/passengers")


def get_passenger(passenger_id):
    return _request("GET", f"/passengers/{passenger_id}")


def lookup_passenger(code):
    return _request("GET", f"/passengers/lookup/{code}")


def create_passenger(cruise_id, full_name, cabin_id=None):
    return _request("POST", f"/cruises/{cruise_id}/passengers",
                     json={"full_name": full_name, "cabin_id": cabin_id})


# ==================== ACTIVITY / EXCURSION / REGISTRATION ====================
def list_activities(cruise_id):
    return _request("GET", "/api/activities/")


def create_activity(cruise_id, data):
    return _request("POST", "/api/activities/", json=data)


def list_excursions(cruise_day_id):
    return _request("GET", f"/cruise-days/{cruise_day_id}/excursions")


def create_excursion(cruise_day_id, data):
    return _request("POST", f"/cruise-days/{cruise_day_id}/excursions", json=data)


def register_activity(passenger_id, activity_id=None, excursion_id=None):
    if activity_id is not None:
        return _request("POST", "/api/activity-registrations/", json={
            "passenger_id": passenger_id,
            "activity_id": activity_id,
        })
    if excursion_id is not None:
        return _request("POST", "/excursion-registrations/", json={
            "passenger_id": passenger_id,
            "excursion_id": excursion_id,
        })
    return None, "Cần có activity_id hoặc excursion_id để đăng ký."


def list_activity_registrations(activity_id):
    return _request("GET", f"/api/activity-registrations/activity/{activity_id}")


def list_excursion_registrations(excursion_id):
    return _request("GET", f"/excursions/{excursion_id}/registrations")


def list_passenger_registrations(passenger_id):
    return _request("GET", f"/passengers/{passenger_id}/registrations")


def cancel_registration(registration_id):
    return _request("POST", f"/api/activity-registrations/{registration_id}/cancel")


# ==================== CHECKIN ====================
def checkin(registration_id, method="qr"):
    return _request("POST", f"/api/activity-registrations/{registration_id}/checkin")


# ==================== ACCOUNT / TRANSACTION (offline-sync) ====================
def get_account(passenger_id):
    return _request("GET", f"/passengers/{passenger_id}/account")


def create_transaction(passenger_id, amount, description, staff_id=None, local_id=None):
    return _request("POST", "/transactions", json={
        "passenger_id": passenger_id,
        "amount": amount,
        "description": description,
        "staff_id": staff_id,
        "local_id": local_id,
    })


def sync_transactions(passenger_id, transactions, staff_id=None):
    """transactions: list các dict {local_id, amount, description}."""
    return _request("POST", "/sync/transactions", json={
        "passenger_id": passenger_id,
        "staff_id": staff_id,
        "transactions": transactions,
    })


def list_passenger_transactions(passenger_id):
    return _request("GET", f"/passengers/{passenger_id}/transactions")


def list_all_transactions():
    return _request("GET", "/transactions")


# ==================== SYSTEM ADMIN ====================
def admin_catalog():
    return _request("GET", "/api/admin/catalog")


def admin_users():
    return _request("GET", "/api/admin/users")


def create_admin_user(data):
    return _request("POST", "/api/admin/users", json=data)


def update_admin_user(user_id, data):
    return _request("PUT", f"/api/admin/users/{user_id}", json=data)


def delete_admin_user(user_id):
    return _request("DELETE", f"/api/admin/users/{user_id}")


def admin_ships():
    return _request("GET", "/api/admin/ships")


def create_admin_ship(data):
    return _request("POST", "/api/admin/ships", json=data)


def update_admin_ship(ship_id, data):
    return _request("PUT", f"/api/admin/ships/{ship_id}", json=data)


def delete_admin_ship(ship_id):
    return _request("DELETE", f"/api/admin/ships/{ship_id}")


def admin_areas():
    return _request("GET", "/api/admin/areas")


def create_admin_area(data):
    return _request("POST", "/api/admin/areas", json=data)


def update_admin_area(area_id, data):
    return _request("PUT", f"/api/admin/areas/{area_id}", json=data)


def delete_admin_area(area_id):
    return _request("DELETE", f"/api/admin/areas/{area_id}")


def admin_policies():
    return _request("GET", "/api/admin/policies")


def update_admin_policy(policy_key, data):
    return _request("PUT", f"/api/admin/policies/{policy_key}", json=data)


def admin_devices():
    return _request("GET", "/api/admin/devices")


def create_admin_device(data):
    return _request("POST", "/api/admin/devices", json=data)


def update_admin_device(device_id, data):
    return _request("PUT", f"/api/admin/devices/{device_id}", json=data)


def delete_admin_device(device_id):
    return _request("DELETE", f"/api/admin/devices/{device_id}")


def admin_logs(limit=200):
    return _request("GET", f"/api/admin/logs?limit={limit}")


def refund_transaction(transaction_id):
    return _request("PUT", f"/transactions/{transaction_id}/refund")


# ==================== HELPER CHO DEMO ====================
def ensure_demo_cruise():
    """Đảm bảo luôn có ít nhất 1 chuyến cruise để demo (lấy chuyến đầu tiên,
    nếu chưa có chuyến nào thì tự tạo 1 chuyến mẫu)."""
    cruises, err = list_cruises()
    if err:
        return None, err
    if cruises:
        return cruises[0], None
    return create_cruise({
        "name": "Vịnh Hạ Long 3N2Đ (Demo)",
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
        "status": "ongoing",
    })


def ensure_demo_passenger(cruise_id, full_name="Hành khách Demo"):
    """Đảm bảo có 1 passenger demo trong chuyến hiện tại (dùng cho tài khoản
    'passenger' quick-login), tự tạo nếu chưa có."""
    passengers, err = list_passengers(cruise_id)
    if err:
        return None, err
    if passengers:
        return passengers[0], None
    return create_passenger(cruise_id, full_name)


# ==================== REPORT ====================
def reconcile_account(account_id):
    return _request("POST", f"/accounts/{account_id}/reconcile")


def get_anomalies():
    return _request("GET", "/transactions/anomalies")


def settle_account(account_id):
    return _request("POST", f"/accounts/{account_id}/settle")


def mark_disputed(transaction_id):
    return _request("PUT", f"/transactions/{transaction_id}/dispute")


def issue_invoice(account_id):
    return _request("POST", f"/accounts/{account_id}/invoice")


def get_dashboard(cruise_id):
    return _request("GET", f"/cruises/{cruise_id}/dashboard")


# ==================== FEEDBACK ====================
def create_feedback(passenger_id, target_type, rating, target_id=None, target_name=None, comment=None):
    return _request("POST", "/feedback", json={
        "passenger_id": passenger_id, "target_type": target_type, "rating": rating,
        "target_id": target_id, "target_name": target_name, "comment": comment,
    })


def list_passenger_feedback(passenger_id):
    return _request("GET", f"/passengers/{passenger_id}/feedback")


# ==================== NOTIFICATION ====================
def list_passenger_notifications(passenger_id, cruise_id=None):
    params = {"cruise_id": cruise_id} if cruise_id else {}
    return _request("GET", f"/passengers/{passenger_id}/notifications", params=params)


def mark_notification_read(notification_id):
    return _request("PUT", f"/notifications/{notification_id}/read")
