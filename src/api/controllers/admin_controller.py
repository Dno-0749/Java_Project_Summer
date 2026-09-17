import csv
import io
import json
from datetime import datetime

from flask import Blueprint, jsonify, make_response, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from infrastructure.databases.factory_database import FactoryDatabase
from infrastructure.models.admin_models import (
    AdminDeviceModel,
    AdminPolicyModel,
    AuditLogModel,
    ShipAreaModel,
    ShipModel,
)
from infrastructure.models.cruise.activity_model import ActivityModel
from infrastructure.models.cruise.cruise_model import CruiseModel
from infrastructure.models.cruise.port_model import PortModel
from infrastructure.models.cruise.shore_excursion_model import ShoreExcursionModel
from infrastructure.models.auth.auth_role_model import AuthRoleModel, AuthUserRoleModel
from infrastructure.models.auth.auth_user_model import AuthUserModel


bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")


def _session():
    return FactoryDatabase.get_database("POSTGREE").new_session()


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _serialize(row):
    return {
        key: _iso(value)
        for key, value in row.__dict__.items()
        if not key.startswith("_")
    }


def _audit(session, action, resource, resource_id=None, details=None):
    session.add(AuditLogModel(
        actor_user_id=request.headers.get("X-User-Id"),
        actor_username=request.headers.get("X-Username"),
        action=action,
        resource=resource,
        resource_id=str(resource_id) if resource_id is not None else None,
        details=json.dumps(details, ensure_ascii=False) if details else None,
    ))


def _crud_collection(model, fields, resource):
    session = _session()
    try:
        if request.method == "GET":
            return jsonify([_serialize(row) for row in session.query(model).order_by(model.id.desc()).all()])

        data = request.get_json(silent=True) or {}
        missing = [field for field in fields if data.get(field) in (None, "")]
        if missing:
            return jsonify({"message": "Thiếu trường bắt buộc", "fields": missing}), 400
        row = model(**{field: data[field] for field in fields if field in data})
        session.add(row)
        session.flush()
        _audit(session, "create", resource, row.id, data)
        session.commit()
        return jsonify(_serialize(row)), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Dữ liệu đã tồn tại hoặc vi phạm ràng buộc."}), 409
    finally:
        session.close()


def _crud_item(model, item_id, fields, resource):
    session = _session()
    try:
        row = session.get(model, item_id)
        if not row:
            return jsonify({"message": "Không tìm thấy dữ liệu."}), 404
        if request.method == "DELETE":
            session.delete(row)
            _audit(session, "delete", resource, item_id)
            session.commit()
            return "", 204
        data = request.get_json(silent=True) or {}
        for field in fields:
            if field in data:
                setattr(row, field, data[field])
        _audit(session, "update", resource, item_id, data)
        session.commit()
        return jsonify(_serialize(row))
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Dữ liệu đã tồn tại hoặc vi phạm ràng buộc."}), 409
    finally:
        session.close()


@bp.route("/ships", methods=["GET", "POST"])
def ships():
    return _crud_collection(ShipModel, ["name", "code"], "ship")


@bp.route("/ships/<int:item_id>", methods=["PUT", "DELETE"])
def ship(item_id):
    return _crud_item(ShipModel, item_id, ["name", "code", "status", "capacity", "description"], "ship")


def _serialize_user(session, user):
    role = session.query(AuthRoleModel).join(
        AuthUserRoleModel, AuthUserRoleModel.role_id == AuthRoleModel.id
    ).filter(AuthUserRoleModel.user_id == user.id).first()
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name or user.username,
        "status": user.status or "Active",
        "passenger_id": user.passenger_id,
        "role": role.name if role else "PASSENGER",
    }


@bp.route("/users", methods=["GET", "POST"])
def users():
    session = _session()
    try:
        if request.method == "GET":
            rows = session.query(AuthUserModel).order_by(AuthUserModel.id.desc()).all()
            return jsonify([_serialize_user(session, row) for row in rows])

        data = request.get_json(silent=True) or {}
        username = str(data.get("username", "")).strip().lower()
        full_name = str(data.get("full_name", "")).strip()
        role_name = str(data.get("role", "PASSENGER")).strip().upper()
        if not username or not full_name:
            return jsonify({"message": "username và full_name là bắt buộc"}), 400
        role = session.query(AuthRoleModel).filter_by(name=role_name).first()
        if not role:
            role = AuthRoleModel(name=role_name, description=role_name)
            session.add(role)
            session.flush()
        user = AuthUserModel(
            username=username,
            email=data.get("email") or f"{username}@local.invalid",
            password_hash=generate_password_hash(data.get("password") or "123456"),
            full_name=full_name,
            status=data.get("status", "Active"),
            passenger_id=data.get("passenger_id"),
        )
        session.add(user)
        session.flush()
        session.add(AuthUserRoleModel(user_id=user.id, role_id=role.id))
        _audit(session, "create", "user", user.id, {"username": username, "role": role_name})
        session.commit()
        return jsonify(_serialize_user(session, user)), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"message": "Username hoặc email đã tồn tại."}), 409
    finally:
        session.close()


