import streamlit as st
from groq import Groq
import os

# --------------------------------
# Page configuration
# --------------------------------
st.set_page_config(
    page_title="AI-Powered Study Buddy",
    layout="centered"
)

# --------------------------------
# GLOBAL CSS (IMPORTANT)
# --------------------------------
st.markdown("""
<style>

/* ROOT BACKGROUND (THIS FIXES WHITE BG) */
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1f4037);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

/* Gradient animation */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Main content glass card */
.block-container {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 2.5rem;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
}

/* Headings */
h1, h2, h3 {
    color: white;
    text-align: center;
}

/* Paragraph text */
p, label, span {
    color: #eaeaea !important;
}

/* Text area & select box */
textarea, select {
    border-radius: 14px !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 30px;
    padding: 0.6rem 2rem;
    font-weight: bold;
    border: none;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.08);
    box-shadow: 0px 10px 25px rgba(0,0,0,0.4);
}

/* Result box */
.stAlert {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------
# Load Groq API Key
# --------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# --------------------------------
# UI HEADER
# --------------------------------
st.markdown("<h1>🤖 AI-Powered Study Buddy</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:18px;'>Explain topics • Summarize notes • Generate quizzes</p>",
    unsafe_allow_html=True
)

# --------------------------------
# Controls
# --------------------------------
option = st.selectbox(
    "Choose a feature",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area(
    "Enter your content",
    height=180,
    placeholder="Example: Define Artificial Intelligence"
)

# --------------------------------
# Button Action
# --------------------------------
if st.button("✨ Generate"):
    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    if len(text) > 1500:
        st.warning("Input too long. Please shorten it.")
        st.stop()

    if option == "Explain Topic":
        prompt = f"Explain this topic in simple student-friendly language:\n{text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize the following notes clearly:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers from the following topic:\n{text}"

    with st.spinner("🚀 AI is thinking..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=350
            )

            output = completion.choices[0].message.content
            st.success("Result")
            st.write(output)

        except Exception as e:
            st.error("AI service temporarily unavailable.")
            st.code(str(e))
