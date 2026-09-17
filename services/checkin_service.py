from infrastructure.repositories.checkin_repository import CheckinRepository


class CheckinService:
    def __init__(self, repository: CheckinRepository = None):
        self.repository = repository or CheckinRepository()

    def checkin(self, registration_id: int, method: str):
        """UC09/UC17: Check-in bằng QR/thẻ/RFID-NFC.
        Business Rule (SRS 3.4.4.3): Một hành khách chỉ có thể check-in một lần
        cho mỗi lượt hoạt động đã đăng ký.
        """
        registration = self.repository.get_registration(registration_id)
        if not registration:
            # Đúng MSG03 trong SRS: "Mã xác thực không hợp lệ hoặc chưa đăng ký hoạt động này."
            raise ValueError("Mã xác thực không hợp lệ hoặc chưa đăng ký hoạt động này.")

        existing = self.repository.get_existing_checkin(registration_id)
        if existing:
            raise ValueError("Hành khách đã check-in cho hoạt động này rồi.")

        if method not in ["qr", "card", "rfid"]:
            raise ValueError("Phương thức check-in không hợp lệ (chỉ nhận qr/card/rfid).")

        checkin = self.repository.add_checkin(registration_id, method)

        try:
            from services.notification_service import NotificationService
            NotificationService().create(
                title="Check-in thành công",
                content="Bạn đã check-in thành công cho hoạt động vừa tham gia.",
                passenger_id=registration.passenger_id,
                category="registration",
                priority="normal",
            )
        except Exception:
            pass

        return checkin
