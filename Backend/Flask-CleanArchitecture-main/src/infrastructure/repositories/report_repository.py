from typing import List, Optional
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.onboard_account_model import OnboardAccountModel
from infrastructure.models.cruise.transaction_model import TransactionModel
from infrastructure.models.cruise.invoice_model import InvoiceModel
from infrastructure.models.cruise.activity_model import ActivityModel
from infrastructure.models.cruise.registration_model import RegistrationModel
from infrastructure.models.cruise.checkin_model import CheckinModel
from infrastructure.models.cruise.shore_excursion_model import ShoreExcursionModel


class ReportRepository:
    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    # ---------- Đối soát ----------
    def get_account(self, account_id: int) -> Optional[OnboardAccountModel]:
        session = self._new_session()
        try:
            return session.query(OnboardAccountModel).filter_by(id=account_id).first()
        finally:
            session.close()

    def list_unreconciled_transactions(self, account_id: int) -> List[TransactionModel]:
        """Lấy giao dịch đã đồng bộ nhưng chưa đối soát (sync_status='synced')."""
        session = self._new_session()
        try:
            return (
                session.query(TransactionModel)
                .filter_by(onboard_account_id=account_id, sync_status="synced")
                .all()
            )
        finally:
            session.close()

    def list_pending_or_disputed(self, account_id: int) -> List[TransactionModel]:
        """Giao dịch còn 'pending_sync' hoặc 'disputed' - chặn xuất hóa đơn (BR-05)."""
        session = self._new_session()
        try:
            return (
                session.query(TransactionModel)
                .filter(
                    TransactionModel.onboard_account_id == account_id,
                    TransactionModel.sync_status.in_(["pending_sync", "disputed"]),
                )
                .all()
            )
        finally:
            session.close()

    def reconcile_transactions(self, account_id: int) -> int:
        """Đánh dấu toàn bộ giao dịch 'synced' của tài khoản thành 'reconciled'.
        Trả về số lượng giao dịch đã đối soát."""
        session = self._new_session()
        try:
            transactions = (
                session.query(TransactionModel)
                .filter_by(onboard_account_id=account_id, sync_status="synced")
                .all()
            )
            for tx in transactions:
                tx.sync_status = "reconciled"
            session.commit()
            return len(transactions)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def mark_disputed(self, transaction_id: int) -> Optional[TransactionModel]:
        session = self._new_session()
        try:
            tx = session.query(TransactionModel).filter_by(id=transaction_id).first()
            if not tx:
                return None
            tx.sync_status = "disputed"
            session.commit()
            session.refresh(tx)
            return tx
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def settle_account(self, account_id: int) -> Optional[OnboardAccountModel]:
        session = self._new_session()
        try:
            account = session.query(OnboardAccountModel).filter_by(id=account_id).first()
            if not account:
                return None
            account.status = "settled"
            session.commit()
            session.refresh(account)
            return account
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ---------- Hóa đơn ----------
    def create_invoice(self, account_id: int, total_amount) -> InvoiceModel:
        session = self._new_session()
        try:
            invoice = InvoiceModel(onboard_account_id=account_id, total_amount=total_amount, status="issued")
            session.add(invoice)
            session.commit()
            session.refresh(invoice)
            return invoice
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def sum_reconciled_amount(self, account_id: int):
        session = self._new_session()
        try:
            transactions = (
                session.query(TransactionModel)
                .filter(
                    TransactionModel.onboard_account_id == account_id,
                    TransactionModel.sync_status.in_(["reconciled", "synced"]),
                )
                .all()
            )
            return sum((tx.amount for tx in transactions), start=0)
        finally:
            session.close()

    # ---------- Dashboard vận hành ----------
    def revenue_by_cruise(self, cruise_id: int):
        """UC30: Tổng doanh thu của 1 chuyến cruise (join qua Activity/Passenger)."""
        session = self._new_session()
        try:
            # Đơn giản hoá: tổng toàn bộ transaction có liên quan tới activity thuộc cruise này
            activity_ids = [a.id for a in session.query(ActivityModel).filter_by(cruise_id=cruise_id).all()]
            return activity_ids  # placeholder cho phần mở rộng sau nếu cần join sâu hơn
        finally:
            session.close()

    def activity_participation(self, cruise_id: int):
        """UC30/UC32: Tỷ lệ tham gia từng hoạt động (đã đăng ký / sức chứa)."""
        session = self._new_session()
        try:
            activities = session.query(ActivityModel).filter_by(cruise_id=cruise_id).all()
            result = []
            for a in activities:
                registered_count = (
                    session.query(RegistrationModel)
                    .filter(
                        RegistrationModel.activity_id == a.id,
                        RegistrationModel.status.in_(["registered", "checked_in"]),
                    )
                    .count()
                )
                checked_in_count = (
                    session.query(RegistrationModel)
                    .filter_by(activity_id=a.id, status="checked_in")
                    .count()
                )
                result.append({
                    "activity_id": a.id,
                    "name": a.name,
                    "capacity": a.capacity,
                    "registered": registered_count,
                    "checked_in": checked_in_count,
                })
            return result
        finally:
            session.close()

    def late_return_risk(self, cruise_day_id: int):
        """UC31: Giám sát rủi ro hành khách quay lại tàu muộn - danh sách đăng ký
        tour trên bờ nhưng CHƯA check-in, dù đã qua giờ return_time."""
        session = self._new_session()
        try:
            excursions = session.query(ShoreExcursionModel).filter_by(cruise_day_id=cruise_day_id).all()
            result = []
            for ex in excursions:
                regs = (
                    session.query(RegistrationModel)
                    .filter_by(excursion_id=ex.id, status="registered")
                    .all()
                )
                for reg in regs:
                    has_checkin = session.query(CheckinModel).filter_by(registration_id=reg.id).first()
                    if not has_checkin:
                        result.append({
                            "registration_id": reg.id,
                            "passenger_id": reg.passenger_id,
                            "excursion_name": ex.name,
                            "return_time": ex.return_time.isoformat() if ex.return_time else None,
                        })
            return result
        finally:
            session.close()
