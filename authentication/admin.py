from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    list_display = ['email', 'username', 'role', 'is_email_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_email_verified', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'role', 'is_email_verified')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'phone', 'role')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""
    list_display = ['full_name', 'user', 'role', 'specialization', 'hospital', 'created_at']
    list_filter = ['user__role', 'gender', 'created_at']
    search_fields = ['full_name', 'user__email', 'specialization', 'hospital', 'license_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'full_name', 'date_of_birth', 'gender', 'blood_group')
        }),
        ('Contact Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Medical Information', {
            'fields': ('allergies',)
        }),
        ('Doctor Information', {
            'fields': ('specialization', 'license_number', 'hospital', 'experience', 
                      'consultation_fee', 'available_slots', 'rating', 'total_consultations')
        }),
        ('Metadata', {
            'fields': ('metadata', 'id', 'created_at', 'updated_at')
        }),
    )
    
    def role(self, obj):
        return obj.user.role
    role.short_description = 'Role'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin interface for PasswordResetToken model"""
    list_display = ['user', 'created_at', 'expires_at', 'used', 'is_valid']
    list_filter = ['used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['id', 'token', 'created_at']
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'
