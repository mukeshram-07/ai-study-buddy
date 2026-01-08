import streamlit as st
from groq import Groq
import os

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Study Buddy",
    layout="centered"
)

# -------------------------------------------------
# GLOBAL THEME (PROFESSIONAL NEUTRAL + TEAL)
# -------------------------------------------------
st.markdown("""
<style>

/* App background */
.stApp {
    background-color: #0B1220;
}

/* Main content container */
.block-container {
    background-color: #111827;
    border-radius: 18px;
    padding: 2.5rem;
    margin-top: 2rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.45);
}

/* Headings */
h1, h2, h3 {
    color: #E5E7EB;
    text-align: center;
}

/* Text */
p, label, span, div {
    color: #9CA3AF;
}

/* Input fields */
textarea, select {
    background-color: #0B1220 !important;
    color: #E5E7EB !important;
    border-radius: 12px !important;
    border: 1px solid #1F2937 !important;
}

/* Primary button */
.stButton > button {
    background-color: #14B8A6;
    color: #FFFFFF;
    border-radius: 28px;
    padding: 0.6rem 2.5rem;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #0D9488;
    transform: scale(1.04);
}

/* Alerts */
.stAlert {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Load API key
# -------------------------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("API key not found in environment.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("<h1>Study Buddy</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:16px;'>An AI-powered academic assistant for understanding, revision, and practice</p>",
    unsafe_allow_html=True
)

# -------------------------------------------------
# FEATURE SELECTION
# -------------------------------------------------
feature = st.selectbox(
    "Select a task",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area(
    "Enter your content",
    height=180,
    placeholder="Example: Define Artificial Intelligence"
)

# -------------------------------------------------
# ACTION
# -------------------------------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some text to continue.")
        st.stop()

    if feature == "Explain Topic":
        prompt = f"Explain the following topic in simple, student-friendly language:\n{text}"
    elif feature == "Summarize Notes":
        prompt = f"Summarize the following study notes clearly:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers based on the following topic:\n{text}"

    with st.spinner("Processing..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350
            )

            st.success("Result")
            st.write(completion.choices[0].message.content)

        except Exception as e:
            st.error("The AI service is temporarily unavailable.")
            st.code(str(e))

# -------------------------------------------------
# ABOUT
# -------------------------------------------------
st.markdown("## About Study Buddy")
st.write(
    """
    Study Buddy is a web-based learning assistant designed to support students
    in understanding academic concepts, revising study material, and testing
    their knowledge through automatically generated quizzes.

    The application focuses on simplicity, clarity, and usability, making it
    suitable for academic environments and self-paced learning.
    """
)
