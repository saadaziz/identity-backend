import os
from dotenv import load_dotenv

# Load .env if available (local dev)
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")  # HMAC key for signing
JWT_ISSUER = os.getenv("JWT_ISSUER", "identity-backend")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 15))

ALLOWED_REDIRECT_URIS = [
    "http://localhost:5000/",
    "https://aurorahours.com/",
    "https://myclient.com/callback",
    "https://anotherapp.saadaziz.com/",
    # ...add others
]