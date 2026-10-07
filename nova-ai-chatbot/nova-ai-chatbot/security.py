"""Security layer: CSRF, origin checks, session hardening, headers, rate limiting, input validation."""
import os, re, time, hmac, secrets, logging
from collections import defaultdict, deque
from datetime import timedelta
from urllib.parse import urlparse
from flask import request, session, abort, jsonify, render_template

log = logging.getLogger("nova.security")

IDLE_SECONDS = 30 * 60          # sign out after 30 minutes of inactivity
ABSOLUTE_SECONDS = 8 * 60 * 60  # and never keep a login longer than 8 hours

# ---------- rate limiting ----------
_hits = defaultdict(deque)
_last_sweep = 0.0

def _sweep(now):
    """Drop stale keys so attackers cannot grow memory with random keys."""
    global _last_sweep
    if now - _last_sweep < 60 and len(_hits) < 5000: return
    _last_sweep = now
    for k in [k for k, q in _hits.items() if not q or q[-1] < now - 3600]: del _hits[k]

def hit(key, limit, window):
    """Sliding-window rate limiter. Returns False when the limit is exceeded."""
    now = time.time(); _sweep(now); q = _hits[key]
    while q and q[0] < now - window: q.popleft()
    if len(q) >= limit: return False
    q.append(now); return True

def throttled(key, limit, window):
    """True when `key` already has `limit` recorded events in the window (does not record a new one)."""
    now = time.time(); q = _hits.get(key)
    if not q: return False
    while q and q[0] < now - window: q.popleft()
    return len(q) >= limit

def record(key):
    now = time.time(); _sweep(now); _hits[key].append(now)

def reset(key):
    _hits.pop(key, None)

# ---------- validation ----------
COMMON_PASSWORDS = {
    "password", "password1", "password12", "password123", "passw0rd123", "1234567890", "12345678910",
    "qwertyuiop", "qwerty12345", "qwerty123456", "iloveyou123", "letmein1234", "welcome1234", "admin12345",
    "abc1234567", "abcd123456", "changeme123", "1q2w3e4r5t", "monkey12345", "dragon12345", "football123",
}
PASSWORD_RULE = "Password needs 10+ characters with letters and numbers."

def check_input(name, email, pw):
    if not 1 <= len(name) <= 60 or re.search(r"[\x00-\x1f\x7f<>]", name): return "Enter a valid name (1-60 characters)."
    if len(email) > 120 or not re.fullmatch(r"[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}", email): return "Enter a valid email."
    if not (10 <= len(pw) <= 128 and re.search(r"[A-Za-z]", pw) and re.search(r"\d", pw)): return PASSWORD_RULE
    low = pw.lower()
    if low in COMMON_PASSWORDS or len(set(low)) < 4: return "That password is too common. Choose a stronger one."
    local = email.split("@")[0].lower()
    if len(local) >= 4 and local in low: return "Password must not contain your email name."

# ---------- secret key ----------
def _weak(key):
    return len(key) < 32 or key.lower().startswith(("change-me", "changeme", "secret", "your-"))

def _secret():
    key = os.environ.get("SECRET_KEY", "")
    if key and not _weak(key): return key
    if key: log.warning("SECRET_KEY is a placeholder/too short; using a generated key stored in .secret_key instead.")
    path = os.path.join(os.environ.get("DATA_DIR") or os.path.dirname(os.path.abspath(__file__)), ".secret_key")
    if not os.path.exists(path):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as f: f.write(secrets.token_hex(32))
    with open(path) as f: return f.read().strip()

# ---------- sessions ----------
def login_user(uid, name):
    """Start a fresh session (prevents fixation) with a new CSRF token."""
    session.clear()
    session["uid"], session["name"] = uid, name
    session["iat"] = time.time()
    session["csrf"] = secrets.token_urlsafe(32)

# ---------- app wiring ----------
def init_security(app):
    app.secret_key = _secret()
    secure = os.environ.get("HTTPS") == "1"
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=secure,
        SESSION_COOKIE_NAME="__Host-nova" if secure else "nova_session",
        PERMANENT_SESSION_LIFETIME=timedelta(seconds=IDLE_SECONDS), MAX_CONTENT_LENGTH=16 * 1024,
        MAX_FORM_MEMORY_SIZE=16 * 1024, JSON_SORT_KEYS=False)

    if os.environ.get("TRUST_PROXY") == "1":  # only enable behind a reverse proxy you control
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    hosts = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]
    if hosts: app.config["TRUSTED_HOSTS"] = hosts

    @app.before_request
    def guard():
        now = time.time()
        if "uid" in session:
            if now - session.get("seen", now) > IDLE_SECONDS or now - session.get("iat", 0) > ABSOLUTE_SECONDS:
                session.clear()
        session["seen"] = now; session.permanent = True
        session.setdefault("csrf", secrets.token_urlsafe(32))
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = request.headers.get("Origin")
            if origin and origin != "null" and urlparse(origin).netloc != request.host: abort(403)
            if origin == "null": abort(403)
            tok = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
            if not hmac.compare_digest(tok.encode(), session["csrf"].encode()): abort(400)

    @app.context_processor
    def inject(): return {"csrf_token": session.get("csrf", "")}

    @app.after_request
    def headers(r):
        csp = ("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; "
               "object-src 'none'; frame-ancestors 'none'; form-action 'self'; base-uri 'none'")
        if secure: csp += "; upgrade-insecure-requests"
        r.headers["Content-Security-Policy"] = csp
        r.headers["X-Content-Type-Options"] = "nosniff"
        r.headers["X-Frame-Options"] = "DENY"
        r.headers["Referrer-Policy"] = "same-origin"
        r.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        r.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        r.headers["Permissions-Policy"] = "camera=(), geolocation=(), payment=(), usb=(), microphone=(self)"
        if secure: r.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if not request.path.startswith("/static"):
            r.headers["Cache-Control"] = "no-store"; r.headers["Pragma"] = "no-cache"
        r.headers.pop("Server", None)
        return r

    msgs = {400: "Request rejected by security check. Refresh the page and try again.", 403: "Forbidden",
            404: "Not found", 405: "Method not allowed", 413: "Request too large", 429: "Too many requests",
            500: "Server error"}
    def handle(code, m):
        if request.path.startswith("/api"): return jsonify(error=m), code
        return render_template("error.html", code=code, message=m), code
    for code, m in msgs.items():
        app.register_error_handler(code, lambda e, m=m, c=code: handle(c, m))
