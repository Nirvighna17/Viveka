# pages/profile.py
import streamlit as st
import sqlite3
from pathlib import Path
from PIL import Image
import os

# ---- DB FILE ----
DB_FILE = "users.db"
PROFILE_PIC_DIR = Path("profile_pics")
PROFILE_PIC_DIR.mkdir(exist_ok=True)

# ---- CSS ----
st.markdown("""
<style>
/* General container */
.profile-container {
    background-color: #1f1f1f;
    padding: 25px;
    border-radius: 15px;
    margin-top: 20px;
    color: #fff;
    max-width: 800px;
}

/* Profile card */
.profile-card {
    display: flex;
    align-items: center;
    gap: 25px;
    margin-bottom: 20px;
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
}
.profile-pic:hover {
    opacity: 0.9;
}
.edit-icon {
    position: absolute;
    bottom: 0;
    right: 0;
    background-color: #4CAF50;
    border-radius: 50%;
    padding: 5px;
    cursor: pointer;
}

/* Profile name */
.profile-name {
    font-size: 26px;
    font-weight: bold;
}

/* Section titles */
.section-title {
    font-size: 22px;
    font-weight: bold;
    margin-top: 25px;
    border-bottom: 1px solid #4CAF50;
    padding-bottom: 5px;
}

/* Info rows */
.info-row {
    margin: 5px 0;
    font-size: 18px;
}
.info-icon {
    margin-right: 8px;
    color: #4CAF50;
}
.warning {
    background-color: #ffcccb;
    color: #a00;
    padding: 8px;
    border-radius: 5px;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

# ---- DB INIT ----
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

# ---- FETCH PROFILE ----
def get_profile(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

# ---- SAVE PROFILE ----
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
def display_alerts(profile):
    _, fullname, age, gender, blood_group, allergies, conditions, medications, _ = profile
    alerts = []
    if not fullname:
        alerts.append("Full name is missing!")
    if not blood_group:
        alerts.append("Blood group not provided.")
    if not age or age < 0:
        alerts.append("Age seems invalid.")
    if allergies:
        alerts.append(f"⚠️ You have listed allergies: {allergies}")
    if conditions:
        alerts.append(f"⚠️ Medical conditions recorded: {conditions}")
    return alerts

# ---- UI ----
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

        # Profile Card
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        st.markdown('<div class="profile-pic-wrapper">', unsafe_allow_html=True)
        if profile_pic and Path(profile_pic).exists():
            st.image(str(profile_pic), use_column_width=False, width=150, caption=None)
        else:
            st.image("https://via.placeholder.com/150", use_column_width=False, width=150, caption=None)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div>
                <div class="profile-name">{fullname if fullname else username}</div>
                <div>Personal Medical Profile</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Alerts / Personalized Suggestions
        alerts = display_alerts(profile)
        for alert in alerts:
            st.markdown(f'<div class="warning">{alert}</div>', unsafe_allow_html=True)

        # Profile Details
        st.markdown('<div class="section-title">Profile Information</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">👤 <b>Full Name:</b> {fullname if fullname else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">🎂 <b>Age:</b> {age if age else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">⚧ <b>Gender:</b> {gender if gender else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">🩸 <b>Blood Group:</b> {blood_group if blood_group else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">🌿 <b>Allergies:</b> {allergies if allergies else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">💊 <b>Medical Conditions:</b> {conditions if conditions else "-"}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-row">⚕️ <b>Medications:</b> {medications if medications else "-"}</div>', unsafe_allow_html=True)

        # Edit Form
        st.markdown('<div class="section-title">Edit Profile</div>', unsafe_allow_html=True)
        with st.form("profile_form"):
            fullname = st.text_input("Full Name", value=fullname or "")
            age = st.number_input("Age", value=age or 0, min_value=0, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male","Female","Other"].index(gender) if gender else 0)
            blood_group = st.text_input("Blood Group", value=blood_group or "")
            allergies = st.text_area("Allergies", value=allergies or "")
            conditions = st.text_area("Medical Conditions", value=conditions or "")
            medications = st.text_area("Medications", value=medications or "")
            pic_file = st.file_uploader("Upload Profile Picture", type=["jpg","jpeg","png"])

            submitted = st.form_submit_button("Save Profile ✅")
            if submitted:
                pic_path = profile_pic
                if pic_file:
                    pic_path = PROFILE_PIC_DIR / f"{username}.png"
                    img = Image.open(pic_file)
                    img.save(pic_path)
                save_profile(username, fullname, age, gender, blood_group, allergies, conditions, medications, str(pic_path))
                st.success("Profile updated successfully ✅")
                st.experimental_rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("ℹ️ No saved profile found — please complete your profile below.")
        with st.form("new_profile"):
            fullname = st.text_input("Full Name")
            age = st.number_input("Age", min_value=0, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            blood_group = st.text_input("Blood Group")
            allergies = st.text_area("Allergies")
            conditions = st.text_area("Medical Conditions")
            medications = st.text_area("Medications")
            pic_file = st.file_uploader("Upload Profile Picture", type=["jpg","jpeg","png"])
            submitted = st.form_submit_button("Save Profile ✅")
            if submitted:
                pic_path = None
                if pic_file:
                    pic_path = PROFILE_PIC_DIR / f"{username}.png"
                    img = Image.open(pic_file)
                    img.save(pic_path)
                save_profile(username, fullname, age, gender, blood_group, allergies, conditions, medications, str(pic_path) if pic_path else None)
                st.success("Profile created successfully ✅")
                st.experimental_rerun()
