import os
import sys
from datetime import datetime

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from functools import wraps

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from supabase_client import get_supabase_client

operations_bp = Blueprint("operations", __name__, url_prefix="/operations")


def _safe_value(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _fetch_table(client, table_name, limit=200):
    response = client.table(table_name).select("*").limit(limit).execute()
    return response.data if hasattr(response, "data") and response.data else []


def _normalise_checkins(rows):
    normalized = []
    for index, item in enumerate(rows, start=1):
        status = str(item.get("status") or item.get("checkin_status") or "Đang ở ngoài tàu")
        status_lower = status.lower()
        if status_lower in {"returned", "completed", "onboard", "đã quay lại"}:
            status = "Đã quay lại"
        elif status_lower in {"late", "overdue", "quay lại trễ", "delayed"}:
            status = "Quay lại trễ"
        elif status_lower in {"not_checked_in", "missing", "chưa check-in"}:
            status = "Chưa check-in"
        else:
            status = "Đang ở ngoài tàu"

        normalized.append({
            "id": item.get("id") or item.get("checkin_id") or f"CHK-{index:04d}",
            "passenger": item.get("passenger_name") or item.get("passenger") or item.get("name") or "Không rõ",
            "cabin": item.get("cabin") or item.get("room") or item.get("cabin_number") or "-",
            "excursion": item.get("excursion_name") or item.get("excursion") or item.get("tour") or "-",
            "checkin_time": item.get("checkin_time") or item.get("checked_in_at") or item.get("created_at") or "-",
            "expected_return": item.get("expected_return") or item.get("return_deadline") or item.get("deadline") or "-",
            "returned_time": item.get("returned_time") or item.get("returned_at") or "",
            "status": status,
        })
    return normalized


def _fetch_checkin_monitor_data():
    client = get_supabase_client()
    rows = _fetch_table(client, "checkins")
    checkins = _normalise_checkins(rows)
    return {
        "checkins": checkins,
        "summary": {
            "total": len(checkins),
            "returned": sum(item["status"] == "Đã quay lại" for item in checkins),
            "outside": sum(item["status"] == "Đang ở ngoài tàu" for item in checkins),
            "late": sum(item["status"] == "Quay lại trễ" for item in checkins),
            "not_checked_in": sum(item["status"] == "Chưa check-in" for item in checkins),
        },
    }


def _fetch_live_dashboard_data():
    client = get_supabase_client()

    table_names = [
        "passengers",
        "activities",
        "shore_excursions",
        "onboard_transactions",
        "checkins",
        "bookings",
    ]
    rows_by_table = {}

    for table_name in table_names:
        rows_by_table[table_name] = _fetch_table(client, table_name, limit=50)

    passengers = rows_by_table.get("passengers", [])
    activities = rows_by_table.get("activities", [])
    excursions = rows_by_table.get("shore_excursions", [])
    transactions = rows_by_table.get("onboard_transactions", [])
    checkins = rows_by_table.get("checkins", [])
    bookings = rows_by_table.get("bookings", [])

    stats = {
        "passengers": len(passengers),
        "activities_today": len(activities),
        "excursions_today": len(excursions),
        "revenue_today": sum(_safe_value(item.get("amount")) for item in transactions if item.get("amount") is not None),
        "checkins_today": len(checkins),
        "pending_registrations": sum(1 for item in bookings if str(item.get("status", "")).lower() in {"pending", "waiting", "new"}),
    }

    recent = []
    for table_name, payload in [
        ("transactions", transactions),
        ("checkins", checkins),
        ("activities", activities),
        ("excursions", excursions),
    ]:
        for item in payload[:5]:
            if table_name == "transactions":
                recent.append({
                    "time": str(item.get("created_at") or item.get("time") or datetime.now().strftime("%H:%M")),
                    "event": f"Giao dịch: {item.get('item') or item.get('name') or 'Thanh toán'}",
                    "user": item.get("staff") or item.get("user") or "System",
                })
            elif table_name == "checkins":
                recent.append({
                    "time": str(item.get("created_at") or item.get("time") or datetime.now().strftime("%H:%M")),
                    "event": item.get("event") or "Check-in hành khách",
                    "user": item.get("staff") or item.get("user") or "Hành khách",
                })
            else:
                recent.append({
                    "time": str(item.get("created_at") or item.get("time") or datetime.now().strftime("%H:%M")),
                    "event": item.get("name") or item.get("title") or f"{table_name.title()} hoạt động",
                    "user": item.get("staff") or item.get("user") or "Hệ thống",
                })

    return {"stats": stats, "recent_activities": recent[:5]}


def operations_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "operations":
            return render_template("system_admin/403.html"), 403
        return f(*args, **kwargs)
    return decorated_function


@operations_bp.route("/dashboard")
@login_required
@operations_access
def dashboard():
    dashboard_data = _fetch_live_dashboard_data()
    return render_template(
        "operations/dashboard.html",
        stats=dashboard_data["stats"],
        recent_activities=dashboard_data["recent_activities"],
        page_title="Dashboard Vận hành"
    )


@operations_bp.route("/checkins")
@login_required
@operations_access
def checkin_monitor():
    monitor_data = _fetch_checkin_monitor_data()
    selected_status = (request.args.get("status") or "all").strip()
    if selected_status != "all":
        monitor_data["checkins"] = [
            item for item in monitor_data["checkins"] if item["status"] == selected_status
        ]
    return render_template(
        "operations/checkins.html",
        checkins=monitor_data["checkins"],
        summary=monitor_data["summary"],
        selected_status=selected_status,
        page_title="Giám sát check-in",
    )