@bp.route("/users/<int:user_id>", methods=["PUT", "DELETE"])
def user(user_id):
    session = _session()
    try:
        row = session.get(AuthUserModel, user_id)
        if not row:
            return jsonify({"message": "Không tìm thấy người dùng."}), 404
        if request.method == "DELETE":
            session.query(AuthUserRoleModel).filter_by(user_id=user_id).delete()
            session.delete(row)
            _audit(session, "delete", "user", user_id)
            session.commit()
            return "", 204
        data = request.get_json(silent=True) or {}
        for field in ("full_name", "email", "status", "passenger_id"):
            if field in data:
                setattr(row, field, data[field])
        if "role" in data:
            role_name = str(data["role"]).upper()
            role = session.query(AuthRoleModel).filter_by(name=role_name).first()
            if not role:
                role = AuthRoleModel(name=role_name, description=role_name)
                session.add(role)
                session.flush()
            session.query(AuthUserRoleModel).filter_by(user_id=user_id).delete()
            session.add(AuthUserRoleModel(user_id=user_id, role_id=role.id))
        _audit(session, "update", "user", user_id, data)
        session.commit()
        return jsonify(_serialize_user(session, row))
    finally:
        session.close()


@bp.route("/areas", methods=["GET", "POST"])
def areas():
    return _crud_collection(ShipAreaModel, ["name"], "ship_area")


@bp.route("/areas/<int:item_id>", methods=["PUT", "DELETE"])
def area(item_id):
    return _crud_item(ShipAreaModel, item_id, ["name", "deck", "status", "description"], "ship_area")


@bp.route("/policies", methods=["GET"])
def policies():
    session = _session()
    try:
        if session.query(AdminPolicyModel).count() == 0:
            defaults = [
                ("registration_capacity_enforced", "true", "Chặn đăng ký khi hoạt động đã đủ chỗ"),
                ("cancellation_window_hours", "24", "Số giờ tối thiểu trước khi hủy đăng ký"),
                ("refund_allowed", "true", "Cho phép hoàn tiền khi giao dịch đủ điều kiện"),
                ("max_refund_days", "7", "Số ngày tối đa được yêu cầu hoàn tiền"),
            ]
            session.add_all([
                AdminPolicyModel(policy_key=key, policy_value=value, description=description)
                for key, value, description in defaults
            ])
            session.commit()
        return jsonify([_serialize(row) for row in session.query(AdminPolicyModel).order_by(AdminPolicyModel.policy_key).all()])
    finally:
        session.close()


@bp.route("/policies/<string:policy_key>", methods=["PUT"])
def policy(policy_key):
    session = _session()
    try:
        data = request.get_json(silent=True) or {}
        value = data.get("policy_value")
        if value is None:
            return jsonify({"message": "policy_value là bắt buộc"}), 400
        row = session.query(AdminPolicyModel).filter_by(policy_key=policy_key).first()
        if not row:
            row = AdminPolicyModel(policy_key=policy_key, policy_value=str(value), description=data.get("description"))
            session.add(row)
        else:
            row.policy_value = str(value)
            if "description" in data:
                row.description = data["description"]
        _audit(session, "update", "policy", policy_key, data)
        session.commit()
        return jsonify(_serialize(row))
    finally:
        session.close()


@bp.route("/devices", methods=["GET", "POST"])
def devices():
    return _crud_collection(AdminDeviceModel, ["device_code", "device_type"], "device")


@bp.route("/devices/<int:item_id>", methods=["PUT", "DELETE"])
def device(item_id):
    return _crud_item(AdminDeviceModel, item_id, ["device_code", "device_type", "status", "location", "assigned_to"], "device")


@bp.route("/logs", methods=["GET"])
def logs():
    session = _session()
    try:
        limit = min(request.args.get("limit", 200, type=int), 1000)
        rows = session.query(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(limit).all()
        return jsonify([_serialize(row) for row in rows])
    finally:
        session.close()


@bp.route("/logs/export.csv", methods=["GET"])
def export_logs():
    session = _session()
    try:
        rows = session.query(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(5000).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "created_at", "actor_user_id", "actor_username", "action", "resource", "resource_id", "details"])
        for row in rows:
            writer.writerow([row.id, _iso(row.created_at), row.actor_user_id, row.actor_username, row.action, row.resource, row.resource_id, row.details])
        response = make_response(output.getvalue())
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        response.headers["Content-Disposition"] = "attachment; filename=audit-logs.csv"
        return response
    finally:
        session.close()


@bp.route("/catalog", methods=["GET"])
def catalog():
    session = _session()
    try:
        return jsonify({
            "cruises": [_serialize(row) for row in session.query(CruiseModel).order_by(CruiseModel.id.desc()).all()],
            "ports": [_serialize(row) for row in session.query(PortModel).order_by(PortModel.id.desc()).all()],
            "activities": [_serialize(row) for row in session.query(ActivityModel).order_by(ActivityModel.id.desc()).all()],
            "excursions": [_serialize(row) for row in session.query(ShoreExcursionModel).order_by(ShoreExcursionModel.id.desc()).all()],
        })
    finally:
        session.close()
