import sys
import requests, logging, jwt, datetime
from config import (
    JWT_SECRET_KEY,
    JWT_ISSUER,
    LOGGING_BACKEND_URL,
    LOGGING_BACKEND_AUD,
    IDENTITY_SUB,
    DEV_MODE
)

logger = logging.getLogger("identity-logger")
logger.setLevel(logging.DEBUG if DEV_MODE else logging.INFO)

# Avoid duplicate handlers (e.g. Flask auto-reload)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_to_stderr(level: str, message: str, context=None):
    if context:
        message += f" | Context: {context}"
    level = level.upper()
    log_fn = getattr(logger, level.lower(), logger.info)
    log_fn(message)

def log_to_logging_service(level: str, message: str, context=None):
    """Send log to centralized logging backend using JWT."""
    try:
        now = datetime.datetime.utcnow()
        payload = {
            "iss": JWT_ISSUER,
            "sub": IDENTITY_SUB,
            "aud": LOGGING_BACKEND_AUD,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=5)
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {
            "service": IDENTITY_SUB,
            "level": level.upper(),
            "message": message,
            "context": context
        }

        response = requests.post(LOGGING_BACKEND_URL+'/log', headers=headers, json=data, timeout=5)
        if response.status_code >= 400:
            logger.warning(f"Central logging failed: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Exception during logging to backend: {e}", exc_info=True)

def unified_log(level: str, message: str, context=None):
    """Log to both stderr and central backend (in production)."""
    log_to_stderr(level, message, context)
    #if not DEV_MODE:
    #    
    log_to_logging_service(level, message, context)