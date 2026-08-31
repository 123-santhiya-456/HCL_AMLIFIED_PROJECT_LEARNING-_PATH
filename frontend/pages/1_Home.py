"""
1_Home.py — Interactive Dashboard for LearnPath AI
Fully redesigned with animated KPIs, interactive Plotly charts, live skill radar,
progress ring, and quick-action shortcuts.
"""
import streamlit as st
import sys, os
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api, demo_data

st.set_page_config(page_title="Dashboard — LearnPath AI", page_icon="🏠", layout="wide")

# ── Auth guard ────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("pages/0_Login.py")
    st.stop()

# ── Data ─────────────────────────────────────────────────────────
user_id   = st.session_state.get("user_id", 1)
demo_mode = st.session_state.get("demo_mode", True)

if demo_mode:
    data    = demo_data.DEMO_DASHBOARD
    profile = demo_data.DEMO_USER
    skills  = demo_data.DEMO_USER["skills"]
else:
    data    = api.get_dashboard(user_id) or demo_data.DEMO_DASHBOARD
    profile = st.session_state.get("profile") or demo_data.DEMO_USER
    skills  = profile.get("skills", demo_data.DEMO_USER["skills"])

if not data:
    st.error("Could not load dashboard data.")
    st.stop()

# ── Metrics ───────────────────────────────────────────────────────
name          = data.get("name", "Learner")
career_goal   = data.get("career_goal", "")
readiness     = data.get("readiness_score", 0)
completion    = data.get("overall_completion", 0)
courses_done  = data.get("courses_completed", 0)
projects_done = data.get("projects_completed", 0)
assessments   = data.get("assessments_taken", 0)
current_phase = data.get("current_phase", "Phase 1: Getting Started")
next_action   = data.get("next_action", "Complete your profile first")
mastered      = data.get("skills_mastered", [])

# ─────────────────────────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 45%, #4c1d95 80%, #0f3460 100%);
    border: 1px solid rgba(102,126,234,0.25);
    border-radius: 24px;
    padding: 36px 48px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 24px 80px rgba(79,70,229,0.3);
    position: relative;
    overflow: hidden;
'>
<div style='position:absolute;top:-80px;right:-60px;width:350px;height:350px;
    background:radial-gradient(circle,rgba(167,139,250,0.1) 0%,transparent 65%);
    pointer-events:none;'></div>

<div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;'>
  <div>
    <div style='font-size:0.8rem;color:#a5b4fc;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;'>Dashboard</div>
    <h2 style='margin:0;font-size:2rem;font-weight:900;letter-spacing:-0.5px;'>
        Welcome back, {name} 👋
    </h2>
    <p style='opacity:0.8;margin:8px 0 0;font-size:1rem;'>
        🎯 Goal: <b>{career_goal}</b>
    </p>
  </div>
  <div style='text-align:right;'>
    <div style='font-size:0.75rem;color:#a5b4fc;font-weight:600;margin-bottom:4px;'>CURRENT PHASE</div>
    <div style='background:rgba(167,139,250,0.2);border:1px solid rgba(167,139,250,0.35);border-radius:12px;padding:8px 18px;font-size:0.9rem;font-weight:700;color:#c4b5fd;'>{current_phase}</div>
    <div style='font-size:0.75rem;color:#6ee7b7;margin-top:10px;font-weight:600;'>▶ Next: {next_action}</div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, "🎯 Readiness",    f"{readiness:.1f}%",  "+4.5%", True),
    (k2, "📈 Completion",   f"{completion:.1f}%",  "+2.1%", True),
    (k3, "📚 Courses Done", str(courses_done),     "+0",    None),
    (k4, "🛠️ Projects",     str(projects_done),    "+0",    None),
    (k5, "✅ Assessments",  str(assessments),      "+0",    None),
]
for col, label, val, delta, pos in kpis:
    with col:
        col.metric(label=label, value=val, delta=delta if pos else None)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# ROW 1 — Gauge + Radar
