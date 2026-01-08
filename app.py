import streamlit as st
from groq import Groq
import os

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="AI-Powered Study Buddy",
    layout="centered"
)

# -------------------------------------------------
# GLOBAL THEME (AI / TECH MODERN)
# -------------------------------------------------
st.markdown("""
<style>

/* ===== ROOT BACKGROUND ===== */
.stApp {
    background-color: #0F172A; /* Dark Navy */
}

/* ===== MAIN CONTENT CARD ===== */
.block-container {
    background-color: #111827; /* Dark card */
    border-radius: 20px;
    padding: 2.5rem;
    margin-top: 1rem;
    box-shadow: 0 20px 40px rgba(0,0,0,0.45);
}

/* ===== HEADINGS ===== */
h1, h2, h3 {
    color: #E5E7EB; /* Primary text */
    text-align: center;
}

/* ===== NORMAL TEXT ===== */
p, label, span, div {
    color: #9CA3AF; /* Secondary text */
}

/* ===== SELECT BOX & TEXT AREA ===== */
textarea, select {
    background-color: #0F172A !important;
    color: #E5E7EB !important;
    border-radius: 14px !important;
    border: 1px solid #1F2937 !important;
}

/* ===== BUTTON (PRIMARY) ===== */
.stButton > button {
    background: linear-gradient(135deg, #38BDF8, #0EA5E9); /* Sky Blue */
    color: #0F172A;
    border-radius: 32px;
    padding: 0.6rem 2.2rem;
    font-weight: 700;
    border: none;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 12px 28px rgba(56,189,248,0.45);
}

/* ===== SUCCESS / RESULT BOX ===== */
.stAlert[data-baseweb="notification"] {
    background-color: #022C22 !important;
    color: #D1FAE5 !important;
    border-radius: 14px;
    border-left: 6px solid #22C55E; /* Green */
}

/* ===== WARNING BOX ===== */
.stAlert[data-baseweb="notification"][role="alert"] {
    border-radius: 14px;
}

/* ===== SCROLLBAR (OPTIONAL POLISH) ===== */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #1F2937;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Load Groq API key
# -------------------------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ GROQ_API_KEY not found in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("<h1>🤖 AI-Powered Study Buddy</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; font-size:18px;'>Explain topics • Summarize notes • Generate quizzes</p>",
    unsafe_allow_html=True
)

# -------------------------------------------------
# USER INPUT CONTROLS
# -------------------------------------------------
option = st.selectbox(
    "Choose a feature",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area(
    "Enter your content",
    height=180,
    placeholder="Example: Define Artificial Intelligence"
)

# -------------------------------------------------
# BUTTON ACTION
# -------------------------------------------------
if st.button("🚀 Generate"):
    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    if len(text) > 1500:
        st.warning("Input too long. Please shorten it.")
        st.stop()

    if option == "Explain Topic":
        prompt = f"Explain this topic in simple student-friendly language:\n{text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize the following notes clearly:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers from the following topic:\n{text}"

    with st.spinner("AI is processing..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful study assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=350
            )

            output = completion.choices[0].message.content
            st.success("Result")
            st.write(output)

        except Exception as e:
            st.error("AI service temporarily unavailable.")
            st.code(str(e))
