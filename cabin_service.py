from domain.models.cabin import Cabin

class CabinService:
    def __init__(self, repository):
        self.repository = repository

    def list_cabins(self):
        return self.repository.list()

    def create_cabin(self, cabin_number, deck_level=None, cabin_type=None, capacity=1, price=0):
        item = Cabin(
            id=None,
            cabin_number=cabin_number,
            deck_level=deck_level,
            cabin_type=cabin_type,
            capacity=int(capacity or 1),
            price=float(price or 0),
        )
        return self.repository.add(item)
