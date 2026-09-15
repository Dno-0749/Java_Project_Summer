import csv
import io
from datetime import datetime
from functools import wraps

from flask import Blueprint, Response, render_template, request
from flask_login import current_user, login_required

import os
import sys

SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from supabase_client import get_supabase_client

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def reports_access(view):
    @wraps(view)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ["admin", "operations"]:
            return render_template("system_admin/403.html"), 403
        return view(*args, **kwargs)

    return decorated_function


def _fetch_rows(client, table_name):
    response = client.table(table_name).select("*").limit(500).execute()
    return response.data if hasattr(response, "data") and response.data else []


def _row_date(row):
    value = row.get("date") or row.get("created_at") or row.get("transaction_date")
    return str(value)[:10] if value else ""


def _filter_by_date(rows, start_date, end_date):
    if not start_date and not end_date:
        return rows
    filtered = []
    for row in rows:
        row_date = _row_date(row)
        if not row_date:
            filtered.append(row)
            continue
        if start_date and row_date < start_date:
            continue
        if end_date and row_date > end_date:
            continue
        filtered.append(row)
    return filtered


def _load_report_rows(start_date=None, end_date=None):
    client = get_supabase_client()
    transactions = _fetch_rows(client, "onboard_transactions")
    activities = _fetch_rows(client, "activities")
    return (
        _filter_by_date(transactions, start_date, end_date),
        _filter_by_date(activities, start_date, end_date),
        "Supabase",
    )


def build_report_data(start_date=None, end_date=None):
    transactions, activities, data_source = _load_report_rows(start_date, end_date)
    revenue = sum(float(
        transaction.get("amount")
        or transaction.get("total_amount")
        or transaction.get("total")
        or 0
    ) for transaction in transactions)
    participants = sum(int(activity.get("registered") or activity.get("participants") or 0) for activity in activities)
    capacity = sum(int(activity.get("capacity") or 0) for activity in activities)
    occupancy_rate = round(participants / capacity * 100, 1) if capacity else 0

    activity_rows = []
    for activity in activities:
        registered = int(activity.get("registered") or activity.get("participants") or 0)
        activity_capacity = int(activity.get("capacity") or 0)
        rate = round(registered / activity_capacity * 100, 1) if activity_capacity else 0
        activity_rows.append({
            **activity,
            "name": activity.get("name") or activity.get("title") or "Hoạt động",
            "type": activity.get("type") or activity.get("category") or "-",
            "registered": registered,
            "capacity": activity_capacity,
            "occupancy_rate": rate,
        })

    return {
        "revenue": revenue,
        "participants": participants,
        "capacity": capacity,
        "occupancy_rate": occupancy_rate,
        "transactions": transactions,
        "activities": activity_rows,
        "data_source": data_source,
        "start_date": start_date or "",
        "end_date": end_date or "",
    }


@reports_bp.route("/")
@login_required
@reports_access
def index():
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    return render_template(
        "reports/index.html",
        report=build_report_data(start_date, end_date),
        page_title="Báo cáo thống kê",
    )


@reports_bp.route("/export.csv")
@login_required
@reports_access
def export_csv():
    report = build_report_data(
        request.args.get("start_date", "").strip(),
        request.args.get("end_date", "").strip(),
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Báo cáo thống kê Cruise Management"])
    writer.writerow(["Ngày xuất", datetime.now().strftime("%Y-%m-%d %H:%M")])
    writer.writerow([])
    writer.writerow(["Chỉ số", "Giá trị"])
    writer.writerow(["Tổng doanh thu", report["revenue"]])
    writer.writerow(["Tổng lượt đăng ký", report["participants"]])
    writer.writerow(["Tổng sức chứa", report["capacity"]])
    writer.writerow(["Công suất trung bình (%)", report["occupancy_rate"]])
    writer.writerow([])
    writer.writerow(["Hoạt động", "Loại", "Đăng ký", "Sức chứa", "Công suất (%)"])
    for activity in report["activities"]:
        writer.writerow([
            activity["name"],
            activity["type"],
            activity["registered"],
            activity["capacity"],
            activity["occupancy_rate"],
        ])

    response = Response(output.getvalue(), mimetype="text/csv; charset=utf-8-sig")
    response.headers["Content-Disposition"] = "attachment; filename=cruise-report.csv"
    return response


def _report_dates():
    return (
        request.args.get("start_date", "").strip(),
        request.args.get("end_date", "").strip(),
    )


@reports_bp.route("/export.xlsx")
@login_required
@reports_access
def export_xlsx():
    from openpyxl import Workbook

    report = build_report_data(*_report_dates())
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Bao cao van hanh"
    sheet.append(["Bao cao thong ke Cruise Management"])
    sheet.append(["Nguon du lieu", report["data_source"]])
    sheet.append(["Tong doanh thu", report["revenue"]])
    sheet.append(["Tong luot dang ky", report["participants"]])
    sheet.append(["Tong suc chua", report["capacity"]])
    sheet.append(["Cong suat trung binh (%)", report["occupancy_rate"]])
    sheet.append([])
    sheet.append(["Hoat dong", "Loai", "Dang ky", "Suc chua", "Cong suat (%)"])
    for activity in report["activities"]:
        sheet.append([
            activity["name"], activity["type"], activity["registered"],
            activity["capacity"], activity["occupancy_rate"],
        ])

    output = io.BytesIO()
    workbook.save(output)
    response = Response(
        output.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response.headers["Content-Disposition"] = "attachment; filename=cruise-report.xlsx"
    return response


@reports_bp.route("/export.pdf")
@login_required
@reports_access
def export_pdf():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph

    report = build_report_data(*_report_dates())
    output = io.BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Cruise Management - Bao cao van hanh", styles["Title"]),
        Paragraph(f"Nguon du lieu: {report['data_source']}", styles["Normal"]),
        Spacer(1, 0.5 * cm),
    ]
    summary = [
        ["Chi so", "Gia tri"],
        ["Tong doanh thu", f"{report['revenue']:,.0f}"],
        ["Tong luot dang ky", str(report["participants"])],
        ["Tong suc chua", str(report["capacity"])],
        ["Cong suat trung binh", f"{report['occupancy_rate']}%"],
    ]
    summary_table = Table(summary, colWidths=[8 * cm, 8 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * cm))
    activity_data = [["Hoat dong", "Loai", "Dang ky", "Suc chua", "Cong suat"]]
    activity_data.extend([
        [item["name"], item["type"], item["registered"], item["capacity"], f"{item['occupancy_rate']}%"]
        for item in report["activities"]
    ])
    activity_table = Table(activity_data, repeatRows=1)
    activity_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#198754")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(activity_table)
    document.build(elements)
    response = Response(output.getvalue(), mimetype="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=cruise-report.pdf"
    return response
