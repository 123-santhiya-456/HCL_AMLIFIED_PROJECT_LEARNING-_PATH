"""
LearnPath AI — Main Streamlit Application Entry Point
Adaptive Personalized Learning Path Recommender
HCLTech AMPLIFIED Hackathon 2026
"""
import streamlit as st
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.utils.api import health_check
from frontend.utils.demo_data import DEMO_USER, DEMO_DASHBOARD

# ─── Page Configuration ─────────────────────────────────────────
st.set_page_config(
    page_title="LearnPath AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "LearnPath AI — HCLTech AMPLIFIED Hackathon 2026",
    }
)

# ─── Global Design System CSS ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── App background ── */
.stApp {
    background: #050b1f !important;
    color: #e2e8f0 !important;
}
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 15% 0%, rgba(102,126,234,0.16) 0%, transparent 55%),
        radial-gradient(ellipse 60% 70% at 85% 100%, rgba(118,75,162,0.14) 0%, transparent 55%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(6,182,212,0.05) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1533 0%, #0a1020 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] .block-container { padding-top: 0.5rem; }

/* ── Header ── */
header[data-testid="stHeader"] {
    background: rgba(5,11,31,0.8) !important;
    backdrop-filter: blur(10px) !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.25s ease !important;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(102,126,234,0.4) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(102,126,234,0.15) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-weight: 800 !important;
    font-size: 1.9rem !important;
}

/* ── Glass card ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 24px;
    backdrop-filter: blur(16px);
    margin-bottom: 16px;
    transition: all 0.25s ease;
}
.glass-card:hover {
    border-color: rgba(102,126,234,0.35);
    box-shadow: 0 12px 40px rgba(102,126,234,0.12);
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4c1d95 80%, #1e3a5f 100%);
    border: 1px solid rgba(102,126,234,0.2);
    border-radius: 24px;
    padding: 44px 52px;
    color: white;
    margin-bottom: 32px;
    box-shadow: 0 24px 80px rgba(79,70,229,0.35);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%; right: -20%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 60%);
    pointer-events: none;
}
.hero-banner h1 {
    font-size: 2.6rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #fff 0%, #c4b5fd 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-banner p { font-size: 1.05rem; opacity: 0.85; margin-top: 10px; }

/* ── Feature card ── */
.feature-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 28px 22px;
    text-align: center;
    transition: all 0.3s ease;
    height: 100%;
}
.feature-card:hover {
    background: rgba(102,126,234,0.08);
    border-color: rgba(102,126,234,0.3);
    transform: translateY(-6px);
    box-shadow: 0 20px 50px rgba(102,126,234,0.15);
}
.feature-icon {
    font-size: 2.4rem;
    margin-bottom: 14px;
    display: block;
}
.feature-title {
    font-weight: 700;
    color: #a5b4fc;
    font-size: 1rem;
    margin-bottom: 8px;
}
.feature-desc {
    font-size: 0.8rem;
    color: #64748b;
    line-height: 1.6;
}

/* ── Score badge ── */
.score-badge {
    display: inline-block;
    background: linear-gradient(135deg, #059669, #10b981);
    color: white;
    border-radius: 50px;
    padding: 5px 16px;
    font-weight: 700;
    font-size: 0.9rem;
    box-shadow: 0 4px 15px rgba(16,185,129,0.4);
}

/* ── Rec card ── */
.rec-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    transition: all 0.3s ease;
}
.rec-card:hover {
    background: rgba(102,126,234,0.08);
    border-color: rgba(102,126,234,0.3);
    transform: translateX(5px);
    box-shadow: 0 8px 30px rgba(102,126,234,0.12);
}

/* ── Phase items ── */
.phase-item { display:flex; align-items:center; gap:12px; padding:12px 16px; border-radius:12px; margin:5px 0; }
.phase-completed { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); }
.phase-current   { background: rgba(102,126,234,0.12); border: 1px solid rgba(102,126,234,0.35); }
.phase-locked    { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07); }

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea, #a78bfa) !important;
    border-radius: 10px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    padding: 12px 24px !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(102,126,234,0.45) !important;
}

