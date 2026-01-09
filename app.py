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
# Streamlit-safe Background + Floating Illustrations
# -----------------------------
st.markdown("""
<style>

/* MAIN APP CONTAINER */
section[data-testid="stAppViewContainer"] {
    background: #ffffff;
}

/* Remove default white blocks */
div[data-testid="stVerticalBlock"] {
    background: transparent;
}

/* Floating illustration images */
.floating-graphics img {
    position: fixed;
    bottom: -160px;
    width: 140px;
    opacity: 0.15;
    animation: floatUp linear infinite;
    z-index: 0;
}

/* Floating animation */
@keyframes floatUp {
    from { transform: translateY(0); }
    to { transform: translateY(-120vh); }
}

/* Individual positions */
.graphic1 { left: 5%; animation-duration: 22s; }
.graphic2 { left: 30%; animation-duration: 26s; }
.graphic3 { left: 60%; animation-duration: 24s; }
.graphic4 { left: 80%; animation-duration: 28s; }

/* Content above graphics */
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
    st.error("GROQ_API_KEY not found.")
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
    placeholder="Example: Artificial Intelligence"
)

# -----------------------------
# Button Logic
# -----------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some content.")
        st.stop()

    if option == "Explain Topic":
        prompt = f"Explain this topic in simple language:\n{text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize the following notes:\n{text}"
    elif option == "Generate Quiz":
        prompt = f"Create 5 quiz questions with answers:\n{text}"
    else:
        prompt = f"""
        Create 6 flashcards.
        Format:
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
                    {"role": "system", "content": "You are a professional study assistant."},
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
