from sqlalchemy import or_

from infrastructure.databases.database_postgres import DatabasePostgres
from infrastructure.models.excursion_registration_model import (
    ExcursionRegistrationModel
)


class ExcursionRegistrationRepository:

    def __init__(self):
        self.database = DatabasePostgres()

    def add(
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
        session = self.database.get_session()

        try:
            item = ExcursionRegistrationModel(
                passenger_id=passenger_id,
                excursion_id=excursion_id,
                booking_id=booking_id,
                guest_code=guest_code,
                passenger_name=passenger_name,
                room=room,
                status=status,
                notes=notes
            )

            session.add(item)
            session.commit()
            session.refresh(item)

            return item

        finally:
            session.close()

    def list(self, excursion_id=None):
        session = self.database.get_session()

        try:
            query = session.query(
                ExcursionRegistrationModel
            )

            if excursion_id is not None:
                query = query.filter(
                    ExcursionRegistrationModel.excursion_id
                    == excursion_id
                )

            return query.order_by(
                ExcursionRegistrationModel.id.desc()
            ).all()

        finally:
            session.close()

    def get_by_id(self, registration_id):
        session = self.database.get_session()

        try:
            return session.query(
                ExcursionRegistrationModel
            ).filter(
                ExcursionRegistrationModel.id
                == registration_id
            ).first()

        finally:
            session.close()

    def find_active_registration(
        self,
        excursion_id,
        passenger_id=None,
        guest_code=None
    ):
        session = self.database.get_session()

        try:
            query = session.query(
                ExcursionRegistrationModel
            ).filter(
                ExcursionRegistrationModel.excursion_id
                == excursion_id
            ).filter(
                ExcursionRegistrationModel.status
                != "CANCELLED"
            )

            conditions = []

            if passenger_id is not None:
                conditions.append(
                    ExcursionRegistrationModel.passenger_id
                    == passenger_id
                )

            if guest_code:
                conditions.append(
                    ExcursionRegistrationModel.guest_code
                    == guest_code
                )

            if not conditions:
                return None

            return query.filter(
                or_(*conditions)
            ).first()

        finally:
            session.close()

    def update_status(
        self,
        registration_id,
        status
    ):
        session = self.database.get_session()

        try:
            item = session.query(
                ExcursionRegistrationModel
            ).filter(
                ExcursionRegistrationModel.id
                == registration_id
            ).first()

            if item is None:
                return None

            item.status = status

            if status == "CANCELLED":
                item.checked_in = False
                item.checked_in_at = None

            session.commit()
            session.refresh(item)

            return item

        finally:
            session.close()

    def check_in(
        self,
        registration_id,
        checked_in_at
    ):
        session = self.database.get_session()

        try:
            item = session.query(
                ExcursionRegistrationModel
            ).filter(
                ExcursionRegistrationModel.id
                == registration_id
            ).first()

            if item is None:
                return None

            item.checked_in = True
            item.checked_in_at = checked_in_at
            item.status = "COMPLETED"

            session.commit()
            session.refresh(item)

            return item

        finally:
            session.close()
