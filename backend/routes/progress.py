"""
Progress and Feedback routes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from backend.schemas.schemas import ProgressUpdate, ProgressResponse, FeedbackSubmit

router = APIRouter()


@router.post("/progress")
def update_progress(payload: ProgressUpdate, db: Session = Depends(get_db)):
    """Update completion progress for a resource."""
    # Check if exists
    prog = db.query(models.Progress).filter_by(
        user_id=payload.user_id,
        resource_id=payload.resource_id,
    ).first()

    if prog:
        prog.completion_percent = payload.completion_percent
        prog.time_spent_hours += payload.time_spent_hours
        prog.updated_at = datetime.datetime.utcnow()
        if payload.completion_percent >= 100.0:
            prog.completed = True
            prog.completed_at = datetime.datetime.utcnow()
    else:
        prog = models.Progress(
            user_id=payload.user_id,
            resource_id=payload.resource_id,
            resource_type=payload.resource_type,
            completion_percent=payload.completion_percent,
            time_spent_hours=payload.time_spent_hours,
            completed=payload.completion_percent >= 100.0,
            completed_at=datetime.datetime.utcnow() if payload.completion_percent >= 100 else None,
        )
        db.add(prog)

    db.commit()
    return {"status": "updated", "completion_percent": payload.completion_percent}


@router.get("/progress/{user_id}", response_model=ProgressResponse)
def get_progress(user_id: int, db: Session = Depends(get_db)):
    """Get full progress summary for a user."""
    user = db.query(models.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    progress_items = db.query(models.Progress).filter_by(user_id=user_id).all()
    assessment_results = db.query(models.AssessmentResult).filter_by(user_id=user_id).all()

    # Compute overall
    if progress_items:
        overall_completion = sum(p.completion_percent for p in progress_items) / len(progress_items)
    else:
        overall_completion = 0.0

    courses_completed = sum(1 for p in progress_items
                            if p.resource_type == "Course" and p.completed)
    projects_completed = sum(1 for p in progress_items
                             if p.resource_type == "Project" and p.completed)
    assessments_taken = len(assessment_results)

    # Skills mastered: assessment_result where mastery is Proficient or Advanced
    skills_mastered = list(set(
        ar.skill for ar in assessment_results
        if ar.mastery_level in ("Proficient", "Advanced")
    ))

    # Current streak (simplified: days since first completion)
    completed_dates = [p.completed_at for p in progress_items if p.completed_at]
    current_streak = len(set(d.date() for d in completed_dates)) if completed_dates else 0

    progress_list = [
        {
            "resource_id": p.resource_id,
            "resource_type": p.resource_type,
            "completion_percent": p.completion_percent,
            "time_spent_hours": p.time_spent_hours,
            "completed": p.completed,
        }
        for p in progress_items
    ]

    return ProgressResponse(
        user_id=user_id,
        overall_completion=round(overall_completion, 1),
        courses_completed=courses_completed,
        projects_completed=projects_completed,
        assessments_taken=assessments_taken,
        skills_mastered=skills_mastered,
        current_streak=current_streak,
        progress_items=progress_list,
    )


@router.post("/feedback")
def submit_feedback(payload: FeedbackSubmit, db: Session = Depends(get_db)):
    """Submit user feedback/rating for a resource."""
    fb = models.Feedback(
        user_id=payload.user_id,
        resource_id=payload.resource_id,
        resource_type=payload.resource_type,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(fb)
    db.commit()
    return {"status": "feedback recorded", "rating": payload.rating}
