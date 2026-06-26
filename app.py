import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import json

st.set_page_config(page_title="Work Schedule Maker", layout="wide")
st.title("🗓️ Employee Work Schedule Generator")
st.markdown("**Save your settings** so they survive refresh!")

# ====================== SESSION STATE ======================
if 'business_hours' not in st.session_state:
    st.session_state.business_hours = {}
if 'employees' not in st.session_state:
    st.session_state.employees = []
if 'generated_df' not in st.session_state:
    st.session_state.generated_df = None

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ====================== SAVE / LOAD ======================
col_save, col_load = st.columns(2)
with col_save:
    if st.button("💾 Save Current Settings"):
        save_data = {
            "business_hours": st.session_state.business_hours,
            "employees": st.session_state.employees
        }
        with open("saved_schedule.json", "w") as f:
            json.dump(save_data, f)
        st.success("✅ Settings Saved!")

with col_load:
    if st.button("📂 Load Saved Settings"):
        try:
            with open("saved_schedule.json", "r") as f:
                loaded = json.load(f)
            st.session_state.business_hours = loaded.get("business_hours", {})
            st.session_state.employees = loaded.get("employees", [])
            st.success("✅ Settings Loaded!")
            st.rerun()
        except:
            st.error("No saved file found. Save first.")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📅 Business Hours")
    for day in days:
        col1, col2 = st.columns(2)
        with col1:
            default_open = datetime.strptime(
                st.session_state.business_hours.get(day, ("09:00", "17:00"))[0], "%H:%M"
            ).time()
            open_time = st.time_input(f"{day} Open", value=default_open, key=f"open_{day}")
        with col2:
            default_close = datetime.strptime(
                st.session_state.business_hours.get(day, ("09:00", "17:00"))[1], "%H:%M"
            ).time()
            close_time = st.time_input(f"{day} Close", value=default_close, key=f"close_{day}")
        
        st.session_state.business_hours[day] = (open_time.strftime("%H:%M"), close_time.strftime("%H:%M"))

    st.header("👥 Employees")
    num_employees = st.number_input("Number of employees", min_value=1, value=max(len(st.session_state.employees), 3), key="num_emp")
    
    current_len = len(st.session_state.employees)
    if num_employees > current_len:
        for _ in range(num_employees - current_len):
            st.session_state.employees.append({"name": f"Employee {len(st.session_state.employees)+1}", 
                                             "max_hours_week": 40, "off_requests": []})
    elif num_employees < current_len:
        st.session_state.employees = st.session_state.employees[:num_employees]

    for i in range(num_employees):
        emp = st.session_state.employees[i]
        with st.expander(f"Employee {i+1}: {emp.get('name', 'New')}"):
            name = st.text_input("Name", value=emp.get("name", ""), key=f"name_{i}")
            max_hours = st.number_input("Max hours per week", min_value=1, value=emp.get("max_hours_week", 40), key=f"hours_{i}")
            off_days = st.multiselect("Days off this week", days, default=emp.get("off_requests", []), key=f"off_{i}")
            
            st.session_state.employees[i] = {"name": name, "max_hours_week": max_hours, "off_requests": off_days}

# ====================== GENERATE ======================
if st.button("🚀 Generate Schedule", type="primary"):
    if not st.session_state.employees:
        st.error("Add at least one employee")
    else:
        with st.spinner("Creating schedule..."):
            schedule_data = []
            for emp in st.session_state.employees:
                row = {"Employee": emp["name"]}
                total_hours = 0
                
                for day in days:
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
                            total_hours += assigned
                        else:
                            row[day] = "OFF (max hours)"
                            row[f"{day}_hours"] = 0
                
                row["Total Hours"] = round(total_hours, 1)
                schedule_data.append(row)
            
            df = pd.DataFrame(schedule_data)
            st.session_state.generated_df = df

            st.success("✅ Schedule Generated!")
            st.dataframe(df, use_container_width=True, height=500)

            # Downloads
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Download CSV", df.to_csv(index=False).encode(), "schedule.csv", "text/csv")
            with col2:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Schedule')
                output.seek(0)
                st.download_button("📥 Download Excel", output, "employee_schedule.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif st.session_state.generated_df is not None:
    st.success("✅ Previous Schedule")
    st.dataframe(st.session_state.generated_df, use_container_width=True, height=500)

st.info("💡 Use **Save Current Settings** after making changes. Then use **Load** after refresh.")
