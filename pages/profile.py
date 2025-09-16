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

# ---- CSS FIX ----
st.markdown("""
<style>
.profile-container {
    background-color: #111111;
    padding: 20px;
    border-radius: 15px;
    margin-top: 20px; /* FIX: Prevents white strip overlap */
}
.profile-card {
    display: flex;
    align-items: center;
    gap: 20px;
}
.profile-pic {
    border-radius: 50%;
    border: 4px solid green;
    width: 150px;
    height: 150px;
    object-fit: cover;
}
.profile-name {
    font-size: 22px;
    font-weight: bold;
}
.section-title {
    font-size: 20px;
    margin-top: 25px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---- INIT DB ----
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

# ---- UI START ----
st.markdown("## Profile Details")  # heading clean, no overlap

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
        if profile_pic and Path(profile_pic).exists():
            st.image(str(profile_pic), use_container_width=False, width=150)
        else:
            st.warning("⚠️ No profile image available.")

        st.markdown(f"""
            <div>
                <div class="profile-name">{fullname if fullname else username}</div>
                <div>Personal medical profile</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Profile Details
        st.markdown('<div class="section-title">Profile Information</div>', unsafe_allow_html=True)
        st.write(f"👤 **Full Name:** {fullname if fullname else '-'}")
        st.write(f"🎂 **Age:** {age if age else '-'}")
        st.write(f"⚧ **Gender:** {gender if gender else '-'}")
        st.write(f"🩸 **Blood Group:** {blood_group if blood_group else '-'}")
        st.write(f"🌿 **Allergies:** {allergies if allergies else '-'}")
        st.write(f"💊 **Conditions:** {conditions if conditions else '-'}")
        st.write(f"⚕️ **Medications:** {medications if medications else '-'}")

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
                st.rerun()

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
                st.rerun()
