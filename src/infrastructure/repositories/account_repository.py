from typing import List, Optional
from datetime import datetime
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.cruise.onboard_account_model import OnboardAccountModel
from infrastructure.models.cruise.transaction_model import TransactionModel


class AccountRepository:
    """
    LƯU Ý QUAN TRỌNG VỀ SESSION:
    Mỗi method dưới đây tự lấy 1 session RIÊNG (qua _new_session()) và dùng
    nhất quán trong suốt method đó, thay vì dùng chung 1 session cho cả
    vòng đời Repository. Lý do: khi xử lý BATCH nhiều giao dịch liên tiếp
    (sync_offline_transactions), nếu dùng chung 1 session rồi đóng (close)
    sau mỗi thao tác, các object đã đóng sẽ bị "detached" và gây lỗi
    'not bound to a Session' khi thao tác tiếp theo cố truy cập lại chúng.
    """

    def _new_session(self):
        return db_factory.get_database('POSTGREE').new_session()

    # ---------- OnboardAccount ----------
    def get_account_by_passenger(self, passenger_id: int) -> Optional[OnboardAccountModel]:
        session = self._new_session()
        try:
            return session.query(OnboardAccountModel).filter_by(passenger_id=passenger_id).first()
        finally:
            session.close()

    def create_account(self, passenger_id: int) -> OnboardAccountModel:
        """BR-01 (SRS): Một hành khách chỉ có một OnboardAccount cho mỗi chuyến đi."""
        session = self._new_session()
        try:
            existing = session.query(OnboardAccountModel).filter_by(passenger_id=passenger_id).first()
            if existing:
                return existing
            account = OnboardAccountModel(passenger_id=passenger_id, balance=0, status="open")
            session.add(account)
            session.commit()
            session.refresh(account)
            return account
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ---------- Transaction ----------
    def get_by_local_id(self, local_id: str) -> Optional[TransactionModel]:
        """Kiểm tra idempotency - transaction này đã được đồng bộ trước đó chưa."""
        if not local_id:
            return None
        session = self._new_session()
        try:
            return session.query(TransactionModel).filter_by(local_id=local_id).first()
        finally:
            session.close()

    def create_transaction(self, account_id: int, amount, description: str,
                            staff_id: int = None, local_id: str = None,
                            sync_status: str = "synced") -> TransactionModel:
        session = self._new_session()
        try:
            tx = TransactionModel(
                local_id=local_id,
                onboard_account_id=account_id,
                staff_id=staff_id,
                amount=amount,
                description=description,
                sync_status=sync_status,
            )
            session.add(tx)

            # Cập nhật số dư tài khoản ngay trong CÙNG session/transaction này
            account = session.query(OnboardAccountModel).filter_by(id=account_id).first()
            if account:
                account.balance = (account.balance or 0) - amount

            session.commit()
            session.refresh(tx)
            return tx
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_transactions(self, account_id: int) -> List[TransactionModel]:
        session = self._new_session()
        try:
            return (
                session.query(TransactionModel)
                .filter_by(onboard_account_id=account_id)
                .order_by(TransactionModel.created_at.desc())
                .all()
            )
        finally:
            session.close()

    def list_all_transactions(self, limit: int = 100) -> List[TransactionModel]:
        """Lấy toàn bộ giao dịch gần nhất - dùng cho màn Lịch sử giao dịch của POS
        (không lọc theo 1 hành khách cụ thể)."""
        session = self._new_session()
        try:
            return (
                session.query(TransactionModel)
                .order_by(TransactionModel.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()

    def refund_transaction(self, transaction_id: int) -> Optional[TransactionModel]:
        session = self._new_session()
        try:
            tx = session.query(TransactionModel).filter_by(id=transaction_id).first()
            if not tx:
                return None
            account = session.query(OnboardAccountModel).filter_by(id=tx.onboard_account_id).first()
            if account:
                account.balance = (account.balance or 0) + tx.amount
            tx.description = f"[ĐÃ HOÀN TIỀN] {tx.description or ''}"
            session.commit()
            session.refresh(tx)
            return tx
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def mark_synced(self, transaction_id: int) -> Optional[TransactionModel]:
        session = self._new_session()
        try:
            tx = session.query(TransactionModel).filter_by(id=transaction_id).first()
            if not tx:
                return None
            tx.sync_status = "synced"
            tx.synced_at = datetime.utcnow()
            session.commit()
            session.refresh(tx)
            return tx
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
