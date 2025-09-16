# app.py — Viveka (User-friendly UI with Matcher & Analyzer)
import streamlit as st
import os, sys
from PIL import Image

# -------------------------------
# Streamlit Config (MUST be first Streamlit command)
# -------------------------------
st.set_page_config(
    page_title="Viveka - Ingredient Safety Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Redirect to login if not logged in
# -------------------------------
try:
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.switch_page("pages/login_signup.py")
except Exception:
    st.warning("⚠️ Please login first from the login page.")

# -------------------------------
# Adjust import path
# -------------------------------
ROOT = os.path.dirname(__file__)
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.append(SRC)

# -------------------------------
# Imports from src
# -------------------------------
from src.ocr_utils import extract_text
from src.matcher import match_ingredients, df as ingredient_df
from src.analyzer import analyze_ingredients, display_analysis

# -------------------------------
# Profile Reminder Notification (first time only)
# -------------------------------
if "profile_popup_shown" not in st.session_state:
    st.session_state["profile_popup_shown"] = False

if not st.session_state["profile_popup_shown"]:
    st.markdown(
        """
        <div style="position:fixed; top:20px; right:20px; background:#222; padding:20px;
                    border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.4); 
                    width:350px; z-index:1000; color:white;">
            <h4 style="margin:0; color:#4CAF50;">💡 Personalize Your Experience</h4>
            <p style="font-size:14px; line-height:1.5; margin-top:8px;">
                For <b>personalized ingredient safety suggestions</b>,  
                go to the <span style="color:#4CAF50;">⚙ Profile section</span>  
                and add your health conditions or allergies.
                <br><br>
                You can continue without creating a profile.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.session_state["profile_popup_shown"] = True

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.title("Viveka")
menu = st.sidebar.radio("Navigate", ["Home", "History", "Profile"])

# Redirect sidebar Profile to profile.py
if menu == "Profile":
    try:
        st.switch_page("pages/profile.py")
    except Exception:
        st.error("Profile page not found. Please check if `pages/profile.py` exists.")

# -------------------------------
# Session State Keys
# -------------------------------
if "ocr_results" not in st.session_state:
    st.session_state["ocr_results"] = []
if "ingredient_list" not in st.session_state:
    st.session_state["ingredient_list"] = []
if "manual_text" not in st.session_state:
    st.session_state["manual_text"] = ""

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.title("Viveka — Ingredient Safety Analyzer")
    st.success("✅ Viveka = Discernment — helping you choose what is safe for your health.")
    st.info("⚠️ This app is for informational purposes only. Not a substitute for medical advice.")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    # ---- Left Column: Upload + OCR ----
    with col1:
        st.subheader("📸 Upload Product Photo")
        uploaded_file = st.file_uploader(
            "Upload a clear photo of the ingredients label", type=["jpg", "jpeg", "png"]
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded photo", width="stretch")

            if st.button("🔍 Read Text", key="read_btn"):
                with st.spinner("Scanning photo for text..."):
                    try:
                        results = extract_text(uploaded_file)
                    except Exception as e:
                        st.error(f"Could not read text: {e}")
                        results = []

                    st.session_state["ocr_results"] = results

                    # Process OCR text into unique tokens
                    lines = [r["text"].strip() for r in results if r.get("text")]
                    seen = set()
                    uniq_lines = []
                    for ln in lines:
                        if ln and ln.lower() not in seen:
                            seen.add(ln.lower())
                            uniq_lines.append(ln)

                    tokens = []
                    for line in uniq_lines:
                        parts = [p.strip() for p in line.replace("/", ",").split(",") if p.strip()]
                        for p in parts:
                            if p.lower() not in [t.lower() for t in tokens]:
                                tokens.append(p)

                    st.session_state["ingredient_list"] = tokens
                    st.session_state["manual_text"] = "\n".join(tokens)

        if st.session_state["ingredient_list"]:
            st.subheader("✅ Detected Ingredients")
            st.write("We found these ingredients from the photo:")
            for i, ing in enumerate(st.session_state["ingredient_list"], 1):
                st.write(f"{i}. {ing}")

    # ---- Right Column: Manual Input + Analysis ----
    with col2:
        st.subheader("✍️ Type or Edit Ingredients")
        st.markdown("You can edit the text below before checking.")
        manual_val = st.text_area(
            "Ingredients (one per line or separated by commas):",
            value=st.session_state.get("manual_text", ""),
            height=300,
            key="manual_input_area",
        )
        st.session_state["manual_text"] = manual_val

        if st.button("✅ Check Ingredients", key="analyze_btn"):
            if not manual_val.strip():
                st.warning("Please enter or upload some ingredients first.")
            else:
                # Split manual input into clean list
                parts = []
                for line in manual_val.splitlines():
                    for tok in line.split(","):
                        t = tok.strip()
                        if t and t.lower() not in [p.lower() for p in parts]:
                            parts.append(t)

                st.subheader("🔎 Final Ingredient List")
                for i, p in enumerate(parts, 1):
                    st.write(f"{i}. {p}")

                # --- Matcher ---
                matched_items = match_ingredients(parts, ingredient_df)

                # --- Analyzer ---
                analysis_df = analyze_ingredients(matched_items)

                # --- Display Editable Table ---
                edited_df = display_analysis(analysis_df)
                st.session_state["final_analysis"] = edited_df

# ---------------------------
# History Page (placeholder)
# ---------------------------
elif menu == "History":
    st.title("📂 Your Past Scans")
    st.info("History of scanned products will appear here (coming soon).")
