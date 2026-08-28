import smtplib
from email.message import EmailMessage

from app.core.config import get_settings


def send_verification_otp(recipient: str, code: str) -> None:
    settings = get_settings()
    if not all((settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.smtp_from_email)):
        raise RuntimeError("Email service is not configured")
    message = EmailMessage()
    message["Subject"] = "ResearchMind AI - Email Verification"
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = recipient
    message.set_content(
        f"Hello,\n\nWelcome to ResearchMind AI.\n\n"
        f"Your email verification code is:\n\n{code}\n\n"
        "This code will expire in 5 minutes.\n\n"
        "If you did not create this account, please ignore this email.\n\n"
        "Regards,\nResearchMind AI"
    )
    # Google displays app passwords in groups of four characters; whitespace
    # copied into .env is formatting, not part of the credential.
    smtp_password = settings.smtp_password.replace(" ", "")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, smtp_password)
        server.send_message(message)


def send_password_reset_otp(recipient: str, code: str) -> None:
    settings = get_settings()
    if not all((settings.smtp_host, settings.smtp_username, settings.smtp_password, settings.smtp_from_email)):
        raise RuntimeError("Email service is not configured")
    message = EmailMessage()
    message["Subject"] = "ResearchMind AI - Password reset code"
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = recipient
    message.set_content(
        f"Your ResearchMind AI password reset code is: {code}\n\n"
        "This code expires in 10 minutes. If you did not request this, ignore this email."
    )
    smtp_password = settings.smtp_password.replace(" ", "")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, smtp_password)
        server.send_message(message)
