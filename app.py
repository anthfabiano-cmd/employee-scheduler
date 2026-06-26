import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="Work Schedule Maker", layout="wide")
st.title("🗓️ Employee Work Schedule Generator")
st.markdown("Adjust hours, add employees, and generate schedules. Data persists on refresh!")

# ====================== SESSION STATE INITIALIZATION ======================
if 'business_hours' not in st.session_state:
    st.session_state.business_hours = {}
if 'employees' not in st.session_state:
    st.session_state.employees = []
if 'generated_df' not in st.session_state:
    st.session_state.generated_df = None

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📅 Business Hours")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day in days:
        col1, col2 = st.columns(2)
        with col1:
            default_open = datetime.strptime(st.session_state.business_hours.get(day, ("09:00", "17:00"))[0], "%H:%M").time()
            open_time = st.time_input(f"{day} Open", value=default_open, key=f"open_{day}")
        with col2:
            default_close = datetime.strptime(st.session_state.business_hours.get(day, ("09:00", "17:00"))[1], "%H:%M").time()
            close_time = st.time_input(f"{day} Close", value=default_close, key=f"close_{day}")
        
        st.session_state.business_hours[day] = (open_time.strftime("%H:%M"), close_time.strftime("%H:%M"))

    st.header("👥 Employees")
    num_employees = st.number_input("Number of employees", min_value=1, value=max(len(st.session_state.employees), 3), key="num_emp")
    
    # Keep employees in sync with session state
    if len(st.session_state.employees) != num_employees:
        while len(st.session_state.employees) < num_employees:
            st.session_state.employees.append({"name": f"Employee {len(st.session_state.employees)+1}", "max_hours_week": 40, "off_requests": []})
        while len(st.session_state.employees) > num_employees:
            st.session_state.employees.pop()

    for i in range(num_employees):
        with st.expander(f"Employee {i+1}: {st.session_state.employees[i]['name']}"):
            name = st.text_input("Name", value=st.session_state.employees[i]["name"], key=f"name_{i}")
            max_hours = st.number_input("Max hours per week", min_value=1, value=st.session_state.employees[i]["max_hours_week"], key=f"hours_{i}")
            off_days = st.multiselect("Days off this week", days, default=st.session_state.employees[i]["off_requests"], key=f"off_{i}")
            
            st.session_state.employees[i] = {"name": name, "max_hours_week": max_hours, "off_requests": off_days}

# ====================== GENERATE SCHEDULE ======================
if st.button("🚀 Generate Schedule", type="primary"):
    if not st.session_state.employees:
        st.error("Please add at least one employee")
    else:
        with st.spinner("Creating schedule..."):
            schedule_data = []
            start_date = datetime(2026, 7, 6)  # Change this date as needed
            
            for emp in st.session_state.employees:
                row = {"Employee": emp["name"]}
                total_hours = 0
                
                for i, day in enumerate(days):
                    if day in emp["off_requests"]:
                        row[day] = "OFF"
                        row[f"{day}_hours"] = 0
                    else:
                        open_t, close_t = st.session_state.business_hours[day]
                        open_time = datetime.strptime(open_t, "%H:%M")
                        close_time = datetime.strptime(close_t, "%H:%M")
                        hours = (close_time - open_time).seconds / 3600
                        
                        assigned = min(hours, emp["max_hours_week"] - total_hours)
                        if assigned > 0:
                            row[day] = f"{open_t} - {close_t} ({assigned:.1f}h)"
                            row[f"{day}_hours"] = assigned
                            total
