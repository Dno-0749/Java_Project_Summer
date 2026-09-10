class TourProvider:
    def __init__(
        self,
        id=None,
        name='',
        contact_person='',
        phone='',
        email='',
        address='',
        status='Đang hợp tác',
        created_at=None,
        updated_at=None
    ):
        self.id = id
        self.name = name
        self.contact_person = contact_person
        self.phone = phone
        self.email = email
        self.address = address
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at