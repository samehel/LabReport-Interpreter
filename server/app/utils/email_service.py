"""
Email service using aiosmtplib for asynchronous email sending.
Supports SMTP with TLS (Gmail, Outlook, Mailtrap, etc.).
"""

import asyncio
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from app.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: Optional[str] = None,
) -> bool:
    """
    Send an email asynchronously via SMTP.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        html_body: HTML content of the email.
        plain_body: Optional plain text fallback.

    Returns:
        True if sent successfully, False otherwise.
    """
    if not settings.SMTP_ENABLED:
        logger.info(f"[EMAIL DISABLED] Would send '{subject}' to {to_email}")
        return True

    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>"
    message["To"] = to_email
    message["Subject"] = subject

    # Plain text fallback
    if plain_body:
        message.attach(MIMEText(plain_body, "plain"))

    # HTML body
    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_USE_TLS,
            start_tls=settings.SMTP_START_TLS,
        )
        logger.info(f"Email sent: '{subject}' → {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_email_background(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: Optional[str] = None,
):
    """
    Fire-and-forget email sending. Creates a background task so the API
    response isn't delayed by email delivery.
    """
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(send_email(to_email, subject, html_body, plain_body))
    except RuntimeError:
        # If no event loop, just log
        logger.warning(f"No event loop for background email to {to_email}")
