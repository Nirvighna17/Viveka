# pages/profile.py — VIVEKA (FINAL, full-featured, 300+ LOC)
# This file preserves the original UI/layout while fixing:
# - session-state login checks
# - safe image handling (fallback to default)
# - forms always include submit buttons
# - persistent saving to SQLite
# - edit mode, health tips, and logout flow
#
# Important: This expects that your login/signup flow sets:
#   st.session_state["logged_in"] = True
#   st.session_state["username"] = "<username>"
#
# If you use different keys in your login page, adapt the checks accordingly.

import streamlit as st
import sqlite3
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# -----------------------------
# Configuration & Paths
# -----------------------------
BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR.parent / "users.db"  # keep DB next to repo root
ASSETS_DIR = BASE_DIR / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_PIC = ASSETS_DIR / "default_profile.png"
# ensure default image exists (create simple placeholder if missing)
if not DEFAULT_PIC.exists():
    try:
        # create a simple circular default image
        img_size = (600, 600)
        bg_color = (245, 245, 245)
        circle_color = (200, 200, 200)
        text_color = (80, 80, 80)
        im = Image.new("RGB", img_size, bg_color)
        draw = ImageDraw.Draw(im)
        # draw circle
        draw.ellipse((50, 50, 550, 550), fill=circle_color)
        # add text "No Photo"
        try:
            # try loading a common font
            font = ImageFont.truetype("DejaVuSans.ttf", 48)
        except Exception:
            font = ImageFont.load_default()
        w, h = draw.textsize("No Photo", font=font)
        draw.text(((img_size[0]-w)/2, (img_size[1]-h)/2), "No Photo", fill=text_color, font=font)
        im.save(DEFAULT_PIC)
    except Exception:
        # If PIL fails, ignore — we'll handle missing default gracefully later
        pass

# -----------------------------
# Database helpers
# -----------------------------
def init_medical_db():
    """Initialize medical_profiles table if not exists."""
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
    """Return profile row tuple or None."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM medical_profiles WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def save_profile(username: str, age, gender, allergies, history, chronic, meds, lifestyle, profile_pic):
    """Insert or update profile for the user."""
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

# -----------------------------
# Session defaults & safety
# -----------------------------
# Ensure session keys exist (prevents KeyError and inconsistent behavior)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "email" not in st.session_state:
    st.session_state["email"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = "user"

# -----------------------------
# Page config & styles
# -----------------------------
st.set_page_config(page_title="Profile | VIVEKA", layout="wide")

st.markdown("""
<style>
/* Container & card styles */
.profile-wrapper {
    display:flex;
    justify-content:center;
    padding-top: 30px;
}
.profile-card {
    width: 360px;
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.98));
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.12);
    text-align:center;
}
.profile-pic {
    width: 160px;
    height: 160px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #4CAF50;
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
    margin-bottom: 12px;
}
.profile-username {
    font-size: 20px;
    font-weight: 700;
    color: #222;
    margin-bottom: 6px;
}
.profile-sub {
    color: #666;
    font-size: 14px;
    margin-bottom: 12px;
}
/* detail cards */
.detail-card {
    background:#fff;
    border-radius:12px;
    padding:14px;
    margin-bottom:12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}
