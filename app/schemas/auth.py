from datetime import date

from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    student = "student"

class RegisterRequest(BaseModel):
    first_name : str
    last_name : str
    email: EmailStr
    phone : str
    date_of_birth : date
    password: str
    role: UserRole

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp_code: str
    
class ResendOtpRequest(BaseModel):
    email: EmailStr
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type: str= "bearer"   
    
class RefreshTokenRequest(BaseModel):
        refresh_token:str
        
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    
class VerifyResetOtpRequest(BaseModel):
    email: EmailStr
    otp_code: str
    
class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str
    
class VerifyResetOTP(BaseModel):
    email : EmailStr
    otp : str
    
class ResetPassword(BaseModel):
    token : str
    new_password : str
