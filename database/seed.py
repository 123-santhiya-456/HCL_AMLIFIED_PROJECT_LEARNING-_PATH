"""
Database seeder — populates courses, projects, skills, prerequisites,
assessments, and creates the demo user 'Santhiya'.

Run:  python database/seed.py
"""
import sys, os, json, csv, ast
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal, init_db, engine
from database import models

# ────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def parse_list(value: str) -> list:
    """Parse a semicolon-separated or comma-separated string into a list."""
    if not value or value.strip().lower() in ("none", "", "nan"):
        return []
    return [v.strip() for v in value.split(";") if v.strip()]


def seed_skills(db):
    if db.query(models.Skill).count() > 0:
        print("  Skills already seeded, skipping.")
        return
    path = os.path.join(DATA_DIR, "skills.csv")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            skill = models.Skill(
                skill_id=row["skill_id"],
                name=row["skill_name"],
                domain=row["domain"],
                description=row["description"],
                target_proficiencies={
                    "Data Scientist": float(row.get("target_proficiency_data_scientist", 70)),
                    "AI Engineer": float(row.get("target_proficiency_ai_engineer", 70)),
                    "ML Engineer": float(row.get("target_proficiency_ml_engineer", 70)),
                    "NLP Engineer": float(row.get("target_proficiency_nlp_engineer", 70)),
                    "Data Analyst": float(row.get("target_proficiency_data_analyst", 70)),
                    "Data Engineer": float(row.get("target_proficiency_data_engineer", 70)),
                }
            )
            db.add(skill)
    db.commit()
    print(f"  ✅ Skills seeded.")


def seed_courses(db):
    if db.query(models.Course).count() > 0:
        print("  Courses already seeded, skipping.")
        return
    path = os.path.join(DATA_DIR, "courses.csv")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            course = models.Course(
                course_id=row["course_id"],
                title=row["title"],
                description=row["description"],
                skills=parse_list(row.get("skills", "")),
                difficulty=row.get("difficulty", "Intermediate"),
                duration_hours=float(row.get("duration_hours", 10)),
                prerequisites=parse_list(row.get("prerequisites", "")),
                career_roles=parse_list(row.get("career_roles", "")),
                resource_type=row.get("resource_type", "Course"),
                rating=float(row.get("rating", 4.0)),
            )
            db.add(course)
    db.commit()
    print(f"  ✅ Courses seeded.")


def seed_projects(db):
    if db.query(models.Project).count() > 0:
        print("  Projects already seeded, skipping.")
        return
    path = os.path.join(DATA_DIR, "projects.csv")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            project = models.Project(
                project_id=row["project_id"],
                title=row["title"],
                description=row["description"],
                skills=parse_list(row.get("skills", "")),
                difficulty=row.get("difficulty", "Intermediate"),
                duration_hours=float(row.get("duration_hours", 15)),
                career_roles=parse_list(row.get("career_roles", "")),
            )
            db.add(project)
    db.commit()
    print(f"  ✅ Projects seeded.")


def seed_assessments(db):
    if db.query(models.Assessment).count() > 0:
        print("  Assessments already seeded, skipping.")
        return
    path = os.path.join(DATA_DIR, "quizzes.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for quiz in data["quizzes"]:
        assessment = models.Assessment(
            quiz_id=quiz["quiz_id"],
            skill=quiz["skill"],
            difficulty=quiz["difficulty"],
            total_questions=len(quiz["questions"]),
            questions=quiz["questions"],
        )
        db.add(assessment)
    db.commit()
    print(f"  ✅ Assessments seeded.")


def seed_demo_user(db):
    """Create the demo learner 'Santhiya' for hackathon demonstration."""
    existing = db.query(models.User).filter_by(name="Santhiya").first()
    if existing:
        print("  Demo user already exists, skipping.")
        return

    # Create user
    user = models.User(name="Santhiya", email="santhiya@demo.learnpath.ai")
    db.add(user)
    db.flush()

    # Create learner profile
    profile = models.LearnerProfile(
        user_id=user.id,
        career_goal="AI Engineer",
        career_goal_raw="I want to become an AI Engineer and learn Generative AI and build RAG applications.",
        experience_level="Intermediate",
        education="B.Tech Computer Science",
        interests=["Generative AI", "RAG", "AI Agents", "LLMs"],
        learning_style="Project-based",
        weekly_hours=10.0,
        timeline_months=6,
        target_skills=["Python", "Machine Learning", "Deep Learning", "NLP",
                        "Transformers", "Embeddings", "RAG", "AI Agents", "LLM", "Generative AI"],
        completed_courses=[],
        readiness_score=46.0,
    )
    db.add(profile)
    db.flush()

    # Create user skills
    demo_skills = [
        ("Python", 80, 95),
        ("SQL", 50, 60),
        ("Machine Learning", 45, 85),
        ("Deep Learning", 20, 95),
        ("NLP", 10, 85),
        ("Transformers", 5, 95),
        ("Embeddings", 0, 95),
        ("RAG", 0, 95),
        ("AI Agents", 0, 95),
        ("LLM", 5, 95),
        ("Generative AI", 5, 95),
        ("Statistics", 35, 70),
        ("NumPy", 60, 85),
        ("Pandas", 55, 70),
    ]

    for skill_name, current, target in demo_skills:
        gap = max(0.0, target - current)
        if gap <= 10:
            cat = "Strong"
        elif gap <= 30:
            cat = "Minor Gap"
        elif gap <= 60:
            cat = "Moderate Gap"
        else:
            cat = "Major Gap"

        us = models.UserSkill(
            profile_id=profile.id,
            skill_name=skill_name,
            current_proficiency=float(current),
            target_proficiency=float(target),
            gap=float(gap),
            gap_category=cat,
        )
        db.add(us)

    db.commit()
    print(f"  ✅ Demo user 'Santhiya' created (user_id={user.id}).")


def run():
    print("🚀 Initializing database...")
    init_db()
    db = SessionLocal()
    try:
        print("📦 Seeding data...")
        seed_skills(db)
        seed_courses(db)
        seed_projects(db)
        seed_assessments(db)
        seed_demo_user(db)
        print("\n✅ All data seeded successfully!")
        print("   Demo user: Santhiya  |  Goal: AI Engineer  |  user_id=1")
    finally:
        db.close()


if __name__ == "__main__":
    run()
