import sys
import json
import requests
from config import (
    JWT_SECRET_KEY,
    JWT_ISSUER,
    LOGGING_BACKEND_URL,
    LOGGING_BACKEND_AUD,
    IDENTITY_SUB,
)

def log_to_stderr(level, message, context=None):
    """Print logs to stderr for cPanel visibility"""
    log_line = f"[{level}] {message} | Context: {context}" if context else f"[{level}] {message}"
    print(log_line, file=sys.stderr)

def log_to_logging_service(level, message, context=None):
    """Send log to logging-backend using a JWT token issued for this service"""
    try:
        import jwt, datetime
        now = datetime.datetime.utcnow()
        payload = {
            "iss": JWT_ISSUER,
            "sub": IDENTITY_SUB,
            "aud": LOGGING_BACKEND_AUD,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=5)  # short-lived
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {
            "service": IDENTITY_SUB,
            "level": level,
            "message": message,
            "context": context
        }

        response = requests.post(LOGGING_BACKEND_URL, headers=headers, json=data)
        if response.status_code >= 400:
            print(f"[WARN] Failed to log to logging-backend: {response.status_code} {response.text}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Exception while logging to logging-backend: {e}", file=sys.stderr)

def unified_log(level, message, context=None):
    """Convenience: log to both stderr and logging-backend"""
    log_to_stderr(level, message, context)
    log_to_logging_service(level, message, context)
