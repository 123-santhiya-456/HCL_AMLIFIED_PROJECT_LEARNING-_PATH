"""
Modular LLM Service.
Supports Gemini and OpenAI through environment variables.
Falls back to rule-based logic if LLM is unavailable.

Configuration (via .env):
  LLM_PROVIDER = gemini | openai
  LLM_API_KEY  = your_api_key
"""
import os
import json
import re
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")  # optional override

# ──────────────────────────────────────────────────────────────────
# Keyword-based fallback extraction
# ──────────────────────────────────────────────────────────────────

ROLE_KEYWORDS = {
    "AI Engineer": ["ai engineer", "build ai", "generative ai", "rag", "llm", "ai agent"],
    "Data Scientist": ["data scientist", "data science", "machine learning", "ml", "predictive"],
    "ML Engineer": ["ml engineer", "machine learning engineer", "mlops", "deploy model"],
    "NLP Engineer": ["nlp", "natural language", "text classification", "chatbot"],
    "Data Analyst": ["data analyst", "analytics", "business intelligence", "sql", "dashboard"],
    "Data Engineer": ["data engineer", "pipeline", "etl", "spark", "kafka"],
}

SKILL_KEYWORDS = {
    "Python": ["python"],
    "SQL": ["sql", "database", "mysql", "postgres"],
    "Machine Learning": ["machine learning", "ml ", "scikit", "sklearn"],
    "Deep Learning": ["deep learning", "neural network", "pytorch", "tensorflow", "keras"],
    "NLP": ["nlp", "natural language", "text"],
    "Transformers": ["transformer", "bert", "gpt", "attention"],
    "Embeddings": ["embedding", "vector", "dense retrieval", "semantic search"],
    "RAG": ["rag", "retrieval augmented", "retrieval-augmented"],
    "AI Agents": ["ai agent", "autonomous agent", "langchain agent", "autogen"],
    "LLM": ["llm", "large language model", "chatgpt", "gemini", "gpt-4"],
    "Generative AI": ["generative ai", "genai", "gen ai", "diffusion", "image generation"],
    "Statistics": ["statistics", "statistical", "probability", "hypothesis"],
    "Data Visualization": ["visualization", "dashboard", "plotly", "tableau"],
    "MLOps": ["mlops", "deployment", "ci/cd", "model serving"],
    "Docker": ["docker", "container", "kubernetes"],
    "Cloud": ["aws", "gcp", "azure", "cloud"],
    "FastAPI": ["fastapi", "api", "rest api"],
    "Computer Vision": ["computer vision", "image", "cnn", "object detection"],
    "Data Engineering": ["data engineering", "pipeline", "etl", "spark"],
}

EXPERIENCE_KEYWORDS = {
    "Beginner": ["beginner", "new", "no experience", "start", "fresh"],
    "Intermediate": ["intermediate", "some experience", "basic knowledge", "familiar"],
    "Advanced": ["advanced", "experienced", "expert", "senior"],
}


def _keyword_extract_goal(text: str) -> Dict:
    """Rule-based goal/skill extraction from free text."""
    text_lower = text.lower()

    # Career goal
    career_goal = "AI Engineer"
    for role, keywords in ROLE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            career_goal = role
            break

    # Target skills
    target_skills = []
    for skill, keywords in SKILL_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            target_skills.append(skill)

    # Current skills (mentioned as "I know", "I have", "experience with")
    current_skills = []
    know_patterns = [r"i know (.+)", r"familiar with (.+)", r"experience (?:in|with) (.+)",
                     r"i have (.+) knowledge", r"background in (.+)"]
    for pattern in know_patterns:
        match = re.search(pattern, text_lower)
        if match:
            phrase = match.group(1)
            for skill, keywords in SKILL_KEYWORDS.items():
                if any(kw in phrase for kw in keywords):
                    current_skills.append(skill)

    # Experience level
    experience_level = "Intermediate"
    for level, keywords in EXPERIENCE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            experience_level = level
            break

    return {
        "career_goal": career_goal,
        "target_skills": target_skills or ["Machine Learning", "Python"],
        "current_skills": current_skills,
        "experience_level": experience_level,
        "interests": target_skills[:3],
    }


# ──────────────────────────────────────────────────────────────────
# LLM providers
# ──────────────────────────────────────────────────────────────────

def _call_gemini(prompt: str, system: str = "") -> Optional[str]:
    """Call Google Gemini API."""
    if not LLM_API_KEY:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=LLM_API_KEY)
        model_name = LLM_MODEL or "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"⚠️  Gemini API error: {e}")
        return None


def _call_openai(prompt: str, system: str = "") -> Optional[str]:
    """Call OpenAI ChatCompletion API."""
    if not LLM_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=LLM_API_KEY)
        model_name = LLM_MODEL or "gpt-3.5-turbo"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(model=model_name, messages=messages,
                                              max_tokens=1000, temperature=0.3)
        return resp.choices[0].message.content
    except Exception as e:
        print(f"⚠️  OpenAI API error: {e}")
        return None


def _call_llm(prompt: str, system: str = "") -> Optional[str]:
    """Route to the configured LLM provider."""
    if LLM_PROVIDER == "openai":
        return _call_openai(prompt, system)
    return _call_gemini(prompt, system)  # default


# ──────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────

