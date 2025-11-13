"""
Professional Email Service
Uses Resend API (modern, reliable) with SMTP fallback
"""
import os
from django.conf import settings
from django.core.mail import send_mail
import requests
import logging

logger = logging.getLogger(__name__)


def send_email_via_resend(to_email, subject, html_content, plain_text_content=None):
    """
    Send email using Resend API (modern, reliable email service)
    Returns True if successful, False otherwise
    """
    resend_api_key = os.getenv('RESEND_API_KEY')
    
    if not resend_api_key:
        logger.warning("RESEND_API_KEY not configured, skipping Resend email")
        return False
    
    try:
        from_email = os.getenv('RESEND_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        
        # Resend API endpoint
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        
        if plain_text_content:
            payload["text"] = plain_text_content
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Email sent successfully via Resend to {to_email}")
            return True
        else:
            logger.error(f"❌ Resend API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending email via Resend: {str(e)}")
        return False


def send_email_via_smtp(to_email, subject, html_content, plain_text_content):
    """
    Send email using Django's SMTP backend (fallback)
    Returns True if successful, False otherwise
    """
    try:
        from_email = settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject=subject,
            message=plain_text_content,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_content,
            fail_silently=False,
        )
        logger.info(f"✅ Email sent successfully via SMTP to {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ Error sending email via SMTP: {str(e)}")
        return False


def send_email_professional(to_email, subject, html_content, plain_text_content=None):
    """
    Professional email sending with automatic fallback:
    1. Try Resend API (modern, reliable)
    2. Fallback to SMTP if Resend fails or not configured
    3. Always log the result
    
    Returns True if email was sent successfully, False otherwise
    """
    logger.info(f"📧 Attempting to send email to {to_email}...")
    
    # Try Resend first (best option)
    if send_email_via_resend(to_email, subject, html_content, plain_text_content):
        return True
    
    # Fallback to SMTP
    logger.info("⚠️ Resend failed or not configured, trying SMTP fallback...")
    if plain_text_content is None:
        # Generate plain text from HTML if not provided
        from django.utils.html import strip_tags
        plain_text_content = strip_tags(html_content)
    
    if send_email_via_smtp(to_email, subject, html_content, plain_text_content):
        return True
    
    # Both methods failed
    logger.error(f"❌ Failed to send email to {to_email} via both Resend and SMTP")
    return False

