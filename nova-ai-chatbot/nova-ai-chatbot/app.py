import os, re, ast, json, random, sqlite3, datetime, logging, operator, urllib.request, urllib.error
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
from functools import wraps
from flask import Flask, g, render_template, request, redirect, session, jsonify, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from security import init_security, hit, throttled, record, reset, check_input, login_user

app = Flask(__name__)
init_security(app)
log = logging.getLogger("nova")
DATA_DIR = os.environ.get("DATA_DIR") or os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(DATA_DIR, "chat.db")
MAX_CHATS_PER_USER, MAX_MESSAGES_PER_CHAT = 100, 400
DUMMY_HASH = generate_password_hash("not-a-real-password")  # equalises login timing for unknown emails

# ---------- database ----------
def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d: d.close()

def init_db():
    c = sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pw TEXT);
    CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY, user_id INT, title TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, chat_id INT, role TEXT, content TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
    """)
    c.commit(); c.close()

def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if "uid" not in session:
            if request.path.startswith("/api"):
                return jsonify(error="Login required"), 401
            return redirect(url_for("login"))
        return f(*a, **k)
    return w

def make_title(text):
    t = " ".join(text.split())
    if len(t) <= 48: return t
    return t[:48].rsplit(" ", 1)[0].rstrip(",.;:-") + "…"

def own_chat(cid):
    return db().execute("SELECT * FROM chats WHERE id=? AND user_id=?", (cid, session["uid"])).fetchone()

# ---------- chatbot brain ----------
JOKES = ["Why do programmers prefer dark mode? Because light attracts bugs.",
         "There are 10 kinds of people: those who understand binary and those who don't.",
         "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'"]
RULES = [
    (r"hello world", ["Here you go:\n```python\nprint('Hello, World!')\n```"]),
    (r"\b(hi|hello|hey|namaste)\b", ["Hello! 👋 How can I help you today?", "Hey there! What's on your mind?"]),
    (r"how are you", ["I'm doing great, thanks for asking! How about you?"]),
    (r"(your name|who are you)", ["I'm Nova, an AI chatbot built with Flask + Python."]),
    (r"\b(joke|funny)\b", JOKES),
    (r"\b(python)\b", ["Python is a versatile language loved for readability. Want a code example? Ask me for 'python hello world'."]),
    (r"\b(flask)\b", ["Flask is a lightweight Python web framework. This whole app runs on it!"]),
    (r"\b(help|what can you do)\b", ["I can chat, tell jokes, do math (try `12*(3+4)`), tell the time/date, and with an AI API key (Gemini or OpenAI) I can answer almost anything."]),
    (r"\b(thanks|thank you)\b", ["You're welcome! 😊"]),
    (r"\b(bye|goodbye)\b", ["Goodbye! Come back anytime. 👋"]),
]

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv, ast.Pow: operator.pow}

def safe_calc(expr):
    """Evaluate plain arithmetic without eval(); bounded so it cannot be used for denial of service."""
    if len(expr) > 100: raise ValueError("too long")
    def ev(n, depth=0):
        if depth > 25: raise ValueError("too deep")
        if isinstance(n, ast.Expression): return ev(n.body, depth + 1)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float): return n.value
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            v = ev(n.operand, depth + 1); return v if isinstance(n.op, ast.UAdd) else -v
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            a, b = ev(n.left, depth + 1), ev(n.right, depth + 1)
            if isinstance(n.op, ast.Pow) and (abs(b) > 64 or abs(a) > 1e9): raise ValueError("power too large")
            return _OPS[type(n.op)](a, b)
        raise ValueError("unsupported")
    return ev(ast.parse(expr, mode="eval"))

def rule_based(text):
    t = text.lower().strip()
    if re.fullmatch(r"[\d\s+\-*/().%]+", t) and re.search(r"\d", t):
        try:
            v = safe_calc(t)
            return f"**{t} = {round(v, 10) if isinstance(v, float) else v}**"
        except Exception: pass
    if "time" in t: return "The time is " + datetime.datetime.now().strftime("%I:%M %p") + "."
    if "date" in t or "today" in t: return "Today is " + datetime.datetime.now().strftime("%A, %d %B %Y") + "."
    for pat, outs in RULES:
        if re.search(pat, t): return random.choice(outs)
    return random.choice(["Interesting! Tell me more.",
        "I'm running in offline mode, so my answers are limited. Add a GEMINI_API_KEY to unlock full AI replies.",
        "Could you rephrase that? Try 'help' to see what I can do."])

SYSTEM_PROMPT = "You are Nova, a helpful, concise, friendly assistant."

GEMINI_FALLBACKS = ["gemini-flash-latest", "gemini-3.7-flash"]

def gemini_reply(history, key):
    models = [os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")] + GEMINI_FALLBACKS
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "model" if m["role"] == "assistant" else "user",
                      "parts": [{"text": m["content"]}]} for m in history[-20:]],
    }).encode()
    last = None
    for model in dict.fromkeys(models):
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            data=body, method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            try: msg = json.load(e)["error"]["message"]
            except Exception: msg = e.reason
            last = RuntimeError(f"Gemini {e.code}: {msg}")
            if e.code in (404, 429) or e.code >= 500: continue  # try the next model
            raise last
        except (TimeoutError, urllib.error.URLError) as e:
            last = RuntimeError(f"Gemini request failed: {e}"); continue
        parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
        if text: return text
        last = RuntimeError("Gemini returned no text (response may have been blocked).")
    raise last
AI_DOWN = "⚠️ The AI service is unavailable right now. Please try again in a moment."

def bot_reply(history):
    gkey = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gkey:
        try: return gemini_reply(history, gkey)
        except Exception as e:
            log.warning("Gemini error: %s", e); return AI_DOWN
    key = os.environ.get("OPENAI_API_KEY")
    if not key: return rule_based(history[-1]["content"])
    try:
        from openai import OpenAI
        r = OpenAI(api_key=key).chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history[-20:])
        return r.choices[0].message.content
    except Exception as e:
        log.warning("OpenAI error: %s", type(e).__name__); return AI_DOWN  # message may echo key fragments, so not logged

# ---------- pages ----------
@app.route("/")
def home(): return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        n, e = (request.form.get(k, "").strip() for k in ("name", "email"))
        p = request.form.get("password", "")
        err = None if hit("signup:" + str(request.remote_addr), 5, 3600) else "Too many sign-ups. Try again later."
        err = err or check_input(n, e, p)
        if err:
            flash(err)
        else:
            try:
                cur = db().execute("INSERT INTO users(name,email,pw) VALUES(?,?,?)", (n, e.lower(), generate_password_hash(p)))
                db().commit(); login_user(cur.lastrowid, n)
                return redirect(url_for("chat"))
            except sqlite3.IntegrityError:
                flash("Email already registered.")
    return render_template("auth.html", mode="signup")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        em = request.form.get("email", "").lower().strip()[:120]
        ip = str(request.remote_addr); k_acct, k_ip = "login:%s:%s" % (ip, em), "login-ip:" + ip
        if throttled(k_acct, 5, 300) or throttled(k_ip, 30, 300):
            flash("Too many attempts. Please wait 5 minutes.")
            return render_template("auth.html", mode="login"), 429
        u = db().execute("SELECT * FROM users WHERE email=?", (em,)).fetchone()
        ok = check_password_hash(u["pw"] if u else DUMMY_HASH, request.form.get("password", "")[:128])
        if u and ok:
            reset(k_acct); login_user(u["id"], u["name"])
            return redirect(url_for("chat"))
        record(k_acct); record(k_ip)  # only failed attempts count towards the lockout
        flash("Invalid email or password.")
    return render_template("auth.html", mode="login")

@app.post("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))

@app.route("/chat")
@login_required
def chat(): return render_template("chat.html", name=session["name"])

# ---------- API ----------
@app.get("/api/chats")
@login_required
def chats():
    rows = db().execute("SELECT id,title,created FROM chats WHERE user_id=? ORDER BY id DESC", (session["uid"],)).fetchall()
    return jsonify([{"id": r["id"], "title": r["title"], "created": (r["created"] or "").replace(" ", "T") + "Z"} for r in rows])

@app.post("/api/chats")
@login_required
def new_chat():
    if not hit("newchat:%s" % session["uid"], 20, 60): return jsonify(error="Slow down a little."), 429
    n = db().execute("SELECT COUNT(*) FROM chats WHERE user_id=?", (session["uid"],)).fetchone()[0]
    if n >= MAX_CHATS_PER_USER: return jsonify(error="Chat limit reached. Delete an old chat to start a new one."), 400
    cur = db().execute("INSERT INTO chats(user_id,title) VALUES(?,?)", (session["uid"], "New chat"))
    db().commit(); return jsonify(id=cur.lastrowid)

@app.get("/api/chats/<int:cid>")
@login_required
def messages(cid):
    if not own_chat(cid): return jsonify(error="Not found"), 404
    rows = db().execute("SELECT role,content FROM messages WHERE chat_id=? ORDER BY id", (cid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.delete("/api/chats/<int:cid>")
@login_required
def delete_chat(cid):
    if not own_chat(cid): return jsonify(error="Not found"), 404
    db().execute("DELETE FROM messages WHERE chat_id=?", (cid,))
    db().execute("DELETE FROM chats WHERE id=?", (cid,)); db().commit()
    return jsonify(ok=True)

@app.post("/api/chats/<int:cid>/send")
@login_required
def send(cid):
    chat = own_chat(cid)
    if not hit("send:%s" % session["uid"], 30, 60): return jsonify(error="Slow down a little."), 429
    data = request.get_json(silent=True)
    text = str(data.get("message", "") if isinstance(data, dict) else "").strip()[:2000]
    if not chat or not text: return jsonify(error="Bad request"), 400
    d = db()
    if d.execute("SELECT COUNT(*) FROM messages WHERE chat_id=?", (cid,)).fetchone()[0] >= MAX_MESSAGES_PER_CHAT:
        return jsonify(error="This conversation is full. Start a new chat to continue."), 400
    d.execute("INSERT INTO messages(chat_id,role,content) VALUES(?,?,?)", (cid, "user", text))
    if chat["title"] == "New chat":
        d.execute("UPDATE chats SET title=? WHERE id=?", (make_title(text), cid))
    rows = d.execute("SELECT role,content FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT 20", (cid,)).fetchall()
    hist = [dict(r) for r in reversed(rows)]
    reply = bot_reply(hist)
    d.execute("INSERT INTO messages(chat_id,role,content) VALUES(?,?,?)", (cid, "assistant", reply))
    d.commit()
    return jsonify(reply=reply)

init_db()
if __name__ == "__main__":
    # Bound to localhost; use gunicorn behind HTTPS for anything public. Debug (Werkzeug console) is opt-in only.
    app.run(host="127.0.0.1", debug=os.environ.get("FLASK_DEBUG") == "1")
