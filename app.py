import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import json

st.set_page_config(page_title="Work Schedule Maker", layout="wide")
st.title("🗓️ Employee Work Schedule Generator")

# ====================== SESSION STATE ======================
if 'business_hours' not in st.session_state:
    st.session_state.business_hours = {}
if 'employees' not in st.session_state:
    st.session_state.employees = []
if 'generated_df' not in st.session_state:
    st.session_state.generated_df = None
if 'uploaded_json' not in st.session_state:
    st.session_state.uploaded_json = None

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ====================== SAVE & LOAD ======================
st.subheader("💾 Save & Load Settings")

col1, col2 = st.columns(2)

with col1:
    if st.button("💾 Prepare Download File"):
        save_data = {
            "business_hours": st.session_state.business_hours,
            "employees": st.session_state.employees
        }
        json_str = json.dumps(save_data, indent=2, default=str)
        st.download_button(
            label="⬇️ Download schedule_settings.json",
            data=json_str,
            file_name="schedule_settings.json",
            mime="application/json",
            key="download_json_btn"
        )

with col2:
    uploaded_file = st.file_uploader("📤 Upload saved settings", type=["json"], key="json_uploader")
    
    if uploaded_file is not None:
        st.session_state.uploaded_json = uploaded_file
        st.info("File selected. Now click the Load button below.")

    if st.session_state.uploaded_json is not None:
        if st.button("✅ Load This File", type="primary", key="load_button"):
            try:
                loaded = json.load(st.session_state.uploaded_json)
                st.session_state.business_hours = loaded.get("business_hours", {})
                st.session_state.employees = loaded.get("employees", [])
                st.success("✅ Settings Loaded Successfully!")
                st.session_state.uploaded_json = None  # Clear after load
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load file: {e}")
                st.session_state.uploaded_json = None

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📅 Business Hours")
    for day in days:
        col_a, col_b = st.columns(2)
        with col_a:
            default_open = datetime.strptime(
                st.session_state.business_hours.get(day, ("09:00", "17:00"))[0], "%H:%M"
            ).time()
            open_time = st.time_input(f"{day} Open", value=default_open, key=f
