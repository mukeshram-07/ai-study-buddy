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
# Animated Background + Floating Graphics
# -----------------------------
st.markdown("""
<style>

/* Gradient background */
body {
    background: linear-gradient(120deg, #1e3c72, #2a5298);
    background-size: 200% 200%;
    animation: gradientBG 10s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Floating illustration container */
.floating-graphics img {
    position: fixed;
    bottom: -150px;
    width: 120px;
    opacity: 0.18;
    animation: floatUp linear infinite;
    z-index: 0;
}

/* Floating animation */
@keyframes floatUp {
    from {
        transform: translateY(0);
    }
    to {
        transform: translateY(-120vh);
    }
}

/* Individual image placement */
.graphic1 {
    left: 5%;
    animation-duration: 22s;
}

.graphic2 {
    left: 30%;
    animation-duration: 26s;
}

.graphic3 {
    left: 60%;
    animation-duration: 24s;
}

.graphic4 {
    left: 80%;
    animation-duration: 28s;
}

/* Keep content above graphics */
.main-content {
    position: relative;
    z-index: 2;
}

</style>

<div class="floating-graphics">
    <img class="graphic1" src="https://cdn-icons-png.flaticon.com/512/3135/3135755.png">
    <img class="graphic2" src="https://cdn-icons-png.flaticon.com/512/1995/1995574.png">
    <img class="graphic3" src="https://cdn-icons-png.flaticon.com/512/201/201818.png">
    <img class="graphic4" src="https://cdn-icons-png.flaticon.com/512/2942/2942920.png">
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
# UI Content
# -----------------------------
st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.title("AI-Powered Study Buddy")
st.caption("Explain concepts • Summarize notes • Generate quizzes • Create flashcards")

option = st.selectbox(
    "Select a learning mode",
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
    placeholder="Example: Explain Artificial Intelligence and its applications"
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
        Explain the following topic clearly in simple student-friendly language.

        Topic:
        {text}
        """

    elif option == "Summarize Notes":
        prompt = f"""
        Summarize the following notes clearly using bullet points.

        Notes:
        {text}
        """

    elif option == "Generate Quiz":
        prompt = f"""
        Create 5 quiz questions with answers based on the topic.

        Topic:
        {text}
        """

    else:
        prompt = f"""
        Create 6 study flashcards.
        Format strictly as:
        Q: Question
        A: Answer

        Content:
        {text}
        """

    with st.spinner("Generating..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional academic study assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=350
            )

            st.success("Result")
            st.write(response.choices[0].message.content)

        except Exception as e:
            st.error("Groq API Error")
            st.code(str(e))

st.markdown('</div>', unsafe_allow_html=True)
