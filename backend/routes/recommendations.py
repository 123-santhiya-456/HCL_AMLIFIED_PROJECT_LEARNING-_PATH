"""
Recommendations and Learning Path routes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from database import models
from backend.schemas.schemas import (
    RecommendationRequest, RecommendationResponse, RecommendationItem,
    LearningPathRequest, LearningPathResponse, LearningPathItemResponse
)
from ml.recommender import generate_recommendations, generate_learning_path
from ml.embeddings import ensure_index_ready

router = APIRouter()


def _load_user_context(user_id: int, db: Session):
    """Helper: load user and profile from DB."""
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    profile = db.query(models.LearnerProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Complete onboarding first.")
    return user, profile


@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest, db: Session = Depends(get_db)):
    """
    Generate personalized course/project recommendations using the hybrid engine.
    """
    user, profile = _load_user_context(payload.user_id, db)

    current_skills = {us.skill_name: us.current_proficiency for us in profile.user_skills}
    feedback = db.query(models.Feedback).filter_by(user_id=user.id).all()
    feedback_list = [
        {"resource_id": f.resource_id, "rating": f.rating}
        for f in feedback
    ]

    # Ensure FAISS index is ready
    from ml.recommender import get_all_resources_as_dicts
    all_res = get_all_resources_as_dicts(db)
    ensure_index_ready(
        [r for r in all_res if r["resource_type"] == "Course"],
        [r for r in all_res if r["resource_type"] == "Project"],
    )

    result = generate_recommendations(
        career_goal=profile.career_goal,
        current_skills=current_skills,
        target_skills=profile.target_skills,
        experience_level=profile.experience_level,
        learning_style=profile.learning_style,
        db=db,
        feedback_history=feedback_list,
        top_n=payload.top_n,
    )

    items = []
    for rec in result["recommendations"]:
        if payload.resource_type and rec.get("resource_type") != payload.resource_type:
            continue
        rid = rec.get("course_id") or rec.get("project_id") or str(rec.get("id", ""))
        items.append(RecommendationItem(
            resource_id=rid,
            title=rec.get("title", ""),
            description=rec.get("description", ""),
            resource_type=rec.get("resource_type", "Course"),
            skills=rec.get("skills", []),
            difficulty=rec.get("difficulty", "Intermediate"),
            duration_hours=rec.get("duration_hours", 10.0),
            rating=rec.get("rating", 4.0),
            final_score=rec.get("final_score", 0.0),
            explanation=rec.get("explanation", ""),
            matched_skills=rec.get("matched_skills", []),
            missing_prerequisites=rec.get("missing_prerequisites", []),
            satisfied_prerequisites=rec.get("satisfied_prerequisites", []),
            score_breakdown=rec.get("score_breakdown", {}),
        ))

    return RecommendationResponse(
        user_id=payload.user_id,
        readiness_score=result["readiness_score"],
        recommendations=items,
        total_resources_searched=result["total_resources"],
    )


@router.post("/learning-path", response_model=LearningPathResponse)
def create_learning_path(payload: LearningPathRequest, db: Session = Depends(get_db)):
    """
    Generate and store a phased, prerequisite-aware learning path.
    """
    user, profile = _load_user_context(payload.user_id, db)
    current_skills = {us.skill_name: us.current_proficiency for us in profile.user_skills}

    result = generate_learning_path(
        career_goal=profile.career_goal,
        current_skills=current_skills,
        target_skills=profile.target_skills,
        weekly_hours=profile.weekly_hours,
        timeline_months=profile.timeline_months,
        experience_level=profile.experience_level,
        learning_style=profile.learning_style,
        db=db,
    )

    # Save learning path to DB
    existing_path = db.query(models.LearningPath).filter_by(user_id=user.id).first()
    if existing_path:
        db.query(models.LearningPathItem).filter_by(path_id=existing_path.id).delete()
        db.delete(existing_path)
        db.flush()

    lp = models.LearningPath(
        user_id=user.id,
        title=f"{profile.career_goal} Learning Path",
        career_goal=profile.career_goal,
        total_phases=result["total_phases"],
        estimated_weeks=result["estimated_weeks"],
    )
    db.add(lp)
    db.flush()

    for item in result["path_items"]:
        lpi = models.LearningPathItem(
            path_id=lp.id,
            order=item["order"],
            phase=item["phase"],
            skill=item["skill"],
            resource_type=item["resource_type"],
            resource_id=item["resource_id"],
            resource_title=item["resource_title"],
            status=item["status"],
            is_milestone=item["is_milestone"],
            estimated_hours=item["estimated_hours"],
            recommendation_score=item["recommendation_score"],
            explanation=item["explanation"],
        )
        db.add(lpi)

    db.commit()

    path_items_resp = [
        LearningPathItemResponse(
            order=i["order"], phase=i["phase"], skill=i["skill"],
            resource_type=i["resource_type"], resource_id=i["resource_id"],
            resource_title=i["resource_title"], status=i["status"],
            is_milestone=i["is_milestone"], estimated_hours=i["estimated_hours"],
            recommendation_score=i["recommendation_score"],
            explanation=i["explanation"],
            prerequisites=i.get("prerequisites", []),
            missing_prerequisites=i.get("missing_prerequisites", []),
        )
        for i in result["path_items"]
    ]

    return LearningPathResponse(
        user_id=payload.user_id,
        career_goal=result["career_goal"],
        total_phases=result["total_phases"],
        total_hours=result["total_hours"],
        estimated_weeks=result["estimated_weeks"],
        estimated_months=result["estimated_months"],
        readiness_score=result["readiness_score"],
        phases=result["phases"],
        path_items=path_items_resp,
    )


@router.get("/learning-path/{user_id}", response_model=LearningPathResponse)
def get_learning_path(user_id: int, db: Session = Depends(get_db)):
    """Retrieve stored learning path for a user."""
    user, profile = _load_user_context(user_id, db)
    lp = db.query(models.LearningPath).filter_by(user_id=user_id).first()

    if not lp:
        # Auto-generate if not exists
        return create_learning_path(LearningPathRequest(user_id=user_id), db=db)

    items = [
        LearningPathItemResponse(
            order=i.order, phase=i.phase, skill=i.skill or "",
            resource_type=i.resource_type, resource_id=i.resource_id or "",
            resource_title=i.resource_title or "", status=i.status,
            is_milestone=i.is_milestone, estimated_hours=i.estimated_hours,
            recommendation_score=i.recommendation_score,
            explanation=i.explanation or "",
            prerequisites=[], missing_prerequisites=[],
        )
        for i in lp.items
    ]

    current_skills = {us.skill_name: us.current_proficiency for us in profile.user_skills}
    from ml.skill_gap import calculate_skill_gaps, calculate_readiness_score
    skill_gaps = calculate_skill_gaps(current_skills, profile.career_goal, profile.target_skills)
    readiness = calculate_readiness_score(skill_gaps)

    return LearningPathResponse(
        user_id=user_id,
        career_goal=lp.career_goal or profile.career_goal,
        total_phases=lp.total_phases,
        total_hours=sum(i.estimated_hours for i in lp.items),
        estimated_weeks=lp.estimated_weeks,
        estimated_months=round(lp.estimated_weeks / 4),
        readiness_score=readiness,
        phases=[],
        path_items=items,
    )
