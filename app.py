from flask import Flask, request, jsonify, render_template, redirect, make_response
import jwt
import datetime
from config import JWT_SECRET_KEY, JWT_ISSUER, JWT_EXPIRATION_MINUTES, ALLOWED_REDIRECT_URIS
from logger_utils import unified_log
from urllib.parse import urlparse, urlencode, parse_qs

app = Flask(__name__)

# Log startup
unified_log("INFO", f"Identity service starting with issuer={JWT_ISSUER}", None)

def is_allowed_redirect(url):
    # Must match a prefix in allowed list
    for allowed in ALLOWED_REDIRECT_URIS:
        if url.startswith(allowed):
            return True
    return False

@app.route("/token", methods=["POST"])
def generate_token():
    try:
        data = request.get_json()
        if not data or "sub" not in data or "aud" not in data:
            unified_log("ERROR", "Missing sub/aud in token request", data)
            return jsonify({"error": "Missing required claims (sub, aud)"}), 400

        now = datetime.datetime.utcnow()
        payload = {
            "iss": JWT_ISSUER,
            "sub": data["sub"],
            "aud": data["aud"],
            "iat": now,
            "exp": now + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
        unified_log("INFO", f"Token generated for sub={data['sub']} aud={data['aud']}")
        return jsonify({"token": token})

    except Exception as e:
        unified_log("ERROR", f"Exception in /token: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/verify", methods=["POST"])
def verify_token():
    try:
        data = request.get_json()
        token = data.get("token")
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], audience=data.get("aud"))
        unified_log("INFO", "Token verification successful", {"claims": decoded})
        return jsonify({"valid": True, "claims": decoded})
    except jwt.ExpiredSignatureError:
        unified_log("WARNING", "Token expired", data)
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError as e:
        unified_log("ERROR", f"Invalid token: {e}", data)
        return jsonify({"valid": False, "error": str(e)}), 401
    except Exception as e:
        unified_log("ERROR", f"Exception in /verify: {e}", data)
        return jsonify({"valid": False, "error": str(e)}), 500

@app.route("/ping")
def ping():
    unified_log("INFO", "Ping called")
    return "OK", 200

@app.route("/debug-env")
def debug_env():
    import os
    return {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
        "JWT_ISSUER": os.getenv("JWT_ISSUER")
    }

# Hardcoded creds for now
USERNAME = "username"
PASSWORD = "password"

@app.route("/login", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == USERNAME and password == PASSWORD:
            # Generate a JWT token for browser demo use
            import datetime, jwt
            now = datetime.datetime.utcnow()
            payload = {
                "iss": JWT_ISSUER,
                "sub": username,
                "aud": "browser-ui",
                "iat": now,
                "exp": now + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
            unified_log("INFO", f"User {username} logged in (web UI)", {"sub": username})
            # Return a cookie for future API calls, or just display it for copy/paste demo
            resp = make_response(render_template("login.html", token=token))
            resp.set_cookie("id_token", token, httponly=True)
            return resp
        else:
            error = "Invalid username or password"
            unified_log("WARNING", "Login failed for web UI", {"username": username})
    return render_template("login.html", error=error)

if __name__ == "__main__":
    app.run(port=5002)
