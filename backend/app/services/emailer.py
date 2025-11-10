import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_email(subject: str, to: str, html: str, attachments=None):
    if not settings.SMTP_HOST:
        # Для MVP тихо выходим, чтобы не падать
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM or "noreply@example.com"
    msg["To"] = to
    msg.add_alternative(html, subtype="html")
    for name, data in (attachments or []):
        msg.add_attachment(data, maintype="application", subtype="pdf", filename=name)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
        s.starttls()
        if settings.SMTP_USER:
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.send_message(msg)
