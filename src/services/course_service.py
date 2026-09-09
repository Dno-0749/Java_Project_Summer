
from typing import List, Optional
from domain.models.course import Course
from domain.models.icourse_repository import ICourseRepository
class CourseService:
    def __init__(self, repository: ICourseRepository):
        self.repository = repository
    def create_course(self, course_name: str, description: str, status: str, start_date, end_date, created_at, updated_at) -> Course:
        course = Course(id=None, course_name=course_name, description=description, status=status, start_date=start_date, end_date=end_date, created_at=created_at, updated_at=updated_at)
        return self.repository.add(course)
    def get_course(self, course_id: int) -> Optional[Course]:
        return self.repository.get_by_id(course_id)

    def list_courses(self) -> List[Course]:
        return self.repository.list()

    def update_course(self, course_id: int, course_name: str, description: str, status: str, start_date, end_date, created_at, updated_at) -> Course:
        course = Course(id=course_id, course_name=course_name, description=description, status=status, start_date=start_date, end_date=end_date, created_at=created_at, updated_at=updated_at)
        return self.repository.update(course)
    def delete_course(self, course_id: int) -> None:
        self.repository.delete(course_id)

    