# 🤖 Multi-Agent AI Orchestration Platform

An advanced AI-powered backend system that uses a multi-agent architecture to process user queries intelligently using LLMs.
The system routes tasks to specialized agents (Coder, Reviewer, Researcher) and improves outputs through a self-healing feedback loop.

---

## 🚀 Features

- 🧠 Multi-Agent system using LangGraph
- ⚡ FastAPI backend for scalable APIs
- 🤖 LLM integration using AWS Bedrock
- 🔁 Self-healing feedback loop for error correction
- 📚 Context-aware research agent
- 👨‍💻 Code generation + review pipeline
- 🧩 Modular backend architecture (controllers, services, repositories)

---

## 🏗️ Architecture

The system works in the following flow:

1. **Intent Classification**
   - Identifies user request type (code, review, research)

2. **Agent Routing**
   - Coder Agent → Generates code
   - Reviewer Agent → Validates and improves output
   - Researcher Agent → Fetches supporting context

3. **Self-Healing Loop**
   - Failed outputs are analyzed
   - Research agent enhances context
   - Code is regenerated automatically

---

## 🛠️ Tech Stack

- Backend: FastAPI  
- AI Frameworks: LangChain, LangGraph  
- Cloud AI: AWS Bedrock  
- Database: PostgreSQL  
- Package Manager: uv  
- Architecture: Modular service-based design  

---

## 📦 Project Setup

This project uses **uv** for dependency and environment management.

### 1. Clone the repository
```bash
git clone https://github.com/aakashkarunanithi/multi-agent-orchestration-platform
cd multi-agent-orchestration-platform

2. Install dependencies
uv sync

3. Setup environment variables

Create a .env file in the root directory:

AWS_ACCESS_KEY=
AWS_SECRET_KEY=
DATABASE_URL=

4. Run the application
uv run src/main.py
📂 Project Structure
📂 Project Structure

src/
 ├── agents/        # AI agents (coder, reviewer, researcher)
 ├── migration/     # Database migration scripts
 ├── models/        # Data models and schemas
 ├── repositories/  # Database access layer
 ├── routers/       # API route definitions
 ├── services/      # Business logic and orchestration
 ├── utils/         # Utility functions and helpers
 ├── main.py        # Application entry point
 └── settings.py    # Configuration and environment variables

🔐 Security
.env is ignored using .gitignore
No sensitive credentials are committed to GitHub
