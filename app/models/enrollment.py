from sqlalchemy import Column, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database import Base


class EnrollmentTable(Base):
    __tablename__ = "enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    course_id = Column(UUID(as_uuid=True),ForeignKey("courses.id", ondelete="CASCADE"),nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    # Prevent duplicate enrollment (same student same course)
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="unique_student_course"),
    )
    
    # Relationships
    student = relationship("UsersTable",back_populates="enrollments")

    course = relationship("CourseTable",back_populates="enrollments")

    grade = relationship("GradeTable",back_populates="enrollment",uselist=False,cascade="all, delete-orphan")