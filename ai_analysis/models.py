from django.db import models
from django.utils import timezone
import uuid


class HealthRecord(models.Model):
    """Model to store health record information"""
    RECORD_TYPES = [
        ('lab_test', 'Lab Test'),
        ('prescription', 'Prescription'),
        ('imaging', 'Imaging'),
        ('consultation', 'Consultation'),
        ('vaccination', 'Vaccination'),
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('ct_scan', 'CT Scan'),
        ('ultrasound', 'Ultrasound'),
        ('other', 'Other'),
    ]
    
    # Use UUID for new records, but keep CharField for backward compatibility
    def generate_uuid():
        return str(uuid.uuid4())
    
    id = models.CharField(max_length=255, primary_key=True, default=generate_uuid)
    # ForeignKey to UserProfile (patient_id will be auto-created by Django)
    patient = models.ForeignKey('authentication.UserProfile', on_delete=models.CASCADE, related_name='health_records', null=True, blank=True, db_column='patient_id')
    record_type = models.CharField(max_length=50, choices=RECORD_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    record_date = models.DateTimeField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.CharField(max_length=255, blank=True, null=True)
    uploaded_by_profile = models.ForeignKey('authentication.UserProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_records', db_column='uploaded_by_profile_id')
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'health_records'
        ordering = ['-record_date', '-uploaded_at']
        indexes = [
            models.Index(fields=['patient', '-record_date']),
            models.Index(fields=['record_type', '-record_date']),
            models.Index(fields=['uploaded_by_profile', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.record_type})"


class AIAnalysis(models.Model):
    """Model to store AI analysis results"""
    id = models.AutoField(primary_key=True)
    record_id = models.CharField(max_length=255)
    summary = models.TextField()
    simplified_summary = models.TextField(blank=True, null=True)  # Re-enabled - column exists
    key_findings = models.JSONField(default=list)
    risk_warnings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    confidence = models.FloatField(default=0.0)
    analysis_type = models.CharField(max_length=100, default='AI Analysis')
    disclaimer = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(default=timezone.now)
    record_title = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'ai_insights'
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"AI Analysis for {self.record_title}"


class MRI_CT_Analysis(models.Model):
    """Model to store MRI/CT scan analysis results from Dr7.ai"""
    SCAN_TYPES = [
        ('MRI', 'MRI'),
        ('CT', 'CT Scan'),
        ('XRAY', 'X-Ray'),
    ]
    
    RISK_LEVELS = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.AutoField(primary_key=True)
    record_id = models.CharField(max_length=255, unique=True)
    patient_id = models.CharField(max_length=255)
    scan_type = models.CharField(max_length=10, choices=SCAN_TYPES)
    
    # Dr7.ai API response fields
    summary = models.TextField(help_text="Detailed analysis summary (>100 words)")
    findings = models.JSONField(default=list, help_text="Structured list of detected abnormalities")
    region = models.CharField(max_length=100, help_text="Anatomical region (e.g., brain, chest, abdomen)")
    clinical_significance = models.TextField(help_text="Medical interpretation and potential conditions")
    recommendations = models.JSONField(default=list, help_text="Next-step advice and follow-up recommendations")
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='moderate')
    
    # Metadata
    source_model = models.CharField(max_length=50, default='medsiglip-v1')
    doctor_access = models.BooleanField(default=False, help_text="Whether doctors can access this analysis")
    api_usage_tokens = models.IntegerField(default=0, help_text="API tokens used for this analysis")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mri_ct_analysis'
        ordering = ['-created_at']
        verbose_name = 'MRI/CT Analysis'
        verbose_name_plural = 'MRI/CT Analyses'
    
    def __str__(self):
        return f"{self.scan_type} Analysis for Record {self.record_id}"
    
    @property
    def disclaimer(self):
        return (
            "**Disclaimer:** This MRI/CT Scan analysis is automatically generated by an AI model "
            "and is provided **for informational purposes only**. It does **not substitute for clinical "
            "judgment or diagnostic evaluation**. Always consult a qualified radiologist or medical "
            "professional for interpretation and treatment decisions."
        )