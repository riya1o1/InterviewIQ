from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import auth_router, resume_router, interview_router, dashboard_router

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview Prep API",
    description="Backend for AI-powered interview preparation platform",
    version="1.0.0"
)

# CORS — allow Streamlit frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router.router)
app.include_router(resume_router.router)
app.include_router(interview_router.router)
app.include_router(dashboard_router.router)


@app.get("/")
def root():
    return {"message": "AI Interview Prep API is running 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}
