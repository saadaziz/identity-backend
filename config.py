import os
from dotenv import load_dotenv

# Load .env if available (local dev)
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")  # Only for signing at the IDP!
JWT_ISSUER = os.getenv("JWT_ISSUER", "https://aurorahours.com/identity-backend")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 15))

# Where the IDP is allowed to redirect back with ?code=
ALLOWED_REDIRECT_URIS = [
    "http://localhost:5000/callback"
]

# Registered OIDC/OAuth clients
ALLOWED_CLIENTS = ["browser-ui"]
CLIENT_SECRETS = {
    "browser-ui": os.getenv("BROWSER_UI_CLIENT_SECRET", "dev-client-secret")
}