# 🛠️ Maintenance – Identity Backend

Routine operational tasks to keep the identity-backend secure, stable, and performant.

---

## 🔁 Secret Rotation

- Rotate `JWT_SECRET_KEY` and `FLASK_SECRET_KEY` periodically.
- Update them via your environment manager (e.g., cPanel).
- Restart the Python app via UI or CLI.

## 🧹 Auth Code Cleanup

- Auth codes stored in SQLite have no TTL.
- They are single-use and deleted during `/token` exchange.
- Optionally, add a cron job to delete codes older than 5 minutes.

## 🛡️ Production Hardening Checklist

- [ ] `DEV_MODE=false`
- [ ] `/test-token` route disabled
- [ ] `/logs` and `/verify` are secured or rate-limited
- [ ] HTTPS enforced via proxy

## 🧪 Health Check

- `/ping` returns 200 OK and is safe for uptime monitoring tools.

## 🧾 Logs

- Logs are streamed to `/log` with JWT auth.
- Local fallback: stderr + rotating file log (default `app.log`).
- Periodically archive or rotate large logs.

---

MIT (c) 2025 Saad Aziz and partners