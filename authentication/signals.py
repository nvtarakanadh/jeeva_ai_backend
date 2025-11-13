from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile
from .utils import send_welcome_email
import threading


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        # Create profile synchronously (fast operation)
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'full_name': instance.get_full_name() or instance.email
            }
        )
        
        # Send welcome email in background thread to avoid blocking registration
        def send_welcome_email_async():
            try:
                print(f"📧 Sending welcome email to {instance.email} in background...")
                send_welcome_email(instance)
            except Exception as e:
                print(f"❌ Error sending welcome email: {str(e)}")
        
        # Start email sending in background thread
        email_thread = threading.Thread(target=send_welcome_email_async)
        email_thread.daemon = True  # Thread will exit when main program exits
        email_thread.start()

