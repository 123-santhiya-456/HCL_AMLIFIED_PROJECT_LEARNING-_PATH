"""
LearnPath AI — Main Streamlit Application Entry Point
Adaptive Personalized Learning Path Recommender
HCLTech AMPLIFIED Hackathon
"""
import streamlit as st
import os
import sys

# Add project root to path
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

# ─── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
/* ─── Global/Fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ─── App Background ─── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%);
    color: #e2e8f0;
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    border-right: 1px solid #2d3748;
}
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }

/* ─── Metric Cards ─── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 16px !important;
    backdrop-filter: blur(10px);
}
[data-testid="metric-container"]:hover {
    border-color: rgba(99,179,237,0.5);
    transform: translateY(-2px);
    transition: all 0.2s ease;
}

/* ─── Cards ─── */
.glass-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(10px);
    margin-bottom: 16px;
    transition: all 0.2s ease;
}
.glass-card:hover { border-color: rgba(99,179,237,0.4); }

/* ─── Hero Banner ─── */
.hero-banner {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6B8DD6 100%);
    border-radius: 20px;
    padding: 40px 48px;
    color: white;
    margin-bottom: 32px;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
}
.hero-banner h1 { font-size: 2.5rem; font-weight: 800; margin: 0; }
.hero-banner p { font-size: 1.1rem; opacity: 0.9; margin-top: 8px; }

/* ─── Score Badge ─── */
.score-badge {
    display: inline-block;
    background: linear-gradient(135deg, #48bb78, #38a169);
    color: white;
    border-radius: 50px;
    padding: 6px 18px;
    font-weight: 700;
    font-size: 1rem;
    box-shadow: 0 4px 15px rgba(72,187,120,0.4);
}

/* ─── Recommendation Card ─── */
.rec-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}
.rec-card:hover {
    background: rgba(102,126,234,0.1);
    border-color: rgba(102,126,234,0.4);
    transform: translateX(4px);
}

/* ─── Phase Item ─── */
.phase-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 10px;
    margin: 4px 0;
}
.phase-completed { background: rgba(72,187,120,0.15); border: 1px solid rgba(72,187,120,0.3); }
.phase-current   { background: rgba(99,179,237,0.15); border: 1px solid rgba(99,179,237,0.4); }
.phase-locked    { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); }

/* ─── Progress Bar ─── */
.stProgress > div > div { 
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
    border-radius: 10px !important;
}

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(102,126,234,0.4) !important;
}

/* ─── Input Widgets ─── */
.stTextInput > div > div > input, .stTextArea > div > div > textarea,
.stSelectbox > div > div > div, .stSlider {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #a0aec0;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
}

