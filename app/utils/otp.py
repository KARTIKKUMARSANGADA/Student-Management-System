import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp_token import OtpTokenTable
from app.config import settings
from fastapi import HTTPException, status


def generate_otp():
    return str(random.randint(100000, 999999))

def create_otp_record(db: Session, user_id):
       
    otp_code = generate_otp()
    
    expires_at = datetime.now() + timedelta(
        minutes=settings.OTP_EXPIRE_MINUTES
    )

    otp = OtpTokenTable(
        user_id=user_id,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False
    )

    db.add(otp)
    db.commit()
    db.refresh(otp)

    return otp_code



def verify_otp(db: Session, user_id, otp_code: str):
    
    otp = (
        db.query(OtpTokenTable)
        .filter(
            OtpTokenTable.user_id == user_id,
            OtpTokenTable.otp_code == otp_code,
            OtpTokenTable.is_used == False
        )
        .order_by(OtpTokenTable.created_at.desc())
        .first()
    )

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )

    if otp.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired"
        )

    # Mark OTP as used
    otp.is_used = True
    db.commit()

    return True
