"""
Dữ liệu mock dùng chung cho 2 module POS (Nhân viên bán hàng & dịch vụ)
và Passenger (Hành khách). Đây là in-memory store cho mục đích demo,
sau này sẽ thay bằng các API call tới backend Flask thật (API_BASE_URL
trong config.py).
"""
from datetime import datetime
import uuid

# ============ Danh mục sản phẩm / dịch vụ bán tại POS ============
POS_ITEMS = [
    {"id": 1, "name": "Cocktail Mojito", "category": "Đồ uống", "price": 180000},
    {"id": 2, "name": "Spa - Massage 60p", "category": "Spa", "price": 1200000},
    {"id": 3, "name": "Wine Tasting", "category": "Đồ uống", "price": 850000},
    {"id": 4, "name": "Specialty Dining", "category": "Ẩm thực", "price": 950000},
    {"id": 5, "name": "Thuê ghế bãi biển VIP", "category": "Tiện ích", "price": 300000},
    {"id": 6, "name": "Giặt ủi nhanh", "category": "Tiện ích", "price": 150000},
    {"id": 7, "name": "Nước suối 500ml", "category": "Đồ uống", "price": 40000},
    {"id": 8, "name": "Bánh ngọt tráng miệng", "category": "Ẩm thực", "price": 120000},
]

# ============ Hành khách (mock passenger, dùng chung 2 module) ============
PASSENGERS = [
    {"id": 1, "name": "Nguyễn Văn A", "cabin": "1204", "card_id": "CR-8821", "balance": 2_150_000},
    {"id": 2, "name": "Trần Thị B", "cabin": "0812", "card_id": "CR-8822", "balance": 850_000},
    {"id": 3, "name": "Lê Hoàng C", "cabin": "1501", "card_id": "CR-8823", "balance": 0},
    {"id": 4, "name": "Phạm Minh D", "cabin": "0605", "card_id": "CR-8824", "balance": 3_400_000},
]

# ============ Lịch trình chuyến đi (mock cho passenger) ============
ITINERARY = [
    {
        "day": 1, "date": "12/09/2026", "port": "Xuất phát - Cảng Nha Trang",
        "arrival": "-", "departure": "18:00",
        "notes": "Nhận phòng từ 14:00. Tiệc chào mừng lúc 19:30 tại Main Deck."
    },
    {
        "day": 2, "date": "13/09/2026", "port": "Trên biển (Sea Day)",
        "arrival": "-", "departure": "-",
        "notes": "Ngày nghỉ trên biển, tham gia các hoạt động giải trí trên tàu."
    },
    {
        "day": 3, "date": "14/09/2026", "port": "Cảng Nam Du",
        "arrival": "07:00", "departure": "17:30",
        "notes": "Có 3 tour tham quan bờ. Giờ tập trung quay lại tàu: 17:00."
    },
    {
        "day": 4, "date": "15/09/2026", "port": "Cảng Phú Quốc",
        "arrival": "08:00", "departure": "22:00",
        "notes": "Cập nhật: đổi giờ rời cảng do thời tiết (ban đầu 20:00)."
    },
]

# ============ Hoạt động trên tàu & tham quan bờ ============
PASSENGER_ACTIVITIES = [
    {"id": 1, "name": "Yoga buổi sáng", "type": "activity", "location": "Sundeck",
     "day": 2, "time": "06:30 - 07:30", "capacity": 40, "registered": 35, "price": 0},
    {"id": 2, "name": "Wine Tasting", "type": "activity", "location": "Sky Lounge",
     "day": 2, "time": "16:00 - 17:30", "capacity": 25, "registered": 25, "price": 850000},
    {"id": 3, "name": "Live Music Night", "type": "activity", "location": "Main Stage",
     "day": 1, "time": "20:00 - 22:00", "capacity": 200, "registered": 178, "price": 0},
    {"id": 4, "name": "Cooking Class", "type": "activity", "location": "Culinary Studio",
     "day": 2, "time": "10:00 - 12:00", "capacity": 15, "registered": 12, "price": 1200000},
    {"id": 5, "name": "Tour khám phá Nam Du", "type": "excursion", "location": "Cảng Nam Du",
     "day": 3, "time": "08:00 - 16:30", "capacity": 50, "registered": 41, "price": 1500000},
    {"id": 6, "name": "Lặn ngắm san hô Phú Quốc", "type": "excursion", "location": "Cảng Phú Quốc",
     "day": 4, "time": "09:00 - 13:00", "capacity": 20, "registered": 20, "price": 2200000},
]

# id các hoạt động mà hành khách demo (passenger đang đăng nhập) đã đăng ký
PASSENGER_REGISTRATIONS = {3, 5}

# ============ Thông báo ============
NOTIFICATIONS = [
    {"id": 1, "priority": "high", "time": "15/09 07:40",
     "title": "Cập nhật giờ rời cảng Phú Quốc",
     "content": "Do thời tiết, tàu sẽ rời cảng lúc 22:00 thay vì 20:00 như dự kiến. Vui lòng quay lại tàu trước 21:30."},
    {"id": 2, "priority": "normal", "time": "14/09 18:05",
     "title": "Cảm ơn bạn đã tham gia Tour Nam Du",
     "content": "Hãy để lại đánh giá của bạn về chuyến tham quan hôm nay."},
    {"id": 3, "priority": "normal", "time": "13/09 09:00",
     "title": "Hoạt động hôm nay",
     "content": "Yoga buổi sáng (06:30), Cooking Class (10:00), Wine Tasting (16:00)."},
    {"id": 4, "priority": "normal", "time": "12/09 14:00",
     "title": "Chào mừng lên tàu!",
     "content": "Chúc bạn có một chuyến đi tuyệt vời. Xem lịch trình chi tiết trong mục Lịch trình."},
]

# ============ Giao dịch (transaction) — dùng chung, mô phỏng offline-sync ============
TRANSACTIONS = [
    {"id": "TX-10021", "passenger_id": 1, "cabin": "1204", "item": "Spa - Massage 60p",
     "amount": 1_200_000, "time": "10:22", "staff": "NV POS 02", "sync_status": "synced"},
    {"id": "TX-10020", "passenger_id": 2, "cabin": "0812", "item": "Wine Tasting",
     "amount": 850_000, "time": "09:45", "staff": "NV POS 01", "sync_status": "synced"},
    {"id": "TX-10019", "passenger_id": 4, "cabin": "1501", "item": "Shore Excursion",
     "amount": 1_500_000, "time": "08:30", "staff": "System", "sync_status": "synced"},
]


def create_transaction(passenger, items, total, staff_name, is_offline=False):
    """Tạo 1 giao dịch mới - mô phỏng đúng luồng đã mô tả trong SRS mục 3.4.6.3:
    mỗi giao dịch có local_id (UUID) sinh tại thiết bị để chống trùng khi đồng bộ.
    """
    tx = {
        "id": f"TX-{10022 + len(TRANSACTIONS)}",
        "local_id": str(uuid.uuid4()),
        "passenger_id": passenger["id"],
        "cabin": passenger["cabin"],
        "item": ", ".join(i["name"] for i in items),
        "amount": total,
        "time": datetime.now().strftime("%H:%M"),
        "staff": staff_name,
        "sync_status": "pending_sync" if is_offline else "synced",
    }
    TRANSACTIONS.insert(0, tx)
    passenger["balance"] -= total
    return tx


def get_passenger_by_id(pid):
    return next((p for p in PASSENGERS if p["id"] == int(pid)), None)


def get_activity_by_id(aid):
    return next((a for a in PASSENGER_ACTIVITIES if a["id"] == int(aid)), None)
