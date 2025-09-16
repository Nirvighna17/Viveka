# pages/profile.py — Viveka Fixed
import streamlit as st
import sqlite3
import os
from pathlib import Path

# ---- DB & ASSETS ----
DB_FILE = "users.db"
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)
DEFAULT_PIC = ASSETS_DIR / "default.png"

# ---- DATABASE FUNCTIONS ----
def init_medical_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS medical_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            age INTEGER,
            gender TEXT,
            allergies TEXT,
            medical_history TEXT,
            chronic_conditions TEXT,
            medications TEXT,
            lifestyle TEXT,
            profile_pic TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_profile(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM medical_profiles WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result

def save_profile(username, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if get_profile(username):
        c.execute("""
            UPDATE medical_profiles
            SET age=?, gender=?, allergies=?, medical_history=?, chronic_conditions=?, medications=?, lifestyle=?, profile_pic=?
            WHERE username=?
        """, (age, gender, allergies, history, chronic, meds, lifestyle, profile_pic, username))
    else:
        c.execute("""
            INSERT INTO medical_profiles (username, age, gender, allergies, medical_history, chronic_conditions, medications, lifestyle, profile_pic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic))
    conn.commit()
    conn.close()

# ---- INIT ----
init_medical_db()
st.set_page_config(page_title="Profile | Viveka", layout="wide")

# ---- LOGIN CHECK ----
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please login first to access your profile.")
    st.stop()

username = st.session_state["username"]
profile = get_profile(username)

# ---- STYLES ----
st.markdown("""
<style>
.profile-container { display: flex; justify-content: center; margin-top: 40px; }
.profile-card { background: #fdfdfd; border-radius: 25px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); padding: 30px 25px; text-align: center; width: 320px; }
.profile-pic { width: 160px; height: 160px; border-radius: 50%; object-fit: cover; border: 4px solid #4CAF50; margin-bottom: 15px; }
.profile-username { font-size: 22px; font-weight: bold; color: #222; margin-bottom: 15px; }
.detail-card { background:#fff; border-radius:15px; padding:20px; box-shadow:0 4px 10px rgba(0,0,0,0.05); margin-bottom:10px; }
.detail-card h4 { margin:0 0 10px 0; color:#222; font-size:16px; border-bottom:1px solid #eee; padding-bottom:5px;}
.detail-card p { margin:0; color:#555; font-size:14px; line-height:1.4;}
</style>
""", unsafe_allow_html=True)

# ---- HEALTH SUGGESTIONS ----
def generate_health_tips(profile):
    tips = []
    if not profile: return tips
    age, gender, allergies, history, chronic, meds, lifestyle = profile[2:9]
    if age and age > 50:
        tips.append(("Age Alert", "Consider regular health checkups for heart and bone health.", "⚠️"))
    if allergies:
        tips.append(("Allergy Alert", f"Watch out for triggers: {allergies}", "❗"))
    if "smoke" in (lifestyle or "").lower():
        tips.append(("Lifestyle Tip", "Consider quitting smoking to improve overall health.", "🚭"))
    if "alcohol" in (lifestyle or "").lower():
        tips.append(("Lifestyle Tip", "Limit alcohol consumption for better liver health.", "🍷"))
    if chronic:
        tips.append(("Chronic Condition", f"Manage your condition: {chronic}. Consult your doctor regularly.", "💊"))
    if not tips:
        tips.append(("General Tip", "Keep a balanced diet and exercise regularly.", "✅"))
    return tips

# ---- DISPLAY PROFILE ----
st.title("Your Medical Profile")

if profile:
    # ---- Profile Card ----
    pic_path = profile[9] if profile[9] and os.path.exists(profile[9]) else str(DEFAULT_PIC)
    st.markdown(f"""
    <div class="profile-container">
        <div class="profile-card">
            <img src="{pic_path}" class="profile-pic"/>
            <div class="profile-username">{username}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Edit Option ----
    edit_mode = st.button("✏️ Edit Profile")

    if edit_mode:
        with st.form("edit_form"):
            col1, col2 = st.columns([1, 2])
            with col1:
                uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
                profile_pic_path = profile[9] if profile and profile[9] else str(DEFAULT_PIC)
                if uploaded_file:
                    save_path = ASSETS_DIR / f"{username}_profile.png"
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    profile_pic_path = str(save_path)
                st.image(profile_pic_path, width=200, caption="Profile Picture")
            with col2:
                age = st.number_input("Age", min_value=0, max_value=120, value=profile[2] if profile else 25)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                                      index=0 if not profile else ["Male", "Female", "Other"].index(profile[3]) if profile[3] else 0)
                allergies = st.text_area("Allergies", value=profile[4] if profile else "")
                history = st.text_area("Medical History", value=profile[5] if profile else "")
                chronic = st.text_area("Chronic Conditions", value=profile[6] if profile else "")
                meds = st.text_area("Current Medications", value=profile[7] if profile else "")
                lifestyle = st.text_area("Lifestyle Notes", value=profile[8] if profile else "")

            submitted = st.form_submit_button("💾 Save Profile")
            if submitted:
                save_profile(username, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic_path)
                st.success("✅ Profile saved successfully!")
                st.rerun()

    # ---- Health Tips ----
    tips = generate_health_tips(profile)
    st.markdown("### 🩺 Health Recommendations / Tips")
    for title, text, icon in tips:
        st.markdown(f"""
            <div class="detail-card" style="border-left:4px solid #4CAF50;">
                <h4>{icon} {title}</h4>
                <p>{text}</p>
            </div>
        """, unsafe_allow_html=True)

else:
    # ---- First Time User → Show Form Directly ----
    st.info("ℹ️ No profile found. Please complete your medical profile.")
    with st.form("new_profile_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
            uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            profile_pic_path = str(DEFAULT_PIC)
            if uploaded_file:
                save_path = ASSETS_DIR / f"{username}_profile.png"
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                profile_pic_path = str(save_path)
            st.image(profile_pic_path, width=200, caption="Profile Picture")
        with col2:
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
            allergies = st.text_area("Allergies")
            history = st.text_area("Medical History")
            chronic = st.text_area("Chronic Conditions")
            meds = st.text_area("Current Medications")
            lifestyle = st.text_area("Lifestyle Notes")

        submitted = st.form_submit_button("💾 Save Profile")
        if submitted:
            save_profile(username, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic_path)
            st.success("✅ Profile created successfully!")
            st.rerun()
# pages/profile.py — Viveka Fixed
import streamlit as st
import sqlite3
import os
from pathlib import Path

# ---- DB & ASSETS ----
DB_FILE = "users.db"
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)
DEFAULT_PIC = ASSETS_DIR / "default.png"

# ---- DATABASE FUNCTIONS ----
def init_medical_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS medical_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            age INTEGER,
            gender TEXT,
            allergies TEXT,
            medical_history TEXT,
            chronic_conditions TEXT,
            medications TEXT,
            lifestyle TEXT,
            profile_pic TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_profile(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM medical_profiles WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result

def save_profile(username, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if get_profile(username):
        c.execute("""
            UPDATE medical_profiles
            SET age=?, gender=?, allergies=?, medical_history=?, chronic_conditions=?, medications=?, lifestyle=?, profile_pic=?
            WHERE username=?
        """, (age, gender, allergies, history, chronic, meds, lifestyle, profile_pic, username))
    else:
        c.execute("""
            INSERT INTO medical_profiles (username, age, gender, allergies, medical_history, chronic_conditions, medications, lifestyle, profile_pic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic))
    conn.commit()
    conn.close()

# ---- INIT ----
init_medical_db()
st.set_page_config(page_title="Profile | Viveka", layout="wide")

# ---- LOGIN CHECK ----
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please login first to access your profile.")
    st.stop()

username = st.session_state["username"]
profile = get_profile(username)

# ---- STYLES ----
st.markdown("""
<style>
.profile-container { display: flex; justify-content: center; margin-top: 40px; }
.profile-card { background: #fdfdfd; border-radius: 25px; box-shadow: 0px 10px 25px rgba(0,0,0,0.15); padding: 30px 25px; text-align: center; width: 320px; }
.profile-pic { width: 160px; height: 160px; border-radius: 50%; object-fit: cover; border: 4px solid #4CAF50; margin-bottom: 15px; }
.profile-username { font-size: 22px; font-weight: bold; color: #222; margin-bottom: 15px; }
.detail-card { background:#fff; border-radius:15px; padding:20px; box-shadow:0 4px 10px rgba(0,0,0,0.05); margin-bottom:10px; }
.detail-card h4 { margin:0 0 10px 0; color:#222; font-size:16px; border-bottom:1px solid #eee; padding-bottom:5px;}
.detail-card p { margin:0; color:#555; font-size:14px; line-height:1.4;}
</style>
""", unsafe_allow_html=True)

# ---- HEALTH SUGGESTIONS ----
def generate_health_tips(profile):
    tips = []
    if not profile: return tips
    age, gender, allergies, history, chronic, meds, lifestyle = profile[2:9]
    if age and age > 50:
        tips.append(("Age Alert", "Consider regular health checkups for heart and bone health.", "⚠️"))
    if allergies:
        tips.append(("Allergy Alert", f"Watch out for triggers: {allergies}", "❗"))
    if "smoke" in (lifestyle or "").lower():
        tips.append(("Lifestyle Tip", "Consider quitting smoking to improve overall health.", "🚭"))
    if "alcohol" in (lifestyle or "").lower():
        tips.append(("Lifestyle Tip", "Limit alcohol consumption for better liver health.", "🍷"))
    if chronic:
        tips.append(("Chronic Condition", f"Manage your condition: {chronic}. Consult your doctor regularly.", "💊"))
    if not tips:
        tips.append(("General Tip", "Keep a balanced diet and exercise regularly.", "✅"))
    return tips

# ---- DISPLAY PROFILE ----
st.title("Your Medical Profile")

if profile:
    # ---- Profile Card ----
    pic_path = profile[9] if profile[9] and os.path.exists(profile[9]) else str(DEFAULT_PIC)
    st.markdown(f"""
    <div class="profile-container">
        <div class="profile-card">
            <img src="{pic_path}" class="profile-pic"/>
            <div class="profile-username">{username}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Edit Option ----
    edit_mode = st.button("✏️ Edit Profile")

    if edit_mode:
        with st.form("edit_form"):
            col1, col2 = st.columns([1, 2])
            with col1:
                uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
                profile_pic_path = profile[9] if profile and profile[9] else str(DEFAULT_PIC)
                if uploaded_file:
                    save_path = ASSETS_DIR / f"{username}_profile.png"
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    profile_pic_path = str(save_path)
                st.image(profile_pic_path, width=200, caption="Profile Picture")
            with col2:
                age = st.number_input("Age", min_value=0, max_value=120, value=profile[2] if profile else 25)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                                      index=0 if not profile else ["Male", "Female", "Other"].index(profile[3]) if profile[3] else 0)
                allergies = st.text_area("Allergies", value=profile[4] if profile else "")
                history = st.text_area("Medical History", value=profile[5] if profile else "")
                chronic = st.text_area("Chronic Conditions", value=profile[6] if profile else "")
                meds = st.text_area("Current Medications", value=profile[7] if profile else "")
                lifestyle = st.text_area("Lifestyle Notes", value=profile[8] if profile else "")

            submitted = st.form_submit_button("💾 Save Profile")
            if submitted:
                save_profile(username, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic_path)
                st.success("✅ Profile saved successfully!")
                st.rerun()

    # ---- Health Tips ----
    tips = generate_health_tips(profile)
    st.markdown("### 🩺 Health Recommendations / Tips")
    for title, text, icon in tips:
        st.markdown(f"""
            <div class="detail-card" style="border-left:4px solid #4CAF50;">
                <h4>{icon} {title}</h4>
                <p>{text}</p>
            </div>
        """, unsafe_allow_html=True)

else:
    # ---- First Time User → Show Form Directly ----
    st.info("ℹ️ No profile found. Please complete your medical profile.")
    with st.form("new_profile_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
            uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            profile_pic_path = str(DEFAULT_PIC)
            if uploaded_file:
                save_path = ASSETS_DIR / f"{username}_profile.png"
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                profile_pic_path = str(save_path)
            st.image(profile_pic_path, width=200, caption="Profile Picture")
        with col2:
            age = st.number_input("Age", min_value=0, max_value=120, value=25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
            allergies = st.text_area("Allergies")
            history = st.text_area("Medical History")
            chronic = st.text_area("Chronic Conditions")
            meds = st.text_area("Current Medications")
            lifestyle = st.text_area("Lifestyle Notes")

        submitted = st.form_submit_button("💾 Save Profile")
        if submitted:
            save_profile(username, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic_path)
            st.success("✅ Profile created successfully!")
            st.rerun()
