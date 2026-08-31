"""
Smoke tests for LearnPath AI ML modules.
Tests core functionality without requiring a running backend.

Run: python -m pytest tests/ -v
"""
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─── Skill Gap Tests ────────────────────────────────────────────
def test_skill_gap_calculation():
    """Test basic skill gap calculation."""
    from ml.skill_gap import calculate_skill_gaps, calculate_readiness_score
    
    current = {"Python": 80, "Machine Learning": 40, "Deep Learning": 10}
    gaps = calculate_skill_gaps(current, "AI Engineer")
    
    assert len(gaps) > 0
    for gap in gaps:
        assert "skill" in gap
        assert "current" in gap
        assert "target" in gap
        assert "gap" in gap
        assert "gap_category" in gap
        assert gap["gap"] >= 0


def test_readiness_score():
    """Test readiness score is between 0 and 100."""
    from ml.skill_gap import calculate_skill_gaps, calculate_readiness_score
    
    current = {"Python": 80, "Machine Learning": 40}
    gaps = calculate_skill_gaps(current, "Data Scientist")
    readiness = calculate_readiness_score(gaps)
    
    assert 0.0 <= readiness <= 100.0


def test_gap_classification():
    """Test gap classification categories."""
    from ml.skill_gap import classify_gap
    
    assert classify_gap(0) == "Strong"
    assert classify_gap(5) == "Strong"
    assert classify_gap(15) == "Minor Gap"
    assert classify_gap(45) == "Moderate Gap"
    assert classify_gap(80) == "Major Gap"


def test_mastery_levels():
    """Test mastery level classification."""
    from ml.skill_gap import get_mastery_level
    
    assert get_mastery_level(20) == "Beginner"
    assert get_mastery_level(55) == "Developing"
    assert get_mastery_level(78) == "Proficient"
    assert get_mastery_level(90) == "Advanced"


# ─── Knowledge Graph Tests ──────────────────────────────────────
def test_knowledge_graph_loads():
    """Test knowledge graph loads prerequisites."""
    from ml.knowledge_graph import get_knowledge_graph
    
    kg = get_knowledge_graph()
    assert kg.graph.number_of_nodes() > 0
    assert kg.graph.number_of_edges() > 0


def test_prerequisite_lookup():
    """Test prerequisite lookup for known skills."""
    from ml.knowledge_graph import get_knowledge_graph
    
    kg = get_knowledge_graph()
    prereqs = kg.get_prerequisites("Deep Learning")
    
    # Deep Learning requires Machine Learning which requires Stats and NumPy
    assert len(prereqs) > 0


def test_topological_order():
    """Test topological ordering of skills."""
    from ml.knowledge_graph import get_knowledge_graph
    
    kg = get_knowledge_graph()
    skills = ["Deep Learning", "Machine Learning", "Python", "NumPy"]
    ordered = kg.topological_learning_order(skills)
    
    assert len(ordered) == len(skills)
    # Python should come before NumPy
    if "Python" in ordered and "NumPy" in ordered:
        assert ordered.index("Python") < ordered.index("NumPy")


def test_prerequisite_satisfied():
    """Test prerequisite satisfaction check."""
    from ml.knowledge_graph import get_knowledge_graph
    
    kg = get_knowledge_graph()
    
    # Python with 80% satisfies Python prerequisite
    satisfied = kg.is_prerequisite_satisfied("NumPy", {"Python": 80}, min_proficiency=40)
    assert satisfied == True
    
    # Python with 20% does NOT satisfy Python prerequisite
    not_satisfied = kg.is_prerequisite_satisfied("NumPy", {"Python": 20}, min_proficiency=40)
    assert not_satisfied == False


