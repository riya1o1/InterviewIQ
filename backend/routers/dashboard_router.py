from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models, auth

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    sessions = db.query(models.InterviewSession).filter(
        models.InterviewSession.user_id == current_user.id,
        models.InterviewSession.is_complete == True
    ).order_by(models.InterviewSession.started_at).all()

    if not sessions:
        return {"total_sessions": 0, "avg_score": 0, "best_score": 0, "improvement": 0}

    scores = [s.total_score for s in sessions if s.total_score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0
    best_score = max(scores) if scores else 0

    # Improvement = difference between first and last session
    improvement = round(scores[-1] - scores[0], 2) if len(scores) > 1 else 0

    return {
        "total_sessions": len(sessions),
        "avg_score": avg_score,
        "best_score": best_score,
        "improvement": improvement
    }


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    sessions = db.query(models.InterviewSession).filter(
        models.InterviewSession.user_id == current_user.id,
        models.InterviewSession.is_complete == True
    ).order_by(models.InterviewSession.started_at.desc()).all()

    return [
        {
            "id": str(s.id),
            "role": s.role,
            "difficulty": s.difficulty,
            "mode": s.mode,
            "total_score": s.total_score,
            "started_at": s.started_at.strftime("%d %b %Y, %I:%M %p")
        }
        for s in sessions
    ]


@router.get("/weak-areas")
def get_weak_areas(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get all answered questions for this user
    sessions = db.query(models.InterviewSession).filter(
        models.InterviewSession.user_id == current_user.id
    ).all()

    session_ids = [s.id for s in sessions]

    questions = db.query(models.Question).filter(
        models.Question.session_id.in_(session_ids)
    ).all()

    # Group scores by category
    category_scores = {}
    for q in questions:
        if q.answer:
            cat = q.category
            if cat not in category_scores:
                category_scores[cat] = []
            category_scores[cat].append(q.answer.score)

    # Calculate avg per category
    suggestions = {
        "DSA": "Practice more LeetCode medium/hard problems",
        "Technical": "Review core concepts for your target role",
        "Project": "Prepare detailed explanations of your projects",
        "Behavioral": "Use the STAR method for behavioral questions"
    }

    weak_areas = []
    for category, scores in category_scores.items():
        avg = round(sum(scores) / len(scores), 2)
        if avg < 7:  # Flag as weak if below 7
            weak_areas.append({
                "category": category,
                "avg_score": avg,
                "suggestion": suggestions.get(category, "Practice more")
            })

    return sorted(weak_areas, key=lambda x: x["avg_score"])


@router.get("/session/{session_id}")
def get_session_detail(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id,
        models.InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        return {"error": "Session not found"}

    questions = db.query(models.Question).filter(
        models.Question.session_id == session_id
    ).order_by(models.Question.order_num).all()

    breakdown = []
    for q in questions:
        item = {
            "question": q.question_text,
            "category": q.category,
            "answered": q.answer is not None
        }
        if q.answer:
            item.update({
                "user_answer": q.answer.user_answer,
                "score": q.answer.score,
                "strengths": q.answer.strengths,
                "gaps": q.answer.gaps,
                "ideal_answer": q.answer.ideal_answer,
                "tips": q.answer.tips
            })
        breakdown.append(item)

    return {
        "session": {
            "role": session.role,
            "difficulty": session.difficulty,
            "mode": session.mode,
            "total_score": session.total_score,
            "started_at": session.started_at.strftime("%d %b %Y, %I:%M %p")
        },
        "breakdown": breakdown
    }
