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

if "active_history" not in st.session_state:
    st.session_state.active_history = None

# -----------------------------
# Styling (Professional)
# -----------------------------
st.markdown("""
<style>
.flashcard {
    border: 1px solid #dcdcdc;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
    background-color: #ffffff;
}
.flashcard-title {
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 10px;
}
.flashcard-text {
    color: #374151;
    font-size: 15px;
}
.sidebar-section {
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar (Menu Bar)
# -----------------------------
st.sidebar.title("Application Menu")

st.sidebar.markdown("### Study Mode")
mode = st.sidebar.radio(
    label="Select mode",
    options=[
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
    st.sidebar.caption("No history available")
else:
    history_labels = [
        f"{i + 1}. {item['mode']}"
        for i, item in enumerate(st.session_state.history)
    ]
    selected = st.sidebar.radio(
        label="History items",
        options=list(range(len(history_labels))),
        format_func=lambda x: history_labels[x],
        index=None
    )
    st.session_state.active_history = selected

st.sidebar.markdown("---")
if st.sidebar.button("Clear History"):
    st.session_state.history.clear()
    st.session_state.active_history = None

# -----------------------------
# Load API Key
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not configured.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# Main Content Area
# -----------------------------
st.title("AI-Powered Study Buddy")
st.caption("Academic assistance for explanation, summarization, quizzes, and flashcards")

# -----------------------------
# Show History Content
# -----------------------------
if st.session_state.active_history is not None:
    record = st.session_state.history[st.session_state.active_history]

    st.subheader("Previous Result")
    st.markdown(f"**Mode:** {record['mode']}")
    st.markdown(f"**Input Content:** {record['input']}")
    st.divider()

    if record["mode"] == "Generate Flashcards":
        for i, (q, a) in enumerate(record["output"], 1):
            st.markdown(f"""
            <div class="flashcard">
                <div class="flashcard-title">Flashcard {i}</div>
                <div class="flashcard-text"><strong>Question:</strong> {q}</div>
                <div class="flashcard-text"><strong>Answer:</strong> {a}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write(record["output"])

    st.stop()

# -----------------------------
# Input Section
# -----------------------------
st.subheader("New Request")

user_input = st.text_area(
    "Enter study content",
    height=180,
    placeholder="Example: Explain artificial intelligence and its applications"
)

# -----------------------------
# Generate Button
# -----------------------------
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
        prompt = f"Explain the following topic clearly for a student:\n{user_input}"
    elif mode == "Summarize Notes":
        prompt = f"Summarize the following notes in a concise manner:\n{user_input}"
    else:
        prompt = f"Create 5 quiz questions with answers:\n{user_input}"

    with st.spinner("Generating response"):
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

            if mode == "Generate Flashcards":
                cards = re.findall(
                    r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n|$)",
                    output,
                    re.S
                )

                st.subheader("Generated Flashcards")

                for i, (q, a) in enumerate(cards, 1):
                    st.markdown(f"""
                    <div class="flashcard">
                        <div class="flashcard-title">Flashcard {i}</div>
                        <div class="flashcard-text"><strong>Question:</strong> {q.strip()}</div>
                        <div class="flashcard-text"><strong>Answer:</strong> {a.strip()}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.session_state.history.append({
                    "mode": mode,
                    "input": user_input,
                    "output": [(q.strip(), a.strip()) for q, a in cards]
                })

            else:
                st.subheader("Result")
                st.write(output)

                st.session_state.history.append({
                    "mode": mode,
                    "input": user_input,
                    "output": output
                })

        except Exception as e:
            st.error("Model request failed.")
            st.code(str(e))
