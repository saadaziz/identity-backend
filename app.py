# todo - production ready checklist:
# - Dev-Only Endpoints Exposed in Production

from flask import Flask, request, redirect, render_template, session, jsonify, url_for
import jwt
import datetime
import uuid
from urllib.parse import urlencode
from config import (
    JWT_SECRET_KEY,
    JWT_ISSUER,
    JWT_EXPIRATION_MINUTES,
    ALLOWED_CLIENTS,
    CLIENT_SECRETS,
    ALLOWED_REDIRECT_URIS,
    DEMO_USERNAME,
    DEMO_PASSWORD,
    FLASK_SECRET_KEY,
    DEV_MODE
)
from logger_utils import unified_log
import sqlite3
import os
    
AUTH_CODE_DB = "authcodes.db"
print("Using auth code DB at:", os.path.abspath(AUTH_CODE_DB))  


def init_code_db():
    with sqlite3.connect(AUTH_CODE_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS codes (
                code TEXT PRIMARY KEY,
                username TEXT,
                client_id TEXT,
                scope TEXT,
                issued_at TIMESTAMP
            )
        """)
        print("Table 'codes' ensured in", AUTH_CODE_DB)  

init_code_db()  # <- OUTSIDE __main__, so always runs

app = Flask(__name__)

app.secret_key = FLASK_SECRET_KEY

# Demo credentials ------- |  MVP todo  | -------- #
USERNAME = DEMO_USERNAME
PASSWORD = DEMO_PASSWORD
unified_log("INFO", f"/username={USERNAME}, password=****")

# Enforce zero defaults in prod, add a fail-fast pattern:
def must_getenv(name):
    val = os.getenv(name)
    if not val:
        raise Exception(f"{name} not set in environment!")
    return val

JWT_SECRET_KEY = must_getenv("JWT_SECRET_KEY")

@app.route("/authorize")
def authorize():
    client_id = request.args.get("client_id")
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state", "")
    scope = request.args.get("scope", "")

    if not client_id or client_id not in ALLOWED_CLIENTS:
        unified_log("WARN", f"/authorize rejected invalid client_id: {client_id}")
        return "Invalid client_id", 400
    if not redirect_uri or not any(redirect_uri.startswith(uri) for uri in ALLOWED_REDIRECT_URIS):
        unified_log("WARN", f"/authorize rejected invalid redirect_uri: {redirect_uri} for client {client_id}")
        return "Invalid redirect_uri", 400

    # Save params for login step (use Flask session, not secure for prod)
    session["client_id"] = client_id
    session["redirect_uri"] = redirect_uri
    session["state"] = state
    session["scope"] = scope

    unified_log("INFO", f"/authorize started for client_id={client_id}, state={state}")
    return render_template("login.html", error=None, state=state)

@app.route("/login", methods=["POST"])
def handle_login():
    username = request.form.get("username")
    password = request.form.get("password")
    print(f"USERNAME='{USERNAME}'", flush=True)
    print(f"PASSWORD='{PASSWORD}'", flush=True)
    print(f"USERNAME='{username}'", flush=True)
    print(f"PASSWORD='{password}'", flush=True)
    state = request.form.get("state", "")
    client_id = session.get("client_id")
    redirect_uri = session.get("redirect_uri")
    scope = session.get("scope", "")

    if username == USERNAME and password == PASSWORD:
        auth_code = str(uuid.uuid4())
        with sqlite3.connect(AUTH_CODE_DB) as conn:
            conn.execute(
                "INSERT INTO codes (code, username, client_id, scope, issued_at) VALUES (?, ?, ?, ?, ?)",
                (auth_code, username, client_id, scope, datetime.datetime.utcnow())
            )

        unified_log("INFO", f"User '{username}' authenticated, auth_code issued {auth_code}, state={state}")

        params = {"code": auth_code}
        if state:
            params["state"] = state

        return redirect(f"{redirect_uri}?{urlencode(params)}")
    else:
        error = "Invalid username or password"
        unified_log("WARN", f"Login failed for username={username}, client_id={client_id}")
        return render_template("login.html", error=error, state=state)

@app.route("/token", methods=["POST"])
def token():
    code = request.form.get("code")
    client_id = request.form.get("client_id")
    client_secret = request.form.get("client_secret")
    redirect_uri = request.form.get("redirect_uri")

    if not client_id or client_id not in ALLOWED_CLIENTS:
        unified_log("WARN", f"/token rejected: invalid client_id {client_id}")
        return jsonify({"error": "Invalid client_id"}), 400
    if CLIENT_SECRETS.get(client_id) != client_secret:
        unified_log("WARN", f"/token rejected: invalid client_secret for {client_id}")
        return jsonify({"error": "Invalid client_secret"}), 401
    if not redirect_uri or not any(redirect_uri.startswith(uri) for uri in ALLOWED_REDIRECT_URIS):
        unified_log("WARN", f"/token rejected: invalid redirect_uri {redirect_uri} for client {client_id}")
        return jsonify({"error": "Invalid redirect_uri"}), 400

    with sqlite3.connect(AUTH_CODE_DB) as conn:
        cur = conn.execute("SELECT username, client_id, scope FROM codes WHERE code=?", (code,))
        row = cur.fetchone()
        if not row:
            unified_log("WARN", f"/token rejected: invalid or expired code {code} for client {client_id}")
            return jsonify({"error": "Invalid or expired code"}), 400

        # Enforce single use: delete code from db
        conn.execute("DELETE FROM codes WHERE code=?", (code,))

        db_username, db_client_id, db_scope = row
        if db_client_id != client_id:
            unified_log("WARN", f"/token client_id mismatch for code {code}: got {client_id}, expected {db_client_id}")
            return jsonify({"error": "client_id mismatch"}), 400

    now = datetime.datetime.utcnow()
    payload = {
        "iss": JWT_ISSUER,
        "sub": db_username,
        "aud": client_id,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES),
        "scope": db_scope or "",
    }
    id_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    unified_log("INFO", f"Issued id_token for user={payload['sub']} client_id={client_id} exp={payload['exp']}")

    response = {
        "id_token": id_token,
        "token_type": "Bearer",
        "expires_in": JWT_EXPIRATION_MINUTES * 60
    }
    return jsonify(response)

@app.route("/.well-known/openid-configuration")
def openid_config():
    base = request.host_url.rstrip("/")
    return jsonify({
        "issuer": JWT_ISSUER,
        "authorization_endpoint": base + url_for("authorize"),
        "token_endpoint": base + url_for("token"),
        "jwks_uri": base + "/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["HS256"],
    })

@app.route("/logout")
def logout():
    session.clear()
    unified_log("INFO", "User session cleared via logout")
    return "Logged out. <a href='/authorize'>Login again</a>", 200

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(force=True)
    token = data.get("token")
    aud = data.get("aud")

    if not token:
        unified_log("WARN", "/verify missing token")
        return jsonify({"error": "Missing token"}), 400

    try:
        # Validate the JWT
        options = {"verify_aud": bool(aud)}
        decoded = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=["HS256"],
            audience=aud,
            issuer=JWT_ISSUER,
            options=options,
        )
        unified_log("INFO", f"/verify success for sub={decoded.get('sub')}, aud={decoded.get('aud')}")
        return jsonify({"valid": True, "claims": decoded})
    except jwt.ExpiredSignatureError:
        unified_log("WARN", "/verify failed: token expired")
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidAudienceError:
        unified_log("WARN", "/verify failed: invalid audience")
        return jsonify({"valid": False, "error": "Invalid audience"}), 401
    except jwt.InvalidIssuerError:
        unified_log("WARN", "/verify failed: invalid issuer")
        return jsonify({"valid": False, "error": "Invalid issuer"}), 401
    except jwt.InvalidTokenError as e:
        unified_log("WARN", f"/verify failed: invalid token ({e})")
        return jsonify({"valid": False, "error": "Invalid token"}), 401



# Do not deploy the following to production - MVP todo ------ #
@app.route("/test-token")
def test_token():

    now = datetime.datetime.utcnow()
    payload = {
        "iss": JWT_ISSUER,
        "sub": "testuser",
        "aud": "logging-service",
        "iat": now,
        "exp": now + datetime.timedelta(minutes=30),
        "scope": "openid"
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return jsonify({"id_token": token})

@app.route("/ping")
def ping():
    return "OK", 200

if not DEV_MODE:
    # Remove or don't register dev/test routes
    app.view_functions.pop('test_token', None)
    #app.view_functions.pop('debug_env', None)
    
if __name__ == "__main__":
    print("Using auth code DB at:", os.path.abspath(AUTH_CODE_DB))
    init_code_db()
    app.run(port=5002, debug=True)
