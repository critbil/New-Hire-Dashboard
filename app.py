import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Orderfiller Performance Runway", layout="wide")

is_shared_view = st.query_params.get("mode") == "shared"

# --- SYSTEM DATA VAULT ---
# Cleaned up and verified: Tyler and Chris are correctly on Shift 1 with ~92 trips completed by Week 3
if "roster_data" not in st.session_state:
    st.session_state.roster_data = [
        # --- Shift 1 (Mon-Thu Day | 4 Days) ---
        {"id": 1, "name": "Marcus D.", "shift": "Shift 1", "tenure": "Week 2", "trips": 48, "base_avg": 44.0},
        {"id": 2, "name": "Elena R.", "shift": "Shift 1", "tenure": "Week 6", "trips": 185, "base_avg": 72.0},
        {"id": 3, "name": "Tyler W. (Outlier - Severe Low)", "shift": "Shift 1", "tenure": "Week 3", "trips": 92, "base_avg": 9.0}, 
        {"id": 4, "name": "Chris B. (Outlier - Mild Low)", "shift": "Shift 1", "tenure": "Week 3", "trips": 88, "base_avg": 29.0},   
        
        # --- Shift 2 (Mon-Thu Night | 4 Days) ---
        {"id": 5, "name": "Devon K.", "shift": "Shift 2", "tenure": "Week 12", "trips": 420, "base_avg": 81.0},
        {"id": 6, "name": "Siddharth P.", "shift": "Shift 2", "tenure": "Week 25", "trips": 992, "base_avg": 98.0},
        {"id": 7, "name": "Dominic V. (Outlier - Elite High)", "shift": "Shift 2", "tenure": "Week 18", "trips": 745, "base_avg": 142.0},
        
        # --- Shift 4 (Fri-Sun Day | 3 Days) ---
        {"id": 8, "name": "Amara T.", "shift": "Shift 4", "tenure": "Week 16", "trips": 712, "base_avg": 88.0},
        {"id": 9, "name": "Gavin J. (Outlier - Severe Low)", "shift": "Shift 4", "tenure": "Week 5", "trips": 140, "base_avg": 22.0}, 
        
        # --- Shift 5 (Fri-Sun Night | 3 Days) ---
        {"id": 10, "name": "Jordan M.", "shift": "Shift 5", "tenure": "Week 22", "trips": 910, "base_avg": 104.0},
        {"id": 11, "name": "Malik X. (Outlier - Elite High)", "shift": "Shift 5", "tenure": "Week 14", "trips": 510, "base_avg": 146.0}
    ]

# --- APP LAYOUT NAVIGATION ---
if is_shared_view:
    st.title("📋 Warehouse Performance Matrix Feed (View-Only)")
else:
    st.title("🚀 Warehouse Roster Weekly Forecasting Dashboard")
st.caption("Active Configurations: 9-Hour Workday (478 Active Mins) | Baseline: 8 Trips Per Shift standard")

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
    # FIXED: Clean slice ensuring string perfectly matches "Shift 1", "Shift 2", etc.
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
        return "Off Shift", "off", 0, 0
    if shift in fri_sun_shifts and day not in fri_sun_days:
        return "Off Shift", "off", 0, 0
        
    random.seed(associate["id"] + len(day))
    daily_variance = random.randint(-4, 4)
    final_perf = round(base + daily_variance, 1)
    
    # Identify Milestone Target Based on Lifecycle Checklist
    if trips < 700:
        target_expectation = 40.0
    elif 700 <= trips < 1000:
        target_expectation = 80.0
    else:
        target_expectation = 100.0
        
    deficit = target_expectation - final_perf
    
    # FIXED REALISTIC MATHEMATICAL FORECAST: 
    # Regardless of speed deficits, an associate works a 9-hr block executing an average standard layout volume of 8 trips/shift.
    trips_per_day = 8
    weekly_multiplier = 4 if shift in mon_thu_shifts else 3
    projected_weekly_trips = trips_per_day * weekly_multiplier
    
    if final_perf >= 140.0:
        return f"{final_perf}% 🔥🔥🔥 anisotropy", "elite", trips_per_day, projected_weekly_trips
    elif deficit >= 30.0:
        return f"{final_perf}% 🚨 Warning", "warning", trips_per_day, projected_weekly_trips
    elif deficit >= 10.0:
        return f"{final_perf}% ⚠️ Caution", "caution", trips_per_day, projected_weekly_trips
    else:
        return f"{final_perf}%", "meeting", trips_per_day, projected_weekly_trips

# Assemble matrix data rows
matrix_rows = []
for a in st.session_state.roster_data:
    if a["shift"] == selected_shift:
        expected_metric, status_tag, daily_trips, weekly_trips = get_daily_forecast(a, selected_day)
        
        weekly_trips_str = f"{weekly_trips} Trips" if expected_metric != "Off Shift" else "0 Trips"
        daily_trips_str = f"{daily_trips} Trips/Day" if expected_metric != "Off Shift" else "-"
        
        matrix_rows.append({
            "Associate Name": a["name"],
            "Assigned Shift": a["shift"],
            "Tenure Stage": a["tenure"],
            "Current Career Trips": a["trips"],
            "Daily Volume Est.": daily_trips_str,
            "Projected Weekly Volume": weekly_trips_str,
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
        current_trips = row["Current Career Trips"]
        week_forecast = row["Projected Weekly Volume"]
        
        if tag == "off":
            st.write(f"💤 **{name}** is scheduled off on {selected_day}.")
        elif tag == "elite":
            st.success(f"🏆 **{name}** (Total: {current_trips}) is pulling an elite **{perf_str}** and is on track to complete **{week_forecast}** for the week!")
        elif tag == "meeting":
            st.success(f"🟢 **{name}** (Total: {current_trips}) is **MEETING TARGET** at **{perf_str}** and is trending toward **{week_forecast}** by Friday!")
        elif tag == "caution":
            st.warning(f"⚠️ **{name}** (Total: {current_trips}) is running a **CAUTION** tier pace of **{perf_str}**. Projected week total: **{week_forecast}**.")
        elif tag == "warning":
            st.error(f"🚨 **{name}** (Total: {current_trips}) is flagged with a **WARNING** pace of **{perf_str}**. Projected week total drops to **{week_forecast}**!")
else:
    st.info(f"No active associates currently tracking under {selected_shift}.")
