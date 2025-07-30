
# Identity Backend Service (JWT Issuer)

This microservice issues and verifies JWT tokens for use across the ecosystem (e.g., Logging Backend, CareerGPT).

---

## Setup

### Environment Variables
Set these in `.env` for local development or in cPanel environment variables for deployment:

```
JWT_SECRET_KEY=<strong-shared-secret>
JWT_ISSUER=identity-backend
JWT_EXPIRATION_MINUTES=15
```

- `JWT_SECRET_KEY` must be shared with services that validate tokens (e.g., logging-backend).
- `JWT_ISSUER` identifies this service.
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
2. Configure environment variables via **Setup Python App**.
3. Click **Run pip install** (or SSH: `pip install -r requirements.txt`).
4. Restart Passenger:

```
touch tmp/restart.txt
```

---

## Endpoints & Testing

### 1. Health Check

**Endpoint:** `GET /ping`

**PowerShell**
```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/ping"
```

**cURL**
```bash
curl -X GET "https://aurorahours.com/identity-backend/ping"
```

**Expected Response:**
```
OK
```

---

### 2. Generate JWT Token

**Endpoint:** `POST /token`

**Request Body Example:**
```json
{
  "sub": "careergpt-backend",
  "aud": "logging-service"
}
```

**PowerShell**
```powershell
$resp = Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/token" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"sub":"careergpt-backend","aud":"logging-service"}'

$token = $resp.token
```

**cURL**
```bash
curl -X POST "https://aurorahours.com/identity-backend/token"   -H "Content-Type: application/json"   -d '{"sub":"careergpt-backend","aud":"logging-service"}'
```

---

### 3. Verify JWT Token

**Endpoint:** `POST /verify`

**Request Body Example:**
```json
{
  "token": "<jwt_here>",
  "aud": "logging-service"
}
```

**PowerShell**
```powershell
Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/verify" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body (@{ token = $token; aud = "logging-service" } | ConvertTo-Json)
```

**cURL**
```bash
curl -X POST "https://aurorahours.com/identity-backend/verify"   -H "Content-Type: application/json"   -d '{"token":"<jwt_here>","aud":"logging-service"}'
```

---

### 4. Combined PowerShell Example: Generate Token & Write to Log

```powershell
# Step 1: Generate JWT
$resp = Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/token" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"sub":"careergpt-backend","aud":"logging-service"}'

$token = $resp.token

# Step 2: Use JWT to write log to logging-backend
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/log" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} `
  -Body '{"service":"careergpt","level":"INFO","message":"Log test via combined PS flow","context":{"user":"saad"}}'
```

---

### 5. Combined PowerShell Example: Generate Token, Write Log & Read Logs

```powershell
# Step 1: Generate JWT
$resp = Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/token" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"sub":"careergpt-backend","aud":"logging-service"}'

$token = $resp.token

# Step 2: Write a log
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/log" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} `
  -Body '{"service":"careergpt","level":"INFO","message":"Testing full flow write","context":{"user":"saad"}}'

# Step 3: Read back logs
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/logs" `
  -Headers @{Authorization = "Bearer $token"}
```

---

## Integration Notes

- `identity-backend` issues JWTs for **service-to-service** and **user-to-service** auth flows.
- `logging-backend` uses this token to validate API calls.
- Ensure `JWT_SECRET_KEY` is the same across all services.

---

## Common Issues / Debugging

- **Invalid audience**: Ensure `aud` in token request matches the target service (e.g., `logging-service`).
- **Expired token**: Request a fresh token via `/token`.
- **Invalid issuer**: Ensure `JWT_ISSUER` matches across services.

---

### Make sure secrets match

```bash
Invoke-RestMethod -Uri "https://aurorahours.com/identity-backend/debug-env"
```

```bash
Invoke-RestMethod -Uri "https://aurorahours.com/logging-backend/debug-env"
```

---

## Coordinated Release Instructions

To ensure `identity-backend` and `logging-backend` are compatible during deployment:

1. Update both repos to use the same `JWT_SECRET_KEY` and `JWT_ISSUER`.
2. Tag each repo with the same release version (e.g., `v1.0.0`):
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. Deploy both services together to avoid mismatched secrets.

### Checking Out Matching Versions
```bash
git clone https://github.com/<your-org>/identity-backend.git
cd identity-backend
git checkout v1.0.0
```

```bash
git clone https://github.com/<your-org>/logging-backend.git
cd logging-backend
git checkout v1.0.0
```

---

## Notes

- JWTs expire based on settings in `identity-backend` (default 15 min).
- `JWT_SECRET_KEY` must match between identity and logging services.
- SQLite is used for simplicity; migrate to MySQL/Postgres for production.

### Environment Variables
Set the same JWT_SECRET_KEY and JWT_ISSUER in both services:
```bash
JWT_SECRET_KEY=your_shared_secret
JWT_ISSUER=identity-backend
```