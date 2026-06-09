from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
from groq_service import generate_questions, evaluate_answer, get_followup_question, transcribe_audio
from datetime import datetime
from fastapi import UploadFile, File

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/start", response_model=schemas.SessionResponse)
def start_session(
    data: schemas.StartSessionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get user's resume
    resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Please upload your resume first")

    # Create session
    session = models.InterviewSession(
        user_id=current_user.id,
        role=data.role,
        difficulty=data.difficulty,
        mode=data.mode
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate questions using Groq
    resume_data = {
        "skills": resume.skills,
        "projects": resume.projects,
        "experience": resume.experience
    }
    try:
        questions_data = generate_questions(data.role, data.difficulty, resume_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")

    # Save questions to DB
    for i, q in enumerate(questions_data):
        question = models.Question(
            session_id=session.id,
            question_text=q.get("question", ""),
            category=q.get("category", "Technical"),
            difficulty=data.difficulty,
            order_num=i + 1
        )
        db.add(question)
    db.commit()

    return session


@router.get("/questions/{session_id}")
def get_session_questions(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = db.query(models.Question).filter(
        models.Question.session_id == session_id
    ).order_by(models.Question.order_num).all()

    return [{"id": str(q.id), "question": q.question_text, "category": q.category} for q in questions]


@router.post("/answer", response_model=schemas.FeedbackResponse)
def submit_answer(
    data: schemas.SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get question
    question = db.query(models.Question).filter(
        models.Question.id == data.question_id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Evaluate with Groq
    try:
        feedback = evaluate_answer(question.question_text, data.user_answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

    # Save answer
    answer = models.Answer(
        question_id=question.id,
        user_answer=data.user_answer,
        score=feedback.get("score", 0),
        strengths=feedback.get("strengths", []),
        gaps=feedback.get("gaps", []),
        ideal_answer=feedback.get("ideal_answer", ""),
        tips=feedback.get("tips", [])
    )
    db.add(answer)
    db.commit()

    return schemas.FeedbackResponse(**feedback)


@router.post("/audio-answer")
async def submit_audio_answer(
    question_id: str,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Transcribe audio
    audio_bytes = await audio.read()
    try:
        transcribed_text = transcribe_audio(audio_bytes, audio.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    # Get question
    question = db.query(models.Question).filter(
        models.Question.id == question_id
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Evaluate transcribed answer
    try:
        feedback = evaluate_answer(question.question_text, transcribed_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

    # Save answer
    answer = models.Answer(
        question_id=question.id,
        user_answer=transcribed_text,
        score=feedback.get("score", 0),
        strengths=feedback.get("strengths", []),
        gaps=feedback.get("gaps", []),
        ideal_answer=feedback.get("ideal_answer", ""),
        tips=feedback.get("tips", [])
    )
    db.add(answer)
    db.commit()

    return {
        "transcribed_text": transcribed_text,
        "feedback": feedback
    }


@router.post("/end/{session_id}")
def end_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Calculate total score
    questions = db.query(models.Question).filter(
        models.Question.session_id == session_id
    ).all()

    scores = []
    breakdown = []
    for q in questions:
        if q.answer:
            scores.append(q.answer.score)
            breakdown.append({
                "question": q.question_text,
                "category": q.category,
                "score": q.answer.score,
                "user_answer": q.answer.user_answer
            })

    avg_score = sum(scores) / len(scores) if scores else 0

    # Update session
    session.total_score = round(avg_score, 2)
    session.ended_at = datetime.utcnow()
    session.is_complete = True
    db.commit()

    return {
        "total_score": round(avg_score, 2),
        "total_questions": len(questions),
        "answered": len(scores),
        "answers_breakdown": breakdown
    }
