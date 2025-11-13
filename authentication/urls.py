from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, logout_view, current_user_view,
    password_reset_request_view, password_reset_confirm_view,
    change_password_view, profile_view, delete_account_view,
    list_doctors_view, list_patients_view
)

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User endpoints
    path('me/', current_user_view, name='current_user'),
    path('profile/', profile_view, name='profile'),
    path('account/delete/', delete_account_view, name='delete_account'),
    
    # Password management
    path('password/reset/request/', password_reset_request_view, name='password_reset_request'),
    path('password/reset/confirm/', password_reset_confirm_view, name='password_reset_confirm'),
    path('password/change/', change_password_view, name='change_password'),
    
    # User lists for appointments
    path('doctors/', list_doctors_view, name='list_doctors'),
    path('patients/', list_patients_view, name='list_patients'),
]

