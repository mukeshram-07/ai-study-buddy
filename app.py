import streamlit as st
import google.generativeai as genai
import os

# ---------------------------------
# Configure Gemini API
# ---------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(
    page_title="AI-Powered Study Buddy",
    layout="centered"
)

# ---------------------------------
# Animated background
# ---------------------------------
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

# ---------------------------------
# UI
# ---------------------------------
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

# ---------------------------------
# Button action
# ---------------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    if len(text) > 1200:
        st.warning("Input too long. Please limit to 1200 characters.")
        st.stop()

    # Prompt creation
    if option == "Explain Topic":
        prompt = f"Explain the following topic in simple student-friendly language:\n{text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize the following notes clearly:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers from the following topic:\n{text}"

    # ---------------------------------
    # Gemini model (FAST & STABLE)
    # ---------------------------------
    model = genai.GenerativeModel("gemini-1.5-flash")

    with st.spinner("Generating response..."):
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 300,
                    "temperature": 0.4
                }
            )

            output = getattr(response, "text", "").strip()

            if output:
                st.success("Result")
                st.write(output)
            else:
                st.warning("AI responded but returned no text. Please try again.")

        except Exception as e:
            st.error("AI service is temporarily busy. Please try again later.")
