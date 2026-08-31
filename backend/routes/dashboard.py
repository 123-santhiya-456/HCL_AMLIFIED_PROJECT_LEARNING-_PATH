"""
Dashboard summary route.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from backend.schemas.schemas import DashboardResponse
from ml.skill_gap import calculate_skill_gaps, calculate_readiness_score

router = APIRouter()


@router.get("/dashboard/{user_id}", response_model=DashboardResponse)
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    """Dashboard summary combining profile, progress, and next recommended action."""
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    profile = db.query(models.LearnerProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    # Skill gaps
    current_skills = {us.skill_name: us.current_proficiency for us in profile.user_skills}
    skill_gaps = calculate_skill_gaps(current_skills, profile.career_goal, profile.target_skills)
    readiness = calculate_readiness_score(skill_gaps)

    # Progress
    progress_items = db.query(models.Progress).filter_by(user_id=user_id).all()
    overall_completion = (
        sum(p.completion_percent for p in progress_items) / len(progress_items)
        if progress_items else 0.0
    )
    courses_completed = sum(1 for p in progress_items if p.resource_type == "Course" and p.completed)
    projects_completed = sum(1 for p in progress_items if p.resource_type == "Project" and p.completed)

    # Assessment results
    assessment_results = db.query(models.AssessmentResult).filter_by(user_id=user_id).all()
    assessments_taken = len(assessment_results)
    skills_mastered = list(set(
        ar.skill for ar in assessment_results if ar.mastery_level in ("Proficient", "Advanced")
    ))

    # Current phase from learning path
    lp = db.query(models.LearningPath).filter_by(user_id=user_id).first()
    current_phase = "Getting Started"
    next_action = "Complete your profile to get started!"
    if lp:
        in_progress = next(
            (i for i in lp.items if i.status == "in_progress"), None
        )
        available = next(
            (i for i in lp.items if i.status == "available"), None
        )
        if in_progress:
            current_phase = f"Phase {in_progress.phase}: {in_progress.skill}"
            next_action = f"Continue: {in_progress.resource_title}"
        elif available:
            current_phase = f"Phase {available.phase}: {available.skill}"
            next_action = f"Start: {available.resource_title}"
        else:
            # Use top priority skill gap
            top_gap = skill_gaps[0] if skill_gaps else None
            if top_gap:
                current_phase = top_gap["skill"]
                next_action = f"Begin learning: {top_gap['skill']}"

    recent_progress = [
        {
            "resource_id": p.resource_id,
            "resource_type": p.resource_type,
            "completion_percent": p.completion_percent,
        }
        for p in sorted(progress_items, key=lambda x: x.updated_at, reverse=True)[:5]
    ]

    return DashboardResponse(
        user_id=user_id,
        name=user.name,
        career_goal=profile.career_goal,
        readiness_score=round(readiness, 1),
        current_phase=current_phase,
        next_action=next_action,
        overall_completion=round(overall_completion, 1),
        courses_completed=courses_completed,
        projects_completed=projects_completed,
        assessments_taken=assessments_taken,
        skills_mastered=skills_mastered,
        recent_activity=recent_progress,
    )
