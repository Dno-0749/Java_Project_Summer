from domain.models.shore_excursion import ShoreExcursion


class ShoreExcursionService:

    def __init__(self, repository):
        self.repository = repository

    def list_excursions(self):
        return self.repository.list()

    def create_excursion(
        self,
        provider_id,
        name,
        date=None,
        time=None,
        location=None,
        port_name=None,
        description=None,
        duration_hours=None,
        capacity=0,
        fee=0,
        price=None
    ):
        item = ShoreExcursion(
            id=None,
            name=name,
            date=date,
            time=time or "",
            location=location or port_name or "",
            provider_id=provider_id,
            capacity=int(capacity or 0),
            registered=0,
            price=float(
                fee if price is None else price
            ),
            status="OPEN",
            description=description or ""
        )

        return self.repository.add(item)

    def update_excursion(
        self,
        excursion_id,
        data
    ):
        allowed = {
            "provider_id",
            "name",
            "date",
            "time",
            "location",
            "description",
            "duration_hours",
            "capacity",
            "registered",
            "fee",
            "price"
        }

        update_data = {}

        for key, value in data.items():
            if key in allowed:
                update_data[key] = value

        if "price" in update_data:
            update_data["fee"] = float(
                update_data.pop("price") or 0
            )

        if "capacity" in update_data:
            update_data["capacity"] = int(
                update_data["capacity"] or 0
            )

        if "registered" in update_data:
            update_data["registered"] = int(
                update_data["registered"] or 0
            )

        if "duration_hours" in update_data:
            update_data["duration_hours"] = float(
                update_data["duration_hours"] or 0
            )

        row = self.repository.update(
            excursion_id,
            update_data
        )

        if not row:
            return None

        return row

    def update_status(
        self,
        excursion_id,
        status
    ):
        allowed = {
            "OPEN",
            "CANCELLED",
            "DELAYED",
            "COMPLETED"
        }

        if status not in allowed:
            return {
                "ok": False,
                "message": "Trạng thái không hợp lệ"
            }

        row = self.repository.update_status(
            excursion_id,
            status
        )

        if not row:
            return {
                "ok": False,
                "message": "Không tìm thấy tour"
            }

        return {
            "ok": True,
            "id": row.id,
            "status": row.status
        }
