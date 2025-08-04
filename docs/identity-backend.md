# 🧩 identity-backend – Overview

The `identity-backend` service is a lightweight OpenID Connect (OIDC) identity provider for issuing and verifying secure JWT tokens.

---

## 🌐 Purpose

- Provides OAuth2 Authorization Code flow with OIDC ID Tokens.
- Supports single sign-on (SSO) for frontend and service-to-service auth.
- Signs and verifies JWT tokens.
- Central point of authentication for the Echo platform.

---

## 🔐 Core Endpoints

| Route       | Method | Purpose                          |
|-------------|--------|----------------------------------|
| `/authorize`| GET    | Starts the OIDC login flow       |
| `/login`    | POST   | Authenticates user, issues code |
| `/token`    | POST   | Exchanges auth code for JWT     |
| `/verify`   | POST   | Validates JWTs (for other services) |
| `/logout`   | GET    | Clears browser session           |
| `/ping`     | GET    | Health check                     |

---

## 🧱 Tech Stack

- **Framework:** Flask (Python)
- **JWT:** PyJWT
- **Storage:** SQLite (for short-lived auth codes)
- **Logging:** JWT-authenticated HTTP POST to `/log`

---

## 🔐 Security Practices

- Auth codes are single-use and stored in `authcodes.db`
- Tokens are signed using `HS256` with short expiration
- All secrets are loaded from environment variables
- Only known `client_id` and `redirect_uri` combinations are allowed
- Production disables test and debug endpoints

---

## 🔄 Flow Summary

1. Frontend redirects to `/authorize`
2. User logs in via `/login`
3. Server redirects back with code
4. Frontend calls `/token` to get JWT
5. JWT used to access other services
6. Services verify JWT via `/verify`

---

MIT (c) 2025 Saad Aziz and partners