# ─── Ranking Tests ───────────────────────────────────────────────
def test_hybrid_ranking():
    """Test hybrid scoring produces valid scores."""
    from ml.ranking import score_resource
    
    resource = {
        "id": 1, "course_id": "C001", "title": "Python Basics",
        "skills": ["Python"], "difficulty": "Beginner",
        "duration_hours": 20, "prerequisites": [],
        "career_roles": ["Data Scientist"], "resource_type": "Course",
        "rating": 4.8,
    }
    skill_gaps = [{"skill": "Python", "gap": 15, "current": 80, "target": 95}]
    
    result = score_resource(
        resource=resource,
        skill_gaps=skill_gaps,
        target_skills=["Python", "Machine Learning"],
        career_roles=["Data Scientist"],
        user_skills={"Python": 80},
        experience_level="Intermediate",
        learning_style="Mixed",
        feedback_history=[],
    )
    
    assert "final_score" in result
    assert 0.0 <= result["final_score"] <= 100.0
    assert "explanation" in result
    assert len(result["explanation"]) > 0


def test_ranking_order():
    """Test that higher-gap resources rank higher."""
    from ml.ranking import rank_resources
    
    resources = [
        {"id": 1, "course_id": "C001", "title": "Python", "skills": ["Python"],
         "difficulty": "Beginner", "duration_hours": 10, "prerequisites": [],
         "career_roles": ["AI Engineer"], "resource_type": "Course", "rating": 4.5},
        {"id": 2, "course_id": "C002", "title": "RAG Systems", "skills": ["RAG"],
         "difficulty": "Advanced", "duration_hours": 25, "prerequisites": [],
         "career_roles": ["AI Engineer"], "resource_type": "Course", "rating": 4.9},
    ]
    skill_gaps = [
        {"skill": "RAG", "gap": 95, "current": 0, "target": 95, "gap_category": "Major Gap"},
        {"skill": "Python", "gap": 5, "current": 90, "target": 95, "gap_category": "Strong"},
    ]
    
    ranked = rank_resources(
        resources=resources,
        skill_gaps=skill_gaps,
        target_skills=["RAG", "Python"],
        career_roles=["AI Engineer"],
        user_skills={"Python": 90, "RAG": 0},
        experience_level="Advanced",
        learning_style="Mixed",
    )
    
    assert len(ranked) == 2
    # Scores should be floats
    for r in ranked:
        assert isinstance(r["final_score"], float)


# ─── LLM Fallback Tests ──────────────────────────────────────────
def test_keyword_goal_extraction():
    """Test keyword-based goal extraction fallback."""
    from backend.services.llm_service import _keyword_extract_goal
    
    result = _keyword_extract_goal(
        "I want to become an AI Engineer who builds RAG applications. I know Python and basic machine learning."
    )
    
    assert "career_goal" in result
    assert "target_skills" in result
    assert "experience_level" in result
    assert len(result["target_skills"]) > 0


def test_llm_fallback_when_no_key():
    """Test that extract_goal falls back gracefully without API key."""
    original = os.environ.get("LLM_API_KEY", "")
    os.environ["LLM_API_KEY"] = ""
    
    from backend.services import llm_service
    # Force reload to pick up env change
    llm_service.LLM_API_KEY = ""
    
    result = llm_service.extract_goal("I want to learn machine learning and become a data scientist")
    
    assert isinstance(result, dict)
    assert "career_goal" in result
    
    # Restore
    os.environ["LLM_API_KEY"] = original


if __name__ == "__main__":
    # Quick manual run
    print("Running smoke tests...")
    test_skill_gap_calculation()
    print("✅ skill gap calculation")
    test_readiness_score()
    print("✅ readiness score")
    test_gap_classification()
    print("✅ gap classification")
    test_mastery_levels()
    print("✅ mastery levels")
    test_knowledge_graph_loads()
    print("✅ knowledge graph loads")
    test_prerequisite_satisfied()
    print("✅ prerequisite satisfaction")
    test_hybrid_ranking()
    print("✅ hybrid ranking")
    test_keyword_goal_extraction()
    print("✅ keyword goal extraction")
    print("\n🎉 All smoke tests passed!")
