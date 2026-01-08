import streamlit as st
from groq import Groq
import os
import PyPDF2

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    layout="centered"
)

# -----------------------------
# Load API key
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("API key not found.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# System Prompt (YOUR RULES)
# -----------------------------
SYSTEM_PROMPT = """
You are an AI Study Buddy designed to support students in understanding academic content.

Your responsibilities are as follows:

1. Analyze the user’s input, which may include:
   - Plain text study notes
   - A direct academic question
   - An uploaded document (PDF, DOCX, or TXT)

2. If study material is provided:
   - Generate a concise and accurate summary.
   - Explain the key concepts in clear, simple, academic language.
   - Generate exactly three quiz questions with answers.

3. If the user asks a direct question:
   - Answer it clearly and correctly.
   - Provide a brief explanation if relevant.
   - Generate exactly three related quiz questions with answers.

4. Structure every response strictly in this format:

Summary:
- ...

Explanation:
- ...

Practice Questions:
1. Question 1
   Answer:
2. Question 2
   Answer:
3. Question 3
   Answer:

5. Maintain a professional and neutral tone.
6. Do not use emojis, slang, or informal language.
7. Do not mention system limitations or constraints.
"""

# -----------------------------
# Helper: Extract text from PDF
# -----------------------------
def extract_text(file):
    if file is None:
        return ""
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

# -----------------------------
# UI
# -----------------------------
st.title("AI Study Buddy")
st.write("Enter a question or notes. Uploading a document is optional.")

uploaded_file = st.file_uploader(
    "Upload document (optional)",
    type=["pdf", "txt"]
)

user_input = st.text_area(
    "Input",
    height=150,
    placeholder="Enter a question or study notes here..."
)

# -----------------------------
# Generate response
# -----------------------------
if st.button("Generate Response"):
    if not user_input.strip() and not uploaded_file:
        st.warning("Please enter text or upload a document.")
        st.stop()

    document_text = extract_text(uploaded_file)

    final_input = f"""
User Input:
{user_input}

Document Content:
{document_text}
"""

    with st.spinner("Processing..."):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": final_input}
            ],
            temperature=0.3,
            max_tokens=500
        )

    response = completion.choices[0].message.content

    st.markdown("### AI Response")
    st.write(response)
