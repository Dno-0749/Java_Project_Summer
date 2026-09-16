from infrastructure.repositories.report_repository import ReportRepository


class ReportService:
    def __init__(self, repository: ReportRepository = None):
        self.repository = repository or ReportRepository()

    # ---------- Đối soát (UC27) ----------
    def reconcile(self, account_id: int):
        account = self.repository.get_account(account_id)
        if not account:
            raise ValueError("Không tìm thấy tài khoản")
        count = self.repository.reconcile_transactions(account_id)
        return {"account_id": account_id, "reconciled_count": count}

    def mark_disputed(self, transaction_id: int):
        tx = self.repository.mark_disputed(transaction_id)
        if not tx:
            raise ValueError("Không tìm thấy giao dịch")
        return tx

    # ---------- Thanh toán cuối chuyến (UC28) ----------
    def settle_final_payment(self, account_id: int):
        """Business Rule BR-05: chỉ xác nhận thanh toán cuối khi không còn
        giao dịch pending_sync/disputed chưa xử lý."""
        pending = self.repository.list_pending_or_disputed(account_id)
        if pending:
            raise ValueError(
                f"Không thể xác nhận thanh toán. Còn {len(pending)} giao dịch "
                f"tranh chấp/chưa đồng bộ chưa được xử lý."
            )
        account = self.repository.settle_account(account_id)
        if not account:
            raise ValueError("Không tìm thấy tài khoản")
        return account

    # ---------- Xuất hóa đơn (UC29) ----------
    def issue_invoice(self, account_id: int):
        """Business Rule BR-05 (SRS 3.7.3):
        Hóa đơn cuối chuyến chỉ được xuất khi tài khoản không còn giao dịch
        tranh chấp chưa xử lý (MSG08 khi bị chặn)."""
        pending = self.repository.list_pending_or_disputed(account_id)
        if pending:
            # Đúng MSG08 trong SRS
            raise ValueError("Không thể xuất hóa đơn. Tài khoản còn giao dịch tranh chấp chưa xử lý.")

        total = self.repository.sum_reconciled_amount(account_id)
        invoice = self.repository.create_invoice(account_id, total)
        # MSG09: "Hóa đơn cuối chuyến đã được xuất thành công."
        return invoice

    # ---------- Dashboard vận hành (UC30-32) ----------
    def activity_participation(self, cruise_id: int):
        return self.repository.activity_participation(cruise_id)

    def late_return_risk(self, cruise_day_id: int):
        return self.repository.late_return_risk(cruise_day_id)

    def operations_summary(self, cruise_id: int):
        """UC32: Báo cáo vận hành tổng hợp sau chuyến đi."""
        participation = self.repository.activity_participation(cruise_id)
        total_registered = sum(p["registered"] for p in participation)
        total_checked_in = sum(p["checked_in"] for p in participation)
        return {
            "cruise_id": cruise_id,
            "activities": participation,
            "total_registered": total_registered,
            "total_checked_in": total_checked_in,
            "checkin_rate": round(total_checked_in / total_registered, 2) if total_registered else 0,
        }

    # Ngưỡng coi là "số tiền lớn bất thường" cho 1 giao dịch đơn lẻ - vượt
    # ngưỡng này không có nghĩa là sai, chỉ là CẦN CHÚ Ý xem lại khi đối soát.
    LARGE_AMOUNT_THRESHOLD = 3_000_000
    # Khoảng thời gian (giây) để coi 2 giao dịch giống nhau là "nghi trùng"
    DUPLICATE_WINDOW_SECONDS = 300  # 5 phút

    def detect_anomalies(self):
        """UC27 (Đối soát): Tự động phát hiện giao dịch bất thường, thay vì
        chỉ dựa vào nhân viên tự đánh dấu tranh chấp thủ công. 2 quy tắc:
          1. Số tiền 1 giao dịch vượt ngưỡng lớn bất thường
          2. Nghi trùng lặp (double-charge): cùng tài khoản, cùng số tiền,
             tạo cách nhau rất gần (trong vài phút) - dấu hiệu bấm nhầm 2 lần.
        """
        transactions = self.repository.list_all_transactions_for_anomaly_scan()

        anomalies = []
        by_account = {}
        for tx in transactions:
            by_account.setdefault(tx.onboard_account_id, []).append(tx)

        for account_id, txs in by_account.items():
            for i, tx in enumerate(txs):
                reasons = []
                if float(tx.amount) >= self.LARGE_AMOUNT_THRESHOLD:
                    reasons.append(f"Số tiền lớn bất thường (≥ {self.LARGE_AMOUNT_THRESHOLD:,.0f}đ)")

                if i > 0:
                    prev = txs[i - 1]
                    if (
                        float(prev.amount) == float(tx.amount)
                        and prev.created_at and tx.created_at
                        and abs((tx.created_at - prev.created_at).total_seconds()) <= self.DUPLICATE_WINDOW_SECONDS
                    ):
                        reasons.append(
                            f"Nghi trùng lặp - giống hệt giao dịch #{prev.id} "
                            f"tạo cách đây {int((tx.created_at - prev.created_at).total_seconds())}s"
                        )

                if reasons:
                    anomalies.append({
                        "transaction_id": tx.id,
                        "account_id": account_id,
                        "amount": float(tx.amount),
                        "description": tx.description,
                        "reasons": reasons,
                    })

        return anomalies
