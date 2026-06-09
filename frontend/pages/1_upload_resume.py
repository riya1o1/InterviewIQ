import streamlit as st
import requests

API = "http://localhost:8000"

st.set_page_config(page_title="Upload Resume", page_icon="📄")

if not st.session_state.get("token"):
    st.warning("Please login first!")
    st.stop()

token = st.session_state.token
headers = {"Authorization": f"Bearer {token}"}

st.title("📄 Upload Your Resume")
st.markdown("Upload your PDF resume — AI will extract your skills, experience, and projects to personalize your interview questions.")
st.divider()

# ── Upload Section ───────────────────────────────────
uploaded_file = st.file_uploader("Choose your resume PDF", type=["pdf"])

if uploaded_file:
    if st.button("🚀 Upload & Analyze Resume", type="primary", use_container_width=True):
        with st.spinner("Extracting text and analyzing with AI..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            r = requests.post(f"{API}/resume/upload", files=files, headers=headers)

        if r.status_code == 200:
            data = r.json()
            st.success("Resume analyzed successfully!")
            st.session_state.resume = data

            # Show extracted data
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🛠️ Skills Detected")
                skills = data.get("skills", [])
                if skills:
                    cols = st.columns(3)
                    for i, skill in enumerate(skills):
                        cols[i % 3].markdown(f"`{skill}`")
                else:
                    st.write("No skills detected")

            with col2:
                st.subheader("💼 Experience")
                for exp in data.get("experience", []):
                    st.markdown(f"**{exp.get('role')}** at {exp.get('company')} — {exp.get('duration')}")

            st.subheader("🚀 Projects")
            for proj in data.get("projects", []):
                with st.expander(proj.get("name", "Project")):
                    st.write(proj.get("description", ""))
                    techs = proj.get("tech", [])
                    if techs:
                        st.write("Tech: " + ", ".join(techs))

            st.divider()
            st.success("✅ Resume saved! Head to **Practice** or **Mock Interview** to begin.")
        else:
            st.error(f"Upload failed: {r.json().get('detail', 'Unknown error')}")

# ── Show existing resume ─────────────────────────────
st.divider()
st.subheader("📋 Current Resume on File")
r = requests.get(f"{API}/resume/me", headers=headers)
if r.status_code == 200:
    data = r.json()
    st.success(f"Resume uploaded on {data['uploaded_at'][:10]}")
    st.write("**Skills:** " + ", ".join(data.get("skills", [])))
else:
    st.info("No resume uploaded yet.")