# ─────────────────────────────────────────────────────────────────
g_col, r_col = st.columns([1, 1])

with g_col:
    st.markdown("""
    <div style='font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:12px;display:flex;align-items:center;gap:8px;'>
        📊 Career Readiness Gauge
    </div>
    """, unsafe_allow_html=True)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=readiness,
        delta={"reference": 50, "valueformat": ".1f", "increasing": {"color": "#10b981"}, "decreasing": {"color": "#ef4444"}},
        title={"text": f"<b>{career_goal}</b><br><span style='font-size:0.75em;color:#94a3b8'>Career Readiness Score</span>", "font": {"size": 14, "color": "#e2e8f0"}},
        number={"suffix": "%", "font": {"size": 42, "color": "#f1f5f9"}, "valueformat": ".1f"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569", "tickwidth": 1, "ticklen": 6,
                     "tickfont": {"color": "#64748b", "size": 11}},
            "bar": {"color": "#667eea", "thickness": 0.28},
            "bgcolor": "rgba(30,27,75,0.6)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30],  "color": "rgba(239,68,68,0.2)"},
                {"range": [30, 60], "color": "rgba(245,158,11,0.2)"},
                {"range": [60, 80], "color": "rgba(59,130,246,0.2)"},
                {"range": [80, 100],"color": "rgba(16,185,129,0.2)"},
            ],
            "threshold": {"line": {"color": "#10b981", "width": 3}, "thickness": 0.75, "value": 70},
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0", "family": "Inter"},
        height=300,
        margin=dict(t=40, b=20, l=30, r=30),
    )
    cont_g = st.container()
    cont_g.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

    # Skill mastery tags
    if mastered:
        tags = " ".join(
            f'<span style="background:rgba(16,185,129,0.15);color:#34d399;border:1px solid rgba(16,185,129,0.25);'
            f'padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:600;margin:2px;display:inline-block;">'
            f'✓ {s}</span>' for s in mastered
        )
        st.markdown(f"""
        <div style='background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);
            border-radius:14px;padding:14px 16px;'>
            <div style='color:#34d399;font-weight:700;font-size:0.85rem;margin-bottom:8px;'>🏆 Mastered Skills</div>
            {tags}
        </div>
        """, unsafe_allow_html=True)

