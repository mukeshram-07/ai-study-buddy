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
# GLOBAL THEME (DARK NAVY + GREEN)
# -------------------------------------------------
st.markdown("""
<style>

/* Root background */
.stApp {
    background-color: #0F172A;
}

/* Top menu bar */
.top-nav {
    display: flex;
    gap: 2rem;
    padding: 1rem 2rem;
    background-color: #020617;
    border-bottom: 1px solid #1F2937;
}

.top-nav a {
    color: #9CA3AF;
    font-weight: 600;
    text-decoration: none;
    font-size: 15px;
}

.top-nav a:hover {
    color: #22C55E;
}

/* Main content card */
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

/* Primary button */
.stButton > button {
    background-color: #22C55E;
    color: #FFFFFF;
    border-radius: 28px;
    padding: 0.6rem 2.2rem;
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
# Load Groq API key
# -------------------------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------------------------
# TOP NAVIGATION (CHATGPT STYLE)
# -------------------------------------------------
menu = st.selectbox(
    "",
    ["Home", "Explain Topic", "Summarize Notes", "Generate Quiz", "About"],
    index=0
)

# -------------------------------------------------
# PAGE CONTENT
# -------------------------------------------------
if menu == "Home":
    st.markdown("## Study Buddy")
    st.write(
        "Study Buddy is an AI-powered academic assistant that helps students "
        "understand concepts, summarize study material, and generate quizzes efficiently."
    )

elif menu == "Explain Topic":
    st.markdown("## Explain Topic")
    text = st.text_area("Enter a topic or question")

    if st.button("Generate Explanation"):
        if not text.strip():
            st.warning("Please enter a topic.")
            st.stop()

        prompt = f"Explain this topic in simple student-friendly language:\n{text}"

        with st.spinner("Processing..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )

            st.success("Explanation")
            st.write(completion.choices[0].message.content)

elif menu == "Summarize Notes":
    st.markdown("## Summarize Notes")
    text = st.text_area("Paste your notes here")

    if st.button("Generate Summary"):
        if not text.strip():
            st.warning("Please enter notes.")
            st.stop()

        prompt = f"Summarize the following notes clearly:\n{text}"

        with st.spinner("Processing..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )

            st.success("Summary")
            st.write(completion.choices[0].message.content)

elif menu == "Generate Quiz":
    st.markdown("## Generate Quiz")
    text = st.text_area("Enter a topic")

    if st.button("Generate Quiz"):
        if not text.strip():
            st.warning("Please enter a topic.")
            st.stop()

        prompt = f"Create 5 quiz questions with answers from this topic:\n{text}"

        with st.spinner("Processing..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )

            st.success("Quiz")
            st.write(completion.choices[0].message.content)

elif menu == "About":
    st.markdown("## About Study Buddy")
    st.write(
        """
        Study Buddy is a web-based AI learning assistant built using:

        - Streamlit for the user interface  
        - Groq (LLaMA 3.1) for AI processing  

        The platform follows a clean, professional design inspired by modern AI tools.
        """
    )
