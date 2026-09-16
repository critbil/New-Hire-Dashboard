import streamlit as st
import pandas as pd
import random

# --- CONFIGURATION & CALCULATIONS ---
# Paid Shift: 9 Hours (540 mins) -> Active Window: 478 mins (minus 20m, 30m breaks, 12m startup)
ACTIVE_PRODUCTION_MINUTES = 478.0

# Set up page configurations
st.set_page_config(page_title="Orderfiller Performance Runway", layout="wide")

# Check if we are in "Shared / View-Only Mode" based on the URL parameter
query_params = st.query_params
is_shared_view = query_params.get("mode") == "shared"

# --- PERSISTENT DATA STORAGE ---
# Keeps data alive within your cloud session
if "associates" not in st.session_state:
    st.session_state.associates = [
        {"id": 1, "name": "Marcus D.", "shift": "Shift 1", "tenure": "Week 2", "trips": 48, "perf": 44},
        {"id": 2, "name": "Elena R.", "shift": "Shift 1", "tenure": "Week 6", "trips": 185, "perf": 72},
        {"id": 3, "name": "Devon K.", "shift": "Shift 2", "tenure": "Week 12", "trips": 420, "perf": 81},
        {"id": 4, "name": "Amara T.", "shift": "Shift 4", "tenure": "Week 16", "trips": 712, "perf": 88},
        {"id": 5, "name": "Jordan M.", "shift": "Shift 5", "tenure": "Week 22", "trips": 910, "perf": 104}, 
        {"id": 6, "name": "Siddharth P.", "shift": "Shift 2", "tenure": "Week 25", "trips": 992, "perf": 98}
    ]

# --- HEADER SECTION ---
if is_shared_view:
    st.title("📋 Orderfiller Performance Feed (View-Only Mode)")
else:
    st.title("🚀 Orderfiller Admin Production Dashboard")
st.caption("Shift Constraints: 9-Hour Workday | 62 Mins Combined Breaks & Startup (478 Active Mins)")

# --- ADMIN ACTIONS (Hidden on Shared Links) ---
if not is_shared_view:
    col_ref, col_sh = st.columns([1, 4])
    with col_ref:
        if st.button("↻ Refresh Live Data", type="secondary"):
            for a in st.session_state.associates:
                a["perf"] = max(20, a["perf"] + random.randint(-3, 3))
                a["trips"] += random.randint(0, 1)
            st.rerun()
    with col_sh:
        # Generates a secure share link tracking the view parameter
        st.link_button("🔗 Generate Shareable Link View", "https://streamlit.io")

st.markdown("---")

# --- FILTERS ---
shifts = ["All Shifts", "Shift 1", "Shift 2", "Shift 4", "Shift 5"]
selected_shift = st.segmented_control("Filter Roster by Active Shift Block:", shifts, default="All Shifts")

# Apply filters
df = pd.DataFrame(st.session_state.associates)
if selected_shift != "All Shifts":
    df = df[df["shift"] == selected_shift]

# --- MAIN DASHBOARD GRID ---
col_roster, col_runway = st.columns([1, 1.8])

with col_roster:
    st.subheader("Associate Roster")
    # Show active rows matching percentages cleanly
    for idx, row in df.iterrows():
        status_color = "green" if row["perf"] >= 100 else ("blue" if row["perf"] >= 80 else "red")
        with st.container(border=True):
            st.markdown(f"### {row['name']} : {row['perf']}%")
            st.text(f"{row['shift']} • {row['tenure']} ({row['trips']} Total Trips)")

with col_runway:
    st.subheader("6-Month Graduation Runway Progress")
    if not df.empty:
        # Target the top matching employee in the sorted track
        focus_emp = df.iloc[0]
        
        # Calculate pacing parameters
        progress = min(1.0, focus_emp["trips"] / 1000.0)
        cases_min = round((focus_emp["perf"] / 100.0) * 5, 2)
        trips_day = round(8 * (focus_emp["perf"] / 100.0))
        days_mult = 4 if focus_emp["shift"] in ["Shift 1", "Shift 2"] else 3
        
        st.info(f"Targeting Metrics For: **{focus_emp['name']}** ({focus_emp['tenure']})")
        st.progress(progress, text=f"Progress to 1,000-Trip Graduation: {focus_emp['trips']} / 1,000 Trips Completed")
        
        # Display Key Analytics Grid
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Production Performance", f"{focus_emp['perf']}%", help="Calculated over 478 active production minutes")
            st.caption(f"Picking Speed: {cases_min} Cases / Min")
        with m2:
            st.metric("Projected Weekly Volume", f"{trips_day * days_mult} Trips", help="Based on schedule hours constraints")
            st.caption(f"Pace: ~{trips_day} long trips per 9-hr day")
            
        # Milestone Outlook Panel Logic
        st.markdown("#### 📋 Milestone Outlook Details")
        if focus_emp["trips"] < 700:
            if focus_emp["perf"] >= 40:
                st.success("On Track. Passed foundational Week 1 Day 4 target milestone baseline (40%).")
            else:
                st.error("Ramp-up Warning. Associate production performance is currently trailing below the required Day 4 40% efficiency target.")
        elif focus_emp["trips"] >= 700 and focus_emp["trips"] < 1000:
            if focus_emp["perf"] >= 80:
                st.success("Checkpoint Passed. Sustaining targeted 80% pace baseline at the 700-trip midpoint.")
            else:
                st.error("Action Plan Needed. Associate reached the 700-trip checkpoint marker but is trailing below the required 80% standard pace.")
        else:
            if focus_emp["perf"] >= 100:
                st.balloons()
                st.success("Graduation Requirements Fulfilled! Employee is producing at full 100%+ veteran standard metrics.")
            else:
                st.warning("1,000 Trip Volume Achieved. However, speed optimization checks are required to fully lock in 100% performance tier graduation status.")
    else:
        st.text("No active employee matching current filtering rules found.")