/* ── Text inputs ── */
.stTextInput > label, .stTextArea > label, .stSelectbox > label, .stSlider > label, .stMultiSelect > label {
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.18) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #64748b;
    font-weight: 600;
    font-size: 0.88rem;
    padding: 8px 18px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    color: #a5b4fc !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

/* ── Alert ── */
.stAlert { border-radius: 14px !important; font-size: 0.88rem !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Sidebar nav ── */
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 12px;
    color: #94a3b8;
    text-decoration: none;
    transition: all 0.2s ease;
    margin: 2px 0;
    font-weight: 500;
    font-size: 0.9rem;
    cursor: pointer;
}
.sidebar-nav-item:hover {
    background: rgba(102,126,234,0.15);
    color: #a5b4fc;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #050b1f; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }

/* ── Step pipeline ── */
.pipeline-step {
    text-align: center;
    padding: 18px 8px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    transition: all 0.25s ease;
}
.pipeline-step:hover {
    background: rgba(102,126,234,0.1);
    border-color: rgba(102,126,234,0.25);
    transform: translateY(-4px);
}
.pipeline-step .step-icon { font-size: 1.6rem; }
.pipeline-step .step-label { font-size: 0.7rem; color: #64748b; font-weight: 600; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────
defaults = {
    "logged_in": False,
    "user_id": None,
    "profile": None,
    "demo_mode": True,
    "backend_online": False,
    "chat_history": [],
    "student_name": "Learner",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Check backend once per session
if "backend_checked" not in st.session_state:
    backend_online = health_check()
    st.session_state.backend_online = backend_online
    st.session_state.demo_mode = not backend_online
    st.session_state.backend_checked = True

# ─── Auth gate ───────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.switch_page("pages/0_Login.py")
    st.stop()

demo_mode = st.session_state.get("demo_mode", True)

# ─── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 12px;'>
        <div style='font-size:2.8rem;animation:pulse 2s infinite;'>🧠</div>
        <div style='font-size:1.25rem;font-weight:900;background:linear-gradient(135deg,#667eea,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.5px;margin-top:6px;'>LearnPath AI</div>
        <div style='font-size:0.7rem;color:#475569;margin-top:3px;font-weight:500;'>Adaptive Learning Platform</div>
    </div>
    <style>@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.05);}}</style>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:8px 0 12px;'>", unsafe_allow_html=True)

    # Status chip
    if demo_mode:
        st.markdown("""<div style='background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:10px;padding:8px 12px;font-size:0.78rem;color:#fbbf24;text-align:center;font-weight:600;'>⚡ Demo Mode Active</div>""", unsafe_allow_html=True)
        if st.button("🔄 Try Live Connection", use_container_width=True):
            online = health_check()
            st.session_state.backend_online = online
            st.session_state.demo_mode = not online
            st.rerun()
    else:
        st.markdown("""<div style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:10px;padding:8px 12px;font-size:0.78rem;color:#34d399;text-align:center;font-weight:600;'>✅ Backend Connected</div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:14px 0 6px;font-size:0.7rem;color:#475569;font-weight:600;letter-spacing:1px;text-transform:uppercase;padding-left:4px;'>Your Profile</div>", unsafe_allow_html=True)

    p = st.session_state.get("profile") or (DEMO_USER if demo_mode else {})
    if p:
        name = p.get("name", st.session_state.get("student_name", "Learner"))
        goal = p.get("career_goal", "AI Engineer")
        readiness = p.get("readiness_score", 0)
        exp = p.get("experience_level", "Intermediate")
        st.markdown(f"""
        <div style='background:rgba(102,126,234,0.07);border:1px solid rgba(102,126,234,0.15);border-radius:16px;padding:16px;text-align:center;'>
            <div style='font-size:2.2rem;margin-bottom:8px;'>👩‍💻</div>
            <div style='font-weight:700;font-size:1rem;color:#f1f5f9;'>{name}</div>
            <div style='font-size:0.75rem;color:#a5b4fc;margin:4px 0;'>🎯 {goal}</div>
            <div style='font-size:0.7rem;color:#64748b;'>{exp}</div>
            <div style='background:linear-gradient(135deg,#059669,#10b981);border-radius:20px;padding:4px 14px;font-size:0.78rem;font-weight:700;color:white;display:inline-block;margin-top:10px;'>
                {readiness:.0f}% Ready
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("💡 Complete onboarding to see your profile")

    st.markdown("<div style='margin:16px 0 6px;font-size:0.7rem;color:#475569;font-weight:600;letter-spacing:1px;text-transform:uppercase;padding-left:4px;'>Navigation</div>", unsafe_allow_html=True)

    # Logout button at bottom
    st.markdown("<div style='margin-top:16px;'>", unsafe_allow_html=True)
    if st.button("🚪 Log Out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/0_Login.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Landing / Home Content ─────────────────────────────────────
student_name = st.session_state.get("student_name", "Learner")

st.markdown(f"""
<div class='hero-banner'>
    <h1>🧠 LearnPath AI</h1>
    <p>Welcome back, <b>{student_name}</b>! Your AI-powered adaptive learning roadmap awaits.</p>
    <p style='font-size:0.85rem;opacity:0.6;margin-top:6px;'>HCLTech AMPLIFIED Hackathon 2026 · Adaptive · Prerequisite-Aware · Personalized</p>
</div>
""", unsafe_allow_html=True)

# ── Feature Cards ──
col1, col2, col3, col4 = st.columns(4)
features = [
    ("🎯", "Goal Understanding", "AI extracts your career goal & target skills from natural language"),
    ("📊", "Skill Gap Analysis", "Quantifies gaps between your current and target proficiencies"),
    ("🗺️", "Smart Roadmap", "Prerequisite-aware path with 100+ curated resources"),
    ("🔄", "Adaptive Engine", "Quiz results dynamically update your skill path"),
]
for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f"""
        <div class='feature-card'>
            <span class='feature-icon'>{icon}</span>
            <div class='feature-title'>{title}</div>
            <div class='feature-desc'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ── Pipeline ──
st.markdown("<div style='font-size:1.1rem;font-weight:700;color:#f1f5f9;margin-bottom:16px;'>🔧 How It Works — AI Pipeline</div>", unsafe_allow_html=True)
pcols = st.columns(8)
steps = [
    ("👤", "Profile"),
    ("🎯", "Goal AI"),
    ("📊", "Skill Gap"),
    ("🕸️", "KG Graph"),
    ("🔍", "Semantic"),
    ("🏆", "Ranking"),
    ("🗺️", "Roadmap"),
    ("📝", "Assess"),
]
for i, (pcol, (icon, label)) in enumerate(zip(pcols, steps)):
    with pcol:
        st.markdown(f"""
        <div class='pipeline-step'>
            <div class='step-icon'>{icon}</div>
            <div class='step-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── CTA ──
col_a, col_b, col_c = st.columns([3, 1, 1])
with col_a:
    if demo_mode:
        st.info("⚡ **Demo Mode Active** — using pre-built demo data. Start the backend to enable live AI features.")
    else:
        st.success("✅ **Live Mode** — All AI features are active. Use the sidebar to navigate!")
with col_b:
    if st.button("🚀 Go to Dashboard", use_container_width=True):
        st.session_state.user_id = 1
        st.session_state.profile = DEMO_USER
        st.switch_page("pages/1_Home.py")
with col_c:
    if st.button("⚡ Quick Demo", use_container_width=True):
        st.session_state.user_id = 1
        st.session_state.profile = DEMO_USER
        st.session_state.demo_mode = True
        st.rerun()
