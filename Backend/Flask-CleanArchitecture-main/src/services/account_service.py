from infrastructure.repositories.account_repository import AccountRepository


class AccountService:
    def __init__(self, repository: AccountRepository = None):
        self.repository = repository or AccountRepository()

    def get_or_create_account(self, passenger_id: int):
        account = self.repository.get_account_by_passenger(passenger_id)
        if not account:
            account = self.repository.create_account(passenger_id)
        return account

    def create_transaction(self, passenger_id: int, amount, description: str,
                            staff_id: int = None, local_id: str = None):
        """UC21/UC23: Ghi nhận giao dịch dịch vụ + Ghi nợ tài khoản trên tàu.
        Trường hợp bình thường (có mạng ngay lúc tạo): sync_status = 'synced'.
        """
        if amount is None or amount <= 0:
            raise ValueError("Số tiền giao dịch phải lớn hơn 0")

        account = self.get_or_create_account(passenger_id)

        # Idempotency: nếu local_id đã tồn tại thì trả về transaction cũ, không tạo mới
        if local_id:
            existing = self.repository.get_by_local_id(local_id)
            if existing:
                return existing

        return self.repository.create_transaction(
            account_id=account.id,
            amount=amount,
            description=description,
            staff_id=staff_id,
            local_id=local_id,
            sync_status="synced",
        )

    def sync_offline_transactions(self, passenger_id: int, transactions: list, staff_id: int = None):
        """UC25: Lưu trữ giao dịch ngoại tuyến + đồng bộ.
        Nhận 1 BATCH giao dịch được lưu offline tại thiết bị POS, mỗi giao dịch có
        local_id (UUID sinh tại thiết bị theo BR-04). Với mỗi giao dịch:
          - Nếu local_id đã tồn tại trên server -> bỏ qua (đã đồng bộ trước đó, tránh trùng)
          - Nếu chưa tồn tại -> tạo mới, đánh dấu sync_status='synced'
        Trả về danh sách kết quả kèm trạng thái để client biết cái nào mới/đã có.
        """
        account = self.get_or_create_account(passenger_id)
        results = []

        for item in transactions:
            local_id = item.get("local_id")
            if not local_id:
                results.append({"local_id": None, "status": "error",
                                 "message": "Thiếu local_id, không thể đảm bảo chống trùng (BR-04)"})
                continue

            existing = self.repository.get_by_local_id(local_id)
            if existing:
                results.append({"local_id": local_id, "status": "already_synced",
                                 "transaction_id": existing.id})
                continue

            try:
                tx = self.repository.create_transaction(
                    account_id=account.id,
                    amount=item["amount"],
                    description=item.get("description"),
                    staff_id=staff_id,
                    local_id=local_id,
                    sync_status="synced",
                )
                results.append({"local_id": local_id, "status": "synced", "transaction_id": tx.id})
            except Exception as e:
                # MSG07 trong SRS: "Đồng bộ thất bại. Vui lòng liên hệ bộ phận Tài chính để xử lý."
                results.append({"local_id": local_id, "status": "sync_failed", "message": str(e)})

        return results

    def refund(self, transaction_id: int):
        """UC24: Hủy/hoàn tiền giao dịch."""
        tx = self.repository.refund_transaction(transaction_id)
        if not tx:
            raise ValueError("Không tìm thấy giao dịch")
        return tx

    def list_transactions(self, passenger_id: int):
        account = self.repository.get_account_by_passenger(passenger_id)
        if not account:
            return []
        return self.repository.list_transactions(account.id)

    def list_all_transactions(self, limit: int = 100):
        return self.repository.list_all_transactions(limit)
