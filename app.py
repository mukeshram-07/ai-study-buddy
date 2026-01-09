import streamlit as st
from groq import Groq
import os
import re

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    layout="centered"
)

# -----------------------------
# Simple Professional Styling
# -----------------------------
st.markdown("""
<style>
.flashcard {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 15px;
    background-color: #ffffff;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}

.flashcard h4 {
    color: #2a5298;
    margin-bottom: 10px;
}

.flashcard p {
    color: #333333;
    font-size: 15px;
}
</style>
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
st.title("AI-Powered Study Buddy")
st.caption("Explain • Summarize • Quiz • Flashcards")

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
    placeholder="Example: Artificial Intelligence"
)

# -----------------------------
# Generate Button
# -----------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some content.")
        st.stop()

    if option == "Generate Flashcards":
        prompt = f"""
        Create exactly 5 study flashcards.
        Use the format:
        Q: Question
        A: Answer

        Content:
        {text}
        """
    elif option == "Explain Topic":
        prompt = f"Explain this topic clearly for a student:\n{text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize the following notes:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers:\n{text}"

    with st.spinner("Generating..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=400
            )

            output = response.choices[0].message.content

            # -----------------------------
            # Flashcard Rendering
            # -----------------------------
            if option == "Generate Flashcards":
                flashcards = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n|$)", output, re.S)

                if not flashcards:
                    st.warning("Could not format flashcards. Try again.")
                else:
                    st.subheader("Flashcards")
                    for i, (q, a) in enumerate(flashcards, 1):
                        st.markdown(f"""
                        <div class="flashcard">
                            <h4>Flashcard {i}</h4>
                            <p><strong>Q:</strong> {q.strip()}</p>
                            <p><strong>A:</strong> {a.strip()}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("Result")
                st.write(output)

        except Exception as e:
            st.error("Groq API Error")
            st.code(str(e))
