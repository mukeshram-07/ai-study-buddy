import streamlit as st
from groq import Groq
import os

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="AI-Powered Study Buddy (Groq)",
    layout="centered"
)

# -----------------------------
# Animated background + UI CSS
# -----------------------------
st.markdown("""
<style>

/* Background animation */
body {
    background: linear-gradient(-45deg, #141e30, #243b55, #1f4037, #99f2c8);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

/* Gradient animation */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Glass card */
.main {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(12px);
    padding: 2rem;
    border-radius: 16px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 25px;
    padding: 0.6rem 1.8rem;
    border: none;
    font-weight: bold;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 8px 20px rgba(0,0,0,0.3);
}

/* Text area */
textarea {
    border-radius: 12px !important;
}

/* Result box */
.stAlert {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load Groq API key
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# UI Header
# -----------------------------
st.markdown("<h1 style='text-align:center;'>🤖 AI-Powered Study Buddy</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:18px;'>Explain topics • Summarize notes • Generate quizzes</p>",
    unsafe_allow_html=True
)

# -----------------------------
# Controls
# -----------------------------
option = st.selectbox(
    "Choose a feature",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area(
    "Enter your content",
    height=180,
    placeholder="Example: Define Artificial Intelligence"
)

# -----------------------------
# Generate Button
# -----------------------------
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

    with st.spinner("🚀 Thinking..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=300
            )

            output = completion.choices[0].message.content
            st.success("Result")
            st.write(output)

        except Exception as e:
            st.error("AI service temporarily unavailable.")
            st.code(str(e))
