# pages/profile.py — VIVEKA (FINAL FULL VERSION, 300+ LOC)
# Features:
# - Large, polished UI with left avatar card and right detail/edit area (no overlap)
# - Safe image handling (saved under assets/, fallback default created)
# - Robust session/login checks using session_state["logged_in"] & ["username"]
# - All forms contain st.form_submit_button()
# - SQLite persistence for medical_profiles
# - Edit toggle, preview, save, and health tips generation
# - Logout with session clear and rerun
# - Uses grid/columns and avoids absolute positioning to prevent overlap

import streamlit as st
import sqlite3
from pathlib import Path
import os
import io
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ---------------------------
# Paths & Setup
# ---------------------------
BASE_DIR = Path(__file__).parent
REPO_ROOT = BASE_DIR.parent
DB_FILE = REPO_ROOT / "users.db"
ASSETS_DIR = REPO_ROOT / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_PIC = ASSETS_DIR / "default_profile.png"

# Create a simple default image if missing
if not DEFAULT_PIC.exists():
    try:
        size = (600, 600)
        bg = (250, 250, 250)
        circle = (230, 230, 230)
        text_col = (90, 90, 90)
        img = Image.new("RGB", size, bg)
        d = ImageDraw.Draw(img)
        d.ellipse((40, 40, 560, 560), fill=circle)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 40)
        except Exception:
            font = ImageFont.load_default()
        w, h = d.textsize("No Photo", font=font)
        d.text(((size[0]-w)/2, (size[1]-h)/2), "No Photo", fill=text_col, font=font)
        img.save(DEFAULT_PIC)
    except Exception:
        pass  # if creation fails, we'll handle missing default later

# ---------------------------
# Database helpers
# ---------------------------
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

