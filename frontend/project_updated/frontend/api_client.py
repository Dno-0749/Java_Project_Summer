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
from config import Config

BASE_URL = Config.API_BASE_URL
TIMEOUT = 5  # giây - tránh treo giao diện quá lâu nếu backend không phản hồi


def _request(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
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
    return _request("GET", f"/cruises/{cruise_id}/activities")


def create_activity(cruise_id, data):
    return _request("POST", f"/cruises/{cruise_id}/activities", json=data)


def list_excursions(cruise_day_id):
    return _request("GET", f"/cruise-days/{cruise_day_id}/excursions")


def create_excursion(cruise_day_id, data):
    return _request("POST", f"/cruise-days/{cruise_day_id}/excursions", json=data)


def register_activity(passenger_id, activity_id=None, excursion_id=None):
    return _request("POST", "/registrations", json={
        "passenger_id": passenger_id,
        "activity_id": activity_id,
        "excursion_id": excursion_id,
    })


def list_activity_registrations(activity_id):
    return _request("GET", f"/activities/{activity_id}/registrations")


def list_excursion_registrations(excursion_id):
    return _request("GET", f"/excursions/{excursion_id}/registrations")


def list_passenger_registrations(passenger_id):
    return _request("GET", f"/passengers/{passenger_id}/registrations")


def cancel_registration(registration_id):
    return _request("PUT", f"/registrations/{registration_id}/cancel")


# ==================== CHECKIN ====================
def checkin(registration_id, method="qr"):
    return _request("POST", "/checkins", json={"registration_id": registration_id, "method": method})


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
