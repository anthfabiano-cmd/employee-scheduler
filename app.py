import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Work Schedule Maker", layout="wide")
st.title("🗓️ Employee Work Schedule Generator")
st.markdown("Adjust hours, add employees, and generate schedules instantly.")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📅 Business Hours")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    business_hours = {}
    
    for day in days:
        col1, col2 = st.columns(2)
        with col1:
            open_time = st.time_input(f"{day} Open", value=datetime.strptime("09:00", "%H:%M").time(), key=f"open_{day}")
        with col2:
            close_time = st.time_input(f"{day} Close", value=datetime.strptime("17:00", "%H:%M").time(), key=f"close_{day}")
        business_hours[day] = (open_time.strftime("%H:%M"), close_time.strftime("%H:%M"))

    st.header("👥 Employees")
    num_employees = st.number_input("Number of employees", min_value=1, value=3)
    employees = []
    
    for i in range(num_employees):
        with st.expander(f"Employee {i+1}"):
            name = st.text_input("Name", value=f"Employee {i+1}", key=f"name_{i}")
            max_hours = st.number_input("Max hours per week", min_value=1, value=40, key=f"hours_{i}")
            off_days = st.multiselect("Days off this week", days, key=f"off_{i}")
            employees.append({"name": name, "max_hours_week": max_hours, "off_requests": off_days})

# ====================== GENERATE SCHEDULE ======================
if st.button("🚀 Generate Schedule", type="primary"):
    if not employees:
        st.error("Please add at least one employee")
    else:
        with st.spinner("Creating schedule..."):
            schedule_data = []
            start_date = datetime(2026, 7, 6)  # Change this date as needed
            
            for emp in employees:
                row = {"Employee": emp["name"]}
                total_hours = 0
                
                for i, day in enumerate(days):
                    if day in emp["off_requests"]:
                        row[day] = "OFF"
                        row[f"{day}_hours"] = 0
                    else:
                        open_t, close_t = business_hours[day]
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
            
            # Show results
            st.success("✅ Schedule Generated!")
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False).encode()
                st.download_button("📥 Download CSV", csv, "schedule.csv", "text/csv")
            with col2:
                excel_buffer = pd.ExcelWriter("schedule.xlsx", engine="openpyxl")
                df.to_excel(excel_buffer, index=False)
                excel_buffer.close()
                with open("schedule.xlsx", "rb") as f:
                    st.download_button("📥 Download Excel", f, "schedule.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.info("💡 Tip: You can later add file upload for employees, required staffing, etc.")