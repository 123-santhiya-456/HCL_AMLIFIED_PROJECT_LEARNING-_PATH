"""
7_Progress.py — Progress dashboard with Plotly charts.
"""
import streamlit as st
import sys, os
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api
from frontend.utils.demo_data import DEMO_USER, DEMO_SKILL_GAP

st.set_page_config(page_title="Progress — LearnPath AI", page_icon="📈", layout="wide")

user_id = st.session_state.get("user_id", 1)
demo_mode = st.session_state.get("demo_mode", True)

st.markdown("""
<div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;padding:24px 32px;color:white;margin-bottom:24px;'>
    <h2 style='margin:0;'>📈 Progress Dashboard</h2>
    <p style='opacity:0.85;margin:4px 0 0;'>Track your learning journey and celebrate milestones.</p>
</div>
""", unsafe_allow_html=True)

# Demo progress data
DEMO_PROGRESS = {
    "overall_completion": 12.0,
    "courses_completed": 0,
    "projects_completed": 0,
    "assessments_taken": 1,
    "skills_mastered": [],
    "current_streak": 3,
    "progress_items": [
        {"resource_id": "C016", "resource_type": "Course", "completion_percent": 45, "time_spent_hours": 12, "completed": False},
        {"resource_id": "Q002", "resource_type": "Assessment", "completion_percent": 100, "time_spent_hours": 1, "completed": True},
    ]
}

if demo_mode:
    progress_data = DEMO_PROGRESS
    profile = DEMO_USER
else:
    progress_data = api.get_progress(user_id) or DEMO_PROGRESS
    profile = st.session_state.get("profile", DEMO_USER)

# ─── Summary Metrics ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📈 Overall", f"{progress_data['overall_completion']:.1f}%")
c2.metric("📚 Courses", progress_data['courses_completed'])
c3.metric("🛠️ Projects", progress_data['projects_completed'])
c4.metric("📝 Assessments", progress_data['assessments_taken'])
c5.metric("🔥 Streak", f"{progress_data['current_streak']} days")

st.markdown("---")

col_l, col_r = st.columns([1, 1])

with col_l:
    st.markdown("### 📊 Learning Progress Chart")
    
    # Weekly progress simulation chart
    import random
    weeks = [f"W{i+1}" for i in range(8)]
    hours = [0, 8, 10, 12, 9, 11, 10, 12]
    cumulative = [0, 8, 18, 30, 39, 50, 60, 72]
    
    fig_prog = go.Figure()
    fig_prog.add_trace(go.Bar(
        name="Weekly Hours",
        x=weeks, y=hours,
        marker_color="rgba(102,126,234,0.7)",
        text=[f"{h}h" for h in hours], textposition="outside",
    ))
    fig_prog.add_trace(go.Scatter(
        name="Cumulative Hours",
        x=weeks, y=cumulative,
        mode="lines+markers",
        line=dict(color="#48bb78", width=2.5),
        marker=dict(size=8, color="#48bb78"),
        yaxis="y2",
    ))
    fig_prog.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        height=300, margin=dict(t=20, b=40, l=20, r=60),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Hours/Week"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, title="Cumulative"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        barmode="group",
    )
    st.plotly_chart(fig_prog, use_container_width=True)

with col_r:
    st.markdown("### 🏆 Skill Mastery Progress")
    
    skill_gaps = DEMO_SKILL_GAP.get("skill_gaps", [])[:8]
    skills_names = [sg["skill_name"] for sg in skill_gaps]
    current_vals = [sg["current_proficiency"] for sg in skill_gaps]
    target_vals = [sg["target_proficiency"] for sg in skill_gaps]
    
    fig_mastery = go.Figure()
    fig_mastery.add_trace(go.Bar(
        name="Current",
        x=skills_names, y=current_vals,
        marker_color="rgba(102,126,234,0.8)",
    ))
    fig_mastery.add_trace(go.Bar(
        name="Target",
        x=skills_names, y=target_vals,
        marker_color="rgba(72,187,120,0.3)",
    ))
    fig_mastery.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        height=300, margin=dict(t=20, b=60, l=20, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        barmode="overlay",
        xaxis=dict(tickangle=-45, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, 105]),
    )
    st.plotly_chart(fig_mastery, use_container_width=True)

