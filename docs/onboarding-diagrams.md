# 🔐 Identity System Architecture (Echo Platform)

## 📦 Container Diagram – Entire Echo Platform

![System Context Diagram](https://aurorahours.com/images/ContainerDiagram–EntireEchoPlatform.png)

```plantuml
@startuml
!theme spacelab
node "User" as User
node "Browser UI" as UI

node "API Gateway" {
  [Flask Server]
}

node "identity-backend" {
  [OIDC Engine]
  [JWT Issuer]
  [SQLite - Auth Codes]
}

node "logging-service"
node "parser-service"
node "worker"

User --> UI : Uses Web App
UI --> [Flask Server] : Auth / Upload / Query
[Flask Server] --> [OIDC Engine] : OIDC Login
[Flask Server] --> "parser-service" : Uploads document
"worker" --> "parser-service" : Triggers parse
"worker" --> [Flask Server] : Updates job status
All --> "logging-service" : POST /log
@enduml

```

## 🌐 System Context Diagram

![System Context Diagram](https://aurorahours.com/images/Identity-system-context.png)

```plantuml
@startuml system_context
!theme spacelab
actor User
package "Echo Platform" {
    [Browser Client (API Gateway)] as Browser
    [identity-backend] as IDP
    [logging-backend] as Logging
    [careergpt-backend] as CareerGPT
}
User --> Browser : Uses web app
Browser --> IDP : OIDC login / SSO
IDP --> Browser : JWT ID Token
Browser --> Logging : API calls with JWT
Browser --> CareerGPT : API calls with JWT
Logging --> IDP : Verify JWT
CareerGPT --> IDP : Verify JWT
@enduml
```

---

## 🔁 OAuth2 / OIDC Authorization Code Flow

![OAuth2 / OIDC Authorization Code Flow](https://aurorahours.com/images/identity-oauth2-oidc-authz-code-flow.png)

```plantuml
@startuml auth_flow
actor User as U
participant "Browser (Client App)\n(API Gateway)" as C
participant "Identity Service\n(identity-backend)" as I

== User initiates protected action ==

U -> C : Request protected resource
C -> C : Check session
alt No JWT
    C -> I : GET /authorize?client_id=...&redirect_uri=...
    I -> U : Login form
    U -> I : POST credentials
    I -> C : Redirect with code
    C -> I : POST /token (exchange code)
    I -> C : Return id_token (JWT)
    C -> C : Store in session
end
C -> U : Serve requested resource
@enduml
```

---

## 🔄 Service-to-Service Auth Flow

![Service-to-Service Auth Flow](https://aurorahours.com/images/identity-service-to-service.png)

```plantuml
@startuml s2s_jwt
participant "Worker Service" as Worker
participant "Logging Service" as LogSvc

Worker -> Worker : Create JWT (sub, aud, exp)
Worker -> LogSvc : POST /log w/ Bearer <JWT>
LogSvc -> LogSvc : Verify JWT
alt Valid
    LogSvc -> LogSvc : Save log entry
    LogSvc -> Worker : 200 OK
else Invalid
    LogSvc -> Worker : 401 Unauthorized
end
@enduml
```

---

## 🗃️ Auth Code Table Schema


![[Auth Code Table Schema]](https://aurorahours.com/images/identity-codes-schema.png)

```plantuml
@startuml auth_code_db
entity "codes" as codes {
  * code : TEXT [PK]
  --
  username : TEXT
  client_id : TEXT
  scope : TEXT
  issued_at : TIMESTAMP
}
@enduml
```

---

## ✅ Component Diagram – Flask API (Portable Version)

![Component Diagram – Flask API (Portable Version)](https://aurorahours.com/images/identity-flask-flow.png)

```plantuml
@startuml

' Grouping the main Flask API components
package "Flask API (Python Flask)" {
  
  rectangle "/authorize\nRoute\nStarts login\n• Validates client_id\n• Saves params to session\n• Renders login page" as Authorize

  rectangle "/login\nRoute\nHandles form POST\n• Checks credentials\n• Issues auth code\n• Stores in SQLite\n• Redirects with code" as Login

  rectangle "/token\nRoute\nExchanges code for JWT\n• Validates code/client\n• Deletes code from DB (single-use)\n• Issues JWT via PyJWT" as Token

  rectangle "/verify\nRoute\nVerifies JWTs\n• Decodes with PyJWT\n• Validates exp, iss, aud\n• Returns decoded claims" as Verify
}

' Define flow between routes
Authorize --> Login : Handles login form
Login --> Token : Redirects with code
Token --> Verify : Issues JWT
@enduml
```
---

## 💡 Deployment Notes

- Reverse proxy assumed (cPanel Passenger WSGI or NGINX)
- All secrets via env vars (no `.env` in production)
- Stateless JWT architecture: horizontally scalable
- Logging centralized to `/log` endpoint

---
MIT (c) 2025 Saad Aziz and partners
