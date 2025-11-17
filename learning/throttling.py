"""
Custom throttling classes for rate limiting.

Provides specialized rate limiting for expensive operations like AI generation.
"""

from rest_framework.throttling import UserRateThrottle


class AIGenerationThrottle(UserRateThrottle):
    """
    Throttle for AI content generation endpoints.

    Limits AI generation requests to prevent abuse and control costs.
    Rate: 10 requests per hour per user (configurable in settings)
    """
    scope = 'ai_generation'

    def allow_request(self, request, view):
        """
        Check if request is allowed under rate limit.

        Args:
            request: HTTP request
            view: View being accessed

        Returns:
            bool: True if allowed, False if throttled
        """
        # Allow staff/superusers higher limits
        if request.user and (request.user.is_staff or request.user.is_superuser):
            # Staff get 5x higher limit
            original_scope = self.scope
            self.scope = 'user'  # Use general user limit
            allowed = super().allow_request(request, view)
            self.scope = original_scope
            return allowed

        return super().allow_request(request, view)


class LoginThrottle(UserRateThrottle):
    """
    Throttle for login attempts to prevent brute force attacks.

    Rate: 5 attempts per minute
    """
    scope = 'login'

    def get_cache_key(self, request, view):
        """
        Generate cache key based on username or IP for anonymous users.

        This allows tracking login attempts per username even before authentication.
        """
        # Try to get username from request data
        username = request.data.get('username')

        if username:
            # Throttle by username
            ident = username
        else:
            # Throttle by IP for requests without username
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
