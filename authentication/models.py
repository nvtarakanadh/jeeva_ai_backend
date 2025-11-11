from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[('patient', 'Patient'), ('doctor', 'Doctor')],
        default='patient'
    )
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """User Profile model for storing additional user information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True,
        null=True
    )
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    allergies = models.JSONField(default=list, blank=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    
    # Doctor-specific fields
    specialization = models.CharField(max_length=255, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    hospital = models.CharField(max_length=255, blank=True, null=True)
    experience = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_slots = models.JSONField(default=list, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_consultations = models.IntegerField(default=0)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.full_name} ({self.user.role})"


class PasswordResetToken(models.Model):
    """Model for storing password reset tokens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'used']),
        ]

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.used and timezone.now() < self.expires_at


class Prescription(models.Model):
    """Prescription model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='prescriptions_as_patient')
    doctor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='prescriptions_as_doctor')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    prescription_date = models.DateField()
    file_url = models.URLField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prescriptions'
        ordering = ['-prescription_date', '-created_at']
        indexes = [
            models.Index(fields=['patient', '-prescription_date']),
            models.Index(fields=['doctor', '-prescription_date']),
        ]

    def __str__(self):
        return f"{self.medication} - {self.patient.full_name}"


class ConsultationNote(models.Model):
    """Consultation note model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='consultation_notes_as_patient')
    doctor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='consultation_notes_as_doctor')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    consultation_date = models.DateField()
    file_url = models.URLField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultation_notes'
        ordering = ['-consultation_date', '-created_at']
        indexes = [
            models.Index(fields=['patient', '-consultation_date']),
            models.Index(fields=['doctor', '-consultation_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.patient.full_name}"


# HealthRecord model is in ai_analysis app to avoid conflicts


class ConsentRequest(models.Model):
    """Consent request model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='consent_requests_as_patient')
    doctor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='consent_requests_as_doctor')
    purpose = models.TextField()
    requested_data_types = models.JSONField(default=list)
    duration_days = models.IntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    response_message = models.TextField(blank=True)
    approved_data_types = models.JSONField(default=list, blank=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'consent_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['doctor', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"Consent Request: {self.patient.full_name} -> {self.doctor.full_name}"


class RecordAccess(models.Model):
    """Record access model - tracks which doctors have access to which patient records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='record_accesses_as_patient')
    doctor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='record_accesses_as_doctor')
    consent_request = models.ForeignKey(ConsentRequest, on_delete=models.CASCADE, related_name='record_accesses', null=True, blank=True)
    allowed_data_types = models.JSONField(default=list)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'record_accesses'
        unique_together = [['patient', 'doctor']]
        indexes = [
            models.Index(fields=['patient', 'is_active']),
            models.Index(fields=['doctor', 'is_active']),
        ]

    def __str__(self):
        return f"Access: {self.doctor.full_name} -> {self.patient.full_name}"
