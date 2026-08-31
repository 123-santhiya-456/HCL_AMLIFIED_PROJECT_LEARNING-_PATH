"""
5_Recommendations.py — Course and project recommendation cards with filtering.
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api
from frontend.utils.demo_data import DEMO_RECOMMENDATIONS, DEMO_SKILL_GAP

st.set_page_config(page_title="Recommendations — LearnPath AI", page_icon="🏆", layout="wide")

if not st.session_state.get("logged_in"):
    st.switch_page("pages/0_Login.py")
    st.stop()

user_id = st.session_state.get("user_id", 1)
demo_mode = st.session_state.get("demo_mode", True)

st.markdown("""
<div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;padding:24px 32px;color:white;margin-bottom:24px;'>
    <h2 style='margin:0;'>🏆 Personalized Recommendations</h2>
    <p style='opacity:0.85;margin:4px 0 0;'>Hybrid AI-ranked courses and projects tailored to your skill gaps and career goal.</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar Filters ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")
    filter_type = st.multiselect("Resource Type", ["Course", "Project"], default=["Course", "Project"])
    filter_difficulty = st.multiselect("Difficulty", ["Beginner", "Intermediate", "Advanced"],
                                        default=["Beginner", "Intermediate", "Advanced"])
    min_score = st.slider("Min Recommendation Score", 0, 100, 50)
    max_duration = st.slider("Max Duration (hours)", 1, 100, 60)
    st.markdown("---")
    top_n = st.slider("Results to show", 5, 30, 15)

# Fetch recommendations
if demo_mode:
    recs = DEMO_RECOMMENDATIONS
    readiness = DEMO_SKILL_GAP.get("readiness_score", 46.0)
else:
    with st.spinner("🤖 Generating personalized recommendations..."):
        result = api.get_recommendations(user_id, top_n=top_n)
    if result:
        recs = result.get("recommendations", [])
        readiness = result.get("readiness_score", 0)
    else:
        st.warning("Backend unavailable — showing demo recommendations.")
        recs = DEMO_RECOMMENDATIONS
        readiness = 46.0

# Refresh button
if st.button("🔄 Refresh Recommendations", use_container_width=False):
    st.rerun()

# ─── Summary ────────────────────────────────────────────────────
st.markdown(f"**{len(recs)} recommendations** ranked by hybrid AI score (skill gap match + goal relevance + prerequisite fit + ...)")

c1, c2 = st.columns([3, 1])
with c1:
    st.progress(int(readiness))
with c2:
    st.markdown(f"**Readiness: {readiness:.1f}%**")

st.markdown("---")

# ─── Score Breakdown Legend ──────────────────────────────────────
with st.expander("ℹ️ How is the Recommendation Score calculated?"):
    weights = [
        ("Skill Gap Match", "30%", "How well this resource addresses your highest-priority gaps"),
        ("Goal Relevance", "25%", "Alignment with your career goal and target skills"),
        ("Prerequisite Fit", "20%", "How many prerequisites you've already satisfied"),
        ("Difficulty Fit", "10%", "Match between resource difficulty and your experience level"),
        ("Learning Preference", "10%", "Alignment with your preferred learning style (e.g. project-based)"),
        ("Feedback Score", "5%", "Rating of the resource by the community"),
    ]
    cols = st.columns(len(weights))
    for i, (name, weight, desc) in enumerate(weights):
        with cols[i]:
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.04);border-radius:10px;padding:12px;text-align:center;'>
                <div style='color:#667eea;font-weight:800;font-size:1.1rem;'>{weight}</div>
                <div style='color:#e2e8f0;font-weight:600;font-size:0.8rem;margin:4px 0;'>{name}</div>
                <div style='color:#718096;font-size:0.7rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ─── Recommendation Cards ────────────────────────────────────────
DIFF_COLOR = {"Beginner": "#48bb78", "Intermediate": "#63b3ed", "Advanced": "#e53e3e"}
TYPE_ICON = {"Course": "📚", "Project": "🛠️"}

