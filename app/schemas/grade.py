from pydantic import BaseModel
from uuid import UUID

class GradeCreate(BaseModel):
    enrollment_id: UUID
    marks_obtained: int
    total_marks: int
    remarks: str | None = None
    
