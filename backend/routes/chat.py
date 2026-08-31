"""
Chat / AI Learning Assistant routes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from backend.schemas.schemas import ChatRequest, ChatResponse
from backend.services.llm_service import chat as llm_chat, is_llm_available
from ml.skill_gap import calculate_skill_gaps, calculate_readiness_score

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """Conversational AI assistant with profile context."""
    user = db.query(models.User).filter_by(id=payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    profile = db.query(models.LearnerProfile).filter_by(user_id=payload.user_id).first()

    # Build profile context string
    if profile:
        current_skills = {us.skill_name: us.current_proficiency for us in profile.user_skills}
        skill_gaps = calculate_skill_gaps(current_skills, profile.career_goal, profile.target_skills)
        readiness = calculate_readiness_score(skill_gaps)

        profile_ctx = (
            f"Name: {user.name}\n"
            f"Career Goal: {profile.career_goal}\n"
            f"Experience Level: {profile.experience_level}\n"
            f"Learning Style: {profile.learning_style}\n"
            f"Weekly Hours: {profile.weekly_hours}h\n"
            f"Timeline: {profile.timeline_months} months\n"
            f"Current Skills: {', '.join(f'{k}:{v:.0f}%' for k,v in current_skills.items())}\n"
            f"Readiness Score: {readiness:.1f}%"
        )
        gap_ctx = "\n".join(
            f"{sg['skill']}: {sg['gap_category']} (gap: {sg['gap']:.0f}%)"
            for sg in skill_gaps[:5]
        )
    else:
        profile_ctx = f"Name: {user.name} | No profile set up yet."
        gap_ctx = "No skill gap data available."

    # Load recent chat history
    history = db.query(models.ChatHistory).filter_by(user_id=payload.user_id).order_by(
        models.ChatHistory.created_at.desc()
    ).limit(10).all()
    messages = [{"role": h.role, "content": h.message} for h in reversed(history)]
    messages.append({"role": "user", "content": payload.message})

    # Get AI response
    reply = llm_chat(messages, profile_context=profile_ctx, skill_gap_context=gap_ctx)

    # Save to history
    db.add(models.ChatHistory(user_id=payload.user_id, role="user", message=payload.message))
    db.add(models.ChatHistory(user_id=payload.user_id, role="assistant", message=reply))
    db.commit()

    return ChatResponse(reply=reply, llm_used=is_llm_available())
