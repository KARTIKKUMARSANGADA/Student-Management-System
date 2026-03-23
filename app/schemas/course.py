from pydantic import BaseModel


class CreateCourseRequest(BaseModel):
    title: str
    description: str
    credit_hours: int
    max_students: int

class UpdateCourseRequest(BaseModel):
    title: str
    description: str
    credit_hours: int
    max_students: int
