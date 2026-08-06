from datetime import date


class Course:
    def __init__(self, id: int, course_name: str, description: str, status: str,start_date :date ,end_date:date,created_at, updated_at):
        self.id = id
        self.course_name = course_name
        self.description = description
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at
        self.updated_at = updated_at 