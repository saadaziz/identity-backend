# ⚙️ Configuration Guide for Echo Identity System

This guide covers all configuration steps for running the `identity-backend` securely and correctly.

---

## 🔐 Required Environment Variables

Set these using your environment manager (e.g. cPanel, systemd, or `.env` file in development):

| Variable                  | Purpose                              | Example Value                                      |
|---------------------------|--------------------------------------|---------------------------------------------------|
| `FLASK_SECRET_KEY`        | Flask session encryption             | (use `secrets.token_urlsafe(32)`)                 |
| `JWT_SECRET_KEY`          | JWT signing key                      | (use `secrets.token_urlsafe(64)`)                 |
| `JWT_ISSUER`              | OIDC issuer URL                      | `https://yourdomain.com/identity-backend`         |
| `JWT_EXPIRATION_MINUTES` | Token lifetime (minutes)             | `15`                                              |
| `DEMO_USERNAME`           | Dev login username                   | `admin`                                           |
| `DEMO_PASSWORD`           | Dev login password                   | `password`                                        |
| `BROWSER_UI_CLIENT_SECRET`| Client secret for browser            | `dev-client-secret`                               |
| `LOGGING_BACKEND_URL`     | Central log POST endpoint            | `https://yourdomain.com/logging-backend/log`      |
| `LOGGING_BACKEND_AUD`     | Expected audience in JWTs            | `logging-service`                                 |
| `IDENTITY_SUB`            | JWT `sub` claim for this service     | `identity-backend`                                |
| `ALLOWED_REDIRECT_URIS`   | Comma-separated list of redirect URIs| `http://localhost:5000/callback`                  |

---

## 🛠 How to Generate Secrets

Use Python’s `secrets` module:

```bash
# Flask secret (for session cookies)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# JWT secret (for signing tokens)
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the output and use it as environment values in your deployment setup.

---

## 🧪 Local Development

1. Create a `.env` file in the project root:

```
FLASK_SECRET_KEY=your_flask_secret
JWT_SECRET_KEY=your_jwt_secret
JWT_ISSUER=http://localhost:5002
JWT_EXPIRATION_MINUTES=15
DEMO_USERNAME=admin
DEMO_PASSWORD=password
BROWSER_UI_CLIENT_SECRET=dev-client-secret
LOGGING_BACKEND_URL=http://localhost:5020/log
LOGGING_BACKEND_AUD=logging-service
IDENTITY_SUB=identity-backend
ALLOWED_REDIRECT_URIS=http://localhost:5000/callback
```

2. Ensure `python-dotenv` is installed and loaded at startup.
3. Never commit `.env` to source control.

---

## 🚀 Production Deployment Notes

- Set all env vars using **cPanel’s Python App UI**, **systemd**, or a **secrets manager**.
- Ensure `DEV_MODE=false`
- Restart your app after setting/changing env vars.
- Keep secrets out of version control.

---

MIT (c) 2025 Saad Aziz and partners