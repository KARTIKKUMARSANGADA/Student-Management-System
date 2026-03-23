from pydantic import BaseModel
from datetime import date
from uuid import UUID

class UpdatePhoneRequest(BaseModel):
    phone:str
        
class UpdateStudent(BaseModel):
    first_name : str
    last_name : str
    phone : str
    date_of_birth : date
    
class GetStudent(BaseModel):
    id : UUID