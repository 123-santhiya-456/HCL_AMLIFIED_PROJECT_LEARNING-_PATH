"""
Pydantic schemas for request/response validation in the FastAPI backend.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


# ─── Learner Profile ────────────────────────────────────────────

class SkillInput(BaseModel):
    skill_name: str
    current_proficiency: float = Field(ge=0, le=100)
    target_proficiency: Optional[float] = None


class ProfileCreate(BaseModel):
    name: str
    email: Optional[str] = None
    career_goal: str
    career_goal_raw: Optional[str] = None
    experience_level: str = "Intermediate"
    education: Optional[str] = None
    interests: List[str] = []
    learning_style: str = "Mixed"
    weekly_hours: float = 5.0
    timeline_months: int = 6
    target_skills: List[str] = []
    skills: List[SkillInput] = []
    completed_courses: List[str] = []


class ProfileResponse(BaseModel):
    user_id: int
    name: str
    career_goal: str
    experience_level: str
    learning_style: str
    weekly_hours: float
    timeline_months: int
    target_skills: List[str]
    readiness_score: float
    skills: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


# ─── Goal Analysis ───────────────────────────────────────────────

class GoalInput(BaseModel):
    text: str
    user_id: Optional[int] = None


class GoalResponse(BaseModel):
    career_goal: str
    target_skills: List[str]
    current_skills: List[str]
    experience_level: str
    interests: List[str]
    llm_used: bool = False


# ─── Skill Gap ───────────────────────────────────────────────────

class SkillGapRequest(BaseModel):
    user_id: int


class SkillGapItem(BaseModel):
    skill: str
    current: float
    target: float
    gap: float
    gap_category: str
    priority: float


class SkillGapResponse(BaseModel):
    user_id: int
    readiness_score: float
    skill_gaps: List[SkillGapItem]
    priority_skills: List[str]


# ─── Recommendations ─────────────────────────────────────────────

class RecommendationRequest(BaseModel):
    user_id: int
    top_n: int = 15
    resource_type: Optional[str] = None  # Course / Project / None = both


class RecommendationItem(BaseModel):
    resource_id: str
    title: str
    description: str
    resource_type: str
    skills: List[str]
    difficulty: str
    duration_hours: float
    rating: float
    final_score: float
    explanation: str
    matched_skills: List[str]
    missing_prerequisites: List[str]
    satisfied_prerequisites: List[str]
    score_breakdown: Dict[str, float]


class RecommendationResponse(BaseModel):
    user_id: int
    readiness_score: float
    recommendations: List[RecommendationItem]
    total_resources_searched: int


# ─── Learning Path ───────────────────────────────────────────────

class LearningPathRequest(BaseModel):
    user_id: int


class LearningPathItemResponse(BaseModel):
    order: int
    phase: int
    skill: str
    resource_type: str
    resource_id: str
    resource_title: str
    status: str
    is_milestone: bool
    estimated_hours: float
    recommendation_score: float
    explanation: str
    prerequisites: List[str]
    missing_prerequisites: List[str]


class LearningPathResponse(BaseModel):
    user_id: int
    career_goal: str
    total_phases: int
    total_hours: float
    estimated_weeks: int
    estimated_months: int
    readiness_score: float
    phases: List[Dict[str, Any]]
    path_items: List[LearningPathItemResponse]


# ─── Assessment ──────────────────────────────────────────────────

class AssessmentQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    skill: Optional[str] = None
    difficulty: Optional[str] = None


class AssessmentResponse(BaseModel):
    quiz_id: str
    skill: str
    difficulty: str
    total_questions: int
    questions: List[AssessmentQuestion]


class AssessmentSubmit(BaseModel):
    user_id: int
    quiz_id: str
    answers: Dict[str, int]  # {question_id: selected_option_index}


class AssessmentResult(BaseModel):
    user_id: int
    quiz_id: str
    skill: str
    score_percent: float
    mastery_level: str
    passed: bool
    correct_count: int
    total_questions: int
    next_action: str
    feedback: str


# ─── Progress ────────────────────────────────────────────────────

class ProgressUpdate(BaseModel):
    user_id: int
    resource_id: str
    resource_type: str = "Course"
    completion_percent: float = Field(ge=0, le=100)
    time_spent_hours: float = 0.0


class ProgressResponse(BaseModel):
    user_id: int
    overall_completion: float
    courses_completed: int
    projects_completed: int
    assessments_taken: int
    skills_mastered: List[str]
    current_streak: int
    progress_items: List[Dict[str, Any]]


# ─── Feedback ────────────────────────────────────────────────────

class FeedbackSubmit(BaseModel):
    user_id: int
    resource_id: str
    resource_type: str = "Course"
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


# ─── Chat ────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    user_id: int
    message: str


class ChatResponse(BaseModel):
    reply: str
    llm_used: bool


# ─── Dashboard ───────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    user_id: int
    name: str
    career_goal: str
    readiness_score: float
    current_phase: str
    next_action: str
    overall_completion: float
    courses_completed: int
    projects_completed: int
    assessments_taken: int
    skills_mastered: List[str]
    recent_activity: List[Dict[str, Any]]
