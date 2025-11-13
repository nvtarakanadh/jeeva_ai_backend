from django.conf import settings
from django.utils.html import strip_tags
from .email_service import send_email_professional


def send_password_reset_email(user, token):
    """Send password reset email to user using professional email service"""
    # Get frontend URL from settings or use default
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    reset_link = f"{frontend_url}/auth/reset-password?token={token}"
    
    subject = 'Reset Your Password - Jeeva AI'
    
    # Create professional email message
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 40px auto; padding: 0; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); padding: 30px 20px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">Jeeva AI</h1>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #1f2937; margin-top: 0; font-size: 22px; font-weight: 600;">Password Reset Request</h2>
                <p style="color: #4b5563; font-size: 16px; margin: 20px 0;">Hello {user.get_full_name() or user.email},</p>
                <p style="color: #4b5563; font-size: 16px; margin: 20px 0;">You requested to reset your password for your Jeeva AI account. Click the button below to reset your password:</p>
                
                <!-- CTA Button -->
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #2563eb; color: #ffffff; padding: 14px 32px; 
                              text-decoration: none; border-radius: 6px; display: inline-block; 
                              font-weight: 600; font-size: 16px; transition: background-color 0.3s;">
                        Reset Password
                    </a>
                </div>
                
                <!-- Alternative Link -->
                <p style="color: #6b7280; font-size: 14px; margin: 30px 0;">Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #2563eb; font-size: 14px; background-color: #f3f4f6; padding: 12px; border-radius: 4px; margin: 20px 0;">{reset_link}</p>
                
                <!-- Expiry Notice -->
                <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px 16px; margin: 30px 0; border-radius: 4px;">
                    <p style="color: #92400e; margin: 0; font-size: 14px; font-weight: 500;">⏰ This link will expire in 1 hour.</p>
                </div>
                
                <!-- Security Notice -->
                <p style="color: #6b7280; font-size: 14px; margin: 30px 0 0 0;">If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f9fafb; padding: 20px 30px; border-top: 1px solid #e5e7eb;">
                <p style="color: #9ca3af; font-size: 12px; margin: 0; text-align: center;">
                    This is an automated message from Jeeva AI. Please do not reply to this email.<br>
                    © {settings.FRONTEND_URL.split('//')[1] if '//' in settings.FRONTEND_URL else 'Jeeva AI'} - All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = f"""
Password Reset Request - Jeeva AI

Hello {user.get_full_name() or user.email},

You requested to reset your password for your Jeeva AI account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this password reset, please ignore this email. Your password will remain unchanged.

---
This is an automated message from Jeeva AI. Please do not reply to this email.
"""
    
    # Use professional email service (Resend with SMTP fallback)
    return send_email_professional(
        to_email=user.email,
        subject=subject,
        html_content=html_message,
        plain_text_content=plain_message
    )


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

