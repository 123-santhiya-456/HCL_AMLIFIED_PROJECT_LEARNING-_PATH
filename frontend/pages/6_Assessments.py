"""
6_Assessments.py — Quiz engine for skill assessment with adaptive feedback.
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api

st.set_page_config(page_title="Assessments — LearnPath AI", page_icon="📝", layout="wide")

if not st.session_state.get("logged_in"):
    st.switch_page("pages/0_Login.py")
    st.stop()

user_id = st.session_state.get("user_id", 1)
demo_mode = st.session_state.get("demo_mode", True)

st.markdown("""
<div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;padding:24px 32px;color:white;margin-bottom:24px;'>
    <h2 style='margin:0;'>📝 Skill Assessments</h2>
    <p style='opacity:0.85;margin:4px 0 0;'>Test your knowledge and unlock the next phase of your learning journey.</p>
</div>
""", unsafe_allow_html=True)

AVAILABLE_ASSESSMENTS = [
    {"skill": "Python", "quiz_id": "Q001", "difficulty": "Beginner"},
    {"skill": "Machine Learning", "quiz_id": "Q002", "difficulty": "Intermediate"},
    {"skill": "Deep Learning", "quiz_id": "Q003", "difficulty": "Intermediate"},
    {"skill": "NLP", "quiz_id": "Q004", "difficulty": "Intermediate"},
    {"skill": "RAG", "quiz_id": "Q005", "difficulty": "Advanced"},
    {"skill": "Statistics", "quiz_id": "Q006", "difficulty": "Beginner"},
    {"skill": "AI Agents", "quiz_id": "Q007", "difficulty": "Advanced"},
    {"skill": "SQL", "quiz_id": "Q008", "difficulty": "Beginner"},
]

DEMO_QUESTIONS = {
    "Machine Learning": {
        "quiz_id": "Q002", "skill": "Machine Learning", "difficulty": "Intermediate",
        "total_questions": 5,
        "questions": [
            {"id": 1, "question": "What is the purpose of the train-test split?",
             "options": ["To increase training data", "To evaluate model generalization on unseen data", "To reduce model complexity", "To improve training speed"]},
            {"id": 2, "question": "Which metric is best for imbalanced classification?",
             "options": ["Accuracy", "F1 Score", "Mean Squared Error", "R-squared"]},
            {"id": 3, "question": "What does overfitting mean?",
             "options": ["Poor training performance", "Good training but poor test performance", "Slow training", "Too few parameters"]},
            {"id": 4, "question": "Which algorithm predicts a continuous numerical value?",
             "options": ["Logistic Regression", "Decision Tree Classifier", "Linear Regression", "KNN Classifier"]},
            {"id": 5, "question": "What is cross-validation used for?",
             "options": ["Transforming features", "Selecting the best model and hyperparameters", "Cleaning data", "Deploying models"]},
        ]
    }
}
DEMO_ANSWERS = {1: 1, 2: 1, 3: 1, 4: 2, 5: 1}

# ─── Assessment Selector ─────────────────────────────────────────
st.markdown("### 🎯 Select a Skill to Assess")
cols = st.columns(4)
selected_assessment = None
for i, a in enumerate(AVAILABLE_ASSESSMENTS):
    with cols[i % 4]:
        DIFF_COLOR = {"Beginner": "#48bb78", "Intermediate": "#63b3ed", "Advanced": "#e53e3e"}
        dc = DIFF_COLOR.get(a["difficulty"], "#63b3ed")
        if st.button(f"{a['skill']}", key=f"sel_{a['skill']}", use_container_width=True):
            st.session_state["selected_quiz_skill"] = a["skill"]
            st.session_state["quiz_submitted"] = False
            st.session_state["quiz_answers"] = {}
            st.session_state["quiz_result"] = None

selected_skill = st.session_state.get("selected_quiz_skill", None)

if not selected_skill:
    st.info("👆 Select a skill above to start the assessment.")
    st.stop()

st.markdown("---")
st.markdown(f"### 📝 {selected_skill} Assessment")

# Load quiz
if demo_mode:
    quiz = DEMO_QUESTIONS.get(selected_skill, DEMO_QUESTIONS["Machine Learning"])
    quiz_data = quiz
else:
    quiz_data = api.get_assessment(selected_skill)
    if not quiz_data:
        quiz_data = DEMO_QUESTIONS.get(selected_skill, DEMO_QUESTIONS["Machine Learning"])

quiz_id = quiz_data.get("quiz_id", "Q002")
questions = quiz_data.get("questions", [])
total_q = quiz_data.get("total_questions", len(questions))

quiz_submitted = st.session_state.get("quiz_submitted", False)
quiz_result = st.session_state.get("quiz_result", None)

if not quiz_submitted:
    st.markdown(f"**{total_q} questions** | Difficulty: **{quiz_data.get('difficulty','')}** | Pass threshold: 70%")
    st.markdown("---")
    
    answers = {}
    for q in questions:
        st.markdown(f"**Q{q['id']}. {q['question']}**")
        options = q.get("options", [])
        choice = st.radio(
            f"q{q['id']}",
            options=options,
            key=f"q_{selected_skill}_{q['id']}",
            label_visibility="collapsed",
        )
        if choice:
            answers[str(q["id"])] = options.index(choice)
        st.markdown("---")
    
    col_a, col_b = st.columns([3, 1])
    with col_b:
        submit_btn = st.button("✅ Submit Assessment", type="primary", use_container_width=True)
    
    if submit_btn:
        if len(answers) < total_q:
            st.warning(f"Please answer all {total_q} questions before submitting.")
        else:
            with st.spinner("Scoring your assessment..."):
                if demo_mode:
                    # Demo: score against known answers
                    correct = sum(1 for qid, ans in answers.items()
                                  if DEMO_ANSWERS.get(int(qid)) == ans)
                    score_pct = (correct / total_q) * 100
                    from ml.skill_gap import get_mastery_level
                    mastery = get_mastery_level(score_pct)
                    passed = score_pct >= 70
                    next_action = "next_skill" if passed else "revision"
                    feedback = (
                        f"{'Excellent!' if mastery == 'Advanced' else 'Great work!' if mastery == 'Proficient' else 'Good progress!'} "
                        f"You scored {score_pct:.0f}% — {mastery} level. "
                        f"{'The next skill is now available!' if passed else 'Review the material and try again!'}"
                    )
                    result = {
                        "score_percent": score_pct, "mastery_level": mastery,
                        "passed": passed, "correct_count": correct,
                        "total_questions": total_q, "next_action": next_action,
                        "feedback": feedback, "skill": selected_skill,
                    }
                else:
                    result = api.submit_assessment(user_id, quiz_id, answers)
            
            st.session_state["quiz_submitted"] = True
            st.session_state["quiz_result"] = result
            st.rerun()

else:
    result = quiz_result
    score = result.get("score_percent", 0)
    mastery = result.get("mastery_level", "")
    passed = result.get("passed", False)
    correct = result.get("correct_count", 0)
    total = result.get("total_questions", 5)

    # Result banner
    color = "#48bb78" if passed else "#e53e3e"
    icon = "🎉" if passed else "💪"
    st.markdown(f"""
    <div style='background:{color}22;border:2px solid {color};border-radius:16px;padding:28px;text-align:center;margin-bottom:20px;'>
        <div style='font-size:3rem;'>{icon}</div>
        <div style='font-size:2rem;font-weight:800;color:{color};'>{score:.0f}%</div>
        <div style='color:#e2e8f0;font-size:1.1rem;font-weight:600;margin-top:4px;'>{mastery} Level</div>
        <div style='color:#a0aec0;margin-top:8px;'>{correct}/{total} correct answers</div>
    </div>
    """, unsafe_allow_html=True)

    # Mastery bar
    MASTERY_THRESHOLDS = {"Beginner": 20, "Developing": 55, "Proficient": 78, "Advanced": 93}
    cols_m = st.columns(4)
    for i, (level, pct) in enumerate(MASTERY_THRESHOLDS.items()):
        with cols_m[i]:
            is_current = level == mastery
            bg = "rgba(102,126,234,0.3)" if is_current else "rgba(255,255,255,0.03)"
            border = "#667eea" if is_current else "rgba(255,255,255,0.1)"
            st.markdown(f"""
            <div style='background:{bg};border:2px solid {border};border-radius:10px;padding:10px;text-align:center;'>
                <div style='color:#e2e8f0;font-weight:{'700' if is_current else '400'};font-size:0.85rem;'>{'▶ ' if is_current else ''}{level}</div>
                <div style='color:#718096;font-size:0.7rem;'>≥ {pct - 20}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    # Feedback card
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.04);border-left:4px solid {"#48bb78" if passed else "#ed8936"};border-radius:8px;padding:16px;margin:12px 0;'>
        <div style='color:#e2e8f0;font-size:0.95rem;'>{result.get("feedback","")}</div>
    </div>
    """, unsafe_allow_html=True)

    c_a, c_b = st.columns(2)
    with c_a:
        if st.button("🔄 Retake Assessment", use_container_width=True):
            st.session_state["quiz_submitted"] = False
            st.session_state["quiz_result"] = None
            st.rerun()
    with c_b:
        if st.button("📚 View Recommendations for this Skill", use_container_width=True):
            st.switch_page("pages/5_Recommendations.py")
