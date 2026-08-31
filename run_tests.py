"""
Quick smoke test runner — verifiable without heavy deps.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

errors = []

def check(name, fn):
    try:
        fn()
        print(f"  ✅  {name}")
    except Exception as e:
        print(f"  ❌  {name} — {e}")
        errors.append((name, str(e)))

print("\n=== LearnPath AI — Smoke Tests ===\n")

# ── Skill gap ──────────────────────────────────────────────────
from ml.skill_gap import calculate_skill_gaps, calculate_readiness_score, classify_gap, get_mastery_level

def t_gaps():
    current = {"Python": 80, "Machine Learning": 45, "Deep Learning": 20, "RAG": 0}
    gaps = calculate_skill_gaps(current, "AI Engineer")
    assert len(gaps) > 0
    readiness = calculate_readiness_score(gaps)
    assert 0 <= readiness <= 100

check("Skill gap calculation", t_gaps)
check("Gap classification — Strong",       lambda: assert_(classify_gap(5)  == "Strong"))
check("Gap classification — Moderate Gap", lambda: assert_(classify_gap(45) == "Moderate Gap"))
check("Gap classification — Major Gap",    lambda: assert_(classify_gap(90) == "Major Gap"))
check("Mastery level — Beginner",  lambda: assert_(get_mastery_level(20) == "Beginner"))
check("Mastery level — Developing",lambda: assert_(get_mastery_level(55) == "Developing"))
check("Mastery level — Proficient",lambda: assert_(get_mastery_level(78) == "Proficient"))
check("Mastery level — Advanced",  lambda: assert_(get_mastery_level(93) == "Advanced"))

def assert_(val):
    if not val:
        raise AssertionError("Assertion failed")

# ── Knowledge graph ────────────────────────────────────────────
from ml.knowledge_graph import LearningKnowledgeGraph

def t_kg():
    kg = LearningKnowledgeGraph()
    assert kg.graph.number_of_nodes() > 5
    assert kg.graph.number_of_edges() > 5
    prereqs = kg.get_prerequisites("Deep Learning")
    assert len(prereqs) > 0
    print(f"      nodes={kg.graph.number_of_nodes()}, edges={kg.graph.number_of_edges()}, DL prereqs={len(prereqs)}", end="")

check("Knowledge graph loads + HAS prerequisites", t_kg)

def t_prereq():
    kg = LearningKnowledgeGraph()
    assert kg.is_prerequisite_satisfied("NumPy", {"Python": 80}) == True
    assert kg.is_prerequisite_satisfied("NumPy", {"Python": 20}) == False

check("Prerequisite satisfaction check", t_prereq)

def t_topo():
    kg = LearningKnowledgeGraph()
    skills = ["Deep Learning", "Machine Learning", "Python", "NumPy"]
    ordered = kg.topological_learning_order(skills)
    assert len(ordered) == len(skills)
    if "Python" in ordered and "NumPy" in ordered:
        assert ordered.index("Python") < ordered.index("NumPy")

check("Topological ordering", t_topo)

# ── Ranking ────────────────────────────────────────────────────
from ml.ranking import score_resource, rank_resources

def t_score():
    current = {"Python": 80, "Machine Learning": 45}
    gaps = calculate_skill_gaps(current, "AI Engineer")
    resource = {
        "id": 1, "course_id": "C001", "title": "ML Fundamentals",
        "skills": ["Machine Learning"], "difficulty": "Intermediate",
        "duration_hours": 35, "prerequisites": [],
        "career_roles": ["AI Engineer"], "resource_type": "Course", "rating": 4.9,
    }
    scored = score_resource(resource, gaps, ["Machine Learning"], ["AI Engineer"],
                            current, "Intermediate", "Project-based", [])
    assert 0 <= scored["final_score"] <= 100
    assert len(scored["explanation"]) > 0
    print(f"      score={scored['final_score']:.1f}%", end="")

check("Hybrid recommendation scoring", t_score)

# ── LLM fallback ───────────────────────────────────────────────
from backend.services.llm_service import _keyword_extract_goal

def t_llm_fallback():
    result = _keyword_extract_goal(
        "I want to become an AI Engineer and build RAG applications. I know Python."
    )
    assert "career_goal" in result
    assert len(result["target_skills"]) > 0
    print(f"      goal={result['career_goal']}, skills={result['target_skills'][:3]}", end="")

check("LLM keyword fallback extraction", t_llm_fallback)

# ── DB init ────────────────────────────────────────────────────
def t_db():
    from database.database import init_db, SessionLocal
    init_db()
    db = SessionLocal()
    from database import models
    count = db.query(models.User).count()
    db.close()
    print(f"      users in DB={count}", end="")

check("Database init + query", t_db)

# ── Summary ────────────────────────────────────────────────────
print(f"\n{'='*40}")
if errors:
    print(f"⚠️  {len(errors)} test(s) FAILED:")
    for name, msg in errors:
        print(f"   - {name}: {msg}")
else:
    print("🎉  ALL SMOKE TESTS PASSED!")
print("="*40)
