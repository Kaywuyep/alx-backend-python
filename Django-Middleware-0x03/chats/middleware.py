import logging
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden

# Configure logging to write to a file
logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(message)s',
    filemode='a'
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get user information
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response
    

class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get current server time
        current_time = datetime.now().time()
        
        # Define allowed hours (9 AM to 6 PM)
        start_time = datetime.strptime("09:00", "%H:%M").time()
        end_time = datetime.strptime("18:00", "%H:%M").time()
        
        # Check if current time is outside allowed hours
        if not (start_time <= current_time <= end_time):
            return HttpResponseForbidden(
                "Access denied. The messaging app is only available between 9:00 AM and 6:00 PM."
            )
        
        # Process the request if within allowed hours
        response = self.get_response(request)
        
        return response