def get_profile(username: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM medical_profiles WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def save_profile(username: str, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    existing = get_profile(username)
    if existing:
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

# ---------------------------
# Session safety defaults
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "email" not in st.session_state:
    st.session_state["email"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = "user"

# ---------------------------
# Page config & CSS
# ---------------------------
st.set_page_config(page_title="Profile | VIVEKA", layout="wide")

st.markdown(
    """
    <style>
    /* Overall layout */
    .page-container { padding: 18px 28px; color: #fff; }
    /* Card + details layout uses columns (no absolute) */
    .profile-wrapper { display:flex; gap:24px; align-items:flex-start; }
    /* Left card */
    .profile-card {
        background: linear-gradient(180deg, #ffffff, #fbfbfb);
        color: #222;
        border-radius: 18px;
        padding: 22px;
        width: 420px;
        box-shadow: 0 18px 40px rgba(0,0,0,0.12);
    }
    .profile-pic { width:160px; height:160px; border-radius:50%; object-fit:cover; border:4px solid #4CAF50; display:block; margin: 0 auto 12px auto; }
    .profile-name { font-size:20px; font-weight:800; text-align:center; margin-bottom:6px; }
    .profile-sub { text-align:center; color:#666; margin-bottom:12px; }
    .logout-btn { margin-top:12px; display:block; }
    /* Right column */
    .detail-panel { flex:1; min-width:380px; }
    .detail-card { background:#fff; border-radius:12px; padding:14px; margin-bottom:12px; color:#222; box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
    .detail-card h4 { margin:0 0 8px 0; }
    .form-grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    @media (max-width: 900px) {
        .profile-wrapper { flex-direction:column; }
        .profile-card { width:100%; }
    }
    /* subtle button styles (Streamlit defaults will still apply) */
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Utility: safe image display
# ---------------------------
def safe_image_display(path_or_obj, width=160, caption=None):
    """
    Accepts a path string/Path, PIL.Image, or bytes and safely displays image.
    Falls back to DEFAULT_PIC if missing/unreadable.
    """
    try:
        if isinstance(path_or_obj, (str, Path)):
            p = Path(path_or_obj)
            if p.exists():
                st.image(str(p), width=width, caption=caption, output_format="PNG")
                return
            else:
                if DEFAULT_PIC.exists():
                    st.image(str(DEFAULT_PIC), width=width, caption=caption, output_format="PNG")
                    return
                else:
                    st.warning("Default profile image not found.")
                    return
        elif hasattr(path_or_obj, "read"):  # file-like
            st.image(path_or_obj, width=width, caption=caption)
            return
        elif isinstance(path_or_obj, Image.Image):
            bio = io.BytesIO()
            path_or_obj.save(bio, format="PNG")
            bio.seek(0)
            st.image(bio, width=width, caption=caption)
            return
        else:
            if DEFAULT_PIC.exists():
                st.image(str(DEFAULT_PIC), width=width, caption=caption)
                return
            else:
                st.warning("Profile image not available.")
    except Exception:
        # avoid bringing media errors to user
        try:
            if DEFAULT_PIC.exists():
                st.image(str(DEFAULT_PIC), width=width, caption=caption)
            else:
                st.warning("Unable to display profile image.")
        except Exception:
            st.warning("Image display error.")

# ---------------------------
# Health tips generator
# ---------------------------
def generate_health_tips(profile_row):
    tips = []
    if not profile_row:
        tips.append(("General", "Complete your profile to get personalized suggestions.", "ℹ️"))
        return tips

    age = profile_row[2] or 0
    allergies = (profile_row[4] or "").strip()
    history = (profile_row[5] or "").strip()
    chronic = (profile_row[6] or "").strip()
    meds = (profile_row[7] or "").strip()
    lifestyle = (profile_row[8] or "").strip().lower()

    if age and age > 60:
        tips.append(("Age Care", "Routine cardiology and bone health check-ups recommended.", "⚠️"))
    if allergies:
        tips.append(("Allergy", f"Watch out for triggers: {allergies}. Carry prescribed medication if recommended.", "❗"))
    if chronic:
        tips.append(("Chronic Condition", f"Manage condition: {chronic}. Regular follow-ups advised.", "💊"))
    if "smoke" in lifestyle:
        tips.append(("Lifestyle", "Consider quitting smoking — big health benefits follow.", "🚭"))
    if "alcohol" in lifestyle:
        tips.append(("Lifestyle", "Limit alcohol consumption to protect liver function.", "🍷"))
    if not tips:
        tips.append(("General", "Balanced diet, regular exercise & routine checkups help most people.", "✅"))

    return tips

# ---------------------------
# Initialize DB and basic checks
# ---------------------------
init_medical_db()

st.title("Profile Details")

# If not logged in, give clear path to login
if not st.session_state.get("logged_in", False) or not st.session_state.get("username"):
    st.warning("⚠️ Please login to access your medical profile.")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔑 Go to Login"):
            try:
                st.switch_page("pages/login_signup.py")
            except Exception:
                try:
                    st.switch_page("login_signup")
                except Exception:
                    st.info("Open the Login page from the sidebar or return to the app home.")
    with col2:
        if st.button("🔁 Continue as guest (view only)"):
            st.info("Guest view: you can inspect the UI but cannot save profile.")
    st.stop()

# Logged-in user
username = st.session_state.get("username")
profile = get_profile(username)  # tuple or None

# Layout columns to avoid overlap: left = card, right = details + edit
col_left, col_right = st.columns([1, 2])

# ---------------------------
# LEFT: Profile card
# ---------------------------
with col_left:
    st.markdown('<div class="profile-wrapper">', unsafe_allow_html=True)
    # Card container uses HTML snippet to maintain pixel-perfect layout
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)

    # Determine pic path (stored in DB column profile[9], if present)
    stored_pic = None
    if profile and len(profile) > 9:
        stored_pic = profile[9]
    pic_path_to_show = stored_pic if stored_pic and Path(stored_pic).exists() else str(DEFAULT_PIC) if DEFAULT_PIC.exists() else None

    # Render image and basic text
    if pic_path_to_show:
        safe_image_display(pic_path_to_show, width=160, caption=None)
    else:
        st.warning("⚠️ No profile image available.")

    st.markdown(f'<div class="profile-name">{username}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-sub">Personal medical profile</div>', unsafe_allow_html=True)

    # Buttons: Edit toggle provided on right; Keep Logout here
    if st.button("🚪 Logout"):
        # Clear session and rerun to reflect changes
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["email"] = ""
        st.session_state["role"] = "user"
        st.success("Logged out successfully.")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# RIGHT: Details, edit form, tips
# ---------------------------
with col_right:
    st.subheader("Profile Details")
    # Show read-only cards if profile exists
    if profile:
        age_disp = profile[2] if profile[2] else "—"
        gender_disp = profile[3] if profile[3] else "—"
        allergies_disp = profile[4] or "Not provided"
        history_disp = profile[5] or "Not provided"
        chronic_disp = profile[6] or "Not provided"
        meds_disp = profile[7] or "Not provided"
        lifestyle_disp = profile[8] or "Not provided"

        st.markdown(f"""
            <div class="detail-card">
                <h4>👤 Basics</h4>
                <p><strong>Age:</strong> {age_disp} &nbsp;&nbsp; <strong>Gender:</strong> {gender_disp}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="detail-card">
                <h4>⚠ Allergies</h4>
                <p>{textwrap.fill(allergies_disp, width=80)}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="detail-card">
                <h4>🧾 Medical History</h4>
                <p>{textwrap.fill(history_disp, width=80)}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="detail-card">
                <h4>💊 Chronic Conditions & Medications</h4>
                <p>{textwrap.fill(chronic_disp, width=80)}</p>
                <p style="margin-top:8px;"><em>Medications:</em> {textwrap.fill(meds_disp, width=80)}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="detail-card">
                <h4>🧭 Lifestyle</h4>
                <p>{textwrap.fill(lifestyle_disp, width=80)}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No saved profile found — please complete your profile below.")

    # Edit toggle
    st.markdown("**Edit Profile**")
    edit_toggle = st.checkbox("Enable editing (check to edit profile)", value=False)

    if edit_toggle:
        # Put edit UI into a form (submit button required; prevents missing submit error)
        with st.form("profile_edit_form"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("**Profile Picture**")
                uploaded = st.file_uploader("Upload (jpg/png)", type=["jpg", "jpeg", "png"], accept_multiple_files=False)
                # preview logic
                preview_path = None
                if uploaded:
                    try:
                        dest = ASSETS_DIR / f"{username}_profile.png"
                        with open(dest, "wb") as f:
                            f.write(uploaded.getbuffer())
                        preview_path = str(dest)
                    except Exception:
                        preview_path = None
                else:
                    if profile and len(profile) > 9 and profile[9] and Path(profile[9]).exists():
                        preview_path = profile[9]
                    elif DEFAULT_PIC.exists():
                        preview_path = str(DEFAULT_PIC)
                safe_image_display(preview_path, width=160, caption="Preview")

            with c2:
                st.markdown("**Personal Details**")
                age_input = st.number_input("Age", min_value=0, max_value=120, value=profile[2] if profile and profile[2] else 25)
                gender_options = ["Male", "Female", "Other"]
                gender_index = 0
                if profile and profile[3] in gender_options:
                    gender_index = gender_options.index(profile[3])
                gender_input = st.selectbox("Gender", gender_options, index=gender_index)
                allergies_input = st.text_area("Allergies", value=profile[4] if profile and profile[4] else "")
                history_input = st.text_area("Medical History", value=profile[5] if profile and profile[5] else "")
                chronic_input = st.text_area("Chronic Conditions", value=profile[6] if profile and profile[6] else "")
                meds_input = st.text_area("Current Medications", value=profile[7] if profile and profile[7] else "")
                lifestyle_input = st.text_area("Lifestyle Notes (e.g., smoke, alcohol, vegan)", value=profile[8] if profile and profile[8] else "")

            submitted = st.form_submit_button("💾 Save Profile")
            if submitted:
                # choose stored pic path
                stored_pic = None
                if uploaded:
                    try:
                        stored_pic = str(ASSETS_DIR / f"{username}_profile.png")
                    except Exception:
                        stored_pic = None
                else:
                    if profile and len(profile) > 9 and profile[9]:
                        stored_pic = profile[9]
                    else:
                        stored_pic = str(DEFAULT_PIC) if DEFAULT_PIC.exists() else None

                try:
                    save_profile(
                        username=username,
                        age=int(age_input) if age_input is not None else None,
                        gender=gender_input,
                        allergies=allergies_input.strip(),
                        history=history_input.strip(),
                        chronic=chronic_input.strip(),
                        meds=meds_input.strip(),
                        lifestyle=lifestyle_input.strip(),
                        profile_pic=stored_pic
                    )
                    st.success("✅ Profile saved successfully.")
                    # refresh local profile and UI
                    profile = get_profile(username)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Could not save profile: {e}")

    # Health recommendations (always visible below)
    st.markdown("---")
    st.subheader("Health Recommendations / Tips")
    tips = generate_health_tips(profile)
    for title, text, icon in tips:
        st.markdown(f"""
            <div class="detail-card" style="border-left:4px solid #4CAF50;">
                <h4>{icon} {title}</h4>
                <p>{text}</p>
            </div>
        """, unsafe_allow_html=True)

# ---------------------------
# End of profile page
# ---------------------------
