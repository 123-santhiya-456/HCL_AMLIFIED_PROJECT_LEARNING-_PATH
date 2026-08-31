"""
SQLAlchemy ORM models for LearnPath AI.
All tables are defined here. The database layer is modular,
allowing easy migration from SQLite to PostgreSQL.
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    profile = relationship("LearnerProfile", back_populates="user", uselist=False)
    learning_paths = relationship("LearningPath", back_populates="user")
    assessments = relationship("AssessmentResult", back_populates="user")
    progress = relationship("Progress", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    career_goal = Column(String(200), nullable=False)
    career_goal_raw = Column(Text, nullable=True)   # original NL input
    experience_level = Column(String(50), default="Beginner")  # Beginner/Intermediate/Advanced
    education = Column(String(200), nullable=True)
    interests = Column(JSON, default=list)           # list of interest strings
    learning_style = Column(String(50), default="Mixed")  # Video/Text/Project-based/Mixed
    weekly_hours = Column(Float, default=5.0)
    timeline_months = Column(Integer, default=6)
    target_skills = Column(JSON, default=list)       # list of skill names
    completed_courses = Column(JSON, default=list)   # list of course IDs
    current_resources = Column(JSON, default=list)
    readiness_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")
    user_skills = relationship("UserSkill", back_populates="profile")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(String(10), unique=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    domain = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    # Target proficiencies per role (stored as JSON)
    target_proficiencies = Column(JSON, default=dict)

    user_skills = relationship("UserSkill", back_populates="skill")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("learner_profiles.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    skill_name = Column(String(100), nullable=False)  # denormalized for speed
    current_proficiency = Column(Float, default=0.0)   # 0–100
    target_proficiency = Column(Float, default=80.0)   # 0–100
    gap = Column(Float, default=0.0)
    gap_category = Column(String(20), default="Major Gap")  # Strong/Minor/Moderate/Major

    profile = relationship("LearnerProfile", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(10), unique=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    skills = Column(JSON, default=list)          # list of skill names
    difficulty = Column(String(20), default="Intermediate")
    duration_hours = Column(Float, default=10.0)
    prerequisites = Column(JSON, default=list)   # list of skill/course names
    career_roles = Column(JSON, default=list)
    resource_type = Column(String(20), default="Course")
    rating = Column(Float, default=4.0)
    embedding_id = Column(Integer, nullable=True)  # FAISS index position


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(10), unique=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    skills = Column(JSON, default=list)
    difficulty = Column(String(20), default="Intermediate")
    duration_hours = Column(Float, default=15.0)
    career_roles = Column(JSON, default=list)
    resource_type = Column(String(20), default="Project")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    career_goal = Column(String(200), nullable=True)
    total_phases = Column(Integer, default=0)
    estimated_weeks = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active/completed/paused
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="learning_paths")
    items = relationship("LearningPathItem", back_populates="path",
                         order_by="LearningPathItem.order")


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    order = Column(Integer, default=0)
    phase = Column(Integer, default=1)
    skill = Column(String(100), nullable=True)
    resource_type = Column(String(20), default="Course")  # Course/Project/Assessment
    resource_id = Column(String(10), nullable=True)
    resource_title = Column(String(200), nullable=True)
    status = Column(String(20), default="locked")  # locked/available/in_progress/completed
    is_milestone = Column(Boolean, default=False)
    estimated_hours = Column(Float, default=0.0)
    recommendation_score = Column(Float, default=0.0)
    explanation = Column(Text, nullable=True)

    path = relationship("LearningPath", back_populates="items")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(String(10), unique=True, index=True)
    skill = Column(String(100), nullable=False)
    difficulty = Column(String(20), default="Intermediate")
    total_questions = Column(Integer, default=5)
    questions = Column(JSON, default=list)


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(String(10), nullable=False)
    skill = Column(String(100), nullable=False)
    score_percent = Column(Float, default=0.0)
    mastery_level = Column(String(20), default="Beginner")
    passed = Column(Boolean, default=False)
    answers = Column(JSON, default=dict)
    taken_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="assessments")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(String(10), nullable=False)
    resource_type = Column(String(20), default="Course")
    completion_percent = Column(Float, default=0.0)
    time_spent_hours = Column(Float, default=0.0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="progress")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(String(10), nullable=False)
    resource_type = Column(String(20), default="Course")
    rating = Column(Integer, default=3)       # 1–5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="feedback")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(10), nullable=False)   # user/assistant
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chat_history")
