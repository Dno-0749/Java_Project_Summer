from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from functools import wraps
from collections import defaultdict
import uuid
import store
import api_client

pos_bp = Blueprint("pos", __name__, url_prefix="/pos")


def pos_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["sales_staff", "finance", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def _get_cart():
    return session.setdefault("pos_cart", {})


def _cart_details():
    cart = _get_cart()
    items = []
    total = 0
    for item_id, qty in cart.items():
        item = next((i for i in store.POS_ITEMS if i["id"] == int(item_id)), None)
        if item:
            subtotal = item["price"] * qty
            items.append({**item, "qty": qty, "subtotal": subtotal})
            total += subtotal
    return items, total


# ==================== BÁN HÀNG ====================

@pos_bp.route("/")
@pos_bp.route("/sales")
@login_required
@pos_access
def sales():
    items, total = _cart_details()
    q = request.args.get("q", "").strip().lower()
    categories = sorted(set(i["category"] for i in store.POS_ITEMS))
    current_cat = request.args.get("cat", categories[0])

    products = store.POS_ITEMS
    if q:
        # Tìm kiếm sản phẩm/dịch vụ - tìm trên TOÀN BỘ danh mục, không giới hạn theo category
        products = [p for p in products if q in p["name"].lower()]

    return render_template(
        "pos/sales.html",
        products=products,
        categories=categories,
        current_cat=current_cat,
        search_query=q,
        cart_items=items,
        cart_total=total,
        page_title="Bán hàng POS",
    )


@pos_bp.route("/cart/add/<int:item_id>", methods=["POST"])
@login_required
@pos_access
def cart_add(item_id):
    cart = _get_cart()
    key = str(item_id)
    cart[key] = cart.get(key, 0) + 1
    session.modified = True
    return redirect(url_for("pos.sales"))


@pos_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
@pos_access
def cart_remove(item_id):
    cart = _get_cart()
    key = str(item_id)
    if key in cart:
        cart[key] -= 1
        if cart[key] <= 0:
            del cart[key]
    session.modified = True
    return redirect(url_for("pos.sales"))


@pos_bp.route("/cart/clear", methods=["POST"])
@login_required
@pos_access
def cart_clear():
    session["pos_cart"] = {}
    session.modified = True
    flash("Đã hủy giao dịch hiện tại.", "info")
    return redirect(url_for("pos.sales"))


# ==================== XÁC THỰC HÀNH KHÁCH & THANH TOÁN ====================

@pos_bp.route("/checkout")
@login_required
@pos_access
def checkout():
    items, total = _cart_details()
    if not items:
        flash("Giỏ hàng đang trống. Vui lòng chọn dịch vụ trước.", "warning")
        return redirect(url_for("pos.sales"))

    cruise, err = api_client.ensure_demo_cruise()
    passengers = []
    if err:
        flash(f"Lỗi kết nối backend: {err}", "danger")
    else:
        passengers, err2 = api_client.list_passengers(cruise["id"])
        if err2:
            flash(f"Lỗi tải danh sách hành khách: {err2}", "danger")
            passengers = []
        elif not passengers:
            names = ["Nguyễn Văn A", "Trần Thị B", "Lê Hoàng C"]
            passengers = []
            for n in names:
                p, e = api_client.create_passenger(cruise["id"], n)
                if p:
                    passengers.append(p)

    view_passengers = []
    for p in passengers:
        account, _ = api_client.get_account(p["id"])
        view_passengers.append({
            "id": p["id"], "name": p["full_name"],
            "cabin": p.get("cabin_id") or "-", "card_id": p.get("qr_code") or "-",
            "balance": float(account["balance"]) if account else 0,
        })

    if not view_passengers:
        flash("Không tìm thấy hành khách nào. Kiểm tra Backend đã chạy và kết nối Supabase chưa.", "danger")
        return redirect(url_for("pos.sales"))

    return render_template(
        "pos/checkout.html",
        passengers=view_passengers,
        cart_items=items,
        cart_total=total,
        page_title="Xác thực hành khách",
    )


@pos_bp.route("/checkout/confirm", methods=["POST"])
@login_required
@pos_access
def checkout_confirm():
    """Xác nhận giao dịch khi ĐANG CÓ MẠNG - ghi thẳng vào backend."""
    items, total = _cart_details()
    if not items:
        return redirect(url_for("pos.sales"))

    passenger_id = request.form.get("passenger_id")
    passenger_name = request.form.get("passenger_name", "Hành khách")
    if not passenger_id:
        flash("Không tìm thấy hành khách. Vui lòng quét lại thẻ/QR.", "danger")
        return redirect(url_for("pos.checkout"))

    description = ", ".join(i["name"] for i in items)
    local_id = str(uuid.uuid4())  # local_id sinh TẠI THIẾT BỊ (BR-04) dù đang online

    tx, err = api_client.create_transaction(
        passenger_id=int(passenger_id), amount=float(total),
        description=description, local_id=local_id,
    )
    if err:
        flash(f"Lỗi tạo giao dịch: {err}", "danger")
        return redirect(url_for("pos.checkout"))

    session["pos_cart"] = {}
    session.modified = True

    # Lưu tạm thông tin để hiển thị trang hóa đơn (receipt), không cần gọi
    # thêm API vì backend chưa có endpoint GET 1 transaction theo id
    session["last_receipt"] = {
        "id": tx["id"], "passenger_name": passenger_name,
        "cart_items": items, "total": total,
        "time": tx.get("created_at", ""), "staff_name": current_user.full_name,
    }
    return redirect(url_for("pos.receipt"))


@pos_bp.route("/receipt")
@login_required
@pos_access
def receipt():
    """UC: Hiển thị hóa đơn/receipt sau khi xác nhận giao dịch thành công."""
    data = session.pop("last_receipt", None)
    if not data:
        flash("Không có hóa đơn nào để hiển thị.", "warning")
        return redirect(url_for("pos.sales"))
    return render_template("pos/receipt.html", receipt=data, page_title="Hóa đơn giao dịch")


# ==================== OFFLINE THẬT (lưu ở trình duyệt + đồng bộ riêng) ====================

@pos_bp.route("/checkout/save-offline", methods=["POST"])
@login_required
@pos_access
def save_offline():
    """Khi tắt mạng (giả lập bằng toggle): KHÔNG gọi backend ở bước này.
    Chuyển sang trang trung gian, trang đó dùng JavaScript lưu giao dịch
    vào localStorage của trình duyệt (thực sự lưu tại thiết bị, không qua
    server), rồi tự động quay lại màn bán hàng."""
    items, total = _cart_details()
    if not items:
        return redirect(url_for("pos.sales"))

    passenger_id = request.form.get("passenger_id")
    passenger_name = request.form.get("passenger_name", "Hành khách")
    if not passenger_id:
        flash("Không tìm thấy hành khách.", "danger")
        return redirect(url_for("pos.checkout"))

    description = ", ".join(i["name"] for i in items)
    local_id = str(uuid.uuid4())

    session["pos_cart"] = {}
    session.modified = True

    return render_template(
        "pos/offline_save.html",
        transaction={
            "local_id": local_id, "passenger_id": int(passenger_id),
            "passenger_name": passenger_name, "amount": float(total),
            "description": description,
        },
        page_title="Đã lưu offline",
    )


@pos_bp.route("/sync-now", methods=["POST"])
@login_required
@pos_access
def sync_now():
    """Nhận batch giao dịch đang chờ đồng bộ từ localStorage (do JS gửi lên
    qua fetch()), gộp theo passenger_id rồi gọi backend /sync/transactions
    cho từng hành khách. Trả JSON để JS xoá đúng các item đã đồng bộ thành
    công khỏi localStorage."""
    payload = request.get_json(silent=True) or {}
    queue = payload.get("transactions", [])
    if not queue:
        return jsonify({"synced_local_ids": [], "failed": []})

    grouped = defaultdict(list)
    for tx in queue:
        grouped[tx["passenger_id"]].append(tx)

    synced_local_ids = []
    failed = []
    for passenger_id, txs in grouped.items():
        result, err = api_client.sync_transactions(
            passenger_id=passenger_id,
            transactions=[{"local_id": t["local_id"], "amount": t["amount"], "description": t["description"]} for t in txs],
            staff_id=None,
        )
        if err:
            for t in txs:
                failed.append({"local_id": t["local_id"], "message": err})
            continue
        for r in result.get("results", []):
            if r["status"] in ("synced", "already_synced"):
                synced_local_ids.append(r["local_id"])
            else:
                failed.append(r)

    return jsonify({"synced_local_ids": synced_local_ids, "failed": failed})


# ==================== LỊCH SỬ, TÌM KIẾM, HOÀN TIỀN ====================

@pos_bp.route("/history")
@login_required
@pos_access
def history():
    transactions, err = api_client.list_all_transactions()
    if err:
        flash(f"Lỗi tải lịch sử giao dịch: {err}", "danger")
        transactions = []

    q = request.args.get("q", "").strip().lower()

    view_transactions = [{
        "id": t["id"], "cabin": t.get("onboard_account_id"),
        "item": t.get("description") or "-", "amount": float(t["amount"]),
        "time": (t.get("created_at") or "")[11:16], "staff": t.get("staff_id") or "-",
        "sync_status": t["sync_status"], "local_id": t.get("local_id") or "-",
    } for t in (transactions or [])]

    if q:
        view_transactions = [
            t for t in view_transactions
            if q in str(t["id"]) or q in t["item"].lower() or q in str(t["cabin"])
        ]

    return render_template(
        "pos/history.html",
        transactions=view_transactions,
        search_query=q,
        page_title="Lịch sử giao dịch ca làm việc",
    )


@pos_bp.route("/transactions/<int:transaction_id>/refund", methods=["POST"])
@login_required
@pos_access
def refund(transaction_id):
    """UC24: Hủy/hoàn tiền giao dịch."""
    result, err = api_client.refund_transaction(transaction_id)
    if err:
        flash(f"Không thể hoàn tiền: {err}", "danger")
    else:
        flash(f"Đã hoàn tiền giao dịch #{transaction_id} thành công.", "success")
    return redirect(url_for("pos.history"))


# ==================== ĐỐI SOÁT (RECONCILIATION) ====================

@pos_bp.route("/reconciliation")
@login_required
@pos_access
def reconciliation():
    """UC27: Xem các giao dịch cần đối soát, đối chiếu, phát hiện bất thường."""
    transactions, err = api_client.list_all_transactions()
    if err:
        flash(f"Lỗi tải giao dịch: {err}", "danger")
        transactions = []

    # Nhóm theo onboard_account_id để đối soát theo từng tài khoản
    groups = defaultdict(list)
    for t in transactions or []:
        groups[t["onboard_account_id"]].append(t)

    view_groups = []
    for account_id, txs in groups.items():
        unreconciled = [t for t in txs if t["sync_status"] == "synced"]
        disputed = [t for t in txs if t["sync_status"] == "disputed"]
        view_groups.append({
            "account_id": account_id,
            "total_transactions": len(txs),
            "unreconciled_count": len(unreconciled),
            "disputed_count": len(disputed),
            "transactions": [{
                "id": t["id"], "item": t.get("description") or "-",
                "amount": float(t["amount"]), "sync_status": t["sync_status"],
            } for t in txs],
        })

    return render_template("pos/reconciliation.html", groups=view_groups, page_title="Đối soát giao dịch")


@pos_bp.route("/accounts/<int:account_id>/reconcile", methods=["POST"])
@login_required
@pos_access
def reconcile_account(account_id):
    result, err = api_client.reconcile_account(account_id)
    if err:
        flash(f"Không thể đối soát: {err}", "danger")
    else:
        flash(f"Đã đối soát {result.get('reconciled_count', 0)} giao dịch cho tài khoản #{account_id}.", "success")
    return redirect(url_for("pos.reconciliation"))


@pos_bp.route("/transactions/<int:transaction_id>/dispute", methods=["POST"])
@login_required
@pos_access
def mark_disputed(transaction_id):
    result, err = api_client.mark_disputed(transaction_id)
    if err:
        flash(f"Không thể đánh dấu tranh chấp: {err}", "danger")
    else:
        flash(f"Đã đánh dấu giao dịch #{transaction_id} là tranh chấp - cần xử lý trước khi xuất hóa đơn.", "warning")
    return redirect(url_for("pos.reconciliation"))