displayed = 0
for rec in recs:
    # Apply filters
    if rec.get("resource_type") not in filter_type:
        continue
    if rec.get("difficulty") not in filter_difficulty:
        continue
    if rec.get("final_score", 0) < min_score:
        continue
    if rec.get("duration_hours", 0) > max_duration:
        continue

    displayed += 1
    score = rec.get("final_score", 0)
    difficulty = rec.get("difficulty", "Intermediate")
    diff_color = DIFF_COLOR.get(difficulty, "#63b3ed")
    type_icon = TYPE_ICON.get(rec.get("resource_type"), "📄")

    with st.container():
        with st.expander(f"{type_icon} **{rec.get('title', 'Untitled')}** &nbsp; Score: {score:.0f}/100", expanded=(displayed <= 3)):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"<p style='color:#a0aec0;margin:0;'>{rec.get('description','')}</p>", unsafe_allow_html=True)
                
                # Matched skills
                matched = rec.get("matched_skills", [])
                if matched:
                    skill_tags = " ".join(
                        f'<span style="background:rgba(102,126,234,0.2);color:#63b3ed;padding:3px 10px;border-radius:15px;font-size:0.75rem;margin:2px;">{s}</span>'
                        for s in matched
                    )
                    st.markdown(f"<div style='margin-top:8px;'>{skill_tags}</div>", unsafe_allow_html=True)
                
                # Why recommended
                st.markdown(f"""
                <div style='background:rgba(102,126,234,0.1);border-left:3px solid #667eea;border-radius:4px;padding:10px 14px;margin-top:12px;'>
                    <div style='color:#63b3ed;font-size:0.75rem;font-weight:700;'>💡 WHY THIS IS RECOMMENDED</div>
                    <div style='color:#e2e8f0;font-size:0.85rem;margin-top:4px;'>{rec.get("explanation","")}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Missing prerequisites
                missing = rec.get("missing_prerequisites", [])
                if missing:
                    st.warning(f"⚠️ Complete first: {', '.join(missing)}")
                
            with col_b:
                # Score gauge
                score_color = "#48bb78" if score >= 80 else "#ed8936" if score >= 60 else "#e53e3e"
                st.markdown(f"""
                <div style='text-align:center;background:rgba(255,255,255,0.04);border-radius:12px;padding:16px;'>
                    <div style='font-size:2rem;font-weight:800;color:{score_color};'>{score:.0f}</div>
                    <div style='color:#718096;font-size:0.7rem;'>/ 100</div>
                    <div style='color:#a0aec0;font-size:0.8rem;margin-top:4px;'>AI Score</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='margin-top:10px;font-size:0.82rem;'>
                    <div style='display:flex;justify-content:space-between;margin:4px 0;'>
                        <span style='color:#718096;'>Difficulty</span>
                        <span style='color:{diff_color};font-weight:600;'>{difficulty}</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;margin:4px 0;'>
                        <span style='color:#718096;'>Duration</span>
                        <span style='color:#e2e8f0;font-weight:600;'>{rec.get("duration_hours",0):.0f}h</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;margin:4px 0;'>
                        <span style='color:#718096;'>Rating</span>
                        <span style='color:#f6e05e;font-weight:600;'>⭐ {rec.get("rating",4.0):.1f}</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;margin:4px 0;'>
                        <span style='color:#718096;'>Type</span>
                        <span style='color:#e2e8f0;font-weight:600;'>{rec.get("resource_type","")}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Score breakdown (no nested expander — Streamlit forbids it)
                breakdown = rec.get("score_breakdown", {})
                if breakdown:
                    rows = "".join(
                        f"<div style='display:flex;justify-content:space-between;font-size:0.8rem;margin:3px 0;'>"
                        f"<span style='color:#a0aec0;'>{factor.replace('_',' ').title()}</span>"
                        f"<span style='color:#63b3ed;font-weight:600;'>{val:.0f}%</span></div>"
                        for factor, val in breakdown.items()
                    )
                    st.markdown(
                        f"<div style='background:rgba(99,179,237,0.07);border-radius:8px;padding:10px 12px;margin-top:8px;'>"
                        f"<div style='color:#63b3ed;font-size:0.72rem;font-weight:700;margin-bottom:6px;'>📊 SCORE BREAKDOWN</div>"
                        f"{rows}</div>",
                        unsafe_allow_html=True
                    )

                # Start button
                rid = rec.get("resource_id", "")
                btn_label = "▶ Start Course" if rec.get("resource_type") == "Course" else "🛠️ Start Project"
                if st.button(btn_label, key=f"start_{rid}_{displayed}", use_container_width=True):
                    if not demo_mode:
                        api.update_progress(user_id, rid, rec.get("resource_type","Course"), 0)
                    st.success(f"Added to your learning path!")

if displayed == 0:
    st.info("No recommendations match your current filters. Try adjusting the filters above.")
