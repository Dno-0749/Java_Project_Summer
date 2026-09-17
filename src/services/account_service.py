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
        Áp dụng hạn mức chi tiêu (credit_limit, mặc định 20 triệu) - từ chối
        giao dịch nếu số dư dự kiến sau khi trừ sẽ vượt quá hạn mức.
        """
        if amount is None or amount <= 0:
            raise ValueError("Số tiền giao dịch phải lớn hơn 0")

        account = self.get_or_create_account(passenger_id)

        # Idempotency: nếu local_id đã tồn tại thì trả về transaction cũ, không tạo mới
        if local_id:
            existing = self.repository.get_by_local_id(local_id)
            if existing:
                return existing

        current_balance = float(account.balance or 0)
        credit_limit = float(account.credit_limit or 20_000_000)
        projected_balance = current_balance - float(amount)
        if projected_balance < -credit_limit:
            raise ValueError(
                f"Thanh toán thất bại: Giao dịch vượt hạn mức chi tiêu cho phép "
                f"({credit_limit:,.0f}đ). Số dư hiện tại: {current_balance:,.0f}đ."
            )

        tx = self.repository.create_transaction(
            account_id=account.id,
            amount=amount,
            description=description,
            staff_id=staff_id,
            local_id=local_id,
            sync_status="synced",
        )

        try:
            from services.notification_service import NotificationService
            NotificationService().create(
                title="Giao dịch mới",
                content=f"Tài khoản của bạn vừa bị ghi nợ {float(amount):,.0f}đ cho: {description or 'dịch vụ'}.",
                passenger_id=passenger_id,
                category="transaction",
                priority="normal",
            )
        except Exception:
            pass

        return tx

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
        running_balance = float(account.balance or 0)
        credit_limit = float(account.credit_limit or 20_000_000)

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

            amount = float(item["amount"])
            projected_balance = running_balance - amount
            if projected_balance < -credit_limit:
                results.append({
                    "local_id": local_id, "status": "sync_failed",
                    "message": f"Thanh toán thất bại: vượt hạn mức chi tiêu cho phép ({credit_limit:,.0f}đ)",
                })
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
                running_balance = projected_balance
                results.append({"local_id": local_id, "status": "synced", "transaction_id": tx.id})
                try:
                    from services.notification_service import NotificationService
                    NotificationService().create(
                        title="Giao dịch mới",
                        content=f"Tài khoản của bạn vừa bị ghi nợ {amount:,.0f}đ cho: {item.get('description') or 'dịch vụ'}.",
                        passenger_id=passenger_id,
                        category="transaction",
                        priority="normal",
                    )
                except Exception:
                    pass
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
