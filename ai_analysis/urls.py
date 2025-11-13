from django.urls import path, re_path
from . import views
from . import media_views

urlpatterns = [
    # Media file serving (for production)
    re_path(r'^media/(?P<file_path>.*)$', media_views.serve_media_file, name='serve_media'),
    # Existing AI analysis endpoints
    path('analyze/prescription/', views.analyze_prescription, name='analyze_prescription'),
    path('analyze/health-record/', views.analyze_health_record, name='analyze_health_record'),
    path('analysis/<str:record_id>/', views.get_analysis, name='get_analysis'),
    path('analyses/', views.list_analyses, name='list_analyses'),
    path('health/', views.health_check, name='health_check'),
    
    # MRI/CT scan analysis endpoints
    path('analyze/mri-ct-scan/', views.analyze_mri_ct_scan, name='analyze_mri_ct_scan'),
    path('mri-ct-analysis/<str:record_id>/', views.get_mri_ct_analysis, name='get_mri_ct_analysis'),
    path('mri-ct-analyses/', views.list_mri_ct_analyses, name='list_mri_ct_analyses'),
    path('mri-ct-analysis/<str:record_id>/doctor-access/', views.update_doctor_access, name='update_doctor_access'),
    
    # Health Records CRUD endpoints (order matters - more specific paths first)
    path('health-records/upload/', views.health_record_upload_file, name='health_record_upload_file'),
    path('health-records/<str:record_id>/', views.health_record_detail, name='health_record_detail'),
    path('health-records/', views.health_records_list_create, name='health_records_list_create'),
]
