import streamlit as st
import google.generativeai as genai
import os
import time

# -----------------------------
# Gemini API
# -----------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="AI Study Buddy", layout="centered")

# -----------------------------
# Animated background
# -----------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
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
# UI
# -----------------------------
st.title("🤖 AI-Powered Study Buddy")
st.write("Explain topics • Summarize notes • Generate quizzes")

option = st.selectbox(
    "Choose a feature",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area("Enter your content")

# -----------------------------
# Mock fallback AI (LOCAL)
# -----------------------------
def mock_ai(option, text):
    if option == "Explain Topic":
        return f"""
**Explanation (Demo Mode):**

{text} refers to a concept in computer science where machines are designed
to simulate human intelligence such as learning, reasoning, and problem-solving.
"""
    elif option == "Summarize Notes":
        return f"""
**Summary (Demo Mode):**

{text[:150]}...
"""
    else:
        return """
**Quiz (Demo Mode):**
1. What is AI?
2. Name one application of AI.
3. What is machine learning?
4. Is AI rule-based or learning-based?
5. Give one real-world example of AI.
"""

# -----------------------------
# Button
# -----------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter text")
        st.stop()

    if len(text) > 1200:
        st.warning("Input too long. Please shorten it.")
        st.stop()

    # Prompt
    if option == "Explain Topic":
        prompt = f"Explain simply:\n{text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers:\n{text}"

    model = genai.GenerativeModel("gemini-1.5-flash")

    with st.spinner("Generating response..."):
        try:
            response = model.generate_content(
                prompt,
                generation_config={"max_output_tokens": 300}
            )

            output = getattr(response, "text", "").strip()

            if output:
                st.success("Result (Live AI)")
                st.write(output)
            else:
                raise Exception("Empty response")

        except Exception:
            time.sleep(1)
            st.warning("Live AI busy — switched to demo mode")
            st.success("Result (Demo AI)")
            st.write(mock_ai(option, text))
