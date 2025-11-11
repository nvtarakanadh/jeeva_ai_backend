from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile
from .utils import send_welcome_email


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(
            user=instance,
            full_name=instance.get_full_name() or instance.email
        )
        # Send welcome email
        try:
            send_welcome_email(instance)
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")

