"""
2_Profile.py — Learner onboarding form for creating/updating a profile.
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api
from frontend.utils.demo_data import DEMO_USER

st.set_page_config(page_title="Learner Profile — LearnPath AI", page_icon="👤", layout="wide")

# ── Auth guard ─────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("pages/0_Login.py")
    st.stop()

demo_mode = st.session_state.get("demo_mode", True)

st.markdown("""
<div style='
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 45%, #4c1d95 100%);
    border: 1px solid rgba(102,126,234,0.25);
    border-radius: 24px;
    padding: 32px 44px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 20px 60px rgba(79,70,229,0.3);
'>
    <h2 style='margin:0;font-size:1.8rem;font-weight:900;letter-spacing:-0.5px;'>👤 Learner Profile</h2>
    <p style='opacity:0.8;margin:6px 0 0;font-size:0.95rem;'>Tell us about yourself so we can build your personalized AI learning roadmap.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Create / Update Profile", "👁️ View Current Profile"])

with tab1:
    with st.form("profile_form", clear_on_submit=False):
        st.markdown("#### 👤 Personal Information")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *", value="Santhiya", placeholder="Enter your name")
            email = st.text_input("Email (optional)", placeholder="your@email.com")
        with c2:
            experience_level = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"], index=1)
            education = st.text_input("Education / Background", value="B.Tech Computer Science")

        st.markdown("#### 🎯 Career Goal")
        goal_text = st.text_area(
            "Describe your career goal in your own words *",
            value="I want to become an AI Engineer and learn Generative AI and build RAG applications.",
            height=80,
            placeholder="e.g., I want to become a Data Scientist within 6 months..."
        )
        
        col_ai, col_btn = st.columns([5, 1])
        with col_btn:
            analyze_btn = st.form_submit_button("🔍 Analyze Goal", type="secondary")

        # Auto-detect skills from goal
        career_goal_final = "AI Engineer"
        target_skills_default = ["Python", "Machine Learning", "Deep Learning", "NLP",
                                  "Transformers", "Embeddings", "RAG", "AI Agents", "LLM", "Generative AI"]

        st.markdown("#### 🛠️ Current Skills & Proficiency")
        st.caption("Rate your current proficiency: 0 = No knowledge, 100 = Expert")

        skill_options = [
            "Python", "SQL", "Statistics", "Linear Algebra", "NumPy", "Pandas",
            "Machine Learning", "Deep Learning", "NLP", "Transformers", "Embeddings",
            "RAG", "AI Agents", "LLM", "Generative AI", "Computer Vision",
            "Data Visualization", "FastAPI", "Docker", "MLOps", "Data Engineering",
        ]
        selected_skills = st.multiselect(
            "Select your existing skills",
            options=skill_options,
            default=["Python", "SQL", "Machine Learning", "Deep Learning", "NLP",
                      "Transformers", "Embeddings", "RAG", "AI Agents", "LLM",
                      "Generative AI", "Statistics", "NumPy", "Pandas"],
        )

        skill_inputs = []
        if selected_skills:
            st.markdown("**Set proficiency for each selected skill:**")
            default_proficiencies = {
                "Python": 80, "SQL": 50, "Machine Learning": 45,
                "Deep Learning": 20, "NLP": 10, "Transformers": 5,
                "Embeddings": 0, "RAG": 0, "AI Agents": 0, "LLM": 5,
                "Generative AI": 5, "Statistics": 35, "NumPy": 60, "Pandas": 55,
            }
            cols = st.columns(min(len(selected_skills), 3))
            for i, skill in enumerate(selected_skills):
                with cols[i % 3]:
                    val = st.slider(skill, 0, 100,
                                    value=default_proficiencies.get(skill, 20),
                                    key=f"skill_{skill}")
                    skill_inputs.append({"skill_name": skill, "current_proficiency": val})

        st.markdown("#### ⚙️ Learning Preferences")
        lc1, lc2, lc3, lc4 = st.columns(4)
        with lc1:
            learning_style = st.selectbox("Learning Style", ["Project-based", "Video", "Text", "Mixed", "Interactive"], index=0)
        with lc2:
            weekly_hours = st.slider("Weekly Hours Available", 1, 40, 10)
        with lc3:
            timeline = st.slider("Target Months", 1, 24, 6)
        with lc4:
            interests = st.multiselect("Interests", ["Generative AI", "RAG", "AI Agents", "Computer Vision", "NLP", "MLOps", "Data Analysis"], default=["Generative AI", "RAG", "AI Agents"])

        st.markdown("---")
        submitted = st.form_submit_button("🚀 Save Profile & Generate Learning Path", type="primary", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        elif not goal_text.strip():
            st.error("Please describe your career goal.")
        elif not skill_inputs:
            st.error("Please select at least one skill.")
        else:
            with st.spinner("🤖 Analyzing your profile with AI..."):
                # Try to extract goal via LLM/fallback
                goal_data = None
                if not demo_mode:
                    goal_data = api.analyze_goal(goal_text)

                # Prepare payload
                payload = {
                    "name": name,
                    "email": email or None,
                    "career_goal": goal_data.get("career_goal", "AI Engineer") if goal_data else "AI Engineer",
                    "career_goal_raw": goal_text,
                    "experience_level": experience_level,
                    "education": education,
                    "interests": interests,
                    "learning_style": learning_style,
                    "weekly_hours": float(weekly_hours),
                    "timeline_months": timeline,
                    "target_skills": goal_data.get("target_skills", target_skills_default) if goal_data else target_skills_default,
                    "skills": skill_inputs,
                    "completed_courses": [],
                }

                if demo_mode:
                    # Use demo data
                    st.session_state.user_id = 1
                    st.session_state.profile = DEMO_USER
                    st.success("✅ Demo profile saved! Navigate to other pages to explore.")
                else:
                    result = api.create_profile(payload)
                    if result:
                        st.session_state.user_id = result["user_id"]
                        st.session_state.profile = result
                        # Generate learning path
                        api.create_learning_path(result["user_id"])
                        st.success(f"✅ Profile created! User ID: {result['user_id']}. Readiness: {result['readiness_score']:.1f}%")
                    else:
                        st.error("Failed to save profile. Check backend connection or try Demo Mode.")

with tab2:
    profile = st.session_state.get("profile", DEMO_USER if demo_mode else None)
    if not profile:
        st.info("No profile loaded yet. Use the form above to create one.")
    else:
        p = profile
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:24px;margin-bottom:16px;'>
            <h3 style='color:#63b3ed;margin:0;'>👩‍💻 {p.get("name","?")}</h3>
            <p style='color:#a0aec0;margin:4px 0;'>🎯 Goal: {p.get("career_goal","?")} &nbsp;|&nbsp; 📚 {p.get("experience_level","?")} &nbsp;|&nbsp; 🎨 {p.get("learning_style","?")} learner</p>
            <p style='color:#a0aec0;margin:4px 0;'>⏰ {p.get("weekly_hours",0):.0f}h/week &nbsp;|&nbsp; 📅 {p.get("timeline_months",0)} months timeline &nbsp;|&nbsp; 🏆 Readiness: <b style='color:#48bb78;'>{p.get("readiness_score",0):.1f}%</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🛠️ Skills Overview")
        skills = p.get("skills", [])
        if skills:
            for sk in skills:
                c1, c2, c3 = st.columns([2, 4, 1])
                with c1:
                    col = "#48bb78" if sk["gap_category"] == "Strong" else "#63b3ed" if sk["gap_category"] == "Minor Gap" else "#ed8936" if sk["gap_category"] == "Moderate Gap" else "#e53e3e"
                    st.markdown(f"<span style='color:#e2e8f0;font-weight:600;'>{sk['skill_name']}</span>", unsafe_allow_html=True)
                with c2:
                    st.progress(int(sk["current_proficiency"]))
                with c3:
                    st.markdown(f"<span style='color:{col};font-size:0.75rem;font-weight:600;'>{sk['gap_category']}</span>", unsafe_allow_html=True)
