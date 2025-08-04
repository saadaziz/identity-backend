# 📊 Logging Integration for identity-backend

identity-backend logs events locally and remotely via JWT-authenticated POSTs to a central logging service.

---

## 🧾 How it Works

- All important events (auth attempts, token issues, errors) are logged via `unified_log()` in `logger_utils.py`.
- It logs to:
  - stderr (visible in cPanel logs)
  - remote service (`LOGGING_BACKEND_URL`) via signed JWT

---

## 🔐 Log Request Format

```json
POST /log
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "service": "identity-backend",
  "level": "INFO",
  "message": "User 'alice' authenticated",
  "context": "optional string or object"
}
```

---

## 🔄 JWT Claims for Logging

| Claim | Description         |
|-------|---------------------|
| `iss` | Must match `JWT_ISSUER` |
| `sub` | `identity-backend` |
| `aud` | Must match `LOGGING_BACKEND_AUD` |
| `exp` | Short-lived (5 mins max) |

---

## 💡 Notes

- In dev mode, failed logs are printed to stderr.
- Tokens are generated at runtime with PyJWT and 5-minute expiration.
- No logs are sent if `LOGGING_BACKEND_URL` is unset.

---

MIT (c) 2025 Saad Aziz and partners