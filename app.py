import streamlit as st
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Page config
st.set_page_config(page_title="AI Study Buddy", layout="centered")

# Animated background
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
    background-size: 400% 400%;
    animation: gradient 10s ease infinite;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
</style>
""", unsafe_allow_html=True)

# UI
st.title("AI-Powered Study Buddy (Gemini)")
st.write("Explain topics • Summarize notes • Generate quizzes")

option = st.selectbox(
    "Choose a feature",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area("Enter your content")

if st.button("Generate"):
    if text.strip() == "":
        st.warning("Please enter some text")
    else:
        if option == "Explain Topic":
            prompt = f"Explain this topic in simple student-friendly language:\n{text}"
        elif option == "Summarize Notes":
            prompt = f"Summarize the following notes clearly:\n{text}"
        else:
            prompt = f"Create 5 quiz questions with answers from this topic:\n{text}"

        with st.spinner("Generating answer (may take a few seconds)..."):

          model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    generation_config={
        "max_output_tokens": 300,
        "temperature": 0.5
    }
)

try:
    response = model.generate_content(prompt)
    st.success("Result")
    st.write(response.text)

except Exception:
    st.error("AI is busy right now. Please try again in a few seconds.")

