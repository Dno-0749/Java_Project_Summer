from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from functools import wraps
import store

pos_bp = Blueprint("pos", __name__, url_prefix="/pos")


def pos_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["sales_staff", "admin"]:
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


def _get_cart():
    """Giỏ hàng lưu trong session của phiên làm việc nhân viên (Flask session)."""
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


@pos_bp.route("/")
@pos_bp.route("/sales")
@login_required
@pos_access
def sales():
    items, total = _cart_details()
    categories = sorted(set(i["category"] for i in store.POS_ITEMS))
    return render_template(
        "pos/sales.html",
        products=store.POS_ITEMS,
        categories=categories,
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


@pos_bp.route("/checkout")
@login_required
@pos_access
def checkout():
    items, total = _cart_details()
    if not items:
        flash("Giỏ hàng đang trống. Vui lòng chọn dịch vụ trước.", "warning")
        return redirect(url_for("pos.sales"))
    return render_template(
        "pos/checkout.html",
        passengers=store.PASSENGERS,
        cart_items=items,
        cart_total=total,
        page_title="Xác thực hành khách",
    )


@pos_bp.route("/checkout/confirm", methods=["POST"])
@login_required
@pos_access
def checkout_confirm():
    items, total = _cart_details()
    if not items:
        return redirect(url_for("pos.sales"))

    passenger_id = request.form.get("passenger_id")
    passenger = store.get_passenger_by_id(passenger_id)
    if not passenger:
        flash("Không tìm thấy hành khách. Vui lòng quét lại thẻ/QR.", "danger")
        return redirect(url_for("pos.checkout"))

    is_offline = request.form.get("offline_mode") == "1"
    tx = store.create_transaction(
        passenger, items, total,
        staff_name=current_user.full_name,
        is_offline=is_offline,
    )

    session["pos_cart"] = {}
    session.modified = True

    if is_offline:
        flash(f"Đã lưu giao dịch {tx['id']} offline — sẽ tự động đồng bộ khi có mạng.", "warning")
    else:
        flash(f"Giao dịch {tx['id']} đã ghi nợ thành công vào tài khoản {passenger['name']}.", "success")

    return redirect(url_for("pos.history"))


@pos_bp.route("/history")
@login_required
@pos_access
def history():
    return render_template(
        "pos/history.html",
        transactions=store.TRANSACTIONS,
        page_title="Lịch sử giao dịch ca làm việc",
    )
