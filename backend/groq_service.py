import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def parse_resume_with_llm(raw_text: str) -> dict:
    """Extract structured data from raw resume text."""
    prompt = f"""You are an expert resume parser.
Extract skills, experience, and projects from this resume text.
Return ONLY valid JSON, no extra text, no markdown:
{{
  "skills": ["Python", "FastAPI"],
  "experience": [
    {{"company": "Capgemini", "role": "Analyst", "duration": "4 months"}}
  ],
  "projects": [
    {{"name": "Brain Tumor Detection", "tech": ["CNN", "TensorFlow"], "description": "..."}}
  ]
}}

Resume text:
{raw_text[:3000]}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.1
    )

    raw = response.choices[0].message.content.strip()
    # Clean any markdown fences if present
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def generate_questions(role: str, difficulty: str, resume_data: dict) -> list:
    """Generate 10 interview questions based on role, difficulty and resume."""
    skills = ", ".join(resume_data.get("skills", [])[:10])
    projects = [p["name"] for p in resume_data.get("projects", [])]

    prompt = f"""You are a senior technical interviewer at a top tech company.
Generate exactly 10 {difficulty} level interview questions for a {role} role.

Candidate's skills: {skills}
Candidate's projects: {", ".join(projects)}

Rules:
- 4 questions: core technical ({role} specific)
- 2 questions: based on their actual projects listed above
- 2 questions: problem solving / DSA concepts
- 2 questions: behavioral / situational

Return ONLY a valid JSON array, no extra text:
[
  {{"question": "...", "category": "Technical", "difficulty": "{difficulty}"}},
  {{"question": "...", "category": "Project", "difficulty": "{difficulty}"}},
  ...
]"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.7
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def evaluate_answer(question: str, user_answer: str) -> dict:
    """Evaluate user's answer and return detailed feedback."""
    prompt = f"""You are a strict but fair technical interviewer evaluating a candidate's answer.

Question: {question}
Candidate's Answer: {user_answer}

Evaluate the answer and return ONLY valid JSON, no extra text:
{{
  "score": 7.5,
  "strengths": ["correctly explained X", "good example given"],
  "gaps": ["missed Y concept", "didn't mention Z"],
  "ideal_answer": "A complete answer would cover...",
  "tips": ["Read about X", "Practice explaining Y more clearly"]
}}

Score guide: 0-3 poor, 4-6 average, 7-8 good, 9-10 excellent."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def get_followup_question(question: str, user_answer: str) -> str:
    """Generate a natural follow-up question for mock interview chatbot."""
    prompt = f"""You are conducting a professional mock interview.
The candidate just answered a question. Ask ONE natural follow-up question.
Keep it under 2 sentences. Be realistic and slightly challenging.

Original question: {question}
Candidate answered: {user_answer}

Respond with ONLY the follow-up question, nothing else."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.6
    )

    return response.choices[0].message.content.strip()


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """Transcribe audio using Groq Whisper API."""
    transcription = client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model="whisper-large-v3",
        language="en"
    )
    return transcription.text
