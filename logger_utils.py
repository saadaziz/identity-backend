import os
import sys
import json
import requests

LOGGING_BACKEND_URL = os.getenv("LOGGING_BACKEND_URL", "https://aurorahours.com/logging-backend/log")
LOGGING_BACKEND_AUD = "logging-service"
IDENTITY_SUB = "identity-backend"  # this service’s identifier

# For JWT auth: use same secret as identity-backend to issue token for itself
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
JWT_ISSUER = os.getenv("JWT_ISSUER", "identity-backend")


def log_to_stderr(level, message, context=None):
    """Print logs to stderr for cPanel visibility"""
    log_line = f"[{level}] {message} | Context: {context}" if context else f"[{level}] {message}"
    print(log_line, file=sys.stderr)


def log_to_logging_service(level, message, context=None):
    """Send log to logging-backend using a JWT token issued for this service"""
    try:
        # Build JWT token manually
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
