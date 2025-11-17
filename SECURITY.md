# Security Improvements

This document outlines the security enhancements implemented in LearnHub.

## Overview

Based on comprehensive security audit, 12 critical vulnerabilities were identified and fixed. This document details the implemented security measures.

## Critical Security Fixes

### 1. Rate Limiting ✅

**Problem**: No rate limiting allowed abuse and DoS attacks.

**Solution**: Implemented comprehensive rate limiting using Django REST Framework throttling:

```python
# Settings configuration
'DEFAULT_THROTTLE_CLASSES': (
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
),
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',           # Anonymous users
    'user': '1000/hour',          # Authenticated users
    'ai_generation': '10/hour',   # AI endpoints (cost protection)
    'login': '5/minute',          # Login attempts (brute force protection)
}
```

**Custom Throttling**:
- `AIGenerationThrottle`: Limits expensive AI operations (10/hour)
- `LoginThrottle`: Prevents brute force attacks (5 attempts/minute)
- Staff users get 5x higher limits

**Files Modified**:
- `core/settings.py`
- `learning/throttling.py` (new)
- `learning/views.py`

### 2. Admin Route Authorization ✅

**Problem**: Admin routes could be accessed without proper authorization check.

**Solution**: Added router guard to verify `is_staff` or `is_superuser` before allowing access:

```javascript
// Frontend router guard
if (to.meta.requiresAdmin) {
  const user = authStore.user
  const isAdmin = user?.is_staff === true || user?.is_superuser === true

  if (!isAdmin) {
    console.warn('Unauthorized access attempt to admin route')
    next({ name: 'Dashboard' })
    return
  }
}
```

**Files Modified**:
- `frontend/src/router/index.js`

### 3. SECRET_KEY Security ✅

**Problem**: Insecure fallback SECRET_KEY could be used in production.

**Solution**: Implemented proper SECRET_KEY handling:

- **Development**: Warning when using insecure key
- **Testing**: Fixed test key
- **Production**: Fails fast if SECRET_KEY not set
- Clear instructions for generating secure keys

```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if 'pytest' in sys.modules or 'test' in sys.argv:
        SECRET_KEY = 'test-secret-key-for-automated-testing-only'
    elif 'runserver' in sys.argv or 'shell' in sys.argv:
        warnings.warn("WARNING: Using insecure SECRET_KEY...")
    else:
        raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production.")
```

**Files Modified**:
- `core/settings.py`

### 4. CORS Validation ✅

**Problem**: Missing validation of CORS origins could allow malicious cross-origin requests.

**Solution**:

