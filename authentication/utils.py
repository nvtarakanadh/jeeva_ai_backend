from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_password_reset_email(user, token):
    """Send password reset email to user"""
    # Get frontend URL from settings or use default
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    reset_link = f"{frontend_url}/auth/reset-password?token={token}"
    
    subject = 'Reset Your Password - Jeeva AI'
    
    # Create email message
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">Password Reset Request</h2>
            <p>Hello {user.get_full_name() or user.email},</p>
            <p>You requested to reset your password for your Jeeva AI account.</p>
            <p>Click the button below to reset your password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background-color: #2563eb; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #2563eb;">{reset_link}</p>
            <p><strong>This link will expire in 1 hour.</strong></p>
            <p>If you didn't request this password reset, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">
                This is an automated message from Jeeva AI. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    # Get email settings
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jeeva.ai')
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise


def send_welcome_email(user):
    """Send welcome email to newly registered user"""
    subject = 'Welcome to Jeeva AI'
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">Welcome to Jeeva AI!</h2>
            <p>Hello {user.get_full_name() or user.email},</p>
            <p>Thank you for registering with Jeeva AI. Your account has been created successfully.</p>
            <p>You can now access all features of our healthcare platform.</p>
            <p>If you have any questions, please don't hesitate to contact our support team.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">
                This is an automated message from Jeeva AI. Please do not reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jeeva.ai')
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {str(e)}")
        # Don't raise - welcome email is not critical

