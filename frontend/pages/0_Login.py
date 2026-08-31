"""
0_Login.py — Student Login Page for LearnPath AI
Handles authentication with demo credentials and session management.
"""
import streamlit as st
import sys, os, hashlib, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils.demo_data import DEMO_USER, DEMO_DASHBOARD

st.set_page_config(
    page_title="Login — LearnPath AI",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #050b1f !important;
    color: #e2e8f0 !important;
}

/* Hide default sidebar toggle on login */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Animated background ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(102,126,234,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 80% 90%, rgba(118,75,162,0.15) 0%, transparent 60%),
        radial-gradient(ellipse 50% 50% at 50% 50%, rgba(6,182,212,0.06) 0%, transparent 70%),
        #050b1f;
    z-index: 0;
    pointer-events: none;
}

/* ── Login container ── */
.login-wrap {
    max-width: 460px;
    margin: 0 auto;
    padding: 40px 0 60px;
    position: relative;
    z-index: 1;
}

.brand-area {
    text-align: center;
    margin-bottom: 36px;
}
.brand-icon {
    font-size: 3.5rem;
    animation: floatIcon 3s ease-in-out infinite;
    display: block;
    margin-bottom: 10px;
}
@keyframes floatIcon {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
.brand-name {
    font-size: 2.2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #667eea, #a78bfa, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}
.brand-sub {
    color: #64748b;
    font-size: 0.88rem;
    margin-top: 4px;
    font-weight: 500;
}

/* ── Card ── */
.login-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 24px;
    padding: 36px 36px 32px;
    backdrop-filter: blur(20px);
    box-shadow: 0 25px 80px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.08);
}

.card-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 6px;
}
.card-sub {
    font-size: 0.83rem;
    color: #64748b;
    margin-bottom: 28px;
}

/* ── Input overrides ── */
.stTextInput > label {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    margin-bottom: 4px !important;
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
    height: auto !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.2) !important;
    outline: none !important;
}

/* ── Primary button ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 14px 24px !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(102,126,234,0.35) !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(102,126,234,0.5) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Demo pill ── */
.demo-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(102,126,234,0.12);
    border: 1px solid rgba(102,126,234,0.2);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.78rem;
    color: #a5b4fc;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}
.demo-pill:hover {
    background: rgba(102,126,234,0.2);
    border-color: rgba(102,126,234,0.4);
}

/* ── Divider ── */
.or-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 20px 0;
    color: #475569;
    font-size: 0.78rem;
    font-weight: 500;
}
.or-divider::before, .or-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.08);
}

/* ── Trust badges ── */
.trust-row {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 32px;
    flex-wrap: wrap;
}
.trust-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.75rem;
    color: #475569;
    font-weight: 500;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-size: 0.88rem !important;
}

/* ── Checkbox ── */
.stCheckbox > label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #667eea !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─── Built-in student accounts ────────────────────────────────────
STUDENTS = {
    "santhiya": {"password": hashlib.sha256("learn123".encode()).hexdigest(), "user_id": 1, "name": "Santhiya", "role": "student"},
    "student":  {"password": hashlib.sha256("student123".encode()).hexdigest(), "user_id": 2, "name": "Student",  "role": "student"},
    "demo":     {"password": hashlib.sha256("demo".encode()).hexdigest(),       "user_id": 1, "name": "Demo User", "role": "student"},
}

def check_credentials(username: str, password: str):
    u = username.lower().strip()
    if u in STUDENTS:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if STUDENTS[u]["password"] == hashed:
            return STUDENTS[u]
    return None

# ─── Already logged in → redirect ─────────────────────────────────
if st.session_state.get("logged_in"):
    st.switch_page("pages/1_Home.py")

# ─── Demo auto-fill helper ─────────────────────────────────────────
if "pre_user" not in st.session_state:
    st.session_state.pre_user = ""
if "pre_pass" not in st.session_state:
    st.session_state.pre_pass = ""

# ─── Page render ──────────────────────────────────────────────────
st.markdown('<div class="login-wrap">', unsafe_allow_html=True)

# Brand
st.markdown("""
<div class="brand-area">
    <span class="brand-icon">🧠</span>
    <div class="brand-name">LearnPath AI</div>
    <div class="brand-sub">HCLTech AMPLIFIED Hackathon 2026 · Adaptive Learning Platform</div>
</div>
""", unsafe_allow_html=True)

# Card
st.markdown("""
<div class="login-card">
    <div class="card-title">Welcome back 👋</div>
    <div class="card-sub">Sign in to continue your personalized learning journey</div>
""", unsafe_allow_html=True)

# Form fields
username = st.text_input("Username", value=st.session_state.pre_user, placeholder="Enter your username", key="login_user")
password = st.text_input("Password", value=st.session_state.pre_pass, placeholder="Enter your password", type="password", key="login_pass")

remember = st.checkbox("Keep me signed in", value=True)

# Login button
login_clicked = st.button("🚀 Sign In", use_container_width=True)

if login_clicked:
    if not username or not password:
        st.error("⚠️ Please enter both username and password.")
    else:
        with st.spinner("Authenticating..."):
            time.sleep(0.6)
            user = check_credentials(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user["user_id"]
            st.session_state.student_name = user["name"]
            st.session_state.profile = DEMO_USER if user["user_id"] == 1 else None
            st.session_state.demo_mode = True
            st.session_state.backend_online = False
            st.session_state.chat_history = []
            st.success(f"✅ Welcome, {user['name']}! Redirecting to your dashboard...")
            time.sleep(0.8)
            st.switch_page("pages/1_Home.py")
        else:
            st.error("❌ Invalid username or password. Try demo / demo  or  santhiya / learn123")

st.markdown('<div class="or-divider">or</div>', unsafe_allow_html=True)

# Demo quick-login
col_d1, col_d2 = st.columns(2)
with col_d1:
    if st.button("⚡ Demo Login", use_container_width=True, help="username: demo | password: demo"):
        st.session_state.pre_user = "demo"
        st.session_state.pre_pass = "demo"
        st.session_state.logged_in = True
        st.session_state.user_id = 1
        st.session_state.student_name = "Demo User"
        st.session_state.profile = DEMO_USER
        st.session_state.demo_mode = True
        st.session_state.backend_online = False
        st.session_state.chat_history = []
        st.rerun()
with col_d2:
    if st.button("📖 Credentials", use_container_width=True, help="Show available credentials"):
        st.info("""
**Demo accounts:**
- `demo` / `demo`  
- `santhiya` / `learn123`  
- `student` / `student123`
        """)

st.markdown("</div>", unsafe_allow_html=True)  # close login-card

# Trust badges
st.markdown("""
<div class="trust-row">
    <div class="trust-item">🔒 Secure Session</div>
    <div class="trust-item">⚡ Demo Mode Ready</div>
    <div class="trust-item">🧠 AI-Powered</div>
    <div class="trust-item">🏆 HCL AMPLIFIED</div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # close login-wrap
