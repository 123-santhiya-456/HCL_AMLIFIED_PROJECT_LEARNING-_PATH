"""
API helper — wraps all backend REST calls for the Streamlit frontend.
Falls back to DEMO_MODE when the backend is unavailable.
"""
import os
import requests
from typing import Dict, List, Optional, Any

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 10  # seconds


def _get(path: str, **kwargs) -> Optional[Dict]:
    try:
        r = requests.get(f"{BACKEND_URL}{path}", timeout=TIMEOUT, **kwargs)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return None


def _post(path: str, data: Dict, **kwargs) -> Optional[Dict]:
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=data, timeout=TIMEOUT, **kwargs)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return None


# ─── Profile ────────────────────────────────────────────────────

def create_profile(payload: Dict) -> Optional[Dict]:
    return _post("/api/profile", payload)


def get_profile(user_id: int) -> Optional[Dict]:
    return _get(f"/api/profile/{user_id}")


# ─── Analysis ───────────────────────────────────────────────────

def analyze_goal(text: str, user_id: int = None) -> Optional[Dict]:
    return _post("/api/analyze-goal", {"text": text, "user_id": user_id})


def get_skill_gap(user_id: int) -> Optional[Dict]:
    return _post("/api/skill-gap", {"user_id": user_id})


# ─── Recommendations ────────────────────────────────────────────

def get_recommendations(user_id: int, top_n: int = 15,
                         resource_type: str = None) -> Optional[Dict]:
    payload = {"user_id": user_id, "top_n": top_n}
    if resource_type:
        payload["resource_type"] = resource_type
    return _post("/api/recommendations", payload)


def get_learning_path(user_id: int) -> Optional[Dict]:
    return _get(f"/api/learning-path/{user_id}")


def create_learning_path(user_id: int) -> Optional[Dict]:
    return _post("/api/learning-path", {"user_id": user_id})


# ─── Assessments ────────────────────────────────────────────────

def get_assessment(skill: str) -> Optional[Dict]:
    return _get(f"/api/assessment/{skill}")


def submit_assessment(user_id: int, quiz_id: str, answers: Dict) -> Optional[Dict]:
    return _post("/api/assessment/result", {
        "user_id": user_id, "quiz_id": quiz_id, "answers": answers
    })


# ─── Progress ───────────────────────────────────────────────────

def update_progress(user_id: int, resource_id: str, resource_type: str,
                     completion_percent: float, time_spent: float = 0.0) -> Optional[Dict]:
    return _post("/api/progress", {
        "user_id": user_id, "resource_id": resource_id,
        "resource_type": resource_type, "completion_percent": completion_percent,
        "time_spent_hours": time_spent,
    })


def get_progress(user_id: int) -> Optional[Dict]:
    return _get(f"/api/progress/{user_id}")


# ─── Feedback ───────────────────────────────────────────────────

def submit_feedback(user_id: int, resource_id: str, resource_type: str,
                     rating: int, comment: str = "") -> Optional[Dict]:
    return _post("/api/feedback", {
        "user_id": user_id, "resource_id": resource_id,
        "resource_type": resource_type, "rating": rating, "comment": comment,
    })


# ─── Chat ───────────────────────────────────────────────────────

def chat(user_id: int, message: str) -> Optional[Dict]:
    return _post("/api/chat", {"user_id": user_id, "message": message})


# ─── Dashboard ──────────────────────────────────────────────────

def get_dashboard(user_id: int) -> Optional[Dict]:
    return _get(f"/api/dashboard/{user_id}")


# ─── Health ─────────────────────────────────────────────────────

def health_check() -> bool:
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False