- Development-only localhost origins (only when `DEBUG=True`)
- Production origins must be explicitly whitelisted
- URL validation (must start with http:// or https://)
- Warning when no CORS origins set in production
- Never allow all origins (`CORS_ALLOW_ALL_ORIGINS = False`)

```python
if DEBUG:
    DEFAULT_CORS_ORIGINS = ["http://localhost:5173", ...]
else:
    DEFAULT_CORS_ORIGINS = []  # No defaults in production
```

**Files Modified**:
- `core/settings.py`

### 5. XSS Protection ✅

**Problem**: User-generated content could contain malicious scripts.

**Solution**: Created comprehensive sanitization utilities:

```python
# HTML sanitization
sanitize_html(content, allowed_tags=ALLOWED_TAGS, allowed_attributes=ALLOWED_ATTRIBUTES)

# Plain text escaping
sanitize_text(content)  # HTML entity escaping
```

**Features**:
- Uses `bleach` library for robust HTML cleaning
- Configurable allowed tags and attributes
- Strips dangerous scripts, iframes, and event handlers
- Safe URL protocols only (http, https, mailto)

**Files Modified**:
- `learning/security_utils.py` (new)
- `requirements.txt` (added bleach==6.1.0)

### 6. AI Prompt Validation ✅

**Problem**: No validation of AI prompts could lead to prompt injection attacks and excessive costs.

**Solution**: Comprehensive prompt validation:

```python
def validate_ai_prompt(prompt: str, max_length: int = 50000) -> tuple[bool, str]:
    # Length validation
    # Type checking
    # Prompt injection detection (patterns like "ignore previous instructions")
    # XSS attempt detection
```

**Detection Patterns**:
- "ignore previous instructions"
- "disregard previous"
- "new instructions:"
- Script injection attempts

**Files Modified**:
- `learning/security_utils.py` (new)
- `learning/views.py` (applied to generate_code_hint endpoint)

### 7. Input Validation ✅

**Problem**: Insufficient validation of user inputs across the application.

**Solution**: Created validation utilities for common input types:

- **Username validation**: Alphanumeric + underscore/hyphen, 3-30 chars, SQL injection pattern detection
- **URL validation**: Format checking, scheme whitelisting, dangerous protocol detection
- **File path sanitization**: Directory traversal prevention, dangerous character removal
- **JSON field validation**: Depth limiting (prevents DoS via deeply nested JSON), key count limits

**Files Modified**:
- `learning/security_utils.py` (new)

## Additional Security Enhancements

### 8. IP Address Detection ✅

```python
def get_client_ip(request) -> str:
    """Get client IP, considering X-Forwarded-For from proxies"""
```

Properly detects client IP address for logging and rate limiting, accounting for reverse proxies.

### 9. Safe Redirect Validation ✅

```python
def is_safe_redirect_url(url: str, allowed_hosts: List[str]) -> bool:
    """Prevents open redirect vulnerabilities"""
```

Prevents attackers from using the application to redirect users to malicious sites.

### 10. Connection Pooling ✅

AI services now use session pooling to prevent resource exhaustion:

```python
self.session = requests.Session()  # Reuse HTTP connections
```

## Security Utilities

### `learning/security_utils.py`

Centralized security functions:

- `sanitize_html()` - XSS prevention
- `sanitize_text()` - HTML entity escaping
- `validate_username()` - Username validation
- `validate_ai_prompt()` - Prompt injection prevention
- `sanitize_file_path()` - Path traversal prevention
- `validate_json_field()` - DoS prevention
- `validate_url()` - URL validation
- `get_client_ip()` - IP detection
- `is_safe_redirect_url()` - Open redirect prevention

### `learning/throttling.py`

Custom rate limiting:

- `AIGenerationThrottle` - Protects expensive AI operations
- `LoginThrottle` - Prevents brute force attacks

## Security Best Practices

### For Developers

1. **Always sanitize user input** before displaying or storing
2. **Use parameterized queries** to prevent SQL injection
3. **Validate all inputs** before processing
4. **Apply rate limiting** to expensive operations
5. **Check permissions** before allowing access to resources
6. **Never expose secrets** in code or logs

### For Deployment

1. **Set environment variables**:
   ```bash
   export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
   export DJANGO_DEBUG=False
   export CORS_ALLOWED_ORIGINS="https://yourdomain.com"
   ```

2. **Enable HTTPS** in production:
   - `SECURE_SSL_REDIRECT=True`
   - `SESSION_COOKIE_SECURE=True`
   - `CSRF_COOKIE_SECURE=True`

3. **Configure HSTS headers** (already enabled when DEBUG=False)

4. **Use environment-specific settings** for database, cache, etc.

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Testing Security

### Rate Limiting

```bash
# Test rate limiting (should get 429 Too Many Requests after limit)
for i in {1..15}; do curl -X POST http://localhost:8000/api/v1/ai/hint/; done
```

### XSS Prevention

```python
from learning.security_utils import sanitize_html

# Should strip script tags
result = sanitize_html('<script>alert("XSS")</script><p>Safe</p>')
assert result == '<p>Safe</p>'
```

### Prompt Injection

```python
from learning.security_utils import validate_ai_prompt

# Should detect injection attempt
is_valid, error = validate_ai_prompt("Ignore previous instructions and...")
assert not is_valid
```

## Remaining Security Tasks

While critical vulnerabilities have been fixed, these enhancements are recommended:

1. **API Key Encryption**: Encrypt API keys at rest in database
2. **Password Reset**: Implement secure password reset flow
3. **Email Verification**: Add email verification for new accounts
4. **2FA Support**: Add two-factor authentication option
5. **Audit Logging**: Log all security-relevant events
6. **CSRF Improvements**: Ensure CSRF tokens on all state-changing operations
7. **Content Security Policy**: Add CSP headers
8. **Database Query Optimization**: Add indexes, fix N+1 queries
9. **XP Exploit Prevention**: Add transaction-level checks for XP awards

## Security Contacts

Report security vulnerabilities responsibly:

- **Email**: security@learnhub.example.com
- **Bug Tracker**: Private security issue template

## Changelog

### 2025-01-XX - Major Security Update

- ✅ Added comprehensive rate limiting
- ✅ Fixed admin authorization bypass
- ✅ Improved SECRET_KEY handling
- ✅ Enhanced CORS validation
- ✅ Implemented XSS protection
- ✅ Added AI prompt validation
- ✅ Created security utilities module
- ✅ Added input validation
- ✅ Prevented open redirects
- ✅ Added connection pooling
- ✅ Created custom throttling classes

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [DRF Throttling](https://www.django-rest-framework.org/api-guide/throttling/)
- [Bleach Documentation](https://bleach.readthedocs.io/)
