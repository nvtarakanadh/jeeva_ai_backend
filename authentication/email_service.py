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

# Also use print for Railway logs visibility
def log_info(msg):
    print(msg)
    logger.info(msg)

def log_error(msg):
    print(msg)
    logger.error(msg)

def log_warning(msg):
    print(msg)
    logger.warning(msg)


def send_email_via_resend(to_email, subject, html_content, plain_text_content=None):
    """
    Send email using Resend API (modern, reliable email service)
    Returns True if successful, False otherwise
    """
    resend_api_key = os.getenv('RESEND_API_KEY')
    
    if not resend_api_key:
        log_warning("⚠️ RESEND_API_KEY not configured, skipping Resend email")
        log_warning("💡 To enable Resend: Add RESEND_API_KEY to Railway environment variables")
        return False
    
    try:
        from_email = os.getenv('RESEND_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        log_info(f"📧 Attempting to send email via Resend to {to_email} from {from_email}")
        
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
        
        log_info(f"📤 Sending request to Resend API...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()
            log_info(f"✅ Email sent successfully via Resend to {to_email}")
            log_info(f"📧 Resend email ID: {response_data.get('id', 'N/A')}")
            return True
        else:
            log_error(f"❌ Resend API error: {response.status_code}")
            log_error(f"❌ Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        log_error(f"❌ Resend API timeout - request took too long")
        return False
    except requests.exceptions.RequestException as e:
        log_error(f"❌ Resend API request error: {str(e)}")
        return False
    except Exception as e:
        log_error(f"❌ Unexpected error sending email via Resend: {str(e)}")
        import traceback
        log_error(f"❌ Traceback: {traceback.format_exc()}")
        return False


def send_email_via_smtp(to_email, subject, html_content, plain_text_content):
    """
    Send email using Django's SMTP backend (fallback)
    Returns True if successful, False otherwise
    """
    try:
        from_email = settings.DEFAULT_FROM_EMAIL
        log_info(f"📧 Attempting to send email via SMTP to {to_email} from {from_email}")
        log_info(f"📧 SMTP Backend: {settings.EMAIL_BACKEND}")
        log_info(f"📧 SMTP Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        log_info(f"📧 SMTP User: {settings.EMAIL_HOST_USER or 'Not configured'}")
        
        send_mail(
            subject=subject,
            message=plain_text_content,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_content,
            fail_silently=False,
        )
        log_info(f"✅ Email sent successfully via SMTP to {to_email}")
        return True
    except Exception as e:
        log_error(f"❌ Error sending email via SMTP: {str(e)}")
        import traceback
        log_error(f"❌ SMTP Traceback: {traceback.format_exc()}")
        return False


def send_email_professional(to_email, subject, html_content, plain_text_content=None):
    """
    Professional email sending with automatic fallback:
    1. Try Resend API (modern, reliable)
    2. Fallback to SMTP if Resend fails or not configured
    3. Always log the result
    
    Returns True if email was sent successfully, False otherwise
    """
    log_info(f"{'='*80}")
    log_info(f"📧 EMAIL SERVICE: Attempting to send email to {to_email}")
    log_info(f"📧 Subject: {subject}")
    log_info(f"{'='*80}")
    
    # Try Resend first (best option)
    log_info("🔄 Step 1: Trying Resend API...")
    if send_email_via_resend(to_email, subject, html_content, plain_text_content):
        log_info("✅ Email sent successfully via Resend!")
        return True
    
    # Fallback to SMTP
    log_info("⚠️ Resend failed or not configured, trying SMTP fallback...")
    if plain_text_content is None:
        # Generate plain text from HTML if not provided
        from django.utils.html import strip_tags
        plain_text_content = strip_tags(html_content)
    
    log_info("🔄 Step 2: Trying SMTP...")
    if send_email_via_smtp(to_email, subject, html_content, plain_text_content):
        log_info("✅ Email sent successfully via SMTP!")
        return True
    
    # Both methods failed
    log_error(f"{'='*80}")
    log_error(f"❌ FAILED: Could not send email to {to_email}")
    log_error(f"❌ Both Resend and SMTP methods failed")
    log_error(f"💡 Check Railway logs above for detailed error messages")
    log_error(f"💡 To fix: Configure RESEND_API_KEY or SMTP settings in Railway")
    log_error(f"{'='*80}")
    return False

