import streamlit as st
from groq import Groq
import os
import re

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "view_index" not in st.session_state:
    st.session_state.view_index = None

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.flashcard {
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 14px;
    background-color: #ffffff;
}
.flashcard-title {
    font-weight: 600;
    margin-bottom: 8px;
}
.history-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.history-label {
    font-size: 14px;
    color: #374151;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar (Menu Bar)
# -----------------------------
st.sidebar.title("Application Menu")
st.sidebar.markdown("### Study Mode")

mode = st.sidebar.selectbox(
    "Mode",
    [
        "Explain Topic",
        "Summarize Notes",
        "Generate Quiz",
        "Generate Flashcards"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### History")

if not st.session_state.history:
    st.sidebar.caption("No records available")
else:
    for i, item in enumerate(st.session_state.history):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.markdown(
                f"<div class='history-label'>{i + 1}. {item['mode']}</div>",
                unsafe_allow_html=True
            )
        with col2:
            if st.button("View", key=f"view_{i}"):
                st.session_state.view_index = i

st.sidebar.markdown("---")
if st.sidebar.button("Clear History"):
    st.session_state.history.clear()
    st.session_state.view_index = None

# -----------------------------
# Load API Key
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not configured.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# Main Area
# -----------------------------
st.title("AI-Powered Study Buddy")
st.caption("Professional academic assistant")

# -----------------------------
# View History Content
# -----------------------------
if st.session_state.view_index is not None:
    record = st.session_state.history[st.session_state.view_index]

    st.subheader("Previous Result")
    st.markdown(f"**Mode:** {record['mode']}")
    st.markdown(f"**Input:** {record['input']}")
    st.divider()

    if record["mode"] == "Generate Flashcards":
        for i, (q, a) in enumerate(record["output"], 1):
            st.markdown(f"""
            <div class="flashcard">
                <div class="flashcard-title">Flashcard {i}</div>
                <div><strong>Question:</strong> {q}</div>
                <div><strong>Answer:</strong> {a}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write(record["output"])

    st.stop()

# -----------------------------
# New Request Section
# -----------------------------
st.subheader("New Request")

user_input = st.text_area(
    "Enter content",
    height=180,
    placeholder="Example: Artificial Intelligence"
)

if st.button("Generate Output"):
    if not user_input.strip():
        st.warning("Input cannot be empty.")
        st.stop()

    if mode == "Generate Flashcards":
        prompt = f"""
        Create exactly 5 study flashcards.
        Format:
        Q: Question
        A: Answer

        Content:
        {user_input}
        """
    elif mode == "Explain Topic":
        prompt = f"Explain this topic clearly:\n{user_input}"
    elif mode == "Summarize Notes":
        prompt = f"Summarize the following notes:\n{user_input}"
    else:
        prompt = f"Create 5 quiz questions with answers:\n{user_input}"

    with st.spinner("Generating"):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional academic assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=400
        )

        result = response.choices[0].message.content

        if mode == "Generate Flashcards":
            cards = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n|$)", result, re.S)

            st.subheader("Generated Flashcards")
            for i, (q, a) in enumerate(cards, 1):
                st.markdown(f"""
                <div class="flashcard">
                    <div class="flashcard-title">Flashcard {i}</div>
                    <div><strong>Question:</strong> {q.strip()}</div>
                    <div><strong>Answer:</strong> {a.strip()}</div>
                </div>
                """, unsafe_allow_html=True)

            st.session_state.history.append({
                "mode": mode,
                "input": user_input,
                "output": [(q.strip(), a.strip()) for q, a in cards]
            })
        else:
            st.subheader("Result")
            st.write(result)

            st.session_state.history.append({
                "mode": mode,
                "input": user_input,
                "output": result
            })
