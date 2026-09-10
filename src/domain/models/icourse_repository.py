from abc import ABC, abstractmethod
from typing import List, Optional
from .course import Course
class ICourseRepository(ABC):
    @abstractmethod
    def add(self, course: Course) -> Course:
        pass

    @abstractmethod
    def get_by_id(self, course_id: int) -> Optional[Course]:
        pass

    @abstractmethod
    def list(self) -> List[Course]:
        pass

    @abstractmethod
    def update(self, course: Course) -> Course:
        pass

    @abstractmethod
    def delete(self, course_id: int) -> None:
        pass 