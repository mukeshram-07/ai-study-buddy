import streamlit as st
from groq import Groq
import os

# -------------------------------------------------
# Page config
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

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #020617;
    border-right: 1px solid #1F2937;
}

/* Main card */
.block-container {
    background-color: #111827;
    border-radius: 20px;
    padding: 2.5rem;
    margin: 1rem;
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

/* Buttons */
.stButton > button {
    background-color: #22C55E;
    color: #022C22;
    border-radius: 30px;
    padding: 0.6rem 2.2rem;
    font-weight: 700;
    border: none;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #16A34A;
    transform: scale(1.05);
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
# SIDEBAR MENU
# -------------------------------------------------
st.sidebar.markdown("## 📘 Study Buddy")

menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🧠 Explain Topic", "✍️ Summarize Notes", "❓ Generate Quiz", "ℹ️ About"]
)

# -------------------------------------------------
# HOME
# -------------------------------------------------
if menu == "🏠 Home":
    st.markdown("## Welcome 👋")
    st.write(
        "Study Buddy is an AI-powered learning assistant that helps students "
        "understand concepts, summarize notes, and generate quizzes instantly."
    )

# -------------------------------------------------
# EXPLAIN TOPIC
# -------------------------------------------------
elif menu == "🧠 Explain Topic":
    st.markdown("## 🧠 Explain Topic")
    text = st.text_area("Enter a topic")

    if st.button("Explain"):
        prompt = f"Explain this topic in simple student-friendly language:\n{text}"

        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )

            st.success("Explanation")
            st.write(completion.choices[0].message.content)

# -------------------------------------------------
# SUMMARIZE NOTES
# -------------------------------------------------
elif menu == "✍️ Summarize Notes":
    st.markdown("## ✍️ Summarize Notes")
    text = st.text_area("Paste your notes")

    if st.button("Summarize"):
        prompt = f"Summarize the following notes clearly:\n{text}"

        with st.spinner("Summarizing..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )

            st.success("Summary")
            st.write(completion.choices[0].message.content)

# -------------------------------------------------
# GENERATE QUIZ
# -------------------------------------------------
elif menu == "❓ Generate Quiz":
    st.markdown("## ❓ Generate Quiz")
    text = st.text_area("Enter topic")

    if st.button("Generate Quiz"):
        prompt = f"Create 5 quiz questions with answers from this topic:\n{text}"

        with st.spinner("Generating quiz..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )

            st.success("Quiz")
            st.write(completion.choices[0].message.content)

# -------------------------------------------------
# ABOUT
# -------------------------------------------------
elif menu == "ℹ️ About":
    st.markdown("## ℹ️ About Study Buddy")
    st.write(
        """
        **Study Buddy** is a web-based AI learning assistant built using:
        - Streamlit (Frontend)
        - Groq LLaMA 3.1 (AI Engine)
        
        The system helps students learn efficiently by providing
        explanations, summaries, and quizzes on demand.
        """
    )
