"""
Hybrid Recommendation Ranking Engine.
Computes a weighted recommendation score combining:
  30% Skill Gap Match
  25% Goal Relevance
  20% Prerequisite Fit
  10% Difficulty Fit
  10% Learning Preference Match
   5% Feedback Score

Every scored resource includes explanation fields.
"""
from typing import List, Dict, Optional


# Weight configuration (must sum to 1.0)
WEIGHTS = {
    "skill_gap_match": 0.30,
    "goal_relevance": 0.25,
    "prerequisite_fit": 0.20,
    "difficulty_fit": 0.10,
    "preference_match": 0.10,
    "feedback_score": 0.05,
}

DIFFICULTY_ORDER = ["Beginner", "Intermediate", "Advanced"]
DIFFICULTY_RANK = {d: i for i, d in enumerate(DIFFICULTY_ORDER)}

EXPERIENCE_TO_DIFFICULTY = {
    "Beginner": "Beginner",
    "Intermediate": "Intermediate",
    "Advanced": "Advanced",
}

LEARNING_STYLE_RESOURCE = {
    "Video": ["Course"],
    "Text": ["Course", "Article"],
    "Project-based": ["Project", "Course"],
    "Mixed": ["Course", "Project"],
    "Interactive": ["Course", "Project"],
}


def _skill_gap_match_score(resource: Dict, skill_gaps: List[Dict]) -> float:
    """
    How well does this resource address the learner's highest-priority skill gaps?
    Score 0–100.
    """
    resource_skills = [s.lower() for s in resource.get("skills", [])]
    if not resource_skills or not skill_gaps:
        return 0.0

    # Build a priority map: skill → gap value
    gap_map = {sg["skill"].lower(): sg["gap"] for sg in skill_gaps}

    matched_gap_total = 0.0
    max_possible = 0.0

    for skill in resource_skills:
        gap = gap_map.get(skill, 0.0)
        matched_gap_total += gap
        max_possible += 100.0

    if max_possible == 0:
        return 0.0

    score = (matched_gap_total / max_possible) * 100
    return min(score, 100.0)


def _goal_relevance_score(resource: Dict, target_skills: List[str],
                           career_roles: List[str]) -> float:
    """
    How relevant is this resource to the learner's career goal?
    Score 0–100.
    """
    resource_skills = [s.lower() for s in resource.get("skills", [])]
    resource_roles = [r.lower() for r in resource.get("career_roles", [])]

    target_lower = [s.lower() for s in target_skills]
    roles_lower = [r.lower() for r in career_roles]

    # Skill overlap
    skill_overlap = len(set(resource_skills) & set(target_lower))
    skill_score = min((skill_overlap / max(len(target_lower), 1)) * 100, 100)

    # Role overlap
    role_overlap = len(set(resource_roles) & set(roles_lower))
    role_score = min((role_overlap / max(len(roles_lower), 1)) * 100, 100)

    return (skill_score * 0.6 + role_score * 0.4)


def _prerequisite_fit_score(resource: Dict, user_skills: Dict[str, float],
                             knowledge_graph) -> float:
    """
    How many of this resource's prerequisites has the user already satisfied?
    Score 0–100.
    """
    prereqs = resource.get("prerequisites", [])
    if not prereqs:
        return 100.0  # no prerequisites needed = perfect fit

    satisfied = sum(
        1 for p in prereqs
        if user_skills.get(p, 0.0) >= 40.0
    )
    score = (satisfied / len(prereqs)) * 100
    return score


def _difficulty_fit_score(resource: Dict, experience_level: str) -> float:
    """
    How well does the resource difficulty match the learner's experience level?
    Score 0–100.
    """
    resource_diff = resource.get("difficulty", "Intermediate")
    target_diff = EXPERIENCE_TO_DIFFICULTY.get(experience_level, "Intermediate")

    resource_rank = DIFFICULTY_RANK.get(resource_diff, 1)
    target_rank = DIFFICULTY_RANK.get(target_diff, 1)

    diff = abs(resource_rank - target_rank)
    # Perfect match = 100, 1 level off = 60, 2 levels off = 20
    scores = {0: 100.0, 1: 60.0, 2: 20.0}
    return scores.get(diff, 0.0)


def _preference_match_score(resource: Dict, learning_style: str) -> float:
    """
    Does this resource type match the learner's preferred learning style?
    Score 0–100.
    """
    preferred_types = LEARNING_STYLE_RESOURCE.get(learning_style, ["Course", "Project"])
    resource_type = resource.get("resource_type", "Course")
    return 100.0 if resource_type in preferred_types else 30.0


