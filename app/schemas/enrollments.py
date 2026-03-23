from pydantic import BaseModel
from uuid import UUID

class CreateEnrollmentRequest(BaseModel):
    student_id: UUID
    course_id: UUID