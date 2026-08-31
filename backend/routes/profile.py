"""
Profile routes — create/read/update learner profiles.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime

from database.database import get_db
from database import models
from backend.schemas.schemas import ProfileCreate, ProfileResponse
from ml.skill_gap import (
    calculate_skill_gaps, calculate_readiness_score,
    get_target_proficiency, classify_gap
)

router = APIRouter()


def _get_or_create_user(db: Session, name: str, email: str = None) -> models.User:
    """Get existing user by email/name or create a new one."""
    if email:
        user = db.query(models.User).filter_by(email=email).first()
        if user:
            return user
    user = db.query(models.User).filter_by(name=name).first()
    if user:
        return user
    user = models.User(name=name, email=email)
    db.add(user)
    db.flush()
    return user


@router.post("/profile", response_model=ProfileResponse)
def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    """Create or update a learner profile."""
    user = _get_or_create_user(db, payload.name, payload.email)

    # Delete existing profile if re-creating
    existing = db.query(models.LearnerProfile).filter_by(user_id=user.id).first()
    if existing:
        db.query(models.UserSkill).filter_by(profile_id=existing.id).delete()
        db.delete(existing)
        db.flush()

    # Compute skill gaps to derive readiness score
    current_skills = {s.skill_name: s.current_proficiency for s in payload.skills}
    skill_gaps = calculate_skill_gaps(current_skills, payload.career_goal, payload.target_skills)
    readiness = calculate_readiness_score(skill_gaps)

    profile = models.LearnerProfile(
        user_id=user.id,
        career_goal=payload.career_goal,
        career_goal_raw=payload.career_goal_raw,
        experience_level=payload.experience_level,
        education=payload.education,
        interests=payload.interests,
        learning_style=payload.learning_style,
        weekly_hours=payload.weekly_hours,
        timeline_months=payload.timeline_months,
        target_skills=payload.target_skills,
        completed_courses=payload.completed_courses,
        readiness_score=readiness,
    )
    db.add(profile)
    db.flush()

    # Store user skills
    for s_input in payload.skills:
        target = s_input.target_proficiency or get_target_proficiency(
            s_input.skill_name, payload.career_goal
        )
        gap = max(0.0, target - s_input.current_proficiency)
        us = models.UserSkill(
            profile_id=profile.id,
            skill_name=s_input.skill_name,
            current_proficiency=s_input.current_proficiency,
            target_proficiency=target,
            gap=gap,
            gap_category=classify_gap(gap),
        )
        db.add(us)

    db.commit()

    skill_list = [
        {
            "skill_name": us.skill_name,
            "current_proficiency": us.current_proficiency,
            "target_proficiency": us.target_proficiency,
            "gap": us.gap,
            "gap_category": us.gap_category,
        }
        for us in db.query(models.UserSkill).filter_by(profile_id=profile.id).all()
    ]

    return ProfileResponse(
        user_id=user.id,
        name=user.name,
        career_goal=profile.career_goal,
        experience_level=profile.experience_level,
        learning_style=profile.learning_style,
        weekly_hours=profile.weekly_hours,
        timeline_months=profile.timeline_months,
        target_skills=profile.target_skills,
        readiness_score=readiness,
        skills=skill_list,
    )


@router.get("/profile/{user_id}", response_model=ProfileResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a learner profile by user ID."""
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    profile = db.query(models.LearnerProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    skill_list = [
        {
            "skill_name": us.skill_name,
            "current_proficiency": us.current_proficiency,
            "target_proficiency": us.target_proficiency,
            "gap": us.gap,
            "gap_category": us.gap_category,
        }
        for us in profile.user_skills
    ]

    return ProfileResponse(
        user_id=user.id,
        name=user.name,
        career_goal=profile.career_goal,
        experience_level=profile.experience_level,
        learning_style=profile.learning_style,
        weekly_hours=profile.weekly_hours,
        timeline_months=profile.timeline_months,
        target_skills=profile.target_skills,
        readiness_score=profile.readiness_score,
        skills=skill_list,
    )
