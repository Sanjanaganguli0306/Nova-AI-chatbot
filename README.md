# 🤖 Nova AI Chatbot

### A Secure, Full-Stack AI Conversational Web Application

Nova AI Chatbot is a modern, responsive AI-powered chatbot built with **Python, Flask, SQLite, HTML, CSS, and JavaScript**. It provides an interactive conversational experience with authentication, persistent chat history, voice interaction, multiple themes, dark mode, and a security-focused backend architecture.

The application works offline with a built-in chatbot and can be connected to **Google Gemini or OpenAI** for real AI-powered responses.

---

## ✨ Why Nova AI?

Nova was designed not just as a chatbot interface, but as a complete web application with a focus on:

* 🔐 Secure user authentication
* 💬 Interactive AI conversations
* 🗂️ Persistent chat history
* 🎙️ Voice input and output
* 🌙 Dark mode and multiple themes
* 📱 Responsive user interface
* 🛡️ CSRF protection and security headers
* 🚦 Rate limiting and request validation
* 🗄️ SQLite-based data persistence
* 🐳 Docker support
* ⚡ Offline chatbot functionality

---

## 🚀 Key Features

### 💬 Intelligent Chat Experience

* Interactive chatbot interface
* Typing animation
* Conversation history
* Built-in offline chatbot
* Gemini/OpenAI integration through environment variables

### 👤 Authentication

* User registration and login
* Secure password hashing using **scrypt**
* Session management
* CSRF protection
* Login protection and rate limiting
* Password validation

### 🎨 Modern UI/UX

* Responsive design
* Dark mode
* 4 customizable themes
* Modern typography and visual design
* Interactive chat interface
* SVG icon system

### 🎙️ Voice Interaction

* Voice input
* Voice output
* Natural conversational experience

### 🗄️ Data Management

* SQLite database
* Persistent chat storage
* Parameterized SQL queries
* Automatic database creation when required

### 🛡️ Security

Nova includes multiple application-level security controls:

* CSRF protection
* Origin validation
* Rate limiting
* Account/request lockout protection
* Strict Content Security Policy
* HSTS support
* Secure cookies
* HttpOnly cookies
* SameSite cookies
* COOP/CORP headers
* Request-size limits
* Input validation
* Auto-escaped templates
* Sanitized Markdown rendering
* Parameterized SQL
* Protected environment variables
* Server-side AI error logging

---

## 🧰 Tech Stack

| Category         | Technology                                |
| ---------------- | ----------------------------------------- |
| Backend          | Python, Flask                             |
| Frontend         | HTML5, CSS3, JavaScript                   |
| Database         | SQLite                                    |
| Templates        | Jinja2                                    |
| AI Integration   | Google Gemini / OpenAI                    |
| Authentication   | Flask-based authentication                |
| Security         | CSRF, CSP, rate limiting, secure sessions |
| Containerization | Docker                                    |
| Development      | VS Code                                   |
| Version Control  | Git & GitHub                              |

---

## 🏗️ Project Architecture

```text
Nova-AI-Chatbot/
│
├── app.py
├── security.py
├── schema.sql
├── chat.db
│
├── templates/
│   ├── base/
│   ├── icons/
│   ├── controls/
│   ├── home/
│   ├── auth/
│   ├── chat/
│   └── error/
│
├── static/
│   ├── style.css
│   ├── app.js
│   ├── theme.js
│   ├── img/
│   └── fonts/
│
├── standalone/
│   └── nova-chat.html
│
├── .vscode/
│
├── requirements.txt
├── package.json
├── Dockerfile
├── .env.example
├── run.sh
├── run.bat
└── README.md
```

The project separates Flask application logic, security controls, templates, static assets, database configuration, and deployment files for easier maintenance and development.

---

## ⚙️ Getting Started

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
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your `.env` file:

```bash
copy .env.example .env
```

For macOS/Linux:

```bash
cp .env.example .env
```

Then add your required configuration and AI API key.

