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

from .models import UserProfile, PasswordResetToken
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
    """List all patients for doctor appointment scheduling"""
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        return cors_response({}, status_code=status.HTTP_200_OK)
    
    try:
        # Only doctors can list patients
        if request.user.role != 'doctor':
            return cors_response({
                'error': 'Only doctors can access this endpoint'
            }, status_code=status.HTTP_403_FORBIDDEN)
        
        # Get all user profiles with role='patient'
        patients = User.objects.filter(role='patient').select_related('profile')
        
        patients_list = []
        for patient in patients:
            try:
                profile = patient.profile
                if profile:
                    patients_list.append({
                        'id': str(profile.id),
                        'name': profile.full_name or patient.email,
                        'email': patient.email,
                        'phone': patient.phone or '',
                    })
            except UserProfile.DoesNotExist:
                # Skip patients without profiles
                continue
        
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
