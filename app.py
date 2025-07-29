from flask import Flask, request, jsonify
import jwt
import datetime
import sys
from config import JWT_SECRET_KEY, JWT_ISSUER, JWT_EXPIRATION_MINUTES

app = Flask(__name__)

# Log startup values
print(f"[DEBUG] JWT_SECRET_KEY loaded: {JWT_SECRET_KEY}", file=sys.stderr)
print(f"[DEBUG] JWT_ISSUER: {JWT_ISSUER}", file=sys.stderr)
print(f"[DEBUG] JWT_EXPIRATION_MINUTES: {JWT_EXPIRATION_MINUTES}", file=sys.stderr)

@app.route("/token", methods=["POST"])
def generate_token():
    try:
        data = request.get_json()

        if not data or "sub" not in data or "aud" not in data:
            print("[DEBUG] Missing sub/aud in request body", file=sys.stderr)
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
        print(f"[DEBUG] Token generated for sub={data['sub']} aud={data['aud']}", file=sys.stderr)
        return jsonify({"token": token})

    except Exception as e:
        print(f"[ERROR] Exception in /token: {e}", file=sys.stderr)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route("/verify", methods=["POST"])
def verify_token():
    try:
        data = request.get_json()
        token = data.get("token")

        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], audience=data.get("aud"))
        return jsonify({"valid": True, "claims": decoded})
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"valid": False, "error": str(e)}), 401
    except Exception as e:
        print(f"[ERROR] Exception in /verify: {e}", file=sys.stderr)
        return jsonify({"valid": False, "error": str(e)}), 500

@app.route("/ping")
def ping():
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5002)
