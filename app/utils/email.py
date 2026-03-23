from email.message import EmailMessage
import smtplib
from app.config import settings

def send_otp_email(to_email: str, otp: str):

    msg = EmailMessage()
    msg["Subject"] = "Verify Your Account - OTP"
    msg["From"] = settings.EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Reply-To"] = settings.EMAIL_ADDRESS

    msg.set_content(f"""
Hello,

Your One Time Password (OTP) is: {otp}

This OTP will expire in 5 minutes.

If you did not request this, please ignore this email.

Regards,
Student Management System
""")

    msg.add_alternative(f"""
    <html>
      <body>
        <h2>Email Verification</h2>
        <p>Your OTP is:</p>
        <h1 style="color:blue;">{otp}</h1>
        <p>This OTP expires in 5 minutes.</p>
      </body>
    </html>
    """, subtype="html")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        server.send_message(msg)