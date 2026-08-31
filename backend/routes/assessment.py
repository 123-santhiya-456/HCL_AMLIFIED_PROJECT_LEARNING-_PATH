"""
Assessment / Quiz routes.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from database import models
from backend.schemas.schemas import AssessmentResponse, AssessmentQuestion, AssessmentSubmit, AssessmentResult
from ml.skill_gap import get_mastery_level

router = APIRouter()

PASS_THRESHOLD = 70.0  # percent to pass


@router.get("/assessment/{skill}", response_model=AssessmentResponse)
def get_assessment(skill: str, db: Session = Depends(get_db)):
    """Get a quiz for a specific skill."""
    assessment = db.query(models.Assessment).filter(
        models.Assessment.skill.ilike(f"%{skill}%")
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail=f"No assessment found for skill: {skill}")

    questions = [
        AssessmentQuestion(
            id=q["id"],
            question=q["question"],
            options=q["options"],
            skill=skill,
            difficulty=assessment.difficulty,
        )
        for q in assessment.questions
    ]

    return AssessmentResponse(
        quiz_id=assessment.quiz_id,
        skill=assessment.skill,
        difficulty=assessment.difficulty,
        total_questions=assessment.total_questions,
        questions=questions,
    )


@router.post("/assessment/result", response_model=AssessmentResult)
def submit_assessment(payload: AssessmentSubmit, db: Session = Depends(get_db)):
    """Submit quiz answers and get scored result with adaptive feedback."""
    assessment = db.query(models.Assessment).filter_by(quiz_id=payload.quiz_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    # Score the answers
    correct = 0
    total = len(assessment.questions)
    for q in assessment.questions:
        qid = str(q["id"])
        submitted_answer = payload.answers.get(qid)
        if submitted_answer is not None and submitted_answer == q["answer"]:
            correct += 1

    score_percent = (correct / total * 100) if total > 0 else 0.0
    passed = score_percent >= PASS_THRESHOLD
    mastery_level = get_mastery_level(score_percent)

    # Adaptive feedback
    if mastery_level == "Beginner":
        next_action = "revision"
        feedback = (
            f"Your mastery is at Beginner level ({score_percent:.0f}%). "
            "We recommend starting with the foundational course and reviewing core concepts "
            "before attempting the assessment again."
        )
    elif mastery_level == "Developing":
        next_action = "revision"
        feedback = (
            f"You're at Developing level ({score_percent:.0f}%). Good progress! "
            "Review the sections you missed and try a practice project "
            "before moving to the next skill."
        )
    elif mastery_level == "Proficient":
        next_action = "next_skill"
        feedback = (
            f"Great work! You're Proficient ({score_percent:.0f}%). "
            "You can proceed to the next skill in your learning path. "
            "Consider doing the practice project to solidify your understanding."
        )
    else:  # Advanced
        next_action = "unlock_advanced"
        feedback = (
            f"Excellent! Advanced mastery ({score_percent:.0f}%). "
            "The next advanced topic in your path is now unlocked. Keep it up!"
        )

    # Save result
    result_rec = models.AssessmentResult(
        user_id=payload.user_id,
        quiz_id=payload.quiz_id,
        skill=assessment.skill,
        score_percent=score_percent,
        mastery_level=mastery_level,
        passed=passed,
        answers=payload.answers,
    )
    db.add(result_rec)

    # Update user skill proficiency based on score
    profile = db.query(models.LearnerProfile).filter_by(user_id=payload.user_id).first()
    if profile:
        user_skill = db.query(models.UserSkill).filter_by(
            profile_id=profile.id, skill_name=assessment.skill
        ).first()
        if user_skill:
            # Blend: 60% existing + 40% quiz score
            new_prof = user_skill.current_proficiency * 0.6 + score_percent * 0.4
            user_skill.current_proficiency = round(new_prof, 1)
            gap = max(0.0, user_skill.target_proficiency - new_prof)
            user_skill.gap = round(gap, 1)

            from ml.skill_gap import classify_gap
            user_skill.gap_category = classify_gap(gap)

    db.commit()

    return AssessmentResult(
        user_id=payload.user_id,
        quiz_id=payload.quiz_id,
        skill=assessment.skill,
        score_percent=score_percent,
        mastery_level=mastery_level,
        passed=passed,
        correct_count=correct,
        total_questions=total,
        next_action=next_action,
        feedback=feedback,
    )
