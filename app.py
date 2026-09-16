import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Orderfiller Tracking Master Dashboard", layout="wide")

is_shared_view = st.query_params.get("mode") == "shared"

# --- SYSTEM DATA VAULT ---
# Recalibrated to ensure Week 3 associates scale logically with your 8 trips/day baseline
if "roster_data" not in st.session_state:
    st.session_state.roster_data = [
        # --- Shift 1 (Mon-Thu Day) ---
        {"id": 1, "name": "Marcus D.", "shift": "Shift 1", "tenure": "Week 2", "trips": 48, "base_avg": 44.0},
        {"id": 2, "name": "Elena R.", "shift": "Shift 1", "tenure": "Week 6", "trips": 185, "base_avg": 72.0},
        {"id": 3, "name": "Tyler W. (Outlier - Severe Low)", "shift": "Shift 1", "tenure": "Week 3", "trips": 92, "base_avg": 9.0}, # Updated to realistic ~90 trips
        {"id": 4, "name": "Chris B. (Outlier - Mild Low)", "shift": "Shift 1", "tenure": "Week 3", "trips": 88, "base_avg": 29.0},   # Updated to realistic ~90 trips
        
        # --- Shift 2 (Mon-Thu Night) ---
        {"id": 5, "name": "Devon K.", "shift": "Shift 2", "tenure": "Week 12", "trips": 420, "base_avg": 81.0},
        {"id": 6, "name": "Siddharth P.", "shift": "Shift 2", "tenure": "Week 25", "trips": 992, "base_avg": 98.0},
        {"id": 7, "name": "Dominic V. (Outlier - Elite High)", "shift": "Shift 2", "tenure": "Week 18", "trips": 745, "base_avg": 142.0},
        
        # --- Shift 4 (Fri-Sun Day) ---
        {"id": 8, "name": "Amara T.", "shift": "Shift 4", "tenure": "Week 16", "trips": 712, "base_avg": 88.0},
        {"id": 9, "name": "Gavin J. (Outlier - Severe Low)", "shift": "Shift 4", "tenure": "Week 5", "trips": 140, "base_avg": 22.0}, # Adjusted for Week 5 timeline
        
        # --- Shift 5 (Fri-Sun Night) ---
        {"id": 10, "name": "Jordan M.", "shift": "Shift 5", "tenure": "Week 22", "trips": 910, "base_avg": 104.0},
        {"id": 11, "name": "Malik X. (Outlier - Elite High)", "shift": "Shift 5", "tenure": "Week 14", "trips": 510, "base_avg": 146.0}
    ]

# --- APP LAYOUT NAVIGATION ---
if is_shared_view:
    st.title("📋 Warehouse Performance Matrix Feed (View-Only)")
else:
    st.title("🚀 Warehouse Roster Weekly Forecasting Dashboard")
st.caption("Active Configurations: 9-Hour Workday (478 Active Mins) | Tenure Constraint: Hard 40% Performance Floor Past Week 2")

st.markdown("---")

# --- USER SELECTION CONTROLS ---
col_shift, col_days = st.columns([1.2, 1.8])

with col_shift:
    st.markdown("#### 1. Select Isolated Shift Group")
    shift_options = [
        "Shift 1 (Mon-Thu | 4am - 3pm)", 
        "Shift 2 (Mon-Thu | 3:30pm - 3am)", 
        "Shift 4 (Fri-Sun | Day Block)", 
        "Shift 5 (Fri-Sun | Night Block)"
    ]
    selected_display = st.selectbox("Choose Target Team:", shift_options, index=0)
    selected_shift = selected_display.split(" (")[0]

with col_days:
    st.markdown("#### 2. Select Target Schedule Day")
    week_days = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    selected_day = st.segmented_control("Select Day to View Expected Performance Matrix:", week_days, default="Monday")

# --- CONFORMING PERFORMANCE MATRICES FORECAST ENGINE ---
def get_daily_forecast(associate, day):
    shift = associate["shift"]
    base = associate["base_avg"]
    trips = associate["trips"]
    
    try:
        tenure_num = int(associate["tenure"].replace("Week ", ""))
    except:
        tenure_num = 1
    
    mon_thu_shifts = ["Shift 1", "Shift 2"]
    fri_sun_shifts = ["Shift 4", "Shift 5"]
    mon_thu_days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    fri_sun_days = ["Saturday", "Sunday", "Friday"]
    
    if shift in mon_thu_shifts and day not in mon_thu_days:
        return "Off Shift", "off"
    if shift in fri_sun_shifts and day not in fri_sun_days:
        return "Off Shift", "off"
        
    random.seed(associate["id"] + len(day))
    daily_variance = random.randint(-4, 4)
    final_perf = round(base + daily_variance, 1)
    
    # --- LOCKED MANDATORY PERFORMANCE FLOOR RULE ---
    if tenure_num > 2:
        if trips < 700:
            target_expectation = 40.0
        elif 700 <= trips < 1000:
            target_expectation = 80.0
        else:
            target_expectation = 100.0
    else:
        if trips < 700:
            target_expectation = 40.0
        elif 700 <= trips < 1000:
            target_expectation = 80.0
        else:
            target_expectation = 100.0
        
    deficit = target_expectation - final_perf
    
    if final_perf >= 140.0:
        return f"{final_perf}% 🔥🔥🔥", "elite"
    elif deficit >= 30.0:
        return f"{final_perf}% 🚨 Warning", "warning"
    elif deficit >= 10.0:
        return f"{final_perf}% ⚠️ Caution", "caution"
    else:
        return f"{final_perf}%", "meeting"

# Assemble matrix data rows
matrix_rows = []
for a in st.session_state.roster_data:
    if a["shift"] == selected_shift:
        expected_metric, status_tag = get_daily_forecast(a, selected_day)
        matrix_rows.append({
            "Associate Name": a["name"],
            "Assigned Shift": a["shift"],
            "Tenure Stage": a["tenure"],
            "Cumulative Trips Completed": a["trips"],
            "Graduation Distance": f"{a['trips']} / 1,000 Trips",
            f"Expected {selected_day} Performance": expected_metric,
            "status_tag": status_tag
        })

# --- DATA SUMMARY SCREEN PRESENTATION ---
st.markdown(f"### 📊 Team Roster: **{selected_shift}** Projections for **{selected_day}**")

if matrix_rows:
    display_df = pd.DataFrame(matrix_rows).drop(columns=["status_tag"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("#### 📋 Coaching & Performance Threshold Highlights")
    for row in matrix_rows:
        name = row["Associate Name"]
        perf_str = row[f"Expected {selected_day} Performance"]
        tag = row["status_tag"]
        trips = row["Cumulative Trips Completed"]
        
        if tag == "off":
            st.write(f"💤 **{name}** is scheduled off on {selected_day}.")
        elif tag == "elite":
            st.success(f"🏆 **{name}** (Trips: {trips}/1000) is pulling an elite, legendary production score of **{perf_str}** today!")
        elif tag == "meeting":
            st.success(f"🟢 **{name}** (Trips: {trips}/1000) is **MEETING TARGET OR ABOVE** at **{perf_str}** for their active hours today. Keep it up!")
        elif tag == "caution":
            st.warning(f"⚠️ **{name}** (Trips: {trips}/1000) is flagged with a **CAUTION** status at **{perf_str}**. Performance is running below expectation!")
        elif tag == "warning":
            st.error(f"🚨 **{name}** (Trips: {trips}/1000) is flagged with an active **WARNING** at **{perf_str}**. Performance is dropping 30%+ below their active milestone hurdle!")
else:
    st.info(f"No active associates currently tracking under {selected_shift}.")
