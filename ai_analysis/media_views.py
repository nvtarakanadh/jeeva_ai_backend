"""
Views for serving media files in production
"""
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import os
from pathlib import Path


@require_http_methods(["GET", "OPTIONS"])
def serve_media_file(request, file_path):
    """
    Serve media files in production.
    This view handles requests for files in the media directory.
    """
    # Handle OPTIONS preflight request
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    # Construct the full file path
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    
    # Security check: ensure the file is within MEDIA_ROOT
    full_path = os.path.normpath(full_path)
    media_root = os.path.normpath(settings.MEDIA_ROOT)
    
    if not full_path.startswith(media_root):
        raise Http404("File not found")
    
    # Check if file exists
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        print(f"❌ Media file not found: {full_path}")
        raise Http404("File not found")
    
    # Determine content type based on file extension
    ext = os.path.splitext(full_path)[1].lower()
    content_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }
    content_type = content_types.get(ext, 'application/octet-stream')
    
    # Serve the file
    try:
        file_handle = open(full_path, 'rb')
        response = FileResponse(file_handle, content_type=content_type)
        
        # Add CORS headers
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # Add cache headers
        response['Cache-Control'] = 'public, max-age=3600'
        
        # Add content disposition for downloads
        filename = os.path.basename(full_path)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        print(f"✅ Serving media file: {full_path} (Content-Type: {content_type})")
        return response
    except Exception as e:
        print(f"❌ Error serving media file: {str(e)}")
        raise Http404("Error serving file")
