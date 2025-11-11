from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for User Profile"""
    class Meta:
        model = UserProfile
        fields = [
            'id', 'full_name', 'date_of_birth', 'gender', 'blood_group',
            'allergies', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'specialization', 'license_number',
            'hospital', 'experience', 'consultation_fee', 'available_slots',
            'rating', 'total_consultations', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'rating', 'total_consultations']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone', 'role', 'is_email_verified',
            'first_name', 'last_name', 'profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_email_verified']


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(required=True, max_length=255)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    role = serializers.ChoiceField(choices=[('patient', 'Patient'), ('doctor', 'Doctor')], default='patient')
    
    # Optional profile fields
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=False, allow_null=True)
    blood_group = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10)
    allergies = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True, default=list)
    
    # Emergency contact fields
    emergency_contact_name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    emergency_contact_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    emergency_contact_relationship = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=50)
    
    # Doctor-specific fields
    specialization = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    license_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    hospital = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    experience = serializers.IntegerField(required=False, default=0)
    consultation_fee = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, default=0.00)

    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists. Please use a different email or try logging in.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Convert empty strings to None for optional fields
        optional_fields = ['phone', 'gender', 'blood_group', 'date_of_birth',
                          'emergency_contact_name', 'emergency_contact_phone', 
                          'emergency_contact_relationship', 'specialization',
                          'license_number', 'hospital']
        for field in optional_fields:
            if field in attrs and attrs[field] == '':
                attrs[field] = None
        
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        full_name = validated_data.pop('full_name')
        role = validated_data.pop('role', 'patient')
        
        # Extract profile data
        profile_data = {
            'full_name': full_name,
            'date_of_birth': validated_data.pop('date_of_birth', None),
            'gender': validated_data.pop('gender', None),
            'blood_group': validated_data.pop('blood_group', None),
            'allergies': validated_data.pop('allergies', []),
            'emergency_contact_name': validated_data.pop('emergency_contact_name', None),
            'emergency_contact_phone': validated_data.pop('emergency_contact_phone', None),
            'emergency_contact_relationship': validated_data.pop('emergency_contact_relationship', None),
            'specialization': validated_data.pop('specialization', None),
            'license_number': validated_data.pop('license_number', None),
            'hospital': validated_data.pop('hospital', None),
            'experience': validated_data.pop('experience', 0),
            'consultation_fee': validated_data.pop('consultation_fee', 0.00),
        }
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', validated_data['email']),
            password=password,
            phone=validated_data.get('phone') or None,  # Use None instead of empty string
            role=role,
            **{k: v for k, v in validated_data.items() if k in ['first_name', 'last_name']}
        )
        
        # Create profile
        UserProfile.objects.create(user=user, **profile_data)
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Try to get user by email (since email is USERNAME_FIELD)
            try:
                user = User.objects.get(email=email)
                # Authenticate using username (which is email in our case)
                user = authenticate(request=self.context.get('request'), username=user.username, password=password)
            except User.DoesNotExist:
                user = None
            
            if not user:
                raise serializers.ValidationError({'detail': 'Invalid email or password.'})
            if not user.is_active:
                raise serializers.ValidationError({'detail': 'User account is disabled.'})
            attrs['user'] = user
        else:
            raise serializers.ValidationError({'detail': 'Must include "email" and "password".'})

        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

