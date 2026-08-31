"""
Analysis routes — goal understanding and skill gap analysis.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from backend.schemas.schemas import (
    GoalInput, GoalResponse, SkillGapRequest, SkillGapResponse, SkillGapItem
)
from backend.services.llm_service import extract_goal, is_llm_available
from ml.skill_gap import calculate_skill_gaps, calculate_readiness_score, get_priority_skills

router = APIRouter()


@router.post("/analyze-goal", response_model=GoalResponse)
def analyze_goal(payload: GoalInput, db: Session = Depends(get_db)):
    """
    Extract structured career goal information from natural-language text.
    Uses LLM with keyword-based fallback.
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Goal text cannot be empty.")

    llm_available = is_llm_available()
    result = extract_goal(payload.text)

    return GoalResponse(
        career_goal=result.get("career_goal", "AI Engineer"),
        target_skills=result.get("target_skills", []),
        current_skills=result.get("current_skills", []),
        experience_level=result.get("experience_level", "Intermediate"),
        interests=result.get("interests", []),
        llm_used=llm_available,
    )


@router.post("/skill-gap", response_model=SkillGapResponse)
def get_skill_gap(payload: SkillGapRequest, db: Session = Depends(get_db)):
    """
    Calculate skill gaps for a user based on their stored profile.
    """
    profile = db.query(models.LearnerProfile).filter_by(user_id=payload.user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please complete onboarding first.")

    current_skills = {us.skill_name: us.current_proficiency for us in profile.user_skills}
    skill_gaps = calculate_skill_gaps(current_skills, profile.career_goal, profile.target_skills)
    readiness = calculate_readiness_score(skill_gaps)
    priority = get_priority_skills(skill_gaps)

    # Update stored readiness
    profile.readiness_score = readiness
    db.commit()

    gap_items = [SkillGapItem(**sg) for sg in skill_gaps]
    return SkillGapResponse(
        user_id=payload.user_id,
        readiness_score=readiness,
        skill_gaps=gap_items,
        priority_skills=priority,
    )
