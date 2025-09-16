# pages/profile.py — Viveka

import streamlit as st
import sqlite3
from pathlib import Path

# ---- DB FILE ----
DB_FILE = "users.db"

# ---- Default Profile Pic ----
DEFAULT_PIC = Path(__file__).parent / "assets" / "default_profile.png"

# ---- DB INIT ----
def init_medical_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS medical_profile (
                    user_id TEXT PRIMARY KEY,
                    allergies TEXT,
                    conditions TEXT,
                    preferences TEXT
                )''')
    conn.commit()
    conn.close()

# ---- SAVE PROFILE ----
def save_profile(user_id, allergies, conditions, preferences):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO medical_profile
                 (user_id, allergies, conditions, preferences)
                 VALUES (?, ?, ?, ?)''',
              (user_id, allergies, conditions, preferences))
    conn.commit()
    conn.close()

# ---- LOAD PROFILE ----
def load_profile(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM medical_profile WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"user_id": row[0], "allergies": row[1], "conditions": row[2], "preferences": row[3]}
    return {"user_id": user_id, "allergies": "", "conditions": "", "preferences": ""}

# ---- MAIN PROFILE PAGE ----
def show_profile():
    st.title("👤 Your Medical Profile")

    if "user_id" not in st.session_state:
        st.warning("⚠️ Please login to view your profile.")
        return

    user_id = st.session_state["user_id"]
    init_medical_db()
    user_data = load_profile(user_id)

    # ---- Profile Picture ----
    if DEFAULT_PIC.exists():
        st.image(str(DEFAULT_PIC), width=200, caption="Profile Picture")
    else:
        st.warning("⚠️ Default profile picture not found.")

    # ---- Form ----
    with st.form("profile_form"):
        st.subheader("Update Your Medical Details")

        allergies = st.text_input("Allergies", user_data.get("allergies", ""))
        conditions = st.text_input("Medical Conditions", user_data.get("conditions", ""))
        preferences = st.text_area("Health Preferences", user_data.get("preferences", ""))

        submitted = st.form_submit_button("💾 Save Profile")
        if submitted:
            save_profile(user_id, allergies, conditions, preferences)
            st.success("✅ Profile saved successfully!")

# ---- Run Page ----
if __name__ == "__main__":
    show_profile()
