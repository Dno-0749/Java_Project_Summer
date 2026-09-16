from domain.models.icourse_repository import ICourseRepository
from domain.models.course import Course
from infrastructure.databases import Base
from domain.models.todo import Todo
from typing import List, Optional
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config
from sqlalchemy import Column, Integer, String, DateTime
from infrastructure.databases import Base

load_dotenv()

class CourseRepository(ICourseRepository):
    def __init__(self):
        self._courses = []
        self._id_counter = 1

    def add(self, course: Course) -> Course:
        course.id = self._id_counter
        self._id_counter += 1
        self._todos.append(course)
        return course

    def get_by_id(self, course_id: int) -> Optional[Course]:
        for course in self._courses:
            if course.id == course_id:
                return course
        return None

    def list(self) -> List[Course]:
        return self._courses

    def update(self, course: Course) -> Course:
        for idx, t in enumerate(self._courses):
            if t.id == course.id:
                self._courses[idx] = course
                return course
        raise ValueError('course not found')

    def delete(self, course_id: int) -> None:
        self._courses = [t for t in self._courses if t.id != course_id] 

