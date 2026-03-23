from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base


class UsersTable(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    otp_tokens = relationship("OtpTokenTable",back_populates="users",cascade="all, delete-orphan")
    student_profile = relationship("StudentProfileTable",back_populates="users",uselist=False)
    enrollments = relationship("EnrollmentTable",back_populates="student",cascade="all, delete-orphan")
    