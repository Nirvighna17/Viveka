# pages/profile.py
import streamlit as st
import sqlite3
from pathlib import Path
from PIL import Image
import io
import base64
import os

# ---- DB CONFIG ----
DB_FILE = "users.db"
PROFILE_PIC_DIR = Path("profile_pics")
PROFILE_PIC_DIR.mkdir(exist_ok=True)

# ---- CSS FOR HIGH-END UI ----
st.markdown("""
<style>
/* Container */
.profile-container {
    max-width: 900px;
    margin: 20px auto;
    padding: 25px;
    border-radius: 15px;
    background: #1e1e1e;
    color: #fff;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Profile Card */
.profile-card {
    display: flex;
    align-items: center;
    gap: 25px;
    flex-wrap: wrap;
    margin-bottom: 25px;
}
.profile-pic-wrapper {
    position: relative;
    width: 150px;
    height: 150px;
}
.profile-pic {
    border-radius: 50%;
    border: 4px solid #4CAF50;
    width: 150px;
    height: 150px;
    object-fit: cover;
    transition: transform 0.2s ease;
}
.profile-pic:hover {
    transform: scale(1.05);
}
.edit-overlay {
    position: absolute;
    bottom: 0;
    right: 0;
    background-color: #4CAF50;
    border-radius: 50%;
    padding: 6px;
    cursor: pointer;
    border: 2px solid #fff;
}

/* Name & Info */
.profile-info {
    flex: 1;
}
.profile-name {
    font-size: 28px;
    font-weight: bold;
}
.profile-subtitle {
    font-size: 16px;
    color: #bbb;
    margin-top: 4px;
}

/* Section Titles */
.section-title {
    font-size: 22px;
    font-weight: bold;
    margin-top: 25px;
    margin-bottom: 10px;
    border-bottom: 2px solid #4CAF50;
    padding-bottom: 5px;
}

/* Info Rows */
.info-row {
    font-size: 18px;
    margin: 6px 0;
}
.info-icon {
    margin-right: 8px;
    color: #4CAF50;
}

/* Personalized Alerts */
.alert-box {
    background-color: #ff4c4c33;
    color: #ff3333;
    padding: 8px;
    border-radius: 6px;
    margin: 5px 0;
}

/* Scrollable Details */
.scrollable {
    max-height: 220px;
    overflow-y: auto;
    padding-right: 5px;
}

/* Form Styling */
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
    background-color: #2c2c2c;
    color: #fff;
}
.stButton>button {
    background-color: #4CAF50;
    color: #fff;
    font-weight: bold;
}
.file-drop {
    border: 2px dashed #4CAF50;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    color: #bbb;
    margin-bottom: 10px;
}
.file-drop:hover {
    background-color: #333;
}
</style>
""", unsafe_allow_html=True)

