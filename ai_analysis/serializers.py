from rest_framework import serializers
from .models import HealthRecord, AIAnalysis, MRI_CT_Analysis


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = '__all__'


class AIAnalysisSerializer(serializers.ModelSerializer):
    ai_disclaimer = serializers.CharField(source='disclaimer', read_only=True)
    
    class Meta:
        model = AIAnalysis
        fields = '__all__'
    
    def to_representation(self, instance):
        """Override to handle simplified_summary column gracefully"""
        data = super().to_representation(instance)
        
        # Try to get simplified_summary, fallback to empty string if column doesn't exist
        try:
            if hasattr(instance, 'simplified_summary') and instance.simplified_summary:
                data['simplifiedSummary'] = instance.simplified_summary
            else:
                data['simplifiedSummary'] = ''
        except Exception:
            data['simplifiedSummary'] = ''
        
        return data


class PrescriptionAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for prescription analysis requests"""
    image = serializers.ImageField()
    title = serializers.CharField(max_length=255, required=False, default="Prescription Analysis")
    description = serializers.CharField(required=False, default="")
    record_type = serializers.CharField(default="prescription")
    patient_id = serializers.CharField(max_length=255, required=False)
    uploaded_by = serializers.CharField(max_length=255, required=False)


class HealthRecordAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for health record analysis requests"""
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default="", allow_blank=True)
    record_type = serializers.CharField()
    service_date = serializers.CharField()  # Changed from DateTimeField to CharField
    file_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    file_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    patient_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    uploaded_by = serializers.CharField(max_length=255, required=False, allow_blank=True)
    record_id = serializers.CharField(max_length=255, required=False, allow_blank=True)  # Add record_id field


class MRI_CT_AnalysisSerializer(serializers.ModelSerializer):
    """Serializer for MRI/CT analysis results"""
    disclaimer = serializers.CharField(source='disclaimer', read_only=True)
    scan_type_display = serializers.CharField(source='get_scan_type_display', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = MRI_CT_Analysis
        fields = [
            'id', 'record_id', 'patient_id', 'scan_type', 'scan_type_display',
            'summary', 'findings', 'region', 'clinical_significance', 
            'recommendations', 'risk_level', 'risk_level_display',
            'source_model', 'doctor_access', 'api_usage_tokens',
            'created_at', 'updated_at', 'disclaimer'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'disclaimer']


class MRI_CT_AnalysisRequestSerializer(serializers.Serializer):
    """Serializer for MRI/CT analysis requests"""
    record_id = serializers.CharField(max_length=255)
    patient_id = serializers.CharField(max_length=255)
    scan_type = serializers.ChoiceField(choices=MRI_CT_Analysis.SCAN_TYPES)
    image_url = serializers.URLField(required=False, allow_blank=True)
    image_file = serializers.ImageField(required=False)
    doctor_access = serializers.BooleanField(default=False)


class MRI_CT_AnalysisResponseSerializer(serializers.Serializer):
    """Serializer for MRI/CT analysis API responses"""
    id = serializers.IntegerField(read_only=True)
    record_id = serializers.CharField()
    patient_id = serializers.CharField()
    scan_type = serializers.CharField()
    summary = serializers.CharField()
    findings = serializers.ListField(child=serializers.CharField())
    region = serializers.CharField()
    clinical_significance = serializers.CharField()
    recommendations = serializers.ListField(child=serializers.CharField())
    risk_level = serializers.CharField()
    source_model = serializers.CharField()
    doctor_access = serializers.BooleanField()
    api_usage_tokens = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    disclaimer = serializers.CharField()
