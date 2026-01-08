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
# Animated background
# -----------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #1f4037, #99f2c8);
    background-size: 400% 400%;
    animation: bg 10s ease infinite;
}
@keyframes bg {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Load API key
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# UI
# -----------------------------
st.title("🤖 AI-Powered Study Buddy (Groq)")
st.write("Explain topics • Summarize notes • Generate quizzes")

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
# Button logic
# -----------------------------
if st.button("Generate"):
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

    with st.spinner("Generating response..."):
        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
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
            st.error("Groq API Error:")
            st.code(str(e))
