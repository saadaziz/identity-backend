import os
from dotenv import load_dotenv

load_dotenv()

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

def get_required_env(key):
    val = os.getenv(key)
    if DEV_MODE:
        return val  # In dev, accept whatever's set (even if None or a placeholder)
    if not val or val.startswith("<") or "secret" in val:
        raise Exception(f"{key} not set or still uses a placeholder!")
    return val

FLASK_SECRET_KEY = get_required_env("FLASK_SECRET_KEY")
JWT_SECRET_KEY = get_required_env("JWT_SECRET_KEY")
JWT_ISSUER = get_required_env("JWT_ISSUER")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 15))
LOGGING_BACKEND_URL = get_required_env("LOGGING_BACKEND_URL")
LOGGING_BACKEND_AUD = get_required_env("LOGGING_BACKEND_AUD")
IDENTITY_SUB = get_required_env("IDENTITY_SUB")
ALLOWED_REDIRECT_URIS = [
    "http://localhost:5000/callback"
]
ALLOWED_CLIENTS = ["browser-ui"]
CLIENT_SECRETS = {
    "browser-ui": get_required_env("BROWSER_UI_CLIENT_SECRET")
}
DEMO_USERNAME = get_required_env("DEMO_USERNAME")
DEMO_PASSWORD = get_required_env("DEMO_PASSWORD")
