import streamlit as st
from groq import Groq
import os
import re

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    layout="wide"
)

# -------------------------------------------------
# Session State Initialization
# -------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "selected_history" not in st.session_state:
    st.session_state.selected_history = None

# -------------------------------------------------
# Theme-aware Styling
# -------------------------------------------------
st.markdown("""
<style>
.flashcard {
    border: 1px solid rgba(150, 150, 150, 0.25);
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 16px;
    background-color: var(--background-color);
    color: var(--text-color);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.flashcard-title {
    font-weight: 600;
    margin-bottom: 10px;
}

.flashcard-content {
    line-height: 1.6;
}

/* Mermaid container */
.mermaid {
    background-color: var(--background-color);
    color: var(--text-color);
    border-radius: 8px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar (Menu Bar)
# -------------------------------------------------
st.sidebar.title("Application Menu")

st.sidebar.markdown("### Study Mode")
mode = st.sidebar.selectbox(
    "Mode",
    [
        "Explain Topic",
        "Summarize Notes",
        "Generate Quiz",
        "Generate Flashcards",
        "Generate Flowchart"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### History")

if not st.session_state.history:
    st.sidebar.caption("No history available")
else:
    for i, item in enumerate(st.session_state.history):
        with st.sidebar.expander(f"{i + 1}. {item['mode']}"):
            st.caption(item["input"][:120] + ("..." if len(item["input"]) > 120 else ""))
            if st.button("Open", key=f"open_{i}"):
                st.session_state.selected_history = i

st.sidebar.markdown("---")
if st.sidebar.button("Clear History"):
    st.session_state.history.clear()
    st.session_state.selected_history = None

# -------------------------------------------------
# Load API Key
# -------------------------------------------------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not configured.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------------------------
# Main Content
# -------------------------------------------------
st.title("AI-Powered Study Buddy")
st.caption(
    "Professional academic assistant for explanations, summaries, quizzes, flashcards, and flowcharts"
)

# -------------------------------------------------
# Display History Record
# -------------------------------------------------
if st.session_state.selected_history is not None:
    record = st.session_state.history[st.session_state.selected_history]

    st.subheader("Previous Result")
    st.markdown(f"**Mode:** {record['mode']}")
    st.markdown(f"**Input:** {record['input']}")
    st.divider()

    if record["mode"] == "Generate Flashcards":
        for idx, (q, a) in enumerate(record["output"], 1):
            st.markdown(f"""
            <div class="flashcard">
                <div class="flashcard-title">Flashcard {idx}</div>
                <div class="flashcard-content"><strong>Question:</strong> {q}</div>
                <div class="flashcard-content"><strong>Answer:</strong> {a}</div>
            </div>
            """, unsafe_allow_html=True)

    elif record["mode"] == "Generate Flowchart":
        st.markdown(record["output"], unsafe_allow_html=True)

    else:
        st.write(record["output"])

    st.stop()

# -------------------------------------------------
# New Request Section
# -------------------------------------------------
st.subheader("New Request")

user_input = st.text_area(
    "Enter study content",
    height=180,
    placeholder="Example: Explain the software development life cycle"
)

# -------------------------------------------------
# Generate Output
# -------------------------------------------------
if st.button("Generate Output"):
    if not user_input.strip():
        st.warning("Input cannot be empty.")
        st.stop()

    # ---------------- Prompt Selection ----------------
    if mode == "Generate Flashcards":
        prompt = f"""
        Create exactly 5 study flashcards.
        Format strictly as:
        Q: Question
        A: Answer

        Content:
        {user_input}
        """

    elif mode == "Generate Flowchart":
        prompt = f"""
        Convert the following topic into a clear flowchart.
        Use Mermaid flowchart syntax only.
        Start with 'graph TD'.
        Do not include explanations or markdown.

        Topic:
        {user_input}
        """

    elif mode == "Explain Topic":
        prompt = f"Explain the following topic clearly for a student:\n{user_input}"

    elif mode == "Summarize Notes":
        prompt = f"Summarize the following notes concisely:\n{user_input}"

    else:
        prompt = f"Create 5 quiz questions with answers:\n{user_input}"

    # ---------------- Model Call ----------------
    with st.spinner("Generating response"):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=500
            )

            result = response.choices[0].message.content

            # ---------------- Rendering ----------------
            if mode == "Generate Flashcards":
                cards = re.findall(
                    r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n|$)",
                    result,
                    re.S
                )

                st.subheader("Generated Flashcards")
                for idx, (q, a) in enumerate(cards, 1):
                    st.markdown(f"""
                    <div class="flashcard">
                        <div class="flashcard-title">Flashcard {idx}</div>
                        <div class="flashcard-content"><strong>Question:</strong> {q.strip()}</div>
                        <div class="flashcard-content"><strong>Answer:</strong> {a.strip()}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.session_state.history.append({
                    "mode": mode,
                    "input": user_input,
                    "output": [(q.strip(), a.strip()) for q, a in cards]
                })

            elif mode == "Generate Flowchart":
                st.subheader("Generated Flowchart")
                st.markdown(f"<div class='mermaid'>{result}</div>", unsafe_allow_html=True)

                st.session_state.history.append({
                    "mode": mode,
                    "input": user_input,
                    "output": f"<div class='mermaid'>{result}</div>"
                })

            else:
                st.subheader("Result")
                st.write(result)

                st.session_state.history.append({
                    "mode": mode,
                    "input": user_input,
                    "output": result
                })

        except Exception as e:
            st.error("Request failed.")
            st.code(str(e))
