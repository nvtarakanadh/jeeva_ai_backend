"""
Custom middleware to ensure CORS headers are always present, even on errors
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import traceback


class CORSExceptionMiddleware(MiddlewareMixin):
    """
    Middleware to add CORS headers to all responses, including error responses
    """
    def process_response(self, request, response):
        # Add CORS headers to all responses
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cache-Control, X-Requested-With, Accept, Origin'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        return response

    def process_exception(self, request, exception):
        """
        Handle exceptions and return JSON response with CORS headers
        """
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ Unhandled exception in middleware: {str(exception)}")
        print(f"❌ Traceback: {error_traceback}")
        
        # Import settings here to avoid circular imports
        from django.conf import settings
        
        # Return JSON error response with CORS headers
        response = JsonResponse({
            'error': f'Internal server error: {str(exception)}',
            'details': str(error_traceback) if settings.DEBUG else None
        }, status=500)
        
        # Add CORS headers
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cache-Control, X-Requested-With, Accept, Origin'
        response['Access-Control-Allow-Credentials'] = 'true'
        
        return response

