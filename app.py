import streamlit as st
import google.generativeai as genai
import os

# -------------------------------
# Configure Gemini API
# -------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(
    page_title="AI-Powered Study Buddy",
    layout="centered"
)

# -------------------------------
# Animated background (CSS)
# -------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
    background-size: 400% 400%;
    animation: gradientBG 10s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# UI
# -------------------------------
st.title("🤖 AI-Powered Study Buddy (Gemini)")
st.write("Explain topics • Summarize notes • Generate quizzes")

option = st.selectbox(
    "Choose a feature",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area(
    "Enter your content",
    height=180,
    placeholder="Example: What is Artificial Intelligence?"
)

# -------------------------------
# Button action
# -------------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    if len(text) > 1200:
        st.warning("Input too long. Please limit to 1200 characters.")
        st.stop()

    # Create prompt
    if option == "Explain Topic":
        prompt = f"Explain the following topic in simple student-friendly language:\n{text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize the following notes clearly:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers from the following topic:\n{text}"

    # Gemini model (stable + fast)
    model = genai.GenerativeModel(
        model_name="gemini-1.0-pro",
        generation_config={
            "max_output_tokens": 300,
            "temperature": 0.4
        }
    )

    with st.spinner("Generating response..."):
        try:
            response = model.generate_content(prompt)

            if response and hasattr(response, "text") and response.text:
                st.success("Result")
                st.write(response.text)
            else:
                st.warning("AI returned no output. Please try again with shorter input.")

        except Exception:
            st.error("AI service is busy or temporarily unavailable. Please try again later.")
