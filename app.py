import streamlit as st
from groq import Groq
import os
import re
import PyPDF2

# ---------------------------------
# Page config
# ---------------------------------
st.set_page_config(page_title="Study Buddy – File Q&A", layout="centered")

# ---------------------------------
# Load API key
# ---------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("API key not found")
    st.stop()

client = Groq(api_key=api_key)

# ---------------------------------
# Helper: Extract text from file
# ---------------------------------
def extract_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    elif file.type == "text/plain":
        return file.read().decode("utf-8")

    else:
        return ""

# ---------------------------------
# Helper: Extract questions
# ---------------------------------
def extract_questions(text):
    lines = text.split("\n")
    questions = []

    for line in lines:
        line = line.strip()
        if (
            line.endswith("?")
            or line.lower().startswith("what")
            or line.lower().startswith("explain")
            or line.lower().startswith("define")
            or line.lower().startswith("discuss")
        ):
            questions.append(line)

    return questions

# ---------------------------------
# UI
# ---------------------------------
st.title("Study Buddy – File Question Answering")
st.write("Upload a file and get answers to all questions automatically.")

uploaded_file = st.file_uploader(
    "Upload PDF or TXT file",
    type=["pdf", "txt"]
)

# ---------------------------------
# Main logic
# ---------------------------------
if uploaded_file:
    with st.spinner("Reading file..."):
        content = extract_text(uploaded_file)

    if not content.strip():
        st.error("Could not extract text from file.")
        st.stop()

    questions = extract_questions(content)

    if not questions:
        st.warning("No questions found in the file.")
        st.stop()

    st.success(f"Found {len(questions)} questions.")

    if st.button("Answer All Questions"):
        for i, q in enumerate(questions, start=1):
            st.markdown(f"### Question {i}")
            st.write(q)

            prompt = f"""
Answer the following academic question clearly and concisely:

Question:
{q}
"""

            with st.spinner("Generating answer..."):
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )

            answer = completion.choices[0].message.content
            st.markdown("**Answer:**")
            st.write(answer)
            st.divider()