> Never commit `.env`, API keys, secret keys, or database credentials to GitHub.

### 5. Run the Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The project also provides Windows and macOS/Linux startup scripts.

---

## 🐳 Run with Docker

Build the Docker image:

```bash
docker build -t nova .
```

Run the application:

```bash
docker run -v nova-data:/data -p 5000:5000 --env-file .env nova
```

The Docker configuration is designed to run the application with a non-root user and persistent application data.

---

## 🔐 Security Architecture

Security was considered throughout the application rather than being added only at the UI level.

### Authentication Security

* scrypt password hashing
* Password complexity validation
* Common-password rejection
* Fresh session on login
* CSRF token generation
* Session expiration
* POST-only logout

### Request Security

* CSRF validation
* Origin checking
* Per-IP and per-account rate limiting
* Lockout protection
* Request-size restrictions
* Chat/message limits

### Browser Security

* Strict Content Security Policy
* HSTS support
* Secure cookie configuration
* HttpOnly cookies
* SameSite cookies
* COOP/CORP protection
* No-store caching

### Application Security

* Parameterized SQL queries
* No use of `eval`
* Bounded AST-based calculator evaluation
* Server-side AI error handling
* API keys transmitted through headers
* Secrets excluded from version control

These security measures are documented in the project's existing implementation.

---

## 📸 Screenshots

### 🏠 Homepage

> Add your homepage screenshot here.

```text
docs/screenshots/homepage.png
```

### 💬 Chat Interface

> Add your chatbot screenshot here.

```text
docs/screenshots/chat.png
```

### 🔐 Authentication

> Add your login/signup screenshot here.

```text
docs/screenshots/authentication.png
```

### 🌙 Dark Mode

> Add your dark-mode screenshot here.

```text
docs/screenshots/dark-mode.png
```

---

## 🎥 Demo

### Live Demo

**Coming soon**

### Project Demo Video

**Coming soon**

> Replace these sections with your deployed application URL and demo video once available.

---

## 📊 Project Highlights

| Area           | Implementation                    |
| -------------- | --------------------------------- |
| Frontend       | Responsive interactive chatbot UI |
| Backend        | Flask REST/web application        |
| Database       | SQLite                            |
| Authentication | Secure user login/signup          |
| AI             | Gemini/OpenAI integration         |
| Voice          | Input & output                    |
| Themes         | Dark mode + 4 themes              |
| Security       | Multi-layer application security  |
| Deployment     | Docker supported                  |
| Offline Mode   | Built-in chatbot                  |

---

## 🧠 What I Learned

Building Nova AI Chatbot provided practical experience in:

* Full-stack web application development
* Python Flask backend development
* Database design with SQLite
* User authentication and session management
* Secure API integration
* Frontend UI/UX development
* Application security
* Environment and secret management
* Docker containerization
* Git and GitHub workflow
* Building applications that can operate with or without external AI services

---

## 🔮 Future Improvements

Potential future enhancements include:

* Streaming AI responses
* Advanced conversation memory
* File and document analysis
* RAG-based knowledge retrieval
* User-specific AI preferences
* Analytics dashboard
* Cloud database support
* Redis-based distributed rate limiting
* Production deployment with CI/CD

---

## 📁 Production Checklist

Before deploying to production:

```text
✓ Set a strong SECRET_KEY
✓ Disable Flask debug mode
✓ Enable HTTPS
✓ Configure ALLOWED_HOSTS
✓ Configure the trusted reverse proxy correctly
✓ Protect all API credentials
✓ Use a production WSGI server
✓ Configure persistent database storage
✓ Use a shared rate-limit store for multiple workers
```

The current project documentation recommends Gunicorn behind HTTPS for production deployment and Redis/shared storage when running multiple workers.

---

## 👩‍💻 Developer

**Sanjana Ganguli**

B.Tech Computer Science Student
Interested in **Software Development, Cloud Computing, Artificial Intelligence, and Machine Learning**.


---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