with r_col:
    st.markdown("""
    <div style='font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:12px;'>
        🕸️ Skill Radar — Current vs Target
    </div>
    """, unsafe_allow_html=True)

    top_skills = skills[:8] if len(skills) >= 8 else skills
    skill_names   = [s["skill_name"] for s in top_skills]
    current_vals  = [s["current_proficiency"] for s in top_skills]
    target_vals   = [s["target_proficiency"] for s in top_skills]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=target_vals + [target_vals[0]],
        theta=skill_names + [skill_names[0]],
        fill='toself',
        name='Target',
        line=dict(color='rgba(102,126,234,0.5)', width=1.5),
        fillcolor='rgba(102,126,234,0.08)',
        marker=dict(size=4, color='#667eea'),
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=current_vals + [current_vals[0]],
        theta=skill_names + [skill_names[0]],
        fill='toself',
        name='Current',
        line=dict(color='rgba(16,185,129,0.9)', width=2),
        fillcolor='rgba(16,185,129,0.15)',
        marker=dict(size=5, color='#10b981'),
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9, color='#475569'),
                            gridcolor='rgba(255,255,255,0.05)', linecolor='rgba(255,255,255,0.05)'),
            angularaxis=dict(tickfont=dict(size=10, color='#94a3b8'), gridcolor='rgba(255,255,255,0.05)',
                             linecolor='rgba(255,255,255,0.05)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        legend=dict(font=dict(size=11, color='#94a3b8'), bgcolor='rgba(0,0,0,0)', borderwidth=0),
        height=320,
        margin=dict(t=20, b=20, l=40, r=40),
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# ROW 2 — Skill Gap Bar + Learning Phases
# ─────────────────────────────────────────────────────────────────
bar_col, phase_col = st.columns([3, 2])

with bar_col:
    st.markdown("""
    <div style='font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:12px;'>
        📊 Skill Gap Analysis
    </div>
    """, unsafe_allow_html=True)

    s_names = [s["skill_name"] for s in skills]
    s_curr  = [s["current_proficiency"] for s in skills]
    s_gap   = [s["gap"] for s in skills]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name='Current',
        x=s_names,
        y=s_curr,
        marker=dict(
            color='rgba(16,185,129,0.75)',
            line=dict(color='rgba(16,185,129,1)', width=1),
        ),
        hovertemplate='<b>%{x}</b><br>Current: %{y}%<extra></extra>',
    ))
    fig_bar.add_trace(go.Bar(
        name='Gap to Close',
        x=s_names,
        y=s_gap,
        marker=dict(
            color='rgba(102,126,234,0.45)',
            line=dict(color='rgba(102,126,234,0.7)', width=1),
        ),
        hovertemplate='<b>%{x}</b><br>Gap: %{y}%<extra></extra>',
    ))
    fig_bar.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', family='Inter', size=11),
        xaxis=dict(tickfont=dict(size=10, color='#64748b'), gridcolor='rgba(255,255,255,0)',
                   linecolor='rgba(255,255,255,0.06)', tickangle=-30),
        yaxis=dict(tickfont=dict(size=10, color='#64748b'), gridcolor='rgba(255,255,255,0.05)',
                   linecolor='rgba(255,255,255,0)', range=[0, 110],
                   title=dict(text='Proficiency (%)', font=dict(size=11, color='#475569'))),
        legend=dict(font=dict(size=11, color='#94a3b8'), bgcolor='rgba(0,0,0,0)', borderwidth=0,
                    orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=340,
        margin=dict(t=30, b=60, l=50, r=20),
        bargap=0.25,
        hoverlabel=dict(bgcolor='#1e1b4b', bordercolor='#667eea', font=dict(color='white')),
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

with phase_col:
    st.markdown("""
    <div style='font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:12px;'>
        🗺️ Learning Path Phases
    </div>
    """, unsafe_allow_html=True)

    phases = demo_data.DEMO_LEARNING_PATH.get("phases", [])
    status_config = {
        "in_progress": ("🔵", "phase-current",   "#a5b4fc"),
        "available":   ("🟢", "phase-completed",  "#34d399"),
        "locked":      ("🔒", "phase-locked",     "#475569"),
        "completed":   ("✅", "phase-completed",  "#34d399"),
    }
    for ph in phases[:8]:
        skill  = ph.get("skill","")
        status = ph.get("status","locked")
        phase_n = ph.get("phase", "?")
        icon, css_cls, color = status_config.get(status, ("🔒","phase-locked","#475569"))
        st.markdown(f"""
        <div class='{css_cls}' style='display:flex;align-items:center;gap:10px;
            padding:10px 14px;border-radius:12px;margin-bottom:5px;'>
            <span style='font-size:1rem;'>{icon}</span>
            <div style='flex:1;'>
                <div style='font-size:0.82rem;font-weight:700;color:{color};'>Phase {phase_n}: {skill}</div>
                <div style='font-size:0.7rem;color:#475569;margin-top:1px;'>{ph.get("gap_category","")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# ROW 3 — Progress Donut + Tips + Quick Actions
# ─────────────────────────────────────────────────────────────────
d_col, tip_col = st.columns([1, 2])

with d_col:
    st.markdown("""
    <div style='font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:12px;'>
        📈 Overall Progress
    </div>
    """, unsafe_allow_html=True)

    # Donut rings
    fig_donut = go.Figure()
    fig_donut.add_trace(go.Pie(
        values=[completion, 100 - completion],
        hole=0.72,
        marker=dict(
            colors=['#667eea', 'rgba(255,255,255,0.04)'],
            line=dict(color=['rgba(102,126,234,0.5)', 'rgba(255,255,255,0.0)'], width=[2, 0]),
        ),
        textinfo='none',
        hoverinfo='skip',
        sort=False,
    ))
    fig_donut.add_annotation(
        text=f"<b>{completion:.0f}%</b><br><span style='font-size:12px;'>Complete</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=22, color='#f1f5f9', family='Inter'),
        align='center',
    )
    fig_donut.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    tl = profile.get("timeline_months", 6)
    wh = profile.get("weekly_hours", 10)
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:14px;'>
        <div style='display:flex;justify-content:space-between;margin-bottom:9px;'>
            <span style='color:#64748b;font-size:0.8rem;font-weight:500;'>📅 Timeline</span>
            <span style='color:#a5b4fc;font-weight:700;font-size:0.85rem;'>{tl} months</span>
        </div>
        <div style='display:flex;justify-content:space-between;margin-bottom:9px;'>
            <span style='color:#64748b;font-size:0.8rem;font-weight:500;'>⏱ Weekly Hours</span>
            <span style='color:#a5b4fc;font-weight:700;font-size:0.85rem;'>{wh}h/wk</span>
        </div>
        <div style='display:flex;justify-content:space-between;'>
            <span style='color:#64748b;font-size:0.8rem;font-weight:500;'>🎓 Experience</span>
            <span style='color:#a5b4fc;font-weight:700;font-size:0.85rem;'>{profile.get("experience_level","Intermediate")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tip_col:
    st.markdown("""
    <div style='font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:12px;'>
        💡 Learning Tips & Quick Actions
    </div>
    """, unsafe_allow_html=True)

    tips = [
        ("📅", "Consistency Wins",  "Daily 30-min sessions beat all-day weekend cramming."),
        ("🎯", "One Skill at a Time", "Deep focus on a single skill maximises retention."),
        ("🛠️", "Build Projects",    "Apply each course concept in a hands-on project."),
        ("📝", "Take Assessments",  "Quizzes unlock the next phase — don't skip them!"),
        ("🤖", "Ask the AI",        "Use the AI Assistant for instant explanations."),
        ("🔄", "Review Regularly",  "Coming back to previous material deepens mastery."),
    ]
    tip_a, tip_b = st.columns(2)
    for i, (icon, title, desc) in enumerate(tips):
        target = tip_a if i % 2 == 0 else tip_b
        with target:
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                border-radius:14px;padding:14px;margin-bottom:10px;transition:all 0.2s ease;'>
                <div style='font-size:1.3rem;margin-bottom:6px;'>{icon}</div>
                <div style='font-weight:700;color:#a5b4fc;font-size:0.85rem;margin-bottom:4px;'>{title}</div>
                <div style='font-size:0.78rem;color:#64748b;line-height:1.5;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# QUICK ACTIONS
# ─────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div style='font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:14px;'>⚡ Quick Actions</div>", unsafe_allow_html=True)

qa1, qa2, qa3, qa4, qa5 = st.columns(5)
with qa1:
    if st.button("📊 Skill Gap", use_container_width=True):
        st.switch_page("pages/3_Skill_Gap.py")
with qa2:
    if st.button("🗺️ Learning Path", use_container_width=True):
        st.switch_page("pages/4_Learning_Path.py")
with qa3:
    if st.button("🏆 Recommendations", use_container_width=True):
        st.switch_page("pages/5_Recommendations.py")
with qa4:
    if st.button("📝 Take Assessment", use_container_width=True):
        st.switch_page("pages/6_Assessments.py")
with qa5:
    if st.button("🤖 AI Assistant", use_container_width=True):
        st.switch_page("pages/8_AI_Assistant.py")
