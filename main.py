# main.py — Viveka Landing Page
import os
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# -------------------------------
# Streamlit Config
# -------------------------------
st.set_page_config(
    page_title="VIVEKA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# Disable Back Button
# -------------------------------
components.html("""
    <script>
        history.pushState(null, '', location.href);
        window.onpopstate = function () {
            history.go(1);
        };
    </script>
""", height=0)

# -------------------------------
# Hide Sidebar
# -------------------------------
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Load Logo Safely
# -------------------------------
logo_path = "assets/logo.png"
logo = None
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
else:
    st.error("❌ Logo not found! Please make sure 'assets/logo.png' exists.")

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(-45deg, #0F2027, #203A43, #2C5364, #141E30);
            background-size: 400% 400%;
            animation: gradientBG 12s ease infinite;
        }
        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        .title {
            font-size: 3rem;
            font-weight: bold;
            color: white;
            text-align: center;
            margin-top: 1rem;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #cccccc;
            text-align: center;
            margin-bottom: 2rem;
        }
        .footer {
            text-align: center;
            font-size: 0.85rem;
            color: #aaaaaa;
            margin-top: 3rem;
        }
        button[kind="primary"] {
            background-color: #4caf50 !important;
            color: white !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Centered Logo
# -------------------------------
if logo:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(logo, width="stretch")

# -------------------------------
# Intro Section
# -------------------------------
st.markdown("<div class='title'>VIVEKA</div>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Discernment for your health · Check food, beverage & medicine ingredients safely.</p>", unsafe_allow_html=True)

st.markdown("### Why choose **Viveka**?")
st.markdown("<p style='color: #cccccc; font-size: 0.95rem;'>Your personal assistant to detect harmful ingredients, side effects & prescription warnings.</p>", unsafe_allow_html=True)

# -------------------------------
# Features
# -------------------------------
features = [
    ("🧾 Ingredient Scan", "Upload or type ingredients and instantly detect harmful or allergenic contents."),
    ("💊 Prescription Check", "Know whether a product should only be taken with doctor’s advice."),
    ("🌍 Global Database", "Covers food, beverages, and medicines with a database of 750+ common ingredients."),
    ("⚠️ Personalized Alerts", "Get warnings based on your medical profile and allergies."),
    ("📂 History Tracking", "Save your scanned products for future reference."),
    ("🔒 Secure & Private", "Your data and medical profile stay safe and confidential.")
]

for i in range(0, len(features), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(features):
            with cols[j]:
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255,255,255,0.05); padding: 1rem 1.2rem;
                                border-radius: 15px; margin-bottom: 1rem;
                                box-shadow: 0 0 8px rgba(255,255,255,0.06);">
                        <h4 style="color: #ffffff; margin-bottom: 0.3rem;">{features[i + j][0]}</h4>
                        <p style="color: #cccccc; font-size: 0.9rem;">{features[i + j][1]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# -------------------------------
# Get Started Button
# -------------------------------
if st.button("Get Started", width="stretch"):
    try:
        st.switch_page("pages/login_signup.py")  # Needs Streamlit >=1.32
    except Exception:
        st.page_link("pages/login_signup.py", label="👉 Go to Login / Signup")

# -------------------------------
# Footer
# -------------------------------
st.markdown("""
    <hr style="margin-top: 3rem; border: 0.5px solid #444444;" />
    <div style='text-align: center; color: #cccccc; font-size: 0.9rem; padding-top: 1rem;'>
        © 2025 <b>Viveka</b> · All rights reserved.<br>
        Made by Nirvighna Shendurnikar 
    </div>
""", unsafe_allow_html=True)
