from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.cruise import Cruise


class ICruiseRepository(ABC):
    @abstractmethod
    def list(self) -> List[Cruise]:
        pass

    @abstractmethod
    def get_by_id(self, cruise_id: int) -> Optional[Cruise]:
        pass

    @abstractmethod
    def add(self, cruise: Cruise) -> Cruise:
        pass

    @abstractmethod
    def update(self, cruise_id: int, data: dict) -> Optional[Cruise]:
        pass

    @abstractmethod
    def delete(self, cruise_id: int) -> bool:
        pass
