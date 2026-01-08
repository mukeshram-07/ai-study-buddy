import streamlit as st
from groq import Groq
import os
import PyPDF2

# ---------------------------------
# Page configuration
# ---------------------------------
st.set_page_config(
    page_title="Study Buddy",
    layout="centered"
)

# ---------------------------------
# ChatGPT-style minimal theme
# ---------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0B1220;
}
.block-container {
    max-width: 720px;
    padding-top: 2rem;
}
h1 {
    text-align: center;
    color: #E5E7EB;
}
p, label, div {
    color: #9CA3AF;
}
textarea {
    background-color: #111827 !important;
    color: #E5E7EB !important;
    border-radius: 14px !important;
    padding-bottom: 2.5rem !important;
}
.upload-row {
    display: flex;
    justify-content: flex-end;
    margin-top: -2.2rem;
    margin-right: 0.6rem;
}
.stButton > button {
    background-color: #10B981;
    color: white;
    border-radius: 22px;
    padding: 0.45rem 1.6rem;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #059669;
}
.chat-box {
    background-color: #111827;
    border-radius: 14px;
    padding: 1.2rem;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# Load API key
# ---------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("API key not found.")
    st.stop()

client = Groq(api_key=api_key)

# ---------------------------------
# Helper: Extract text from PDF
# ---------------------------------
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

# ---------------------------------
# UI
# ---------------------------------
st.markdown("<h1>Study Buddy</h1>", unsafe_allow_html=True)
st.write("Ask questions, upload documents, or generate quizzes.")

# Chat input
user_input = st.text_area(
    "Message",
    height=120,
    placeholder="Ask something or paste content here..."
)

# Upload button positioned like ChatGPT (end of box)
st.markdown("<div class='upload-row'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Attach file",
    type=["pdf", "txt"],
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# Action selector
action = st.selectbox(
    "Action",
    ["Explain", "Summarize", "Generate 3 Quiz Questions"]
)

# ---------------------------------
# Send button
# ---------------------------------
if st.button("Send"):
    if not user_input.strip() and not uploaded_file:
        st.warning("Enter text or upload a document.")
        st.stop()

    document_text = extract_text(uploaded_file)

    if action == "Explain":
        prompt = f"""
Explain the following content in simple student-friendly language.

User input:
{user_input}

Document content (if any):
{document_text}
"""

    elif action == "Summarize":
        prompt = f"""
Summarize the following content clearly.

User input:
{user_input}

Document content (if any):
{document_text}
"""

    else:
        prompt = f"""
Generate exactly 3 quiz questions with answers from the following content.

User input:
{user_input}

Document content (if any):
{document_text}
"""

    with st.spinner("Thinking..."):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )

    response = completion.choices[0].message.content

    # Chat-style output
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    st.markdown("**Assistant**")
    st.write(response)
    st.markdown("</div>", unsafe_allow_html=True)
