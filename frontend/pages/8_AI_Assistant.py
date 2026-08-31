"""
8_AI_Assistant.py — Conversational AI learning assistant with profile context.
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api
from frontend.utils.demo_data import DEMO_USER

st.set_page_config(page_title="AI Assistant — LearnPath AI", page_icon="🤖", layout="wide")

if not st.session_state.get("logged_in"):
    st.switch_page("pages/0_Login.py")
    st.stop()

user_id = st.session_state.get("user_id", 1)
demo_mode = st.session_state.get("demo_mode", True)

st.markdown("""
<div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;padding:24px 32px;color:white;margin-bottom:24px;'>
    <h2 style='margin:0;'>🤖 AI Learning Assistant</h2>
    <p style='opacity:0.85;margin:4px 0 0;'>Ask anything about your learning path, skill gaps, or recommendations.</p>
</div>
""", unsafe_allow_html=True)

col_chat, col_ctx = st.columns([3, 1])

with col_ctx:
    profile = st.session_state.get("profile", DEMO_USER)
    st.markdown("""
    <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:16px;'>
        <div style='color:#63b3ed;font-weight:700;margin-bottom:12px;'>📋 Your Context</div>
    """, unsafe_allow_html=True)
    if profile:
        st.markdown(f"**👤** {profile.get('name','?')}")
        st.markdown(f"**🎯** {profile.get('career_goal','?')}")
        st.markdown(f"**📊** Readiness: {profile.get('readiness_score',0):.0f}%")
        st.markdown(f"**⏰** {profile.get('weekly_hours',0):.0f}h/week")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 💡 Suggested Questions")
    suggested = [
        "What should I learn next?",
        "Explain my skill gaps",
        "How long will this roadmap take?",
        "Why was Machine Learning recommended?",
        "Can I skip prerequisites?",
        "What to do if I fail an assessment?",
        "Suggest a project for my level",
    ]
    for q in suggested:
        if st.button(q, key=f"sugg_{q}", use_container_width=True):
            st.session_state["pending_chat"] = q
            st.rerun()

with col_chat:
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Welcome message
    if not st.session_state.chat_history:
        profile_name = profile.get("name", "Learner") if profile else "Learner"
        goal = profile.get("career_goal", "your goal") if profile else "your goal"
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": (
                f"Hi {profile_name}! 👋 I'm your LearnPath AI Learning Assistant.\n\n"
                f"I know your profile and learning path towards **{goal}**. "
                "I can help you understand your skill gaps, explain recommendations, "
                "suggest what to do next, or answer any questions about your learning journey.\n\n"
                "What would you like to know? 🚀"
            )
        })

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])

    # Handle pending suggestions
    pending = st.session_state.pop("pending_chat", None)

    # Chat input
    user_input = st.chat_input("Ask me anything about your learning journey...")
    
    if pending or user_input:
        message = pending or user_input
        
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": message})

        # Get AI response
        with st.spinner("🤖 Thinking..."):
            if demo_mode:
                # Use fallback LLM logic
                from backend.services.llm_service import chat as llm_chat
                recent = st.session_state.chat_history[-6:]
                
                profile_ctx = ""
                if profile:
                    profile_ctx = (
                        f"Name: {profile.get('name','')}, Goal: {profile.get('career_goal','')}, "
                        f"Experience: {profile.get('experience_level','')}, "
                        f"Weekly Hours: {profile.get('weekly_hours',0)}, "
                        f"Readiness: {profile.get('readiness_score',0):.0f}%"
                    )
                    
                gap_ctx = "Key gaps: Deep Learning (75%), NLP (75%), Transformers (90%), RAG (95%), AI Agents (95%)"
                reply = llm_chat(recent, profile_context=profile_ctx, skill_gap_context=gap_ctx)
            else:
                result = api.chat(user_id, message)
                reply = result.get("reply", "I'm having trouble responding right now. Please try again.") if result else "Backend unavailable."

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    # Clear history button
    if st.session_state.chat_history and len(st.session_state.chat_history) > 1:
        if st.button("🗑️ Clear Conversation", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()
