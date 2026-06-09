from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ── AUTH ──────────────────────────────────────────────
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── RESUME ────────────────────────────────────────────
class ResumeResponse(BaseModel):
    id: UUID
    skills: List[str]
    experience: List[dict]
    projects: List[dict]
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ── INTERVIEW ─────────────────────────────────────────
class StartSessionRequest(BaseModel):
    role: str          # Backend, ML Engineer, Full Stack, Data Analyst
    difficulty: str    # Easy, Medium, Hard
    mode: str          # Practice, Mock

class SessionResponse(BaseModel):
    id: UUID
    role: str
    difficulty: str
    mode: str
    started_at: datetime

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: UUID
    question_text: str
    category: str
    order_num: float

    class Config:
        from_attributes = True

class SubmitAnswerRequest(BaseModel):
    question_id: UUID
    user_answer: str

class FeedbackResponse(BaseModel):
    score: float
    strengths: List[str]
    gaps: List[str]
    ideal_answer: str
    tips: List[str]

class SessionCompleteResponse(BaseModel):
    total_score: float
    total_questions: int
    answers_breakdown: List[dict]


# ── DASHBOARD ─────────────────────────────────────────
class DashboardStats(BaseModel):
    total_sessions: int
    avg_score: float
    best_score: float
    improvement: float  # % improvement from first to last session

class WeakArea(BaseModel):
    category: str
    avg_score: float
    suggestion: str
