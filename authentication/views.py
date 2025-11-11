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

from .models import UserProfile, PasswordResetToken
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ChangePasswordSerializer, UserProfileSerializer
)
from .utils import send_password_reset_email

User = get_user_model()


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
            if 'duplicate key' in error_message.lower() or 'already exists' in error_message.lower():
                if 'email' in error_message.lower():
                    error_message = 'An account with this email already exists.'
                elif 'username' in error_message.lower():
                    error_message = 'This username is already taken.'
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
    
    # In development mode, always print the reset link to console
    if settings.DEBUG:
        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        print(f"\n{'='*80}")
        print(f"{' '*20}PASSWORD RESET LINK (Development Mode)")
        print(f"{'='*80}")
        print(f"Email: {user.email}")
        print(f"Reset Link: {reset_link}")
        print(f"{'='*80}\n")
        print("⚠️  IMPORTANT: In development mode, emails are NOT sent via SMTP.")
        print("⚠️  Copy the reset link above and use it to reset your password.\n")
    
    # Send email with reset link
    try:
        send_password_reset_email(user, token)
        # In development, console backend will also print the email
        response_message = 'If an account exists with this email, a password reset link has been sent.'
        if settings.DEBUG:
            response_message += ' Check the Django console for the reset link.'
        return Response({
            'message': response_message
        }, status=status.HTTP_200_OK)
    except Exception as e:
        # Log error but don't reveal it to user
        print(f"Error sending email: {str(e)}")
        # In development, the link was already printed above
        response_message = 'If an account exists with this email, a password reset link has been sent.'
        if settings.DEBUG:
            response_message += ' Check the Django console for the reset link.'
        return Response({
            'message': response_message
        }, status=status.HTTP_200_OK)


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
