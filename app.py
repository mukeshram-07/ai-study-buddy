import streamlit as st
from groq import Groq
import os
import PyPDF2

# ---------------------------------
# Page setup
# ---------------------------------
st.set_page_config(page_title="Study Buddy – Document AI", layout="centered")

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
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text

    elif file.type == "text/plain":
        return file.read().decode("utf-8")

    return ""

# ---------------------------------
# UI
# ---------------------------------
st.title("Study Buddy – Document Assistant")
st.write("Upload a document and choose what you want to do.")

uploaded_file = st.file_uploader(
    "Upload PDF or TXT file",
    type=["pdf", "txt"]
)

task = st.selectbox(
    "Choose an action",
    ["Explain Content", "Summarize Document", "Generate 3 Quiz Questions"]
)

# ---------------------------------
# Main logic
# ---------------------------------
if uploaded_file:
    with st.spinner("Reading document..."):
        document_text = extract_text(uploaded_file)

    if not document_text.strip():
        st.error("Unable to extract text from the document.")
        st.stop()

    if st.button("Process Document"):
        if task == "Explain Content":
            prompt = f"""
Explain the following content in simple student-friendly language:

{document_text}
"""

        elif task == "Summarize Document":
            prompt = f"""
Summarize the following document clearly and concisely:

{document_text}
"""

        else:  # Generate 3 Quiz Questions
            prompt = f"""
Create exactly 3 quiz questions with answers from the following document:

{document_text}
"""

        with st.spinner("Generating response..."):
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )

        st.success("Result")
        st.write(completion.choices[0].message.content)
