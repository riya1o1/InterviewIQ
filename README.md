# AI Interview Preparation Platform

An AI-powered platform that helps you prepare for technical interviews by generating personalized questions from your resume, evaluating your answers, and tracking your progress over time.

## Features
- **Resume Upload** — AI parses your skills, experience, and projects
- **AI Question Generation** — Role-specific questions using Groq LLM (Llama 3.1)
- **Speech-to-Text** — Answer questions by voice using Whisper
- **AI Feedback & Scoring** — Detailed evaluation with strengths, gaps, and ideal answers
- **Mock Interview Mode** — Timed sessions with 10 back-to-back questions
- **Progress Dashboard** — Track improvement and identify weak areas

## Tech Stack
- **Backend:** FastAPI + PostgreSQL + SQLAlchemy
- **Frontend:** Streamlit
- **AI:** Groq API (Llama 3.1 + Whisper)
- **Auth:** JWT
- **Containerization:** Docker + docker-compose

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/riya1o1/ai-interview-prep
cd ai-interview-prep
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

### 3. Run with Docker
```bash
docker-compose up --build
```

### 4. Access the app
- Frontend: http://localhost:8501
- Backend API docs: http://localhost:8000/docs

## Project Structure
```
ai-interview-prep/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── models.py            # Database models
│   ├── schemas.py           # Request/response schemas
│   ├── auth.py              # JWT authentication
│   ├── groq_service.py      # Groq LLM + Whisper
│   ├── resume_parser.py     # PDF text extraction
│   └── routers/             # API route handlers
├── frontend/
│   ├── app.py               # Streamlit main page
│   └── pages/               # Multi-page navigation
├── docker-compose.yml
└── requirements.txt
```

## Environment Variables
```
DATABASE_URL=postgresql://user:password@localhost:5432/interview_prep
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-api-key
```

## Demo
*Coming soon*

## 👩‍💻 Built by Riya Singh
