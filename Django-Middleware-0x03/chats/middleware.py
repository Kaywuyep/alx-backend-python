import logging
import time
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from collections import defaultdict, deque
from django.http import JsonResponse

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
    

class OffensiveLanguageMiddleware(MiddlewareMixin):
    # Class-level storage for tracking IP requests
    ip_requests = defaultdict(deque)
    
    # Configuration
    MAX_MESSAGES = 5  # Maximum messages allowed
    TIME_WINDOW = 60  # Time window in seconds (1 minute)
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Only check POST requests (chat messages)
        if request.method == 'POST':
            # Get client IP address
            ip_address = self.get_client_ip(request)
            current_time = time.time()
            
            # Clean old requests outside the time window
            self.clean_old_requests(ip_address, current_time)
            
            # Check if user has exceeded the limit
            if len(self.ip_requests[ip_address]) >= self.MAX_MESSAGES:
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'message': f'You can only send {self.MAX_MESSAGES} messages per minute. Please wait before sending another message.',
                        'retry_after': self.get_retry_after(ip_address, current_time)
                    },
                    status=429  # Too Many Requests
                )
            
            # Add current request to tracking
            self.ip_requests[ip_address].append(current_time)
        
        # Process the request
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get the real IP address of the client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def clean_old_requests(self, ip_address, current_time):
        """Remove requests that are outside the time window"""
        cutoff_time = current_time - self.TIME_WINDOW
        requests_queue = self.ip_requests[ip_address]
        
        # Remove old requests
        while requests_queue and requests_queue[0] < cutoff_time:
            requests_queue.popleft()
    
    def get_retry_after(self, ip_address, current_time):
        """Calculate how long the user should wait before trying again"""
        if not self.ip_requests[ip_address]:
            return 0
        
        oldest_request = self.ip_requests[ip_address][0]
        wait_time = self.TIME_WINDOW - (current_time - oldest_request)
        return max(0, int(wait_time))
