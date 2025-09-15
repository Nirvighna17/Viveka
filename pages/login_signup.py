import streamlit as st
import sqlite3
import hashlib
import os
import smtplib
import random
from email.message import EmailMessage
import streamlit.components.v1 as components

components.html("""
    <script>
        history.pushState(null, '', location.href);
        window.onpopstate = function () {
            history.go(1);
        };
    </script>
""", height=0)

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Login | VIVEKA",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---- HIDE SIDEBAR ----
hide_sidebar = """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_sidebar, unsafe_allow_html=True)

# ---- CUSTOM CSS ----
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(-45deg, #141E30, #243B55, #0F2027, #2C5364);
            background-size: 400% 400%;
            animation: gradientBG 12s ease infinite;
        }

        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        .title {
            font-size: 2.5rem;
            font-weight: bold;
            color: white;
            text-align: center;
            margin-bottom: 1rem;
        }

        .subtitle {
            font-size: 1rem;
            color: #cccccc;
            text-align: center;
            margin-bottom: 2rem;
        }

        .login-box {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 15px;
            max-width: 400px;
            margin: auto;
            box-shadow: 0 0 12px rgba(255,255,255,0.08);
        }

        label {
            color: #ffffff !important;
        }

        .stTextInput > div > input {
            background-color: #111 !important;
            color: white !important;
        }

        .stPassword > div > input {
            background-color: #111 !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---- DATABASE SETUP ----
DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, email, password, role="user"):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                  (username, email, hashed_pw, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute("SELECT email, role FROM users WHERE username = ? AND password = ?",
              (username, hashed_pw))
    result = c.fetchone()
    conn.close()
    return result

def update_password(email, new_password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    hashed_pw = hash_password(new_password)
    c.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, email))
    conn.commit()
    conn.close()

def email_exists(email):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# ---- EMAIL FUNCTIONS ----
def send_verification_email(receiver_email):
    otp = str(random.randint(100000, 999999))
    msg = EmailMessage()
    msg["Subject"] = "Viveka - Email Verification Code"
    msg["From"] = "Viveka <nirvighnalnct@gmail.com>"
    msg["To"] = receiver_email
    msg.set_content(f"Your verification code is: {otp}")

    msg.add_alternative(f"""
    <!DOCTYPE html>
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background-color: #fff; padding: 30px; border-radius: 10px;">
          <h2 style="color: #2C5364; text-align: center;">Welcome to Viveka!</h2>
          <p>Thanks for signing up on <strong>Viveka</strong>.</p>
          <p style="margin: 20px 0; padding: 15px; background-color: #f0f8ff; border-left: 5px solid #2C5364;">
             <strong>Your verification code:</strong> <span style="font-size: 1.5em; color: #2C5364;">{otp}</span>
          </p>
          <p>Enter this code to complete your signup process.</p>
          <br>
          <p>Regards,<br><strong>Team Viveka</strong></p>
        </div>
      </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("nirvighnalnct@gmail.com", "ahrz xkyo qntf okpj")
            smtp.send_message(msg)
        return otp
    except Exception as e:
        st.error(f"❌ Email send failed: {e}")
        return None

