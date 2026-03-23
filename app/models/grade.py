from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base


class GradeTable(Base):
    __tablename__ = "grades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    enrollment_id = Column(UUID(as_uuid=True),ForeignKey("enrollments.id"),unique=True)

    marks_obtained = Column(Integer)
    total_marks = Column(Integer)
    grade_letter = Column(String)
    remarks = Column(String)
    graded_at = Column(DateTime, default=datetime.utcnow)

    enrollment = relationship("EnrollmentTable",back_populates="grade")