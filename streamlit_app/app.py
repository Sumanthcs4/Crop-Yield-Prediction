import streamlit as st
import requests
from PIL import Image
import base64
import os  # ✅ added for path handling

# === Page Config ===
st.set_page_config(page_title="Crop Yield Prediction", layout="centered")

# === Background Styling + Input Fixes ===
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}

        .block-container {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 3rem;
            border-radius: 1rem;
        }}

        input, select, textarea {{
            color: black !important;
            background-color: #f1f1f1 !important;
        }}

        ::placeholder {{
            color: #000 !important;
            opacity: 1 !important;
        }}

        label {{
            color: black !important;
            font-weight: 600 !important;
        }}

        .form-wrapper {{
            margin-top: 12vh;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ Corrected background path
bg_path = os.path.join("streamlit_app", "assets", "background.png")
set_background(bg_path)

# === Header Wrapper ===
st.markdown("<div class='form-wrapper'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>Crop Yield Prediction</h1>", unsafe_allow_html=True)

# === Input Form ===
with st.form("predict_form"):
    col1, col2 = st.columns(2)

    with col1:
        Area = st.text_input("Area (e.g., Karnataka)")
        Crop = st.text_input("Crop (e.g., Rice)")
        Item = st.text_input("Item (e.g., Rice)")
        average_rain_fall_mm_per_year = st.number_input("Average Rainfall (mm/year)", format="%.2f")

    with col2:
        Season = st.text_input("Season (e.g., Rabi)")
        Year = st.number_input("Year", min_value=2000, max_value=2100, value=2023, step=1)
        pesticides_tonnes = st.number_input("Pesticides Used (tonnes)", format="%.2f")
        avg_temp = st.number_input("Average Temperature (°C)", format="%.2f")

    submitted = st.form_submit_button("Predict")

st.markdown("</div>", unsafe_allow_html=True)

# === API Request & Prediction ===
if submitted:
    with st.spinner("Predicting..."):
        input_payload = {
            "Area": Area,
            "Crop": Crop,
            "Season": Season,
            "Year": int(Year),
            "Item": Item,
            "average_rain_fall_mm_per_year": average_rain_fall_mm_per_year,
            "pesticides_tonnes": pesticides_tonnes,
            "avg_temp": avg_temp
        }

        try:
            response = requests.post("http://127.0.0.1:8000/predict", json=input_payload)
            if response.status_code == 200:
                prediction = response.json().get("Predicted_Yield", "N/A")
                st.success(f"🌾 Predicted Crop Yield: **{prediction:.2f}** tonnes/hectare")
            else:
                st.error("❌ Prediction failed. Check FastAPI backend.")
        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")
