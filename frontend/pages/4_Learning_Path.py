"""
4_Learning_Path.py — Visual prerequisite-aware learning roadmap.
"""
import streamlit as st
import sys, os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils import api
from frontend.utils.demo_data import DEMO_LEARNING_PATH

st.set_page_config(page_title="Learning Path — LearnPath AI", page_icon="🗺️", layout="wide")

user_id = st.session_state.get("user_id", 1)
demo_mode = st.session_state.get("demo_mode", True)

if demo_mode:
    data = DEMO_LEARNING_PATH
else:
    data = api.get_learning_path(user_id) or DEMO_LEARNING_PATH

st.markdown("""
<div style='background:linear-gradient(135deg,#667eea,#764ba2);border-radius:16px;padding:24px 32px;color:white;margin-bottom:24px;'>
    <h2 style='margin:0;'>🗺️ Learning Roadmap</h2>
    <p style='opacity:0.85;margin:4px 0 0;'>Your personalized, prerequisite-aware learning path to reach your career goal.</p>
</div>
""", unsafe_allow_html=True)

# ─── Summary ────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🎯 Career Goal", data.get("career_goal", ""))
c2.metric("📚 Total Phases", data.get("total_phases", 0))
c3.metric("⏱️ Total Hours", f"{data.get('total_hours', 0):.0f}h")
c4.metric("📅 Estimated Months", data.get("estimated_months", 0))
c5.metric("🏆 Readiness", f"{data.get('readiness_score', 0):.1f}%")

st.markdown("---")

phases = data.get("phases", [])
path_items = data.get("path_items", [])

# ─── Visual Roadmap ──────────────────────────────────────────────
st.markdown("### 🗺️ Phase-by-Phase Roadmap")

if phases:
    STATUS_ICON = {
        "completed": "✅", "in_progress": "▶️", "available": "🔓", "locked": "🔒"
    }
    STATUS_COLOR = {
        "completed": "#48bb78", "in_progress": "#63b3ed",
        "available": "#ed8936", "locked": "#4a5568"
    }

    cols_per_row = 4
    for row_start in range(0, len(phases), cols_per_row):
        row_phases = phases[row_start:row_start + cols_per_row]
        cols = st.columns(len(row_phases))
        for i, ph in enumerate(row_phases):
            status = ph.get("status", "locked")
            icon = STATUS_ICON.get(status, "🔒")
            color = STATUS_COLOR.get(status, "#4a5568")
            bg = f"rgba({','.join(str(int(color.lstrip('#')[j:j+2], 16)) for j in (0,2,4))},0.15)"
            
            with cols[i]:
                st.markdown(f"""
                <div style='background:{bg};border:2px solid {color};border-radius:14px;padding:16px;text-align:center;margin-bottom:8px;min-height:130px;'>
                    <div style='font-size:1.8rem;'>{icon}</div>
                    <div style='color:#a0aec0;font-size:0.7rem;font-weight:700;letter-spacing:1px;margin:4px 0;'>PHASE {ph.get("phase","")}</div>
                    <div style='color:#e2e8f0;font-weight:700;font-size:0.95rem;'>{ph.get("skill","")}</div>
                    <div style='color:{color};font-size:0.75rem;font-weight:600;margin-top:6px;'>{status.replace("_"," ").title()}</div>
                    <div style='color:#718096;font-size:0.7rem;margin-top:4px;'>Gap: {ph.get("gap",0):.0f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Arrow between rows
        if row_start + cols_per_row < len(phases):
            st.markdown("<div style='text-align:center;font-size:1.5rem;color:#667eea;padding:8px;'>↓</div>", unsafe_allow_html=True)

# ─── Detailed Path Items ─────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Detailed Learning Steps")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    show_type = st.multiselect("Filter by Type", ["Course", "Assessment", "Project"], default=["Course", "Assessment", "Project"])
with filter_col2:
    show_status = st.multiselect("Filter by Status", ["in_progress", "available", "locked", "completed"], 
                                  default=["in_progress", "available", "locked", "completed"])

TYPE_ICON = {"Course": "📚", "Assessment": "📝", "Project": "🛠️"}
STATUS_ICON2 = {"completed": "✅", "in_progress": "▶️", "available": "🔓", "locked": "🔒"}

for item in path_items:
    if item.get("resource_type") not in show_type:
        continue
    if item.get("status") not in show_status:
        continue

    status = item.get("status", "locked")
    type_icon = TYPE_ICON.get(item["resource_type"], "📄")
    status_icon = STATUS_ICON2.get(status, "🔒")
    bg_color = "rgba(72,187,120,0.08)" if status == "completed" else \
               "rgba(99,179,237,0.08)" if status == "in_progress" else \
               "rgba(237,137,54,0.08)" if status == "available" else \
               "rgba(255,255,255,0.02)"
    border_color = "#48bb78" if status == "completed" else \
                   "#63b3ed" if status == "in_progress" else \
                   "#ed8936" if status == "available" else "#2d3748"

    with st.expander(f"{status_icon} {type_icon} Phase {item.get('phase','')} — {item.get('resource_title', item.get('skill',''))}"):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown(f"**Skill:** {item.get('skill','')}")
            st.markdown(f"**Type:** {item.get('resource_type','')}")
        with cc2:
            st.markdown(f"**Status:** {status.replace('_',' ').title()}")
            st.markdown(f"**Est. Hours:** {item.get('estimated_hours',0):.0f}h")
        with cc3:
            if item.get("recommendation_score", 0) > 0:
                st.markdown(f"**Score:** {item.get('recommendation_score',0):.0f}/100")
            if item.get("is_milestone"):
                st.markdown("🏆 **Milestone Assessment**")
        
        if item.get("explanation"):
            st.info(f"💡 {item['explanation']}")
        
        prereqs = item.get("prerequisites", [])
        missing = item.get("missing_prerequisites", [])
        if prereqs:
            st.markdown(f"**Prerequisites:** {', '.join(prereqs)}")
        if missing:
            st.warning(f"⚠️ Complete first: {', '.join(missing)}")

        if status in ("available", "in_progress") and item["resource_type"] == "Course":
            if st.button(f"▶ Mark as In Progress", key=f"start_{item['order']}"):
                if not demo_mode:
                    api.update_progress(user_id, item.get("resource_id",""), "Course", 0)
                st.success("Marked as in progress!")
