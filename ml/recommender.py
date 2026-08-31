"""
Recommendation Orchestrator.
Ties together skill-gap analysis, knowledge graph,
semantic search, and hybrid ranking to produce
personalized learning recommendations and roadmaps.
"""
import os
import sys
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.skill_gap import calculate_skill_gaps, calculate_readiness_score, get_priority_skills
from ml.knowledge_graph import get_knowledge_graph
from ml.embeddings import semantic_search, ensure_index_ready
from ml.ranking import rank_resources


def _career_goal_to_roles(career_goal: str) -> List[str]:
    """Map a career goal string to a list of canonical role names."""
    goal_lower = career_goal.lower()
    role_map = {
        "ai engineer": ["AI Engineer"],
        "data scientist": ["Data Scientist"],
        "ml engineer": ["ML Engineer"],
        "machine learning engineer": ["ML Engineer"],
        "nlp engineer": ["NLP Engineer"],
        "data analyst": ["Data Analyst"],
        "data engineer": ["Data Engineer"],
        "full stack": ["Full Stack Developer"],
        "backend": ["Backend Developer"],
        "computer vision": ["Computer Vision Engineer"],
        "research": ["Research Scientist"],
    }
    for key, roles in role_map.items():
        if key in goal_lower:
            return roles
    # Default: return the goal itself as a role
    return [career_goal.split()[0:2] and " ".join(career_goal.split()[:2]) or career_goal]


def get_all_resources_as_dicts(db) -> List[Dict]:
    """Fetch all courses and projects from DB as plain dicts."""
    from database.models import Course, Project
    courses = db.query(Course).all()
    projects = db.query(Project).all()

    resources = []
    for c in courses:
        resources.append({
            "id": c.id,
            "course_id": c.course_id,
            "title": c.title,
            "description": c.description,
            "skills": c.skills or [],
            "difficulty": c.difficulty,
            "duration_hours": c.duration_hours,
            "prerequisites": c.prerequisites or [],
            "career_roles": c.career_roles or [],
            "resource_type": "Course",
            "rating": c.rating,
        })
    for p in projects:
        resources.append({
            "id": p.id,
            "project_id": p.project_id,
            "title": p.title,
            "description": p.description,
            "skills": p.skills or [],
            "difficulty": p.difficulty,
            "duration_hours": p.duration_hours,
            "prerequisites": [],
            "career_roles": p.career_roles or [],
            "resource_type": "Project",
            "rating": 4.5,
        })
    return resources


def generate_recommendations(
    career_goal: str,
    current_skills: Dict[str, float],
    target_skills: List[str],
    experience_level: str,
    learning_style: str,
    db,
    feedback_history: List[Dict] = None,
    top_n: int = 15,
) -> Dict:
    """
    Main recommendation function.

    Steps:
    1. Calculate skill gaps
    2. Get all resources from DB
    3. Semantic search (if embeddings available)
    4. Hybrid ranking
    5. Return ranked recommendations + readiness info
    """
    # Step 1: Skill gap analysis
    skill_gaps = calculate_skill_gaps(current_skills, career_goal, target_skills)
    readiness = calculate_readiness_score(skill_gaps)
    priority_skills = get_priority_skills(skill_gaps, top_n=5)

    # Step 2: Get all resources
    all_resources = get_all_resources_as_dicts(db)

    # Step 3: Semantic search for query
    query = f"{career_goal} {' '.join(target_skills or priority_skills)}"
    semantic_results = semantic_search(query, top_k=50)

    # Build semantic score map
    sem_map: Dict[str, float] = {}
    for sr in semantic_results:
        rid = sr.get("course_id") or sr.get("project_id") or str(sr.get("id", ""))
        sem_map[rid] = sr.get("semantic_score", 0.0)

    # Inject semantic scores into all_resources
    for res in all_resources:
        rid = res.get("course_id") or res.get("project_id") or str(res.get("id", ""))
        res["semantic_score"] = sem_map.get(rid, 0.0)

    # Step 4: Hybrid ranking
    career_roles = _career_goal_to_roles(career_goal)
    kg = get_knowledge_graph()

    ranked = rank_resources(
        resources=all_resources,
        skill_gaps=skill_gaps,
        target_skills=target_skills or priority_skills,
        career_roles=career_roles,
        user_skills=current_skills,
        experience_level=experience_level,
        learning_style=learning_style,
        feedback_history=feedback_history or [],
        knowledge_graph=kg,
        top_n=top_n,
    )

    return {
        "skill_gaps": skill_gaps,
        "readiness_score": readiness,
        "priority_skills": priority_skills,
        "recommendations": ranked,
        "total_resources": len(all_resources),
    }