def extract_goal(text: str) -> Dict:
    """
    Extract structured goal information from natural-language input.
    Returns Pydantic-validated dict. Falls back to keyword extraction.
    """
    system = (
        "You are an AI career advisor. Extract structured information from the learner's goal."
        " Respond ONLY with valid JSON matching this schema:\n"
        "{\n"
        '  "career_goal": "string",\n'
        '  "target_skills": ["list of strings"],\n'
        '  "current_skills": ["list of strings"],\n'
        '  "experience_level": "Beginner|Intermediate|Advanced",\n'
        '  "interests": ["list of strings"]\n'
        "}"
    )

    result = _call_llm(
        prompt=f"Extract goal info from: \"{text}\"",
        system=system
    )

    if result:
        try:
            # Strip markdown code fences if present
            clean = re.sub(r"```(?:json)?|```", "", result).strip()
            parsed = json.loads(clean)
            # Validate essential fields
            if "career_goal" in parsed and "target_skills" in parsed:
                return parsed
        except Exception:
            pass

    # Fallback
    print("ℹ️  Using keyword-based goal extraction (LLM unavailable or parse failed).")
    return _keyword_extract_goal(text)


def generate_explanation(
    resource_title: str,
    skill_gaps: List[Dict],
    career_goal: str,
    experience_level: str,
    matched_skills: List[str],
    satisfied_prereqs: List[str],
    score: float,
) -> str:
    """
    Generate a human-readable recommendation explanation via LLM.
    Falls back to rule-based template.
    """
    # Build context for LLM
    gap_summary = "; ".join(
        [f"{sg['skill']} (gap: {sg['gap']:.0f}%)" for sg in skill_gaps[:3]]
    )
    prompt = (
        f"Explain in 2-3 sentences WHY '{resource_title}' is recommended "
        f"for a learner whose goal is '{career_goal}' at {experience_level} level. "
        f"Key skill gaps: {gap_summary}. "
        f"Skills addressed: {', '.join(matched_skills)}. "
        f"Prerequisites already met: {', '.join(satisfied_prereqs) or 'None'}. "
        f"Recommendation score: {score:.0f}/100. "
        "Be specific and motivating."
    )

    result = _call_llm(prompt)
    if result and len(result) > 20:
        return result.strip()

    # Fallback template
    lines = [f"Recommended because:"]
    for i, sg in enumerate(skill_gaps[:2], 1):
        if sg["skill"] in matched_skills:
            lines.append(
                f"{i}. '{sg['skill']}' is required for {career_goal} "
                f"(your proficiency: {sg['current']:.0f}%, target: {sg['target']:.0f}%)."
            )
    if satisfied_prereqs:
        lines.append(f"{len(lines)}. Prerequisites satisfied: {', '.join(satisfied_prereqs)}.")
    lines.append(f"Recommendation score: {score:.0f}/100.")
    return "\n".join(lines)


def chat(
    messages: List[Dict[str, str]],
    profile_context: str = "",
    skill_gap_context: str = "",
) -> str:
    """
    Conversational AI assistant with learner profile context.
    messages: list of {"role": "user"|"assistant", "content": "..."}
    """
    system = (
        "You are LearnPath AI Assistant, a helpful AI learning coach. "
        "Answer questions about the learner's learning plan, skill gaps, and recommendations. "
        "Be concise, specific, and motivating. Use the learner profile context provided.\n\n"
        f"LEARNER PROFILE CONTEXT:\n{profile_context}\n\n"
        f"SKILL GAP CONTEXT:\n{skill_gap_context}"
    )

    # Format conversation for the LLM
    last_user_msg = messages[-1]["content"] if messages else ""

    # Build full conversation string
    conv_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages[-6:]])

    result = _call_llm(
        prompt=f"Conversation history:\n{conv_str}\n\nRespond as the AI assistant:",
        system=system
    )

    if result and len(result) > 5:
        return result.strip()

    # Fallback responses based on keywords
    q = last_user_msg.lower()
    if "next" in q or "what should" in q:
        return (
            "Based on your profile, I recommend focusing on your highest-priority skill gap. "
            "Check the Learning Path page for your personalized roadmap and next steps."
        )
    elif "skip" in q:
        return (
            "Skipping prerequisites is not recommended — they build the foundation for advanced topics. "
            "However, if you already have solid practical experience, you can take the assessment to prove mastery."
        )
    elif "gap" in q or "skill" in q:
        return (
            "Your skill gaps are visualized on the Skill Gap page. "
            "The largest gaps are your highest priorities. "
            "Focus on one skill at a time following the recommended learning path."
        )
    elif "time" in q or "long" in q:
        return (
            "Your estimated learning timeline is shown on the Learning Path page. "
            "It depends on your weekly availability and the number of skills to cover. "
            "Consistent daily practice will help you stay on track!"
        )
    elif "fail" in q or "score" in q or "assessment" in q:
        return (
            "If you score below 70% on an assessment, don't worry! "
            "The system will recommend revision resources and an easier starting point. "
            "Retake the assessment after revising — you've got this!"
        )
    else:
        return (
            "Great question! Use the navigation menu to explore your Skill Gap analysis, "
            "Learning Path, and Recommendations. I'm here to help you succeed on your learning journey!"
        )


def is_llm_available() -> bool:
    """Quick check to see if the LLM API key is configured."""
    return bool(LLM_API_KEY)
