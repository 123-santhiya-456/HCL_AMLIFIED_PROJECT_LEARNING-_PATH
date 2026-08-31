"""
1_Home.py — Welcome dashboard showing career goal, readiness, and next action.
"""
import streamlit as st
import sys, os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api, demo_data

st.set_page_config(page_title="Home — LearnPath AI", page_icon="🏠", layout="wide")

# Session guard
user_id = st.session_state.get("user_id", 1)
demo_mode = st.session_state.get("demo_mode", True)

# Fetch data
if demo_mode:
    data = demo_data.DEMO_DASHBOARD
    profile = demo_data.DEMO_USER
else:
    data = api.get_dashboard(user_id)
    profile = st.session_state.get("profile", {})

if not data:
    st.error("Could not load dashboard. Please check the backend connection.")
    st.stop()

# ─── Header ─────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:20px;padding:32px 40px;color:white;margin-bottom:24px;box-shadow:0 20px 60px rgba(102,126,234,0.4);'>
    <h1 style='margin:0;font-size:2rem;'>Welcome back, {data.get("name","Learner")} 👋</h1>
    <p style='opacity:0.9;margin:8px 0 0;font-size:1.05rem;'>🎯 Goal: <b>{data.get("career_goal","")}</b> &nbsp;|&nbsp; Keep up the great work!</p>
</div>
""", unsafe_allow_html=True)

# ─── Key Metrics ─────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
readiness = data.get("readiness_score", 0)
completion = data.get("overall_completion", 0)
courses_done = data.get("courses_completed", 0)
projects_done = data.get("projects_completed", 0)
assessments = data.get("assessments_taken", 0)

c1.metric("🎯 Readiness", f"{readiness:.1f}%", help="Overall readiness to achieve your career goal")
c2.metric("📈 Completion", f"{completion:.1f}%", help="Overall learning path completion")
c3.metric("📚 Courses Done", courses_done)
c4.metric("🛠️ Projects Done", projects_done)
c5.metric("✅ Assessments", assessments)

st.markdown("---")

# ─── Two column layout ───────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    st.markdown("### 🗺️ Current Status")
    
    current_phase = data.get("current_phase", "Getting Started")
    next_action = data.get("next_action", "Complete your profile")
    mastered = data.get("skills_mastered", [])

    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:20px;margin-bottom:12px;'>
        <div style='color:#a0aec0;font-size:0.8rem;font-weight:600;letter-spacing:1px;'>CURRENT PHASE</div>
        <div style='color:#63b3ed;font-size:1.2rem;font-weight:700;margin-top:6px;'>{current_phase}</div>
        <div style='color:#a0aec0;font-size:0.8rem;margin-top:12px;font-weight:600;letter-spacing:1px;'>NEXT ACTION</div>
        <div style='color:#48bb78;font-size:1rem;font-weight:600;margin-top:6px;'>▶ {next_action}</div>
    </div>
    """, unsafe_allow_html=True)

    if mastered:
        st.markdown(f"""
        <div style='background:rgba(72,187,120,0.1);border:1px solid rgba(72,187,120,0.3);border-radius:10px;padding:14px;'>
            <div style='color:#48bb78;font-weight:700;'>🏆 Skills Mastered</div>
            <div style='margin-top:8px;'>{" ".join(f'<span style="background:rgba(72,187,120,0.2);color:#48bb78;padding:4px 10px;border-radius:20px;font-size:0.8rem;margin:2px;">{s}</span>' for s in mastered)}</div>
        </div>
        """, unsafe_allow_html=True)

    # Quick tips
    st.markdown("### 💡 Learning Tips")
    tips = [
        "📅 Consistent daily practice beats long weekend sessions",
        "🎯 Focus on one skill at a time for maximum retention",
        "🛠️ Apply knowledge through projects after each course",
        "📝 Take assessments to unlock the next skill in your path",
    ]
    for tip in tips:
        st.markdown(f"<div style='color:#a0aec0;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.9rem;'>{tip}</div>", unsafe_allow_html=True)

with right:
    st.markdown("### 📊 Readiness Gauge")
    
    # Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=readiness,
        delta={"reference": 50, "valueformat": ".1f"},
        title={"text": "Career Readiness", "font": {"size": 14, "color": "#a0aec0"}},
        number={"suffix": "%", "font": {"size": 28, "color": "#e2e8f0"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#718096"},
            "bar": {"color": "#667eea", "thickness": 0.3},
            "bgcolor": "rgba(255,255,255,0.05)",
            "bordercolor": "rgba(255,255,255,0.1)",
            "steps": [
                {"range": [0, 40], "color": "rgba(229,62,62,0.3)"},
                {"range": [40, 70], "color": "rgba(237,137,54,0.3)"},
                {"range": [70, 100], "color": "rgba(72,187,120,0.3)"},
            ],
            "threshold": {"line": {"color": "#48bb78", "width": 3}, "value": 70},
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
        height=220,
        margin=dict(t=30, b=0, l=20, r=20),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Timeline
    timeline_months = profile.get("timeline_months", 6) if profile else 6
    weekly_hours = profile.get("weekly_hours", 10) if profile else 10
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.04);border-radius:12px;padding:16px;margin-top:8px;'>
        <div style='display:flex;justify-content:space-between;margin-bottom:10px;'>
            <span style='color:#a0aec0;font-size:0.85rem;'>📅 Target Timeline</span>
            <span style='color:#63b3ed;font-weight:700;'>{timeline_months} months</span>
        </div>
        <div style='display:flex;justify-content:space-between;margin-bottom:10px;'>
            <span style='color:#a0aec0;font-size:0.85rem;'>⏰ Weekly Hours</span>
            <span style='color:#63b3ed;font-weight:700;'>{weekly_hours}h/week</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span style='color:#a0aec0;font-size:0.85rem;'>🎓 Experience Level</span>
            <span style='color:#63b3ed;font-weight:700;'>{profile.get("experience_level","Intermediate") if profile else "Intermediate"}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Quick navigation ────────────────────────────────────────────
st.markdown("---")
st.markdown("### ⚡ Quick Actions")
q1, q2, q3, q4 = st.columns(4)
with q1:
    if st.button("📊 View Skill Gaps", use_container_width=True):
        st.switch_page("pages/3_Skill_Gap.py")
with q2:
    if st.button("🗺️ View Learning Path", use_container_width=True):
        st.switch_page("pages/4_Learning_Path.py")
with q3:
    if st.button("🏆 Get Recommendations", use_container_width=True):
        st.switch_page("pages/5_Recommendations.py")
with q4:
    if st.button("🤖 Ask AI Assistant", use_container_width=True):
        st.switch_page("pages/8_AI_Assistant.py")