def generate_learning_path(
    career_goal: str,
    current_skills: Dict[str, float],
    target_skills: List[str],
    weekly_hours: float,
    timeline_months: int,
    experience_level: str,
    learning_style: str,
    db,
) -> Dict:
    """
    Generate a phased, prerequisite-aware learning roadmap.
    """
    # Get recommendations to find best resource per skill
    rec_result = generate_recommendations(
        career_goal=career_goal,
        current_skills=current_skills,
        target_skills=target_skills,
        experience_level=experience_level,
        learning_style=learning_style,
        db=db,
        top_n=50,
    )

    skill_gaps = rec_result["skill_gaps"]
    recommendations = rec_result["recommendations"]
    readiness = rec_result["readiness_score"]

    # Knowledge graph phases
    kg = get_knowledge_graph()
    phases = kg.generate_learning_phases(
        target_skills=target_skills,
        user_skills=current_skills,
        skill_gaps=skill_gaps,
        career_goal=career_goal,
    )

    # Build a map: skill → best recommended resource
    skill_to_resource: Dict[str, Dict] = {}
    skill_to_project: Dict[str, Dict] = {}

    for rec in recommendations:
        for skill in rec.get("skills", []):
            if skill not in skill_to_resource and rec["resource_type"] == "Course":
                skill_to_resource[skill] = rec
            elif skill not in skill_to_project and rec["resource_type"] == "Project":
                skill_to_project[skill] = rec

    # Assemble path items
    path_items = []
    total_hours = 0.0
    phase_num = 0

    for phase_info in phases:
        skill = phase_info["skill"]
        phase_num += 1

        # Find best course for this skill
        course = skill_to_resource.get(skill)
        project = skill_to_project.get(skill)

        # Course item
        if course:
            path_items.append({
                "order": len(path_items) + 1,
                "phase": phase_num,
                "skill": skill,
                "resource_type": "Course",
                "resource_id": course.get("course_id", ""),
                "resource_title": course.get("title", ""),
                "status": phase_info["status"],
                "is_milestone": False,
                "estimated_hours": course.get("duration_hours", 10),
                "recommendation_score": course.get("final_score", 0.0),
                "explanation": course.get("explanation", ""),
                "prerequisites": phase_info.get("prerequisites", []),
                "missing_prerequisites": phase_info.get("missing_prerequisites", []),
                "gap": phase_info.get("gap", 0),
                "gap_category": phase_info.get("gap_category", ""),
            })
            total_hours += course.get("duration_hours", 10)

        # Assessment milestone
        path_items.append({
            "order": len(path_items) + 1,
            "phase": phase_num,
            "skill": skill,
            "resource_type": "Assessment",
            "resource_id": f"ASSESS_{skill.upper().replace(' ', '_')}",
            "resource_title": f"{skill} Assessment",
            "status": "locked" if phase_info["status"] == "locked" else phase_info["status"],
            "is_milestone": True,
            "estimated_hours": 1.0,
            "recommendation_score": 0.0,
            "explanation": f"Assessment to validate {skill} mastery before proceeding.",
            "prerequisites": [skill],
            "missing_prerequisites": [],
            "gap": 0,
            "gap_category": "",
        })
        total_hours += 1.0

        # Add project for major-gap skills
        if project and phase_info.get("gap_category") in ("Major Gap", "Moderate Gap"):
            path_items.append({
                "order": len(path_items) + 1,
                "phase": phase_num,
                "skill": skill,
                "resource_type": "Project",
                "resource_id": project.get("project_id", ""),
                "resource_title": project.get("title", ""),
                "status": "locked" if phase_info["status"] == "locked" else phase_info["status"],
                "is_milestone": False,
                "estimated_hours": project.get("duration_hours", 15),
                "recommendation_score": project.get("final_score", 0.0),
                "explanation": project.get("explanation", ""),
                "prerequisites": [],
                "missing_prerequisites": [],
                "gap": 0,
                "gap_category": "",
            })
            total_hours += project.get("duration_hours", 15)

    # Calculate timeline
    weekly_hours = max(weekly_hours, 1.0)
    total_weeks = round(total_hours / weekly_hours)
    actual_months = round(total_weeks / 4)

    return {
        "phases": phases,
        "path_items": path_items,
        "total_phases": phase_num,
        "total_hours": round(total_hours, 1),
        "estimated_weeks": total_weeks,
        "estimated_months": actual_months,
        "readiness_score": readiness,
        "skill_gaps": skill_gaps,
        "career_goal": career_goal,
    }
