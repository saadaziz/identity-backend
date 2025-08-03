import os
from dotenv import load_dotenv

# Load .env if available (local dev)
load_dotenv()

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default")  
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-default")  # Only for signing at the IDP!
JWT_ISSUER = os.getenv("JWT_ISSUER", "https://aurorahours.com/identity-backend")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 15))
LOGGING_BACKEND_URL = os.getenv("LOGGING_BACKEND_URL", "https://aurorahours.com/logging-backend/log")
LOGGING_BACKEND_AUD = os.getenv("LOGGING_BACKEND_AUD", "logging-service")
IDENTITY_SUB = os.getenv("IDENTITY_SUB", "identity-backend")

# Where the IDP is allowed to redirect back with ?code=
ALLOWED_REDIRECT_URIS = [
    "http://localhost:5000/callback"
]

# Registered OIDC/OAuth clients
ALLOWED_CLIENTS = ["browser-ui"]
CLIENT_SECRETS = {
    "browser-ui": os.getenv("BROWSER_UI_CLIENT_SECRET", "dev-client-secret-default")
}
DEMO_USERNAME = os.getenv("DEMO_USERNAME", "default")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "default")
DEV_MODE = os.environ.get("DEV_MODE", "false").lower() == "true"
