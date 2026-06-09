import streamlit as st

st.set_page_config(
    page_title="AI Interview Prep",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State Init ──────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# ── Auth UI ─────────────────────────────────────────
import requests
API = "http://localhost:8000"

def login(email, password):
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

def signup(name, email, password):
    r = requests.post(f"{API}/auth/signup", json={"name": name, "email": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    return None

# ── Main Page ────────────────────────────────────────
if not st.session_state.token:
    st.title("🎯 AI Interview Preparation Platform")
    st.markdown("*Upload your resume → Get AI-generated questions → Practice & improve*")
    st.divider()

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Welcome back!")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True, type="primary"):
            token = login(email, password)
            if token:
                st.session_state.token = token
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab2:
        st.subheader("Create your account")
        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up", use_container_width=True, type="primary"):
            token = signup(name, email, password)
            if token:
                st.session_state.token = token
                st.success("Account created!")
                st.rerun()
            else:
                st.error("Signup failed — email may already be registered")

else:
    # Logged in — show navigation
    st.title("🎯 AI Interview Prep")
    st.success(f"You're logged in! Use the sidebar to navigate.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📄 **Step 1:** Upload Resume")
    with col2:
        st.info("🎤 **Step 2:** Start Practice / Mock")
    with col3:
        st.info("📊 **Step 3:** Track Progress")

    st.divider()
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()
