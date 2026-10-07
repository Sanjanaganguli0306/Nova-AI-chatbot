# Nova AI Chatbot (Flask + SQLite)

A responsive AI chatbot web app: attractive homepage, chat UI, typing animation, chat history, login/signup,
dark mode, 4 themes, voice input/output, SQLite storage and a security layer. Works offline with a built-in bot;
add a Gemini (or OpenAI) key in `.env` for real AI replies.

## Run in VS Code
1. Open this folder in VS Code (`File > Open Folder`).
2. Terminal: `python -m venv .venv`, then activate it
   (Windows `.venv\Scripts\activate`, macOS/Linux `source .venv/bin/activate`).
3. `pip install -r requirements.txt`
4. `cp .env.example .env` (Windows: `copy .env.example .env`) and edit values.
5. `python app.py` (or press F5 / use "Run Nova AI (Flask)") and open http://127.0.0.1:5000
Shortcuts: `./run.sh` (macOS/Linux), `run.bat` (Windows), `npm start` (needs Node only for the npm shortcut).
Docker: `docker build -t nova . && docker run -v nova-data:/data -p 5000:5000 --env-file .env nova`

## Structure
```
app.py              Flask routes, bot logic, SQLite access
security.py         CSRF, headers, rate limiting, validation
schema.sql / chat.db  Database schema and empty database (auto-created if missing)
templates/          base, icons (SVG sprite), controls, home, auth, chat, error (Jinja2)
static/             style.css, app.js, theme.js, img/favicon.svg, fonts/ (Inter, SIL OFL licence)
standalone/         nova-chat.html - single-file demo (runs without Python)
.vscode/            launch + recommended extensions
requirements.txt  package.json  Dockerfile  .env.example  run.sh  run.bat
```
## Security
- **Auth:** scrypt password hashing, constant-time login (no user-enumeration timing), 10+ char passwords with letters and numbers (common passwords rejected), fresh session and CSRF token on login, 30-minute idle and 8-hour absolute session expiry, logout is POST-only.
- **Requests:** CSRF tokens on every state-changing request, Origin checking, per-IP/per-account rate limiting with lockout, request size limits, per-user chat and message caps.
- **Browser:** strict CSP (no inline scripts/styles, no objects, no framing), HSTS (when `HTTPS=1`), `__Host-` cookie prefix, HttpOnly + SameSite cookies, COOP/CORP, no-store caching, auto-escaped templates and a sanitising Markdown renderer.
- **Data & code:** parameterised SQL, no `eval` (the calculator uses a bounded AST evaluator), upstream AI errors are logged server-side and never shown to users, API keys are sent in headers and never logged.
- **Secrets:** `.env`, `chat.db` and `.secret_key` are git-ignored and excluded from Docker images. Weak or placeholder `SECRET_KEY` values are rejected.

Production checklist: set a strong `SECRET_KEY` (`python -c "import secrets; print(secrets.token_hex(32))"`), `FLASK_DEBUG=0`, `HTTPS=1`, `ALLOWED_HOSTS=your.domain`, and `TRUST_PROXY=1` only behind your own reverse proxy. Run `gunicorn app:app` behind HTTPS (the Docker image runs as a non-root user with a read-only code directory and data in `/data`, e.g. `docker run -v nova-data:/data -p 5000:5000 --env-file .env nova`).
Rate-limit counters are in memory (per process); use a shared store such as Redis if you run multiple workers. Chat messages are sent to the AI provider you configure (Gemini/OpenAI).