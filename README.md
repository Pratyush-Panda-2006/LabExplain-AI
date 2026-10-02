# ⚡ LabExplain

> **Zero-login, peer-accessible university code tutor powered by Google Gemma 2 (`gemma2-9b-it`) via Groq Cloud.**  
> *Built for the DEV Hacktoberfest Weekend Challenge.*

---

## 🎯 Problem Statement
In university coding labs, undergraduate students often encounter unfamiliar syntax and cryptic runtime errors (e.g., Python context managers, recursion base cases, pointer dereferencing in C/C++). However, students cannot safely use commercial AI tools on public lab machines because doing so requires logging into personal accounts, creating serious credential exposure and session leakage risks on untrusted workstations.

## 💡 The Solution
**LabExplain** is a zero-login, peer-accessible code tutor:
1. Students sit down at any university lab computer.
2. Enter the active 6-digit lab session PIN (`482910` or set by the instructor/TA).
3. Paste their confusing code snippet.
4. Receive an encouraging, line-by-line pedagogical breakdown powered by Google's open-weight **Gemma 2 (`gemma2-9b-it`)** running at ultra-low latency on Groq Cloud.

---

## 🏗️ Architecture & Project Layout

```
labexplain-ai/
├── main.py              # Application entrypoint, CORS, lifespan & static mount
├── config.py            # Environment configuration & constant-time PIN validator
├── routers/
│   └── explain.py       # POST /api/explain endpoint with Pydantic v2 schemas
├── services/
│   └── llm_service.py   # Groq / Gemma 2 inference service & error handling
├── static/
│   └── index.html       # Zero-login student single-page application (SPA)
├── test_app.py          # Pytest suite for API endpoints and validation
├── requirements.txt     # Pinned Python dependencies
├── .env.example         # Environment variable template
└── .gitignore           # Git ignore rules
```

---

## 🚀 Quickstart

### 1. Clone the repository & install dependencies
```bash
git clone https://github.com/your-username/labexplain-ai.git
cd labexplain-ai
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to include your Groq API key:
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
SESSION_PIN=482910
PORT=8000
```

### 3. Run the Application
```bash
python main.py
```
Or with Uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 🧪 Running Tests

LabExplain includes unit and integration tests covering authentication, input constraints, health check, and model inference:

```bash
pytest test_app.py -v
```

---

## 📡 API Reference

### Health Check
- **`GET /health`**
- Response:
  ```json
  {
    "status": "ok",
    "model": "gemma2-9b-it",
    "service": "LabExplain",
    "session_pin_configured": true,
    "groq_configured": true
  }
  ```

### Line-by-Line Code Explanation
- **`POST /api/explain`**
- Request Body:
  ```json
  {
    "pin": "482910",
    "code": "with open('data.txt') as f:\n    data = f.read()",
    "language": "python"
  }
  ```
- Response (`200 OK`):
  ```json
  {
    "explanation": "### 📝 Overview\n...\n### 🔍 Line-by-Line Breakdown\n...\n### 💡 Tutor's Lab Takeaway\n..."
  }
  ```

---

## 🌐 Deploy to Render

1. Create a **New Web Service** on [Render](https://render.com).
2. Connect your GitHub repository.
3. Configure the service:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set Environment Variables:
   - `GROQ_API_KEY`: Your Groq Cloud API key.
   - `SESSION_PIN`: Your lab session PIN (e.g. `482910`).
