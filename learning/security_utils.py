"""
Security utilities for input validation and sanitization.

Provides functions to prevent XSS, SQL injection, and other security vulnerabilities.
"""

import re
import html
import bleach
from typing import Any, Dict, List


# Allowed HTML tags for rich content (very restrictive by default)
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li',
    'a', 'code', 'pre', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
]

# Allowed HTML attributes
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'code': ['class'],
}

# Allowed URL protocols
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(content: str, allowed_tags: List[str] = None, allowed_attributes: Dict = None) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Uses bleach library to clean HTML while preserving safe tags.

    Args:
        content: HTML content to sanitize
        allowed_tags: List of allowed HTML tags (defaults to ALLOWED_TAGS)
        allowed_attributes: Dict of allowed attributes per tag (defaults to ALLOWED_ATTRIBUTES)

    Returns:
        str: Sanitized HTML content

    Example:
        >>> sanitize_html('<script>alert("XSS")</script><p>Safe content</p>')
        '<p>Safe content</p>'
    """
    if not content:
        return ""

    tags = allowed_tags if allowed_tags is not None else ALLOWED_TAGS
    attrs = allowed_attributes if allowed_attributes is not None else ALLOWED_ATTRIBUTES

    # Clean HTML using bleach
    cleaned = bleach.clean(
        content,
        tags=tags,
        attributes=attrs,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Remove disallowed tags entirely
    )

    return cleaned


def sanitize_text(content: str) -> str:
    """
    Sanitize plain text content by escaping HTML entities.

    Use this for user input that should be displayed as plain text.

    Args:
        content: Text content to sanitize

    Returns:
        str: HTML-escaped text

    Example:
        >>> sanitize_text('<script>alert("XSS")</script>')
        '&lt;script&gt;alert("XSS")&lt;/script&gt;'
    """
    if not content:
        return ""

    return html.escape(str(content))


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username format.

    Ensures username contains only safe characters.

    Args:
        username: Username to validate

    Returns:
        tuple: (is_valid, error_message)

    Rules:
        - 3-30 characters
        - Only letters, numbers, underscores, and hyphens
        - Must start with a letter or number
    """
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 30:
        return False, "Username must be at most 30 characters"

    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens, and must start with a letter or number"

    # Check for SQL injection patterns (paranoid check)
    dangerous_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute', 'drop', 'insert', 'update', 'delete']
    username_lower = username.lower()
    for pattern in dangerous_patterns:
        if pattern in username_lower:
            return False, "Username contains invalid characters"

    return True, ""


def validate_ai_prompt(prompt: str, max_length: int = 50000) -> tuple[bool, str]:
    """
    Validate AI prompt input.

    Prevents prompt injection and ensures reasonable length.

    Args:
        prompt: AI prompt to validate
        max_length: Maximum allowed length

    Returns:
        tuple: (is_valid, error_message)
    """
    if not prompt:
        return False, "Prompt cannot be empty"

    if not isinstance(prompt, str):
        return False, "Prompt must be a string"

    if len(prompt) > max_length:
        return False, f"Prompt exceeds maximum length of {max_length} characters"

    # Check for potential prompt injection patterns
    suspicious_patterns = [
        r'ignore\s+(previous|above|all)\s+instructions',
        r'disregard\s+(previous|above|all)',
        r'system\s*:\s*you\s+are',
        r'forget\s+(everything|all|previous)',
        r'new\s+instructions\s*:',
        r'<\s*script\s*>',  # XSS attempt
        r'javascript\s*:',  # XSS attempt
    ]

    prompt_lower = prompt.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, prompt_lower):
            return False, "Prompt contains potentially malicious content"

    return True, ""


def sanitize_file_path(file_path: str) -> str:
    """
    Sanitize file path to prevent directory traversal attacks.

    Removes dangerous characters and path traversal sequences.

    Args:
        file_path: File path to sanitize

    Returns:
        str: Sanitized file path

    Example:
        >>> sanitize_file_path('../../../etc/passwd')
        'etc/passwd'
    """
    if not file_path:
        return ""

    # Remove null bytes
    file_path = file_path.replace('\0', '')

    # Remove path traversal sequences
    file_path = file_path.replace('..', '')

    # Remove leading slashes
    file_path = file_path.lstrip('/')

    # Replace backslashes with forward slashes
    file_path = file_path.replace('\\', '/')

    # Remove duplicate slashes
    file_path = re.sub(r'/+', '/', file_path)

    # Remove dangerous characters
    file_path = re.sub(r'[<>:"|?*]', '', file_path)

    return file_path


def validate_json_field(data: Any, max_depth: int = 5, max_keys: int = 100) -> tuple[bool, str]:
    """
    Validate JSONField data to prevent DoS attacks via deeply nested structures.

    Args:
        data: JSON data to validate
        max_depth: Maximum nesting depth
        max_keys: Maximum number of keys in any object

    Returns:
        tuple: (is_valid, error_message)
    """
    def check_depth(obj, current_depth=0):
        if current_depth > max_depth:
            return False, f"JSON nesting exceeds maximum depth of {max_depth}"

        if isinstance(obj, dict):
            if len(obj) > max_keys:
                return False, f"JSON object has more than {max_keys} keys"

            for value in obj.values():
                is_valid, error = check_depth(value, current_depth + 1)
                if not is_valid:
                    return False, error

        elif isinstance(obj, list):
            if len(obj) > max_keys:
                return False, f"JSON array has more than {max_keys} items"

            for item in obj:
                is_valid, error = check_depth(item, current_depth + 1)
                if not is_valid:
                    return False, error

        return True, ""

    return check_depth(data)


def validate_url(url: str, allowed_schemes: List[str] = None) -> tuple[bool, str]:
    """
    Validate URL format and scheme.

    Args:
        url: URL to validate
        allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])

    Returns:
        tuple: (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"

    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']

    # Basic URL format check
    url_pattern = re.compile(
        r'^(?:(?:' + '|'.join(allowed_schemes) + r'):\/\/)'  # Scheme
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # Domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # Optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if not url_pattern.match(url):
        return False, "Invalid URL format"

    # Check for dangerous patterns
    dangerous_patterns = [
        'javascript:',
        'data:',
        'vbscript:',
        'file:',
    ]

    url_lower = url.lower()
    for pattern in dangerous_patterns:
        if pattern in url_lower:
            return False, f"URL scheme '{pattern}' is not allowed"

    return True, ""


# Rate limiting utilities

def get_client_ip(request) -> str:
    """
    Get client IP address from request, considering proxies.

    Args:
        request: Django HTTP request

    Returns:
        str: Client IP address
    """
    # Check for X-Forwarded-For header (from proxy)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP (client IP)
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def is_safe_redirect_url(url: str, allowed_hosts: List[str]) -> bool:
    """
    Check if redirect URL is safe (prevents open redirect vulnerabilities).

    Args:
        url: URL to check
        allowed_hosts: List of allowed host names

    Returns:
        bool: True if URL is safe to redirect to
    """
    if not url:
        return False

    # Relative URLs are safe
    if url.startswith('/') and not url.startswith('//'):
        return True

    # Check if URL is for an allowed host
    for host in allowed_hosts:
        if url.startswith(f'http://{host}') or url.startswith(f'https://{host}'):
            return True

    return False