.detail-card h4 { margin:0 0 8px 0; font-size:16px; }
.detail-card p { margin:0; color:#444; font-size:14px; }

/* form layout */
.form-grid { display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 800px) {
  .form-grid { grid-template-columns: 1fr; }
}

/* small helpers */
.small-muted { color:#888; font-size:13px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Utility functions
# -----------------------------
def safe_image_display(path_or_obj, width=200, caption=None):
    """
    Display image safely. path_or_obj may be:
      - a Path or str path to file (exists check performed)
      - a bytes-like object or PIL.Image
    Falls back to DEFAULT_PIC if path missing or unreadable.
    """
    try:
        if isinstance(path_or_obj, (str, Path)):
            p = Path(path_or_obj)
            if p.exists():
                st.image(str(p), width=width, caption=caption)
                return
            else:
                # fallback to default
                if DEFAULT_PIC.exists():
                    st.image(str(DEFAULT_PIC), width=width, caption=caption)
                    return
                else:
                    st.warning("⚠️ Profile image not found and no default available.")
                    return
        elif isinstance(path_or_obj, Image.Image):
            bio = io.BytesIO()
            path_or_obj.save(bio, format="PNG")
            bio.seek(0)
            st.image(bio, width=width, caption=caption)
            return
        elif isinstance(path_or_obj, (bytes, bytearray)):
            st.image(path_or_obj, width=width, caption=caption)
            return
        else:
            # fallback
            if DEFAULT_PIC.exists():
                st.image(str(DEFAULT_PIC), width=width, caption=caption)
            else:
                st.warning("⚠️ Profile image not available.")
    except Exception as ex:
        # avoid raising MediaFileStorageError to UI — show fallback
        try:
            if DEFAULT_PIC.exists():
                st.image(str(DEFAULT_PIC), width=width, caption=caption)
            else:
                st.warning("⚠️ Could not display profile image.")
        except Exception:
            st.warning("⚠️ Image display error.")

def generate_health_tips(profile_row):
    """
    Accepts profile row (tuple from DB) and returns list of tips.
    profile_row mapping (by index): [0]=id, [1]=username, [2]=age, [3]=gender,
    [4]=allergies, [5]=medical_history, [6]=chronic_conditions, [7]=medications, [8]=lifestyle, [9]=profile_pic
    """
    tips = []
    if not profile_row:
        return [("General", "Complete your profile to get personalized suggestions.", "ℹ️")]
    # extract safely
    age = profile_row[2] or 0
    allergies = profile_row[4] or ""
    history = profile_row[5] or ""
    chronic = profile_row[6] or ""
    meds = profile_row[7] or ""
    lifestyle = profile_row[8] or ""

    if isinstance(age, (int, float)) and age > 60:
        tips.append(("Age Care", "At your age, regular cardiology and bone health check-ups are recommended.", "⚠️"))
    if allergies:
        tips.append(("Allergy Alert", f"Watch for triggers: {allergies}. Carry emergency medication if prescribed.", "❗"))
    if chronic:
        tips.append(("Chronic Condition", f"Manage your condition: {chronic}. Regular follow-ups advised.", "💊"))
    if "smoke" in lifestyle.lower():
        tips.append(("Lifestyle", "Quitting smoking significantly improves long-term outcomes.", "🚭"))
    if "alcohol" in lifestyle.lower():
        tips.append(("Lifestyle", "Limit alcohol intake for better liver health.", "🍷"))
    if not tips:
        tips.append(("General Tip", "Maintain balanced diet, exercise, and regular health check-ups.", "✅"))
    return tips

# -----------------------------
# Main UI logic
# -----------------------------
init_medical_db()

st.title("Your Medical Profile")  # Page heading

# -- login check --
if not st.session_state.get("logged_in", False) or not st.session_state.get("username"):
    # If user not logged in, show clear message and quick link to login
    st.warning("⚠️ Please login first to access your profile.")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        if st.button("🔑 Go to Login"):
            # Try to switch to login page, best-effort; adapt page name if different
            try:
                st.switch_page("pages/login_signup.py")
            except Exception:
                try:
                    st.switch_page("login_signup")
                except Exception:
                    st.info("Please open the Login page from the sidebar or the main menu.")
    with col_b:
        if st.button("🔁 Continue as guest (view only)"):
            st.info("Viewing in guest mode. Login to edit and save your profile.")
    st.stop()

# At this point, user is logged in
username = st.session_state.get("username")
profile = get_profile(username)  # row or None

# Layout: left column = profile card, right column = details & edit
left_col, right_col = st.columns([1, 2])

# -----------------------------
# LEFT: Profile card (avatar + quick info + logout)
# -----------------------------
with left_col:
    st.markdown('<div class="profile-wrapper">', unsafe_allow_html=True)
    # card HTML wrapper
    if profile:
        # compute pic path: prefer profile[9], fallback to DEFAULT_PIC
        stored_pic = profile[9] if len(profile) > 9 and profile[9] else None
        pic_to_display = stored_pic if stored_pic and Path(stored_pic).exists() else str(DEFAULT_PIC)
    else:
        pic_to_display = str(DEFAULT_PIC)

    # render card using markup to retain tight layout like original
    profile_card_html = f"""
    <div class="profile-card">
        <img src="{pic_to_display}" class="profile-pic"/>
        <div class="profile-username">{username}</div>
        <div class="profile-sub">Personal medical profile</div>
    </div>
    """
    st.markdown(profile_card_html, unsafe_allow_html=True)

    # Logout button
    if st.button("🚪 Logout"):
        # clear session keys relevant to auth and profile
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["email"] = ""
        st.session_state["role"] = "user"
        st.success("Logged out successfully.")
        # try to redirect to login page
        try:
            st.experimental_rerun()
        except Exception:
            st.stop()

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# RIGHT: Profile details, edit form, health tips
# -----------------------------
with right_col:
    # show existing profile details (read-only) and an Edit toggle
    st.subheader("Profile Details")

    # If profile exists show read-only detail cards
    if profile:
        # Display a few detail blocks (Allergies, Chronic, Meds)
        allergies_text = profile[4] or "Not provided"
        history_text = profile[5] or "Not provided"
        chronic_text = profile[6] or "Not provided"
        meds_text = profile[7] or "Not provided"
        lifestyle_text = profile[8] or "Not provided"
        age_display = profile[2] if profile[2] else "—"
        gender_display = profile[3] if profile[3] else "—"

        # Detail cards in stacked manner to mimic original UI
        st.markdown(f"""
            <div class="detail-card">
                <h4>👤 Basic</h4>
                <p><strong>Age:</strong> {age_display} &nbsp; &nbsp; <strong>Gender:</strong> {gender_display}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="detail-card">
                <h4>⚠ Allergies</h4>
                <p>{textwrap.fill(allergies_text, width=80)}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="detail-card">
                <h4>🧾 Medical History</h4>
                <p>{textwrap.fill(history_text, width=80)}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="detail-card">
                <h4>💊 Chronic Conditions / Medications</h4>
                <p>{textwrap.fill(chronic_text, width=80)}</p>
                <p style="margin-top:8px;"><em>Medications:</em> {textwrap.fill(meds_text, width=80)}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="detail-card">
                <h4>🧭 Lifestyle</h4>
                <p>{textwrap.fill(lifestyle_text, width=80)}</p>
            </div>
        """, unsafe_allow_html=True)

    else:
        st.info("No saved profile found — please complete your profile with the form below.")

    # Edit mode toggle (keeps UI similar to original; originally had an Edit button)
    st.markdown("**Edit Profile**")
    edit_toggle = st.checkbox("Enable editing (check to edit profile)", value=False)

    if edit_toggle:
        # Use form to ensure Submit button and grouped saving (fixes 'missing submit' issue)
        with st.form("profile_edit_form"):
            col1, col2 = st.columns([1, 2])
            # left column: profile picture upload & preview
            with col1:
                st.markdown("**Profile Picture**")
                uploaded = st.file_uploader("Upload (jpg/png)", type=["jpg", "jpeg", "png"], accept_multiple_files=False)
                # determine preview pic path/value
                preview_path = None
                if uploaded:
                    # save uploaded file to assets with username-based filename
                    try:
                        dest = ASSETS_DIR / f"{username}_profile.png"
                        with open(dest, "wb") as f:
                            f.write(uploaded.getbuffer())
                        preview_path = str(dest)
                    except Exception:
                        preview_path = None
                else:
                    # if no new upload, use stored pic or default
                    if profile and len(profile) > 9 and profile[9] and Path(profile[9]).exists():
                        preview_path = profile[9]
                    else:
                        preview_path = str(DEFAULT_PIC)

                # display preview safely
                safe_image_display(preview_path, width=200, caption="Profile Picture Preview")

            # right column: text inputs
            with col2:
                st.markdown("**Personal Details**")
                age_input = st.number_input("Age", min_value=0, max_value=120, value=profile[2] if profile and profile[2] else 25)
                gender_input = st.selectbox("Gender", ["Male", "Female", "Other"], index=(["Male","Female","Other"].index(profile[3]) if profile and profile[3] in ["Male","Female","Other"] else 0))
                allergies_input = st.text_area("Allergies", value=profile[4] if profile and profile[4] else "")
                history_input = st.text_area("Medical History", value=profile[5] if profile and profile[5] else "")
                chronic_input = st.text_area("Chronic Conditions", value=profile[6] if profile and profile[6] else "")
                meds_input = st.text_area("Current Medications", value=profile[7] if profile and profile[7] else "")
                lifestyle_input = st.text_area("Lifestyle Notes (e.g., smoke, alcohol, vegan)", value=profile[8] if profile and profile[8] else "")

            # submit button (CRITICAL: included so form actually submits)
            submitted = st.form_submit_button("💾 Save Profile")
            if submitted:
                # determine stored_profile_pic: prefer newly uploaded dest, else keep existing, else default
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

                # Save to DB
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
                    # refresh profile variable to reflect new data
                    profile = get_profile(username)
                    # uncheck edit toggle by rerunning (keeps UI tidy)
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Error saving profile: {e}")

    # After edit or read-only, show health tips based on current profile
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

# -----------------------------
# End of file — keep UI consistent with original large layout
# -----------------------------
