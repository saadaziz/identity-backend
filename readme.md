
# Identity Backend Service (JWT Issuer)

This microservice acts as the **JWT authority** for your ecosystem. It issues signed JWTs for other services (like the Logging Backend) to authenticate API calls.

---

## Setup

### Environment Variables

Set these in `.env` for local development, or in cPanel’s Python environment for deployment:

```
JWT_SECRET_KEY = <generate-a-strong-random-string>
JWT_ISSUER = identity-backend
JWT_EXPIRATION_MINUTES = 15
```

- `JWT_SECRET_KEY` must be **shared with other services** that validate JWTs.
- `JWT_ISSUER` identifies this service as the token authority.
- `JWT_EXPIRATION_MINUTES` sets token lifespan (default 15 minutes).

---

### Requirements

Install dependencies:

```
pip install -r requirements.txt
```

Dependencies include:
- Flask
- PyJWT
- python-dotenv

---

### Deployment (cPanel)

1. Upload code to `/identity-backend`.
2. Configure environment variables in **Setup Python App**.
3. Click **Run pip install** (or SSH: `pip install -r requirements.txt`).
4. Restart Passenger:
```
touch tmp/restart.txt
```

---

## Endpoints

### Health Check
```
GET /ping
```
Returns `OK` to confirm the service is running.

---

### Generate JWT Token
```
POST /token
```

#### Request Body
```json
{
  "sub": "careergpt-backend",
  "aud": "logging-service"
}
```

- `sub`: The subject (who the token is for, e.g., `careergpt-backend`).
- `aud`: The audience (who the token is intended for, e.g., `logging-service`).

#### PowerShell Example

```powershell
$resp = Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/token" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"sub":"careergpt-backend","aud":"logging-service"}'

$token = $resp.token
```

---

### Verify JWT Token
```
POST /verify
```

#### Request Body
```json
{
  "token": "<jwt_here>",
  "aud": "logging-service"
}
```

#### Response
```json
{
  "valid": true,
  "claims": {
    "iss": "identity-backend",
    "sub": "careergpt-backend",
    "aud": "logging-service",
    "iat": 1691234567,
    "exp": 1691235467
  }
}
```

---

## Integration with Logging Backend

1. Obtain a token from `identity-backend` using `/token`.
2. Pass that token to `logging-backend` endpoints in the `Authorization` header:

```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/logs" `
  -Headers @{Authorization = "Bearer $token"}
```

---

## Notes

- Tokens are signed with `HS256` (HMAC) using `JWT_SECRET_KEY`.
- All microservices validating tokens must use the **same secret**.
- For production, rotate secrets periodically and use secure storage (e.g., cPanel environment variables).
