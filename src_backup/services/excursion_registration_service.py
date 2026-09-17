from datetime import datetime

from infrastructure.repositories.excursion_registration_repository import (
    ExcursionRegistrationRepository
)


class ExcursionRegistrationService:

    def __init__(self):
        self.repository = ExcursionRegistrationRepository()

    def list_registrations(
        self,
        excursion_id=None
    ):
        return self.repository.list(
            excursion_id=excursion_id
        )

    def create_registration(
        self,
        passenger_id,
        excursion_id,
        booking_id=None,
        guest_code=None,
        passenger_name=None,
        room=None,
        status="REGISTERED",
        notes=None
    ):
        allowed_statuses = {
            "REGISTERED",
            "CONFIRMED",
            "CANCELLED",
            "COMPLETED"
        }

        if status not in allowed_statuses:
            raise ValueError(
                "Tráº¡ng thÃ¡i Ä‘Äƒng kÃ½ khÃ´ng há»£p lá»‡."
            )

        existing = self.repository.find_active_registration(
            excursion_id,
            passenger_id,
            guest_code
        )

        if existing is not None:
            raise ValueError(
                "HÃ nh khÃ¡ch Ä‘Ã£ Ä‘Äƒng kÃ½ tour nÃ y."
            )

        return self.repository.add(
            passenger_id=passenger_id,
            excursion_id=excursion_id,
            booking_id=booking_id,
            guest_code=guest_code,
            passenger_name=passenger_name,
            room=room,
            status=status,
            notes=notes
        )

    def update_status(
        self,
        registration_id,
        status
    ):
        allowed_statuses = {
            "REGISTERED",
            "CONFIRMED",
            "CANCELLED",
            "COMPLETED"
        }

        if status not in allowed_statuses:
            raise ValueError(
                "Tráº¡ng thÃ¡i Ä‘Äƒng kÃ½ khÃ´ng há»£p lá»‡."
            )

        registration = self.repository.get_by_id(
            registration_id
        )

        if registration is None:
            return None

        return self.repository.update_status(
            registration_id,
            status
        )

    def check_in(
        self,
        registration_id
    ):
        registration = self.repository.get_by_id(
            registration_id
        )

        if registration is None:
            return None

        if registration.status == "CANCELLED":
            raise ValueError(
                "KhÃ´ng thá»ƒ check-in Ä‘Äƒng kÃ½ Ä‘Ã£ há»§y."
            )

        return self.repository.check_in(
            registration_id,
            datetime.utcnow()
        )
