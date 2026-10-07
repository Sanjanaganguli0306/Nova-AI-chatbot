# 🤖 Nova AI Chatbot

> **A modern, secure, and responsive AI-powered conversational web application built with Flask and SQLite.**

Nova AI Chatbot is a full-stack conversational web application designed to provide a clean and engaging AI chat experience. It combines a responsive interface with authentication, persistent chat history, multiple themes, voice interaction, local/offline bot functionality, and a security-focused backend.

The application can work with a built-in offline bot or connect to **Google Gemini / OpenAI** through environment-based API configuration for real AI responses.

---

## ✨ Features

### 💬 Intelligent Chat Experience

* Modern conversational chat interface
* Real-time typing animation
* Persistent chat history
* Built-in offline chatbot
* Optional Gemini / OpenAI integration
* Markdown message rendering

### 🔐 Authentication & Security

* User registration and login
* Secure password hashing using **scrypt**
* CSRF protection
* Session management
* Rate limiting and account lockout
* Request validation and size limits
* Secure HTTP headers
* Content Security Policy (CSP)
* Secure cookies with HttpOnly and SameSite protection
* Origin validation
* Parameterized SQL queries
* API keys protected through environment variables

### 🎨 Modern User Interface

* Responsive design
* Dark mode
* Multiple visual themes
* Clean landing/home page
* Interactive controls
* Custom SVG icons
* Smooth user interactions

### 🎙️ Voice Features

* Voice input
* Voice output
* Interactive conversational experience

### 💾 Data Management

* SQLite database
* Persistent user and chat data
* Automatic database creation when required
* Structured database schema

### 🚀 Deployment

* Local Flask development
* Docker support
* Gunicorn production server
* Windows and macOS/Linux run scripts
* VS Code launch configuration

---

## 🛠️ Tech Stack

| Technology          | Purpose                   |
| ------------------- | ------------------------- |
| **Python**          | Core application logic    |
| **Flask**           | Backend web framework     |
| **SQLite**          | Database                  |
| **HTML5**           | Application structure     |
| **CSS3**            | Styling and responsive UI |
| **JavaScript**      | Client-side interactions  |
| **Jinja2**          | Server-side templating    |
| **Gemini / OpenAI** | Optional AI responses     |
| **Docker**          | Containerization          |
| **Gunicorn**        | Production WSGI server    |

---

## 📁 Project Structure

```text
Nova-AI-Chatbot/
│
├── app.py                  # Flask routes, chatbot logic and database access
├── security.py             # Security, CSRF, headers, rate limiting and validation
├── schema.sql              # Database schema
├── chat.db                 # SQLite database
│
├── templates/
│   ├── base
│   ├── icons
│   ├── controls
│   ├── home
│   ├── auth
│   ├── chat
│   └── error
│
├── static/
│   ├── style.css
│   ├── app.js
│   ├── theme.js
│   ├── img/
│   └── fonts/
│
├── standalone/
│   └── nova-chat.html      # Standalone single-file demo
│
├── .vscode/                # VS Code configuration
├── requirements.txt        # Python dependencies
├── package.json            # npm configuration
├── Dockerfile              # Docker configuration
├── .env.example            # Environment configuration template
├── run.sh                  # macOS/Linux startup script
├── run.bat                 # Windows startup script
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/nova-ai-chatbot.git
cd nova-ai-chatbot
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your `.env` file from the provided example.

#### Windows

```bash
copy .env.example .env
```

#### macOS / Linux

```bash
cp .env.example .env
```

Then configure the required environment values.

For AI-powered responses, add your supported **Gemini or OpenAI API configuration** according to `.env.example`.

> **Never commit API keys, passwords, `.env`, database secrets, or private credentials to GitHub.**

### 5. Run the Application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 🖥️ Run with VS Code

1. Open the project folder in **VS Code**.
2. Open **Terminal → New Terminal**.
3. Create and activate the virtual environment.
4. Install dependencies.
5. Configure `.env`.
6. Run:

```bash
python app.py
```

You can also use the included VS Code launch configuration.

---

## 🐳 Run with Docker

Build the image:

```bash
docker build -t nova .
```

Run the application:

```bash
docker run \
  -v nova-data:/data \
  -p 5000:5000 \
  --env-file .env \
  nova
