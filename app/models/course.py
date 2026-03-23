from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class CourseTable(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String, nullable=False)
    description = Column(String)
    credit_hours = Column(Integer)
    max_students = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    enrollments = relationship(
        "EnrollmentTable",
        back_populates="course",
        cascade="all, delete-orphan"
    )