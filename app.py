import streamlit as st
from groq import Groq
import os

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    layout="centered"
)

# -----------------------------
# Animated Background + Floating Icons
# -----------------------------
st.markdown("""
<style>
/* Gradient background */
body {
    background: linear-gradient(-45deg, #1e3c72, #2a5298);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Floating icons */
.floating-icons span {
    position: fixed;
    bottom: -50px;
    font-size: 28px;
    opacity: 0.25;
    animation: floatUp linear infinite;
    z-index: 0;
}

@keyframes floatUp {
    from {
        transform: translateY(0);
    }
    to {
        transform: translateY(-110vh);
    }
}

/* Individual icon positions & speeds */
.floating-icons span:nth-child(1) { left: 10%; animation-duration: 14s; }
.floating-icons span:nth-child(2) { left: 25%; animation-duration: 18s; }
.floating-icons span:nth-child(3) { left: 40%; animation-duration: 16s; }
.floating-icons span:nth-child(4) { left: 55%; animation-duration: 20s; }
.floating-icons span:nth-child(5) { left: 70%; animation-duration: 17s; }
.floating-icons span:nth-child(6) { left: 85%; animation-duration: 19s; }

/* Content on top */
.main-content {
    position: relative;
    z-index: 2;
}
</style>

<div class="floating-icons">
    <span>📘</span>
    <span>🎓</span>
    <span>📚</span>
    <span>✏️</span>
    <span>💡</span>
    <span>🧠</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Load API Key
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found. Please add it to environment variables.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# UI
# -----------------------------
st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.title("AI-Powered Study Buddy")
st.caption("Explain • Summarize • Quiz • Flashcards")

option = st.selectbox(
    "Select a study mode",
    [
        "Explain Topic",
        "Summarize Notes",
        "Generate Quiz",
        "Generate Flashcards"
    ]
)

text = st.text_area(
    "Enter your study content",
    height=180,
    placeholder="Example: Artificial Intelligence and its applications"
)

# -----------------------------
# Button Logic
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
        Explain the following topic in simple, student-friendly language.
        Use examples where helpful.

        Topic:
        {text}
        """

    elif option == "Summarize Notes":
        prompt = f"""
        Summarize the following notes clearly.
        Use bullet points.

        Notes:
        {text}
        """

    elif option == "Generate Quiz":
        prompt = f"""
        Create 5 quiz questions with answers.
        Mix conceptual and factual questions.

        Topic:
        {text}
        """

    else:  # Flashcards
        prompt = f"""
        Create 6 study flashcards.
        Format strictly as:
        Q: Question
        A: Answer

        Content:
        {text}
        """

    with st.spinner("Processing..."):
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

            st.success("Generated Output")
            st.write(completion.choices[0].message.content)

        except Exception as e:
            st.error("Groq API Error")
            st.code(str(e))

st.markdown('</div>', unsafe_allow_html=True)
