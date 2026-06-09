from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="user")
    sessions = relationship("InterviewSession", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    raw_text = Column(Text, nullable=False)
    skills = Column(JSON, default=[])
    experience = Column(JSON, default=[])
    projects = Column(JSON, default=[])
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class InterviewSession(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)       # Backend, ML, Full Stack etc
    difficulty = Column(String, nullable=False) # Easy, Medium, Hard
    mode = Column(String, nullable=False)       # Practice, Mock
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    total_score = Column(Float, nullable=True)
    is_complete = Column(Boolean, default=False)

    user = relationship("User", back_populates="sessions")
    questions = relationship("Question", back_populates="session")


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # DSA, Technical, Project, Behavioral
    difficulty = Column(String, nullable=False)
    order_num = Column(Float, nullable=False)
    asked_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    score = Column(Float, nullable=True)
    strengths = Column(JSON, default=[])
    gaps = Column(JSON, default=[])
    ideal_answer = Column(Text, nullable=True)
    tips = Column(JSON, default=[])
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="answer")