# ---- DATABASE FUNCTIONS ----
def init_profile_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        fullname TEXT,
        age INTEGER,
        gender TEXT,
        blood_group TEXT,
        allergies TEXT,
        conditions TEXT,
        medications TEXT,
        profile_pic TEXT
    )''')
    conn.commit()
    conn.close()

def get_profile(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def save_profile(username, fullname, age, gender, blood_group, allergies, conditions, medications, profile_pic):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO profiles
        (username, fullname, age, gender, blood_group, allergies, conditions, medications, profile_pic)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (username, fullname, age, gender, blood_group, allergies, conditions, medications, profile_pic))
    conn.commit()
    conn.close()

# ---- PERSONALIZED ALERTS ----
def personalized_alerts(profile):
    _, fullname, age, gender, blood_group, allergies, conditions, medications, _ = profile
    alerts = []
    if not fullname: alerts.append("Full name is missing!")
    if not blood_group: alerts.append("Blood group not provided!")
    if not age or age <= 0: alerts.append("Age seems invalid!")
    if allergies: alerts.append(f"⚠️ Allergies recorded: {allergies}")
    if conditions: alerts.append(f"⚠️ Medical conditions recorded: {conditions}")
    return alerts

# ---- IMAGE HANDLER ----
def save_uploaded_image(file, username):
    path = PROFILE_PIC_DIR / f"{username}.png"
    img = Image.open(file)
    img.save(path)
    return str(path)

# ---- MAIN UI ----
st.markdown("## Your Medical Profile")

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please login to view your profile.")
else:
    username = st.session_state["username"]
    init_profile_db()
    profile = get_profile(username)

    if profile:
        (u, fullname, age, gender, blood_group,
         allergies, conditions, medications, profile_pic) = profile

        st.markdown('<div class="profile-container">', unsafe_allow_html=True)

        # PROFILE CARD
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown('<div class="profile-pic-wrapper">', unsafe_allow_html=True)
        if profile_pic and Path(profile_pic).exists():
            st.image(str(profile_pic), use_column_width=False, width=150)
        else:
            st.image("https://via.placeholder.com/150", use_column_width=False, width=150)
        st.markdown('</div>', unsafe_allow_html=True)

        # Name and subtitle
        st.markdown(f'''
            <div class="profile-info">
                <div class="profile-name">{fullname if fullname else username}</div>
                <div class="profile-subtitle">Personal Medical Profile</div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # PERSONALIZED ALERTS
        alerts = personalized_alerts(profile)
        for alert in alerts:
            st.markdown(f'<div class="alert-box">{alert}</div>', unsafe_allow_html=True)

        # PROFILE DETAILS
        st.markdown('<div class="section-title">Profile Information</div>', unsafe_allow_html=True)
        st.markdown('<div class="scrollable">', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">👤 <b>Full Name:</b> {fullname if fullname else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">🎂 <b>Age:</b> {age if age else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">⚧ <b>Gender:</b> {gender if gender else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">🩸 <b>Blood Group:</b> {blood_group if blood_group else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">🌿 <b>Allergies:</b> {allergies if allergies else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">💊 <b>Medical Conditions:</b> {conditions if conditions else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">⚕️ <b>Medications:</b> {medications if medications else "-"}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # EDIT FORM WITH DRAG & DROP IMAGE UPLOAD
        st.markdown('<div class="section-title">Edit Profile</div>', unsafe_allow_html=True)
        with st.form("profile_form"):
            fullname = st.text_input("Full Name", value=fullname or "")
            age = st.number_input("Age", value=age or 0, min_value=0, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male","Female","Other"].index(gender) if gender else 0)
            blood_group = st.text_input("Blood Group", value=blood_group or "")
            allergies = st.text_area("Allergies", value=allergies or "")
            conditions = st.text_area("Medical Conditions", value=conditions or "")
            medications = st.text_area("Medications", value=medications or "")

            st.markdown('<div class="file-drop">Drag & drop or click to upload new profile picture</div>', unsafe_allow_html=True)
            pic_file = st.file_uploader("", type=["jpg","jpeg","png"], label_visibility="collapsed")

            submitted = st.form_submit_button("Save Profile ✅")
            if submitted:
                pic_path = profile_pic
                if pic_file:
                    pic_path = save_uploaded_image(pic_file, username)
                save_profile(username, fullname, age, gender, blood_group, allergies, conditions, medications, pic_path)
                st.success("Profile updated successfully ✅")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # NEW PROFILE
        st.info("ℹ️ No saved profile found — please complete your profile below.")
        with st.form("new_profile"):
            fullname = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            blood_group = st.text_input("Blood Group")
            allergies = st.text_area("Allergies")
            conditions = st.text_area("Medical Conditions")
            medications = st.text_area("Medications")
            st.markdown('<div class="file-drop">Drag & drop or click to upload profile picture</div>', unsafe_allow_html=True)
            pic_file = st.file_uploader("", type=["jpg","jpeg","png"], label_visibility="collapsed")
            submitted = st.form_submit_button("Save Profile ✅")
            if submitted:
                pic_path = None
                if pic_file:
                    pic_path = save_uploaded_image(pic_file, username)
                save_profile(username, fullname, age, gender, blood_group, allergies, conditions, medications, pic_path)
                st.success("Profile created successfully ✅")
                st.rerun()
