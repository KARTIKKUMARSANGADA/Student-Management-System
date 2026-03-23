from sqlalchemy import Column, String, DateTime, ForeignKey, false
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class StudentProfileTable(Base):
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    first_name = Column(String,nullable=False)
    last_name = Column(String,nullable=False)
    phone = Column(String(10),nullable=False)
    date_of_birth = Column(DateTime,nullable=True)

    users = relationship("UsersTable",back_populates="student_profile")