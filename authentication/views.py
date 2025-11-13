from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import secrets
import hashlib
import threading

from .models import UserProfile, PasswordResetToken, RecordAccess, ConsentRequest
from django.db import models
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ChangePasswordSerializer, UserProfileSerializer
)
from .utils import send_password_reset_email

User = get_user_model()


def cors_response(data, status_code=200):
    """Helper function to add CORS headers to responses"""
    response = Response(data, status=status_code)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cache-Control, X-Requested-With, Accept, Origin'
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Max-Age'] = '86400'
    return response


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Get user data with profile
            user_serializer = UserSerializer(user)
            
            return Response({
                'message': 'User registered successfully. Please check your email to verify your account.',
                'user': user_serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            error_message = str(e)
            print(f"Registration error: {error_message}")
            print(traceback.format_exc())
            
            # Handle specific database errors with better messages
            if 'duplicate key' in error_message.lower() or 'already exists' in error_message.lower() or 'unique constraint' in error_message.lower():
                # Check if user already exists
                email = request.data.get('email', '')
                if email and User.objects.filter(email=email).exists():
                    error_message = 'An account with this email already exists. Please use a different email or try logging in.'
                elif 'email' in error_message.lower():
                    error_message = 'An account with this email already exists. Please use a different email or try logging in.'
                elif 'username' in error_message.lower():
                    error_message = 'This username is already taken. Please choose a different username.'
                elif 'profile' in error_message.lower() or 'profiles' in error_message.lower():
                    # Profile already exists - user exists but profile creation failed
                    error_message = 'An account with this email already exists. Please try logging in instead.'
                else:
                    error_message = 'An account with this information already exists. Please try logging in.'
                
                return Response({
                    'detail': error_message,
                    'error': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'detail': error_message,
                'error': 'Registration failed. Please check the server logs for details.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(generics.GenericAPIView):
    """User login endpoint with JWT tokens"""
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Get user data with profile
        user_serializer = UserSerializer(user)
        
        return Response({
            'message': 'Login successful',
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """User logout endpoint"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_view(request):
    """Get current authenticated user"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request_view(request):
    """Request password reset - sends email with reset token"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal if user exists for security
        return Response({
            'message': 'If an account exists with this email, a password reset link has been sent.'
        }, status=status.HTTP_200_OK)
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Create password reset token (expires in 1 hour)
    expires_at = timezone.now() + timedelta(hours=1)
    PasswordResetToken.objects.create(
        user=user,
        token=token_hash,
        expires_at=expires_at
    )
    
    # Always print the reset link to console/logs (for debugging in production too)
    reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
    print(f"\n{'='*80}")
    print(f"{' '*20}PASSWORD RESET LINK")
    print(f"{'='*80}")
    print(f"Email: {user.email}")
    print(f"Reset Link: {reset_link}")
    print(f"{'='*80}\n")
    if settings.DEBUG:
        print("⚠️  IMPORTANT: In development mode, emails are NOT sent via SMTP.")
        print("⚠️  Copy the reset link above and use it to reset your password.\n")
    else:
        print("⚠️  Check Railway logs above for the reset link if email is not received.\n")
    
    # Track if email was sent successfully
    email_sent = {'status': False}
    
    # Send email with reset link in background thread to avoid blocking
    def send_email_async():
        try:
            print(f"Attempting to send password reset email to {user.email}...")
            result = send_password_reset_email(user, token)
            email_sent['status'] = result
            if result:
                print(f"✅ Password reset email sent successfully to {user.email}")
            else:
                print(f"⚠️ Password reset email failed to send to {user.email}")
                print(f"💡 Use the reset link from logs: {reset_link}")
        except Exception as e:
            # Log error but don't block the response
            email_sent['status'] = False
            print(f"❌ Error sending email to {user.email}: {str(e)}")
            print(f"❌ Email backend: {settings.EMAIL_BACKEND}")
            print(f"❌ Email host: {settings.EMAIL_HOST}")
            print(f"❌ Email user configured: {bool(settings.EMAIL_HOST_USER)}")
            import traceback
            print(f"❌ Full traceback:\n{traceback.format_exc()}")
            print(f"💡 Use the reset link from logs: {reset_link}")
    
    # Start email sending in background thread
    email_thread = threading.Thread(target=send_email_async)
    email_thread.daemon = True  # Thread will exit when main program exits
    email_thread.start()
    
    # Prepare response
    response_data = {
        'message': 'If an account exists with this email, a password reset link has been sent.',
    }
    
    # Always include reset link in response for easy access (especially when email fails)
    # This helps users get the link immediately without checking logs
    response_data['reset_link'] = reset_link
    response_data['note'] = 'Check your email. If email is not received, use the reset_link from this response.'
    
    if settings.DEBUG:
        response_data['message'] += ' Check the Django console for the reset link.'
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm_view(request):
    """Confirm password reset with token"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    
    # Hash the token to match stored hash
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    try:
        reset_token = PasswordResetToken.objects.get(token=token_hash, used=False)
    except PasswordResetToken.DoesNotExist:
        return Response({
            'error': 'Invalid or expired reset token.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if token is valid
    if not reset_token.is_valid():
        return Response({
            'error': 'Invalid or expired reset token.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update password
    user = reset_token.user
    user.set_password(new_password)
    user.save()
    
    # Mark token as used
    reset_token.used = True
    reset_token.save()
    
    return Response({
        'message': 'Password has been reset successfully.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """Change password for authenticated user"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    new_password = serializer.validated_data['new_password']
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'Password has been changed successfully.'
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account_view(request):
    """Delete user account and all associated data"""
    try:
        user = request.user
        
        # Delete user profile (cascade will handle related data)
        if hasattr(user, 'profile'):
            user.profile.delete()
        
        # Delete the user (this will cascade delete related data)
        user.delete()
        
        return Response({
            'message': 'Account deleted successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error deleting account: {str(e)}")
        print(traceback.format_exc())
        return Response({
            'detail': 'Failed to delete account. Please try again or contact support.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Get or update user profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.email
        )
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(profile, data=request.data, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'OPTIONS'])
@permission_classes([permissions.IsAuthenticated])
def list_doctors_view(request):
    """List all doctors for patient appointment booking"""
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return cors_response({}, status_code=status.HTTP_200_OK)
    
    try:
        # Get all user profiles with role='doctor'
        doctors = User.objects.filter(role='doctor').select_related('profile')
        
        doctors_list = []
        for doctor in doctors:
            try:
                profile = doctor.profile
                if profile:
                    doctors_list.append({
                        'id': str(profile.id),
                        'name': profile.full_name or doctor.email,
                        'specialization': profile.specialization or 'General Medicine',
                        'email': doctor.email,
                        'hospital': profile.hospital or '',
                    })
            except UserProfile.DoesNotExist:
                # Skip doctors without profiles
                continue
        
        return cors_response({
            'count': len(doctors_list),
            'results': doctors_list
        }, status_code=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ Error in list_doctors_view: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return cors_response({
            'error': f'Failed to fetch doctors: {str(e)}'
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'OPTIONS'])
@permission_classes([permissions.IsAuthenticated])
def list_patients_view(request):
    """List patients that the doctor has access to (via RecordAccess)"""
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return cors_response({}, status_code=status.HTTP_200_OK)
    
    try:
        # Only doctors can list patients
        if request.user.role != 'doctor':
            return cors_response({
                'error': 'Only doctors can access this endpoint'
            }, status_code=status.HTTP_403_FORBIDDEN)
        
        # Get doctor's profile
        doctor_profile = UserProfile.objects.filter(user=request.user).first()
        if not doctor_profile:
            return cors_response({
                'error': 'Doctor profile not found'
            }, status_code=status.HTTP_404_NOT_FOUND)
        
        # Get patients that this doctor has active access to via RecordAccess
        from django.utils import timezone
        now = timezone.now()
        
        record_accesses = RecordAccess.objects.filter(
            doctor=doctor_profile,
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).select_related('patient', 'patient__user')
        
        patients_list = []
        for access in record_accesses:
            patient_profile = access.patient
            patient_user = patient_profile.user
            patients_list.append({
                'id': str(patient_profile.id),
                'name': patient_profile.full_name or patient_user.email,
                'email': patient_user.email,
                'phone': patient_user.phone or '',
            })
        
        return cors_response({
            'count': len(patients_list),
            'results': patients_list
        }, status_code=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ Error in list_patients_view: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return cors_response({
            'error': f'Failed to fetch patients: {str(e)}'
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'OPTIONS'])
@permission_classes([permissions.IsAuthenticated])
def doctor_patients_detailed_view(request):
    """Get detailed patient list for doctor with stats (consent status, record counts, etc.)"""
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return cors_response({}, status_code=status.HTTP_200_OK)
    
    try:
        # Only doctors can access this
        if request.user.role != 'doctor':
            return cors_response({
                'error': 'Only doctors can access this endpoint'
            }, status_code=status.HTTP_403_FORBIDDEN)
        
        # Get doctor's profile
        doctor_profile = UserProfile.objects.filter(user=request.user).first()
        if not doctor_profile:
            return cors_response({
                'error': 'Doctor profile not found'
            }, status_code=status.HTTP_404_NOT_FOUND)
        
        # Get patients that this doctor has active access to
        from django.utils import timezone
        from django.db.models import Count, Q, Max
        from ai_analysis.models import HealthRecord
        
        now = timezone.now()
        
        # Get active record accesses
        record_accesses = RecordAccess.objects.filter(
            doctor=doctor_profile,
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).select_related('patient', 'patient__user', 'consent_request')
        
        patients_list = []
        for access in record_accesses:
            patient_profile = access.patient
            patient_user = patient_profile.user
            
            # Get consent status
            consent_status = 'active'
            if access.consent_request:
                consent_status = access.consent_request.status
            elif access.expires_at and access.expires_at < now:
                consent_status = 'expired'
            
            # Count health records for this patient
            health_record_count = HealthRecord.objects.filter(patient=patient_profile).count()
            
            # Calculate age
            age = None
            if patient_profile.date_of_birth:
                today = timezone.now().date()
                age = today.year - patient_profile.date_of_birth.year - (
                    (today.month, today.day) < (patient_profile.date_of_birth.month, patient_profile.date_of_birth.day)
                )
            
            patients_list.append({
                'id': str(patient_profile.id),
                'userId': str(patient_user.id),
                'name': patient_profile.full_name or patient_user.email,
                'email': patient_user.email,
                'phone': patient_user.phone or '',
                'age': age or 25,
                'gender': patient_profile.gender or 'Unknown',
                'lastVisit': patient_profile.updated_at.isoformat() if patient_profile.updated_at else patient_profile.created_at.isoformat(),
                'consentStatus': consent_status,
                'recordCount': health_record_count,
            })
        
        return cors_response({
            'count': len(patients_list),
            'results': patients_list
        }, status_code=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ Error in doctor_patients_detailed_view: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return cors_response({
            'error': f'Failed to fetch patient details: {str(e)}'
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'OPTIONS'])
@permission_classes([permissions.IsAuthenticated])
def doctor_dashboard_stats_view(request):
    """Get dashboard statistics for doctor (total patients, consents, records)"""
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return cors_response({}, status_code=status.HTTP_200_OK)
    
    try:
        # Only doctors can access this
        if request.user.role != 'doctor':
            return cors_response({
                'error': 'Only doctors can access this endpoint'
            }, status_code=status.HTTP_403_FORBIDDEN)
        
        # Get doctor's profile
        doctor_profile = UserProfile.objects.filter(user=request.user).first()
        if not doctor_profile:
            return cors_response({
                'error': 'Doctor profile not found'
            }, status_code=status.HTTP_404_NOT_FOUND)
        
        from django.utils import timezone
        from django.db.models import Count, Q
        from ai_analysis.models import HealthRecord
        
        now = timezone.now()
        
        # Count unique patients with active access
        unique_patients = RecordAccess.objects.filter(
            doctor=doctor_profile,
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).values('patient').distinct().count()
        
        # Count consent requests
        consent_requests = ConsentRequest.objects.filter(doctor=doctor_profile)
        pending_consents = consent_requests.filter(status='pending').count()
        active_consents = consent_requests.filter(status='approved').count()
        
        # Count total health records for patients this doctor has access to
        patient_ids = RecordAccess.objects.filter(
            doctor=doctor_profile,
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).values_list('patient_id', flat=True)
        
        total_records = HealthRecord.objects.filter(patient_id__in=patient_ids).count()
        
        return cors_response({
            'totalPatients': unique_patients,
            'pendingConsents': pending_consents,
            'activeConsents': active_consents,
            'totalRecords': total_records
        }, status_code=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ Error in doctor_dashboard_stats_view: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return cors_response({
            'error': f'Failed to fetch dashboard stats: {str(e)}'
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