st.markdown("---")

# ─── Progress by Resource ─────────────────────────────────────────
st.markdown("### 📋 Course & Project Progress")

COURSE_NAMES = {
    "C016": "Machine Learning Fundamentals",
    "C021": "Deep Learning with PyTorch",
    "C025": "NLP Fundamentals",
    "C027": "Transformers & Attention",
    "Q002": "ML Assessment",
}

progress_items = progress_data.get("progress_items", [])
if progress_items:
    for item in progress_items:
        rid = item["resource_id"]
        name = COURSE_NAMES.get(rid, rid)
        pct = item["completion_percent"]
        hours = item.get("time_spent_hours", 0)
        completed = item.get("completed", False)
        
        c1, c2, c3, c4 = st.columns([3, 4, 1, 1])
        with c1:
            status_icon = "✅" if completed else "▶️" if pct > 0 else "⏳"
            st.markdown(f"<span style='color:#e2e8f0;font-weight:600;'>{status_icon} {name}</span>", unsafe_allow_html=True)
        with c2:
            st.progress(int(pct))
        with c3:
            st.markdown(f"<span style='color:#63b3ed;font-weight:700;'>{pct:.0f}%</span>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<span style='color:#718096;font-size:0.85rem;'>{hours:.1f}h</span>", unsafe_allow_html=True)
else:
    st.info("No progress data yet. Start learning to see your progress here!")

# Progress update
st.markdown("---")
st.markdown("### ✏️ Update Progress")

with st.form("progress_form"):
    uc1, uc2, uc3 = st.columns(3)
    with uc1:
        up_resource = st.selectbox("Resource", ["C016", "C021", "C025", "C027"])
    with uc2:
        up_pct = st.slider("Completion %", 0, 100, 50)
    with uc3:
        up_hours = st.number_input("Hours spent", 0.0, 200.0, 1.0, step=0.5)

    if st.form_submit_button("💾 Save Progress"):
        if not demo_mode:
            api.update_progress(user_id, up_resource, "Course", up_pct, up_hours)
        st.success(f"Progress saved: {COURSE_NAMES.get(up_resource, up_resource)} — {up_pct}%")

# ─── Milestones ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🌟 Milestones")
milestones = [
    ("🎯", "Profile Created", True),
    ("📊", "First Skill Gap Analysis", True),
    ("📚", "First Course Started", True if progress_items else False),
    ("📝", "First Assessment Taken", progress_data["assessments_taken"] > 0),
    ("✅", "First Course Completed", progress_data["courses_completed"] > 0),
    ("🛠️", "First Project Completed", progress_data["projects_completed"] > 0),
    ("🏆", "First Skill Mastered", len(progress_data["skills_mastered"]) > 0),
    ("🎓", "Learning Path Completed", progress_data["overall_completion"] >= 100),
]

m_cols = st.columns(4)
for i, (icon, name, done) in enumerate(milestones):
    with m_cols[i % 4]:
        bg = "rgba(72,187,120,0.15)" if done else "rgba(255,255,255,0.03)"
        border = "#48bb78" if done else "rgba(255,255,255,0.1)"
        op = "1" if done else "0.4"
        st.markdown(f"""
        <div style='background:{bg};border:1px solid {border};border-radius:12px;padding:14px;text-align:center;opacity:{op};margin-bottom:8px;'>
            <div style='font-size:1.5rem;'>{icon}</div>
            <div style='color:#e2e8f0;font-size:0.8rem;font-weight:600;margin-top:4px;'>{name}</div>
            <div style='color:{"#48bb78" if done else "#718096"};font-size:0.7rem;'>{"✅ Done" if done else "⏳ Pending"}</div>
        </div>
        """, unsafe_allow_html=True)
