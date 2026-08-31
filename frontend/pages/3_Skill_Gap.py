"""
3_Skill_Gap.py — Skill gap visualization with radar and bar charts.
"""
import streamlit as st
import sys, os
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api
from frontend.utils.demo_data import DEMO_SKILL_GAP, DEMO_USER

st.set_page_config(page_title="Skill Gap — LearnPath AI", page_icon="📊", layout="wide")

user_id = st.session_state.get("user_id", 1)
demo_mode = st.session_state.get("demo_mode", True)

# Fetch data
if demo_mode:
    data = DEMO_SKILL_GAP
else:
    data = api.get_skill_gap(user_id) or DEMO_SKILL_GAP

st.markdown("""
<div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;padding:24px 32px;color:white;margin-bottom:24px;'>
    <h2 style='margin:0;'>📊 Skill Gap Analysis</h2>
    <p style='opacity:0.85;margin:4px 0 0;'>Your current vs. target proficiency for each skill required for your career goal.</p>
</div>
""", unsafe_allow_html=True)

readiness = data.get("readiness_score", 0)
skill_gaps = data.get("skill_gaps", [])
priority_skills = data.get("priority_skills", [])

# ─── Summary Cards ───────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
major = sum(1 for sg in skill_gaps if sg["gap_category"] == "Major Gap")
moderate = sum(1 for sg in skill_gaps if sg["gap_category"] == "Moderate Gap")
minor = sum(1 for sg in skill_gaps if sg["gap_category"] == "Minor Gap")
strong = sum(1 for sg in skill_gaps if sg["gap_category"] == "Strong")

c1.metric("🎯 Readiness Score", f"{readiness:.1f}%")
c2.metric("🔴 Major Gaps", major, help="Gap > 60 points")
c3.metric("🟠 Moderate Gaps", moderate, help="Gap 31–60 points")
c4.metric("🟢 Strong Skills", strong + minor, help="Gap ≤ 30 points")

st.markdown("---")

# ─── Charts ─────────────────────────────────────────────────────
col_l, col_r = st.columns([3, 2])

with col_l:
    st.markdown("### 📈 Current vs Target Proficiency")
    
    skills = [sg["skill"] for sg in skill_gaps]
    current = [sg["current"] for sg in skill_gaps]
    target = [sg["target"] for sg in skill_gaps]
    gaps = [sg["gap"] for sg in skill_gaps]
    categories = [sg["gap_category"] for sg in skill_gaps]

    # Color by gap category
    cat_colors = {
        "Strong": "#48bb78",
        "Minor Gap": "#63b3ed",
        "Moderate Gap": "#ed8936",
        "Major Gap": "#e53e3e",
    }
    colors = [cat_colors.get(c, "#a0aec0") for c in categories]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Current Proficiency",
        x=skills, y=current,
        marker_color=colors,
        text=[f"{v:.0f}%" for v in current],
        textposition="outside",
    ))
    fig_bar.add_trace(go.Scatter(
        name="Target Proficiency",
        x=skills, y=target,
        mode="markers+lines",
        marker=dict(color="#667eea", size=8, symbol="diamond"),
        line=dict(color="#667eea", width=1.5, dash="dot"),
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", size=11),
        height=400, margin=dict(t=20, b=60, l=20, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", yanchor="top", y=0.99),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickangle=-30),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, 110]),
        bargap=0.3,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_r:
    st.markdown("### 🕸️ Skill Radar Chart")
    
    radar_skills = skills[:8]  # top 8 for radar
    radar_current = current[:8]
    radar_target = target[:8]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=radar_current + [radar_current[0]],
        theta=radar_skills + [radar_skills[0]],
        fill="toself",
        name="Current",
        fillcolor="rgba(102,126,234,0.3)",
        line=dict(color="#667eea", width=2),
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=radar_target + [radar_target[0]],
        theta=radar_skills + [radar_skills[0]],
        fill="toself",
        name="Target",
        fillcolor="rgba(72,187,120,0.1)",
        line=dict(color="#48bb78", width=2, dash="dot"),
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                           gridcolor="rgba(255,255,255,0.1)", tickcolor="#718096"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        height=380,
        margin=dict(t=20, b=20, l=40, r=40),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ─── Detailed Table ───────────────────────────────────────────────
st.markdown("### 📋 Detailed Gap Analysis")

GAP_ICONS = {"Strong": "🟢", "Minor Gap": "🔵", "Moderate Gap": "🟠", "Major Gap": "🔴"}

for sg in skill_gaps:
    icon = GAP_ICONS.get(sg["gap_category"], "⚪")
    cat_color = cat_colors.get(sg["gap_category"], "#a0aec0")
    progress_pct = int(sg["current"])
    gap_val = sg["gap"]

    with st.container():
        c1, c2, c3, c4, c5 = st.columns([2.5, 3, 1, 1, 1.5])
        with c1:
            st.markdown(f"<span style='font-weight:600;color:#e2e8f0;'>{icon} {sg['skill']}</span>", unsafe_allow_html=True)
        with c2:
            st.progress(progress_pct)
        with c3:
            st.markdown(f"<span style='color:#63b3ed;font-weight:700;'>{sg['current']:.0f}%</span>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<span style='color:#48bb78;font-weight:700;'>{sg['target']:.0f}%</span>", unsafe_allow_html=True)
        with c5:
            st.markdown(f"<span style='color:{cat_color};font-size:0.8rem;font-weight:600;'>{sg['gap_category']}</span>", unsafe_allow_html=True)

# ─── Priority Skills ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎯 Top Priority Skills to Focus On")
if priority_skills:
    cols = st.columns(len(priority_skills))
    for i, skill in enumerate(priority_skills):
        with cols[i]:
            sg = next((s for s in skill_gaps if s["skill"] == skill), {})
            st.markdown(f"""
            <div style='background:rgba(229,62,62,0.1);border:1px solid rgba(229,62,62,0.3);border-radius:12px;padding:16px;text-align:center;'>
                <div style='font-size:0.7rem;color:#a0aec0;font-weight:700;letter-spacing:1px;'>PRIORITY {i+1}</div>
                <div style='color:#e2e8f0;font-weight:700;font-size:0.95rem;margin:6px 0;'>{skill}</div>
                <div style='color:#e53e3e;font-weight:700;font-size:1.2rem;'>Gap: {sg.get("gap",0):.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
