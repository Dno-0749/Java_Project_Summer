from datetime import datetime, timezone
from threading import Lock


class OperationsService:
    """Operations use cases backed by an in-memory store until a repository is wired."""

    def __init__(self):
        self._lock = Lock()
        self.activities = {}
        self.participants = []
        self.checkins = []
        self.transactions = []
        self.reports = {}
        self._next_activity_id = 1
        self._next_participant_id = 1
        self._next_checkin_id = 1
        self._next_transaction_id = 1

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    def create_activity(self, data):
        capacity = int(data["capacity"])
        if capacity < 1:
            raise ValueError("capacity must be greater than zero")
        with self._lock:
            activity = {
                "id": self._next_activity_id,
                "name": data["name"],
                "service_type": data.get("service_type", "activity"),
                "scheduled_at": data.get("scheduled_at"),
                "capacity": capacity,
                "status": data.get("status", "SCHEDULED"),
                "created_at": self._now(),
            }
            self.activities[activity["id"]] = activity
            self._next_activity_id += 1
            return activity

    def list_activities(self):
        result = []
        for activity in self.activities.values():
            registered = sum(
                item["activity_id"] == activity["id"]
                for item in self.participants
            )
            result.append({
                **activity,
                "registered": registered,
                "available_capacity": max(activity["capacity"] - registered, 0),
            })
        return result

    def add_participant(self, activity_id, data):
        activity = self.activities.get(activity_id)
        if not activity:
            raise KeyError("activity not found")
        registered = sum(
            item["activity_id"] == activity_id for item in self.participants
        )
        if registered >= activity["capacity"]:
            raise ValueError("activity capacity has been reached")
        participant = {
            "id": self._next_participant_id,
            "activity_id": activity_id,
            "passenger_id": data["passenger_id"],
            "registered_at": self._now(),
        }
        self.participants.append(participant)
        self._next_participant_id += 1
        return participant

    def record_checkin(self, data):
        checkin = {
            "id": self._next_checkin_id,
            "passenger_id": data["passenger_id"],
            "activity_id": data.get("activity_id"),
            "trip_id": data.get("trip_id"),
            "status": data.get("status", "CHECKED_IN"),
            "expected_return_at": data.get("expected_return_at"),
            "returned_at": data.get("returned_at"),
            "checked_at": self._now(),
        }
        self.checkins.append(checkin)
        self._next_checkin_id += 1
        return checkin

    def list_checkins(self, status=None):
        return [
            item for item in self.checkins
            if not status or item["status"] == status
        ]

    def late_return_risks(self):
        return [
            item for item in self.checkins
            if item["status"] in {"LATE", "MISSING", "AT_RISK"}
        ]

    def record_transaction(self, data):
        transaction = {
            "id": self._next_transaction_id,
            "trip_id": data.get("trip_id"),
            "service_type": data.get("service_type", "other"),
            "amount": float(data["amount"]),
            "created_at": self._now(),
        }
        self.transactions.append(transaction)
        self._next_transaction_id += 1
        return transaction

    def dashboard(self):
        return {
            "activities": len(self.activities),
            "services": len({item["service_type"] for item in self.activities.values()}),
            "passengers_registered": len(self.participants),
            "capacity": sum(item["capacity"] for item in self.activities.values()),
            "capacity_used": len(self.participants),
            "revenue": sum(item["amount"] for item in self.transactions),
            "checkins": len(self.checkins),
            "late_return_risks": len(self.late_return_risks()),
        }

    def save_report(self, trip_id, data):
        report = {
            "trip_id": trip_id,
            "summary": data.get("summary", ""),
            "incidents": data.get("incidents", []),
            "recommendations": data.get("recommendations", []),
            "created_at": self._now(),
        }
        self.reports[trip_id] = report
        return report

    def get_report(self, trip_id):
        return self.reports.get(trip_id)