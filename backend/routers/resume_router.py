from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth
from resume_parser import extract_text_from_pdf
from groq_service import parse_resume_with_llm

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/upload", response_model=schemas.ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Read file bytes
    file_bytes = await file.read()

    # Extract raw text from PDF
    raw_text = extract_text_from_pdf(file_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Parse with Groq LLM
    try:
        parsed = parse_resume_with_llm(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM parsing failed: {str(e)}")

    # Delete old resume if exists
    old_resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id
    ).first()
    if old_resume:
        db.delete(old_resume)
        db.commit()

    # Save new resume
    resume = models.Resume(
        user_id=current_user.id,
        raw_text=raw_text,
        skills=parsed.get("skills", []),
        experience=parsed.get("experience", []),
        projects=parsed.get("projects", [])
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


@router.get("/me", response_model=schemas.ResumeResponse)
def get_my_resume(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    resume = db.query(models.Resume).filter(
        models.Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded yet")

    return resume
