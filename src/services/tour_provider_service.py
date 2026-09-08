from domain.models.tour_provider import TourProvider

class TourProviderService:
    def __init__(self, repository):
        self.repository = repository

    def list_providers(self):
        return self.repository.list()

    def create_provider(self, name, contact_phone, contact_email, address):
        item = TourProvider(
            id=None,
            name=name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            address=address,
            status='ACTIVE',
        )
        return self.repository.add(item)