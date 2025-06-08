import logging
import time
from datetime import datetime, timedelta
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, JsonResponse
from collections import defaultdict, deque
from django.contrib.auth.models import Group

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


class RolepermissionMiddleware(MiddlewareMixin):
    # Define protected paths that require admin/moderator access
    PROTECTED_PATHS = [
        '/admin/',
        '/moderator/',
    ]
    
    # Define allowed roles
    ALLOWED_ROLES = ['admin', 'moderator']
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Check if the requested path requires special permissions
        if self.requires_permission(request.path):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return HttpResponseForbidden(
                    "Authentication required. Please log in to access this resource."
                )
            
            # Check if user has required role
            if not self.has_required_role(request.user):
                return HttpResponseForbidden(
                    "Access denied. Admin or moderator privileges required to access this resource."
                )
        
        # Process the request if permission checks pass
        response = self.get_response(request)
        return response
    
    def requires_permission(self, path):
        """Check if the requested path requires admin/moderator permissions"""
        return any(path.startswith(protected_path) for protected_path in self.PROTECTED_PATHS)
    
    def has_required_role(self, user):
        """Check if user has admin or moderator role"""
        # Check if user is superuser (Django's built-in admin)
        if user.is_superuser:
            return True
        
        # Check if user is staff (Django's built-in staff status)
        if user.is_staff:
            return True
        
        # Check user groups for admin/moderator roles
        user_groups = user.groups.values_list('name', flat=True)
        return any(role.lower() in [group.lower() for group in user_groups] for role in self.ALLOWED_ROLES)
        
        # Check custom user profile
        # if hasattr(user, 'profile') and hasattr(user.profile, 'role'):
        #     return user.profile.role.lower() in [role.lower() for role in self.ALLOWED_ROLES]
        
        # Check custom user fields
        # if hasattr(user, 'role'):
        #     return user.role.lower() in [role.lower() for role in self.ALLOWED_ROLES]
