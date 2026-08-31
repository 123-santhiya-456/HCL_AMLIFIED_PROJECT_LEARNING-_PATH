"""
Skill Gap Analyzer
Computes the gap between current and target skill proficiencies
and classifies each gap by severity.
"""
from typing import Dict, List, Tuple

# Mastery classification thresholds for assessment results
MASTERY_THRESHOLDS = {
    "Beginner": (0, 40),
    "Developing": (41, 70),
    "Proficient": (71, 85),
    "Advanced": (86, 100),
}

GAP_CATEGORIES = [
    (0, 10, "Strong"),
    (11, 30, "Minor Gap"),
    (31, 60, "Moderate Gap"),
    (61, 100, "Major Gap"),
]

# Canonical target proficiencies per career goal (used as fallback)
TARGET_PROFICIENCIES = {
    "AI Engineer": {
        "Python": 95, "Machine Learning": 85, "Deep Learning": 95,
        "NLP": 85, "Transformers": 95, "Embeddings": 95, "RAG": 95,
        "AI Agents": 95, "LLM": 95, "Generative AI": 95,
        "Statistics": 70, "Linear Algebra": 85, "NumPy": 85, "Pandas": 70,
        "FastAPI": 75, "Docker": 70,
    },
    "Data Scientist": {
        "Python": 90, "SQL": 80, "Statistics": 90, "Machine Learning": 95,
        "Deep Learning": 70, "NumPy": 85, "Pandas": 90, "Data Visualization": 80,
        "Feature Engineering": 80, "Explainable AI": 75,
        "Hyperparameter Tuning": 70,
    },
    "ML Engineer": {
        "Python": 90, "Machine Learning": 95, "Deep Learning": 90,
        "MLOps": 90, "Feature Engineering": 90, "Docker": 75,
        "Cloud": 75, "FastAPI": 70, "Statistics": 85,
        "Hyperparameter Tuning": 85,
    },
    "NLP Engineer": {
        "Python": 85, "NLP": 95, "Transformers": 95, "Deep Learning": 85,
        "Machine Learning": 75, "Embeddings": 90, "LLM": 85,
    },
    "Data Analyst": {
        "SQL": 90, "Python": 70, "Data Visualization": 90,
        "Statistics": 80, "Pandas": 85, "Excel": 60,
    },
    "Data Engineer": {
        "Python": 80, "SQL": 90, "Data Engineering": 95, "Docker": 70,
        "Cloud": 70, "Pandas": 80,
    },
}


def classify_gap(gap: float) -> str:
    """Return gap category label based on numeric gap value."""
    for lo, hi, label in GAP_CATEGORIES:
        if lo <= gap <= hi:
            return label
    return "Major Gap"


def get_target_proficiency(skill_name: str, career_goal: str) -> float:
    """Return the target proficiency for a skill given a career goal."""
    goal_key = career_goal.strip().title()
    # Try exact match first
    targets = TARGET_PROFICIENCIES.get(goal_key, {})
    if skill_name in targets:
        return float(targets[skill_name])
    # Keyword-based fallback
    for goal, tgts in TARGET_PROFICIENCIES.items():
        if goal.lower() in career_goal.lower() or career_goal.lower() in goal.lower():
            if skill_name in tgts:
                return float(tgts[skill_name])
    return 80.0  # default target


def calculate_skill_gaps(
    current_skills: Dict[str, float],
    career_goal: str,
    target_skills: List[str] = None,
) -> List[Dict]:
    """
    Calculate skill gaps for a learner.

    Args:
        current_skills: {skill_name: current_proficiency}
        career_goal: Career goal string e.g. "AI Engineer"
        target_skills: Optional list of required skills; inferred from goal if None

    Returns:
        List of skill gap dicts with gap analysis.
    """
    # Determine which skills to include
    goal_key = career_goal.strip().title()
    canonical = TARGET_PROFICIENCIES.get(goal_key, {})
    # Fuzzy match if needed
    if not canonical:
        for goal, tgts in TARGET_PROFICIENCIES.items():
            if goal.lower() in career_goal.lower():
                canonical = tgts
                break

    if target_skills:
        skills_to_check = {s: canonical.get(s, 80.0) for s in target_skills}
    elif canonical:
        skills_to_check = canonical
    else:
        # Generic fallback: just analyse what the user has
        skills_to_check = {s: 80.0 for s in current_skills}

    # Also include skills the user has but aren't in target (so they're shown)
    for s in current_skills:
        if s not in skills_to_check:
            skills_to_check[s] = 80.0

    gaps = []
    for skill_name, target in skills_to_check.items():
        current = current_skills.get(skill_name, 0.0)
        gap = max(0.0, target - current)
        category = classify_gap(gap)
        gaps.append({
            "skill": skill_name,
            "current": current,
            "target": target,
            "gap": gap,
            "gap_category": category,
            "priority": gap,  # higher gap = higher priority
        })

    # Sort by gap descending (biggest gaps first)
    gaps.sort(key=lambda x: x["priority"], reverse=True)
    return gaps


def calculate_readiness_score(skill_gaps: List[Dict]) -> float:
    """
    Overall readiness score: weighted average of (current/target) ratios.
    Returns 0–100.
    """
    if not skill_gaps:
        return 0.0
    total_weight = 0.0
    weighted_sum = 0.0
    for sg in skill_gaps:
        target = sg["target"] if sg["target"] > 0 else 1.0
        current = min(sg["current"], target)
        ratio = current / target
        weight = target  # higher target skills are weighted more
        weighted_sum += ratio * weight
        total_weight += weight
    if total_weight == 0:
        return 0.0
    return round((weighted_sum / total_weight) * 100, 1)


def get_mastery_level(score: float) -> str:
    """Convert a quiz/assessment score to a mastery level label."""
    for level, (lo, hi) in MASTERY_THRESHOLDS.items():
        if lo <= score <= hi:
            return level
    return "Beginner"


def get_priority_skills(skill_gaps: List[Dict], top_n: int = 5) -> List[str]:
    """Return the top N skills to focus on, sorted by gap severity."""
    major = [sg for sg in skill_gaps if sg["gap_category"] in ("Major Gap", "Moderate Gap")]
    return [sg["skill"] for sg in major[:top_n]]
