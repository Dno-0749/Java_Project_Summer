from sqlalchemy import Column, Integer, String, DateTime
from infrastructure.databases.base import Base

class ProgramModel(Base):
    __tablename__ = 'programs'
    __table_args__ = {'extend_existing': True}  # Thêm dòng này

    id = Column(Integer, primary_key=True)

    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime) 
    
    
    # create table programs(
    #     id Int primary key,
    #     title nvarchar(255) not null,....
    # )