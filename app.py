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
st.title("AI-Powered Study Buddy")
st.caption("Explain topics • Summarize notes • Generate quizzes • Create flashcards")

option = st.selectbox(
    "Select a study tool",
    [
        "Explain Topic",
        "Summarize Notes",
        "Generate Quiz",
        "Generate Flashcards"
    ]
)

text = st.text_area(
    "Enter your content",
    height=180,
    placeholder="Example: Artificial Intelligence and its applications"
)

# -----------------------------
# Button logic
# -----------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some content.")
        st.stop()

    if len(text) > 1500:
        st.warning("Input too long. Please shorten it.")
        st.stop()

    if option == "Explain Topic":
        prompt = f"""
        Explain the following topic in clear, simple, student-friendly language.
        Use examples where appropriate.

        Topic:
        {text}
        """

    elif option == "Summarize Notes":
        prompt = f"""
        Summarize the following notes clearly.
        Use bullet points and keep it concise.

        Notes:
        {text}
        """

    elif option == "Generate Quiz":
        prompt = f"""
        Create 5 quiz questions with answers based on the following topic.
        Mix conceptual and factual questions.

        Topic:
        {text}
        """

    else:  # Generate Flashcards
        prompt = f"""
        Create 6 study flashcards from the following content.
        Format strictly as:
        Q: Question
        A: Answer

        Content:
        {text}
        """

    with st.spinner("Generating response..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional academic study assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=350
            )

            output = completion.choices[0].message.content

            st.success("Result")
            st.write(output)

        except Exception as e:
            st.error("Groq API Error")
            st.code(str(e))