/* ─── Expander ─── */
.streamlit-expanderHeader { color: #63b3ed !important; font-weight: 600 !important; }

/* ─── Alert boxes ─── */
.stAlert { border-radius: 12px !important; }

/* ─── Sidebar nav links ─── */
.sidebar-nav-item {
    display: block;
    padding: 10px 16px;
    border-radius: 10px;
    color: #a0aec0;
    text-decoration: none;
    transition: all 0.2s ease;
    margin: 2px 0;
    font-weight: 500;
}
.sidebar-nav-item:hover, .sidebar-nav-item.active {
    background: rgba(102,126,234,0.2);
    color: #63b3ed;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Initialization ───────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "profile" not in st.session_state:
    st.session_state.profile = None
if "demo_mode" not in st.session_state:
    # Check backend connectivity
    backend_online = health_check()
    st.session_state.demo_mode = not backend_online
    st.session_state.backend_online = backend_online
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

demo_mode = st.session_state.get("demo_mode", True)

# ─── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
        <div style='font-size:2.5rem;'>🧠</div>
        <div style='font-size:1.3rem;font-weight:800;color:#63b3ed;'>LearnPath AI</div>
        <div style='font-size:0.75rem;color:#718096;margin-top:2px;'>Adaptive Learning Recommender</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Connection status
    if demo_mode:
        st.warning("⚡ Demo Mode (backend offline)")
        if st.button("🔄 Reconnect", use_container_width=True):
            st.session_state.backend_online = health_check()
            st.session_state.demo_mode = not st.session_state.backend_online
            st.rerun()
    else:
        st.success("✅ Connected to Backend")

    st.divider()

    # User info in sidebar
    if st.session_state.get("profile"):
        p = st.session_state.profile
        name = p.get("name", "Learner")
        goal = p.get("career_goal", "")
        readiness = p.get("readiness_score", 0)
        user_id = st.session_state.user_id or p.get("user_id", 1)
        st.markdown(f"""
        <div class='glass-card' style='margin:0 0 12px;text-align:center;'>
            <div style='font-size:2rem;'>👩‍💻</div>
            <div style='font-weight:700;font-size:1rem;color:#e2e8f0;margin-top:4px;'>{name}</div>
            <div style='color:#63b3ed;font-size:0.8rem;margin:4px 0;'>🎯 {goal}</div>
            <div style='color:#48bb78;font-size:0.85rem;font-weight:600;'>Readiness: {readiness:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if demo_mode:
            p = DEMO_USER
            st.markdown(f"""
            <div class='glass-card' style='margin:0 0 12px;text-align:center;'>
                <div style='font-size:2rem;'>👩‍💻</div>
                <div style='font-weight:700;font-size:1rem;color:#e2e8f0;margin-top:4px;'>{p['name']}</div>
                <div style='color:#63b3ed;font-size:0.8rem;margin:4px 0;'>🎯 {p['career_goal']}</div>
                <div style='color:#48bb78;font-size:0.85rem;font-weight:600;'>Demo Profile</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("💡 Complete onboarding to get started!")

    st.markdown("**Navigation**")

# ─── Landing Page Content ────────────────────────────────────────
st.markdown("""
<div class='hero-banner'>
    <h1>🧠 LearnPath AI</h1>
    <p>Your AI-Powered Adaptive Learning Path Recommender</p>
    <p style='font-size:0.9rem;opacity:0.75;margin-top:4px;'>HCLTech AMPLIFIED Hackathon 2026</p>
</div>
""", unsafe_allow_html=True)

# Feature highlights
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""<div class='glass-card' style='text-align:center;'>
        <div style='font-size:2rem;'>🎯</div>
        <div style='font-weight:700;color:#63b3ed;margin-top:8px;'>Goal Understanding</div>
        <div style='font-size:0.8rem;color:#718096;margin-top:4px;'>AI extracts your career goal and target skills from natural language</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class='glass-card' style='text-align:center;'>
        <div style='font-size:2rem;'>📊</div>
        <div style='font-weight:700;color:#63b3ed;margin-top:8px;'>Skill Gap Analysis</div>
        <div style='font-size:0.8rem;color:#718096;margin-top:4px;'>Quantifies gaps between your current and target proficiencies</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class='glass-card' style='text-align:center;'>
        <div style='font-size:2rem;'>🗺️</div>
        <div style='font-weight:700;color:#63b3ed;margin-top:8px;'>Smart Roadmap</div>
        <div style='font-size:0.8rem;color:#718096;margin-top:4px;'>Prerequisite-aware learning path with 100+ curated resources</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown("""<div class='glass-card' style='text-align:center;'>
        <div style='font-size:2rem;'>🔄</div>
        <div style='font-weight:700;color:#63b3ed;margin-top:8px;'>Adaptive Engine</div>
        <div style='font-size:0.8rem;color:#718096;margin-top:4px;'>Dynamically adjusts recommendations based on quiz results</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# How it works
st.markdown("### 🔧 How It Works")
cols = st.columns(8)
steps = [
    ("👤", "Profile"),
    ("🎯", "Goal AI"),
    ("📊", "Skill Gap"),
    ("🕸️", "Knowledge Graph"),
    ("🔍", "Semantic Search"),
    ("🏆", "Ranking"),
    ("🗺️", "Roadmap"),
    ("📝", "Assessment"),
]
for i, (icon, label) in enumerate(steps):
    with cols[i]:
        st.markdown(f"""<div style='text-align:center;padding:12px 4px;background:rgba(255,255,255,0.03);border-radius:10px;border:1px solid rgba(255,255,255,0.08);'>
            <div style='font-size:1.5rem;'>{icon}</div>
            <div style='font-size:0.7rem;color:#a0aec0;margin-top:4px;font-weight:600;'>{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

if demo_mode:
    st.info("⚡ **Demo Mode Active** — Using pre-built demo data. Start the backend to enable live features. Use the **Learner Profile** page to onboard!")

col_a, col_b = st.columns([2,1])
with col_a:
    st.success("👈 **Use the sidebar navigation** to explore all features, or start with **Learner Profile** to onboard.")
with col_b:
    if st.button("🚀 Quick Start with Demo Profile", use_container_width=True):
        st.session_state.user_id = 1
        st.session_state.profile = DEMO_USER
        st.session_state.demo_mode = True
        st.success("Demo profile loaded! Navigate using the sidebar.")
        st.rerun()
