from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import UsersTable
from app.models.student_profile import StudentProfileTable
from app.models.otp_token import OtpTokenTable
from app.models.refresh_token import RefreshTokenTable
from app.schemas.auth import (
    RegisterRequest,
    VerifyOtpRequest,
    ResendOtpRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_token
from app.utils.email import send_otp_email
from app.utils.otp import create_otp_record

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =========================================================
# REGISTER
# =========================================================
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):

    existing_user = db.query(UsersTable).filter(
        UsersTable.email == payload.email
    ).first()

    if existing_user:
        raise HTTPException(400, "Email already registered")

    new_user = UsersTable(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_verified=False,
        is_active=True
    )

    db.add(new_user)
    db.flush()

    if payload.role == "student":
        db.add(StudentProfileTable(
            user_id=new_user.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone,
            date_of_birth=payload.date_of_birth,
        ))

    otp_code = create_otp_record(db, new_user.id)

    send_otp_email(new_user.email, otp_code)

    return {"message": "User registered. OTP sent to email."}


# =========================================================
# VERIFY OTP
# =========================================================
@router.post("/verify-otp")
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):

    user = db.query(UsersTable).filter(
        UsersTable.email == payload.email
    ).first()

    if not user:
        raise HTTPException(404, "User not found")

    otp_record = db.query(OtpTokenTable).filter(
        OtpTokenTable.user_id == user.id,
        OtpTokenTable.otp_code == payload.otp_code,
        OtpTokenTable.is_used == False
    ).first()

    if not otp_record:
        raise HTTPException(400, "Invalid OTP")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(400, "OTP expired")

    otp_record.is_used = True
    user.is_verified = True
    db.commit()

    return {"message": "Account verified successfully"}


# =========================================================
# RESEND OTP
# =========================================================
@router.post("/resend-otp")
def resend_otp(payload: ResendOtpRequest, db: Session = Depends(get_db)):

    user = db.query(UsersTable).filter(
        UsersTable.email == payload.email
    ).first()

    if not user:
        raise HTTPException(404, "User not found")

    if user.is_verified:
        raise HTTPException(400, "User already verified")

    db.query(OtpTokenTable).filter(
        OtpTokenTable.user_id == user.id,
        OtpTokenTable.is_used == False
    ).delete()

    otp_code = create_otp_record(db, user.id)
    db.commit()

    send_otp_email(user.email, otp_code)

    return {"message": "OTP resent successfully"}


# =========================================================
# LOGIN
# =========================================================
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(UsersTable).filter(
        UsersTable.email == payload.email
    ).first()

    if not user:
        raise HTTPException(404, "User not found")

    if not user.is_verified:
        raise HTTPException(403, "Please verify your email first")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")

    access_token = create_access_token(
        {"sub": str(user.id), "role": user.role}
    )

    refresh_token = create_refresh_token(
        {"sub": str(user.id), "type": "refresh"}
    )

    db.add(RefreshTokenTable(
        user_id=user.id,
        token=refresh_token,
        is_revoked=False
    ))

    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


# =========================================================
# REFRESH TOKEN (ROTATION)
# =========================================================
@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):

    token_payload = verify_token(payload.refresh_token)

    if token_payload is None or token_payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid or expired refresh token")

    user_id = token_payload.get("sub")

    stored_token = db.query(RefreshTokenTable).filter(
        RefreshTokenTable.token == payload.refresh_token,
        RefreshTokenTable.is_revoked == False
    ).first()

    if not stored_token:
        raise HTTPException(401, "Refresh token revoked or not found")

    stored_token.is_revoked = True

    new_access_token = create_access_token({"sub": user_id})
    new_refresh_token = create_refresh_token({"sub": user_id, "type": "refresh"})

    db.add(RefreshTokenTable(
        user_id=user_id,
        token=new_refresh_token,
        is_revoked=False
    ))

    db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


# =========================================================
# GENERATE ACCESS TOKEN ONLY (NO ROTATION)
# =========================================================
@router.post("/refresh-access-token", response_model=TokenResponse)
def refresh_access_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):

    token_payload = verify_token(payload.refresh_token)

    if token_payload is None or token_payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid or expired refresh token")

    user_id = token_payload.get("sub")

    stored_token = db.query(RefreshTokenTable).filter(
        RefreshTokenTable.token == payload.refresh_token,
        RefreshTokenTable.is_revoked == False
    ).first()

    if not stored_token:
        raise HTTPException(401, "Refresh token revoked or not found")

    new_access_token = create_access_token({"sub": user_id})

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=payload.refresh_token,
        token_type="bearer"
    )


# =========================================================
# LOGOUT (PROTECTED)
# =========================================================
@router.post("/logout")
def logout(
    payload: RefreshTokenRequest,
    current_user: UsersTable = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    stored_token = db.query(RefreshTokenTable).filter(
        RefreshTokenTable.token == payload.refresh_token,
        RefreshTokenTable.user_id == current_user.id
    ).first()

    if not stored_token:
        raise HTTPException(404, "Refresh token not found")

    stored_token.is_revoked = True
    db.commit()

    return {"message": "Logout successful"}