```

The Docker configuration runs the application as a non-root user and stores application data in `/data`.

---

## 🔒 Security

Security is a major part of Nova AI Chatbot.

### Authentication

* scrypt password hashing
* Password strength validation
* Common-password rejection
* Constant-time login behavior
* Secure session creation
* Idle and absolute session expiration
* POST-only logout

### Request Protection

* CSRF protection
* Origin validation
* Rate limiting
* Account lockout
* Request-size restrictions
* Per-user chat/message limits

### Browser Security

* Content Security Policy
* HSTS support
* HttpOnly cookies
* SameSite cookies
* `__Host-` cookie prefix
* COOP/CORP headers
* No-store caching
* Auto-escaped templates

### Data & Application Security

* Parameterized SQL queries
* No unsafe `eval()` usage
* Bounded calculator evaluation
* Server-side AI error logging
* API keys transmitted through headers
* Sensitive configuration stored through environment variables

The project also excludes sensitive files such as `.env`, database secrets, and secret keys from version control.

---

## 🎨 User Experience

Nova AI Chatbot focuses on creating a modern conversational experience with:

* Responsive interface
* Dark mode
* Multiple themes
* Typing animation
* Chat history
* Voice interaction
* Clean authentication screens
* Interactive chatbot interface

---

## 🤖 AI Integration

Nova supports two modes:

### Offline Mode

The application can run using its built-in chatbot without requiring an external AI API.

### AI Provider Mode

For advanced AI responses, configure a supported provider such as:

* Google Gemini
* OpenAI

API credentials should be stored securely in `.env` and should **never be hard-coded into source files**.

---

## 📊 Application Architecture

```text
                   ┌──────────────────────┐
                   │      User / Browser  │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   HTML / CSS / JS    │
                   │   Responsive UI      │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │       Flask          │
                   │   Backend / Routes   │
                   └──────────┬───────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
       ┌────────────────┐          ┌─────────────────┐
       │     SQLite     │          │   AI Provider   │
       │ Users / Chats  │          │ Gemini / OpenAI │
       └────────────────┘          └─────────────────┘
```

---

## 📸 Screenshots

> Add screenshots of your application here to showcase the UI.

### 🏠 Homepage

```text
Add your homepage screenshot here
```

### 💬 Chat Interface

```text
Add your chatbot screenshot here
```

### 🔐 Authentication

```text
Add your login/signup screenshot here
```

### 🌙 Dark Mode

```text
Add your dark-mode screenshot here
```

---

## 🎥 Demo

**Live Demo:** `Add your deployed URL here`

**Demo Video:** `Add your demo video link here`

> A live demo and short project walkthrough are recommended for recruiters and reviewers.

---

## ⚙️ Production Configuration

Before deploying to production, configure:

```text
SECRET_KEY=<strong-secret-key>
FLASK_DEBUG=0
HTTPS=1
ALLOWED_HOSTS=<your-domain>
```

For production deployment, the project can be served using Gunicorn behind HTTPS:

```bash
gunicorn app:app
```

For multiple workers, use a shared rate-limit store such as Redis rather than relying only on in-memory counters.

---

## 🧪 Standalone Demo

The repository also includes:

```text
standalone/nova-chat.html
```

This provides a single-file version of the chat interface that can run without the Python backend.

---

## 🔮 Future Enhancements

Potential improvements include:

* Streaming AI responses
* Advanced conversation memory
* File/document-based conversations
* RAG-powered knowledge retrieval
* Admin dashboard
* Analytics and usage monitoring
* Redis-based distributed rate limiting
* Cloud deployment
* Automated testing and CI/CD
* Additional AI model providers

---

## 📌 Project Highlights

* **Full-stack conversational application**
* **Secure authentication system**
* **SQLite persistence**
* **Optional real AI integration**
* **Responsive modern UI**
* **Dark mode and multiple themes**
* **Voice interaction**
* **Docker-ready**
* **Production security considerations**
* **Offline chatbot capability**

---

## 👩‍💻 Author

**Sanjana Ganguli**

B.Tech Computer Science Student
Interested in Software Development, Cloud Computing & Artificial Intelligence

### Connect With Me

* **LinkedIn:** Add your LinkedIn profile
* **GitHub:** Add your GitHub profile
* **Portfolio:** Add your portfolio URL

---

## ⭐ Support

If you find **Nova AI Chatbot** useful or interesting, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

Add your preferred open-source license here, such as **MIT License**, if you intend to distribute the project under that license.
