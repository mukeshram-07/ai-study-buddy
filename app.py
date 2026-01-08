import streamlit as st
from groq import Groq
import os

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Study Buddy",
    layout="wide"
)

# -------------------------------------------------
# Session state for navigation
# -------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

def go(page_name):
    st.session_state.page = page_name

# -------------------------------------------------
# GLOBAL THEME (DARK NAVY + GREEN)
# -------------------------------------------------
st.markdown("""
<style>

/* Root */
.stApp {
    background-color: #0F172A;
}

/* Top menubar */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.8rem 2rem;
    background-color: #020617;
    border-bottom: 1px solid #1F2937;
}

/* Logo */
.logo {
    font-size: 18px;
    font-weight: 700;
    color: #E5E7EB;
}

/* Nav center */
.nav-center {
    display: flex;
    gap: 1.8rem;
}

.nav-item {
    color: #9CA3AF;
    font-weight: 500;
    cursor: pointer;
}

.nav-item:hover {
    color: #22C55E;
}

/* Right actions */
.nav-right {
    color: #9CA3AF;
    font-weight: 500;
}

/* Main container */
.block-container {
    background-color: #111827;
    border-radius: 20px;
    padding: 2.5rem;
    margin: 2rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.45);
}

/* Headings */
h1, h2, h3 {
    color: #E5E7EB;
}

/* Text */
p, label, span, div {
    color: #9CA3AF;
}

/* Inputs */
textarea, select {
    background-color: #0F172A !important;
    color: #E5E7EB !important;
    border-radius: 12px !important;
    border: 1px solid #1F2937 !important;
}

/* Primary buttons */
.stButton > button {
    background-color: #22C55E;
    color: #FFFFFF; /* FIXED: visible white text */
    border-radius: 28px;
    padding: 0.6rem 2.4rem;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #16A34A;
    transform: scale(1.04);
}

/* Success box */
.stAlert {
    background-color: #022C22 !important;
    color: #D1FAE5 !important;
    border-left: 6px solid #22C55E;
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Load API key
# -------------------------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("API key not found.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------------------------
# TOP SAAS MENUBAR
# -------------------------------------------------
st.markdown(
    """
    <div class="topbar">
        <div class="logo">Study Buddy</div>
        <div class="nav-center">
            <div class="nav-item" onclick="window.location.hash='#Dashboard'">Dashboard</div>
            <div class="nav-item" onclick="window.location.hash='#Features'">Features</div>
            <div class="nav-item" onclick="window.location.hash='#Workspace'">Workspace</div>
            <div class="nav-item" onclick="window.location.hash='#History'">History</div>
            <div class="nav-item" onclick="window.location.hash='#Resources'">Resources</div>
            <div class="nav-item" onclick="window.location.hash='#Help'">Help</div>
        </div>
        <div class="nav-right">Profile</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------
st.markdown("## Dashboard")
st.write(
    "Study Buddy is a modern learning assistant designed to support students "
    "with concept understanding, revision, and self-assessment in a structured way."
)

# -------------------------------------------------
# WORKSPACE (MAIN AI AREA)
# -------------------------------------------------
st.markdown("## Workspace")

feature = st.selectbox(
    "Choose a feature",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area(
    "Enter your content",
    height=180,
    placeholder="Example: Define Artificial Intelligence"
)

if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    if feature == "Explain Topic":
        prompt = f"Explain this topic in simple student-friendly language:\n{text}"
    elif feature == "Summarize Notes":
        prompt = f"Summarize the following notes clearly:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers from the following topic:\n{text}"

    with st.spinner("Processing..."):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350
        )

        st.success("Result")
        st.write(completion.choices[0].message.content)

# -------------------------------------------------
# ABOUT
# -------------------------------------------------
st.markdown("## About Study Buddy")
st.write(
    """
    Study Buddy is a web-based academic support platform created to help students
    learn more effectively. The system assists users by explaining complex topics
    in simple language, summarizing study material, and generating practice quizzes.

    The application follows a clean, professional SaaS-style interface inspired by
    modern productivity and AI tools, ensuring ease of use, clarity, and scalability
    for future enhancements.
    """
)
