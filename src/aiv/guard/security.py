"""
aiv/guard/security.py

Security utilities for the GitHub Action.
"""

from __future__ import annotations

import html
import json
import re
from typing import Any
from urllib.parse import urlparse


def sanitize_for_shell(value: str) -> str:
    """
    Sanitize a value for safe shell usage.

    Note: Prefer avoiding shell entirely. This is a fallback.
    """
    # Remove shell metacharacters
    dangerous_chars = r'[;&|`$(){}[\]<>\'"]'
    return re.sub(dangerous_chars, '', value)


def sanitize_for_markdown(value: str) -> str:
    """Sanitize value for inclusion in markdown comments."""
    # Escape HTML entities
    value = html.escape(value)
    # Escape markdown special chars
    value = re.sub(r'([*_~`#])', r'\\\1', value)
    return value


def truncate_for_log(value: str, max_length: int = 1000) -> str:
    """Truncate long values for safe logging."""
    if len(value) <= max_length:
        return value
    return value[:max_length] + f"... [truncated, {len(value)} total chars]"


def validate_url_structure(url: str) -> bool:
    """
    Validate URL structure without network access.

    Rejects:
    - Non-HTTP(S) schemes
    - localhost/private IPs
    - Unusual ports
    """
    try:
        parsed = urlparse(url)

        # Must be HTTPS (HTTP allowed for testing)
        if parsed.scheme not in ('http', 'https'):
            return False

        # No localhost or private IPs
        hostname = parsed.hostname or ''
        if hostname in ('localhost', '127.0.0.1', '0.0.0.0'):
            return False
        if hostname.startswith('192.168.') or hostname.startswith('10.'):
            return False

        # No unusual ports
        if parsed.port and parsed.port not in (80, 443, 8080):
            return False

        return True

    except Exception:
        return False


def safe_json_loads(data: str, max_size: int = 1_000_000) -> Any:
    """Load JSON with size limit to prevent DoS."""
    if len(data) > max_size:
        raise ValueError(f"JSON exceeds max size of {max_size} bytes")

    return json.loads(data)