def send_reset_otp(receiver_email):
    otp = str(random.randint(100000, 999999))
    msg = EmailMessage()
    msg["Subject"] = "Viveka - Password Reset Code"
    msg["From"] = "Viveka <nirvighnalnct@gmail.com>"
    msg["To"] = receiver_email
    msg.set_content(f"Your OTP for resetting your password is: {otp}")

    msg.add_alternative(f"""
    <!DOCTYPE html>
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background-color: #fff; padding: 30px; border-radius: 10px;">
          <h2 style="color: #2C5364; text-align: center;">Viveka Password Reset</h2>
          <p>We received a request to reset your password.</p>
          <p style="margin: 20px 0; padding: 15px; background-color: #f0f8ff; border-left: 5px solid #2C5364;">
             <strong>OTP Code:</strong> <span style="font-size: 1.5em; color: #2C5364;">{otp}</span>
          </p>
          <p>Enter this code to proceed.</p>
          <br>
          <p>Regards,<br><strong>Team Viveka</strong></p>
        </div>
      </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("nirvighnalnct@gmail.com", "ahrz xkyo qntf okpj")
            smtp.send_message(msg)
        return otp
    except Exception as e:
        st.error(f"❌ Email send failed: {e}")
        return None

# ---- Init DB ----
init_db()

# ---- HEADER ----
st.markdown("<div class='title'>Welcome to Viveka</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>We pray for your Good health</div>", unsafe_allow_html=True)

# ---- TABS ----
tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])

# ---- LOGIN TAB ----
with tab1:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        result = validate_user(username, password)
        if result:
            email, role = result
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["email"] = email
            st.session_state["role"] = role
            st.success("✅ Login successful!")
            st.switch_page("pages/app.py")
        else:
            st.error("❌ Invalid username or password.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- SIGNUP TAB ----
with tab2:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    new_email = st.text_input("Email", key="signup_email")
    new_user = st.text_input("Create Username", key="signup_user")
    new_pass = st.text_input("Create Password", type="password", key="signup_pass")
    confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass")
    role = "user"

    if "otp_sent" not in st.session_state:
        st.session_state.otp_sent = False
        st.session_state.otp_code = ""
        st.session_state.otp_entered = ""

    if st.button("📤 Send Verification Code"):
        if new_user.strip() == "" or new_pass.strip() == "" or new_email.strip() == "":
            st.error("⚠️ Email, username, and password cannot be empty.")
        elif new_pass != confirm_pass:
            st.error("❌ Passwords do not match.")
        elif "@" not in new_email or "." not in new_email:
            st.error("❌ Please enter a valid email address.")
        elif email_exists(new_email):  # 🔥 Check if email already registered
            st.error("⚠️ This email is already registered. Please log in instead.")
        else:
            otp = send_verification_email(new_email)
            if otp:
                st.session_state.otp_sent = True
                st.session_state.otp_code = otp
                st.success("✅ Verification code sent to your email.")

    if st.session_state.otp_sent:
        st.session_state.otp_entered = st.text_input("Enter Verification Code")
        if st.button("✅ Complete Sign Up"):
            if st.session_state.otp_entered == st.session_state.otp_code:
                if email_exists(new_email):  # ✅ Double-check before final insert
                    st.error("⚠️ This email is already registered. Please log in.")
                else:
                    success = add_user(new_user, new_email, new_pass)
                    if success:
                        st.success("🎉 Account created! Please login.")
                        st.session_state.otp_sent = False
                    else:
                        st.error("❌ Username already exists.")
            else:
                st.error("❌ Invalid verification code.")

    st.markdown("</div>", unsafe_allow_html=True)

# ---- FORGOT PASSWORD TAB ----
with tab3:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    if "fp_otp_sent" not in st.session_state:
        st.session_state["fp_otp_sent"] = False
        st.session_state["fp_otp_code"] = ""
        st.session_state["fp_email"] = ""

    fp_email = st.text_input("Enter your registered email")

    if st.button("📤 Send OTP"):
        otp = send_reset_otp(fp_email)
        if otp:
            st.session_state["fp_otp_sent"] = True
            st.session_state["fp_otp_code"] = otp
            st.session_state["fp_email"] = fp_email
            st.success("✅ OTP sent to your email!")

    if st.session_state["fp_otp_sent"]:
        entered_otp = st.text_input("Enter the OTP sent to your email")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")

        if st.button("🔁 Reset Password"):
            if entered_otp == st.session_state["fp_otp_code"]:
                if new_password == confirm_new_password and len(new_password) >= 6:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    hashed_pw = hash_password(new_password)
                    c.execute("UPDATE users SET password = ? WHERE email = ?",
                              (hashed_pw, st.session_state["fp_email"]))
                    conn.commit()
                    conn.close()
                    st.success("✅ Password updated successfully! Please login.")
                    # Reset session
                    st.session_state["fp_otp_sent"] = False
                    st.session_state["fp_otp_code"] = ""
                    st.session_state["fp_email"] = ""
                else:
                    st.error("❌ Passwords don't match or too short.")
            else:
                st.error("❌ Invalid OTP.")
    st.markdown("</div>", unsafe_allow_html=True)