def _feedback_score(resource: Dict, feedback_history: List[Dict]) -> float:
    """
    Learner feedback score for this resource (if any prior feedback exists).
    Score 0–100.
    """
    resource_id = resource.get("id") or resource.get("course_id") or resource.get("project_id")
    for fb in feedback_history:
        if fb.get("resource_id") == resource_id:
            # Convert 1–5 rating to 0–100
            return (fb.get("rating", 3) / 5) * 100
    # No feedback: use resource's own rating if available
    rating = resource.get("rating", 3.5)
    return ((rating - 1) / 4) * 100  # normalize 1–5 → 0–100


def score_resource(
    resource: Dict,
    skill_gaps: List[Dict],
    target_skills: List[str],
    career_roles: List[str],
    user_skills: Dict[str, float],
    experience_level: str,
    learning_style: str,
    feedback_history: List[Dict],
    knowledge_graph=None,
) -> Dict:
    """
    Compute the full hybrid recommendation score for a single resource.
    Returns the resource dict enriched with score fields.
    """
    scores = {
        "skill_gap_match": _skill_gap_match_score(resource, skill_gaps),
        "goal_relevance": _goal_relevance_score(resource, target_skills, career_roles),
        "prerequisite_fit": _prerequisite_fit_score(resource, user_skills, knowledge_graph),
        "difficulty_fit": _difficulty_fit_score(resource, experience_level),
        "preference_match": _preference_match_score(resource, learning_style),
        "feedback_score": _feedback_score(resource, feedback_history),
    }

    # Weighted total
    total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    total = round(min(total, 100.0), 1)

    # --- Generate explanation ---
    reason_parts = []
    resource_skills = resource.get("skills", [])
    prereqs = resource.get("prerequisites", [])

    gap_map = {sg["skill"]: sg for sg in skill_gaps}
    matched_gaps = [s for s in resource_skills if s in gap_map and gap_map[s]["gap"] > 10]

    if matched_gaps:
        top_skill = max(matched_gaps, key=lambda s: gap_map[s]["gap"])
        sg = gap_map[top_skill]
        reason_parts.append(
            f"'{top_skill}' addresses a key skill gap "
            f"(current: {sg['current']:.0f}%, target: {sg['target']:.0f}%)."
        )

    if scores["goal_relevance"] >= 60:
        reason_parts.append(f"Highly relevant to your '{career_roles[0] if career_roles else 'career'}' goal.")

    satisfied_prereqs = [p for p in prereqs if user_skills.get(p, 0) >= 40]
    missing_prereqs = [p for p in prereqs if user_skills.get(p, 0) < 40]
    if satisfied_prereqs:
        reason_parts.append(f"You already satisfy prerequisites: {', '.join(satisfied_prereqs)}.")
    if missing_prereqs:
        reason_parts.append(f"Note: first complete {', '.join(missing_prereqs)}.")

    if scores["difficulty_fit"] == 100:
        reason_parts.append(
            f"Difficulty ({resource.get('difficulty', '')}) matches your {experience_level} level."
        )

    explanation = " ".join(reason_parts) if reason_parts else "Recommended based on your profile."

    result = dict(resource)
    result.update({
        "final_score": total,
        "score_breakdown": scores,
        "explanation": explanation,
        "missing_prerequisites": [p for p in prereqs if user_skills.get(p, 0) < 40],
        "satisfied_prerequisites": [p for p in prereqs if user_skills.get(p, 0) >= 40],
        "matched_skills": [s for s in resource_skills if s in {sg["skill"] for sg in skill_gaps}],
    })
    return result


def rank_resources(
    resources: List[Dict],
    skill_gaps: List[Dict],
    target_skills: List[str],
    career_roles: List[str],
    user_skills: Dict[str, float],
    experience_level: str = "Intermediate",
    learning_style: str = "Mixed",
    feedback_history: List[Dict] = None,
    knowledge_graph=None,
    top_n: int = 20,
) -> List[Dict]:
    """
    Score and rank all candidate resources.
    Returns top_n resources sorted by final_score descending.
    """
    feedback_history = feedback_history or []
    scored = []
    for res in resources:
        scored_res = score_resource(
            resource=res,
            skill_gaps=skill_gaps,
            target_skills=target_skills,
            career_roles=career_roles,
            user_skills=user_skills,
            experience_level=experience_level,
            learning_style=learning_style,
            feedback_history=feedback_history,
            knowledge_graph=knowledge_graph,
        )
        scored.append(scored_res)

    # Sort by final score descending
    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:top_n]
