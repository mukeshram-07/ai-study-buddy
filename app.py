import streamlit as st
from groq import Groq
import os
import PyPDF2

# ---------------------------------
# Page configuration
# ---------------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    layout="centered"
)

# ---------------------------------
# Minimal ChatGPT-style theme
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

/* Text */
h1 { color: #E5E7EB; text-align: center; }
p, label, div { color: #9CA3AF; }

/* Textarea */
textarea {
    background-color: #111827 !important;
    color: #E5E7EB !important;
    border-radius: 14px !important;
    padding-bottom: 2.8rem !important;
}

/* Upload icon row */
.upload-icon {
    display: flex;
    justify-content: flex-end;
    margin-top: -2.6rem;
    margin-right: 0.8rem;
}

/* Button */
.stButton > button {
    background-color: #10B981;
    color: white;
    border-radius: 22px;
    padding: 0.5rem 1.8rem;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #059669;
}

/* Response box */
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
# System Prompt (fixed structure)
# ---------------------------------
SYSTEM_PROMPT = """
You are an AI Study Buddy designed to support students in understanding academic content.

Always structure your response as:

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

Maintain a professional academic tone.
"""

# ---------------------------------
# Helper: Extract text from PDF/TXT
# ---------------------------------
def extract_text(file):
    if not file:
        return ""
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    return ""

# ---------------------------------
# UI
# ---------------------------------
st.markdown("<h1>AI Study Buddy</h1>", unsafe_allow_html=True)
st.write("Ask a question or paste study material. File upload is optional.")

# Message box (NO label)
user_input = st.text_area(
    label="",
    height=130,
    placeholder="Ask a question or paste study content here..."
)

# Upload icon aligned to right of box
st.markdown("<div class='upload-icon'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Attach file",
    type=["pdf", "txt"],
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------
# Action
# ---------------------------------
if st.button("Send"):
    if not user_input.strip() and not uploaded_file:
        st.warning("Please enter text or upload a document.")
        st.stop()

    doc_text = extract_text(uploaded_file)

    final_prompt = f"""
User Text:
{user_input}

Document Content:
{doc_text}
"""

    with st.spinner("Processing..."):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

    response = completion.choices[0].message.content

    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
    st.markdown("**Assistant**")
    st.write(response)
    st.markdown("</div>", unsafe_allow_html=True)
