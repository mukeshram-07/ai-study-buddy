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
# Session State
# -------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "selected_history" not in st.session_state:
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
# Styling (Theme Aware)
# -------------------------------------------------
st.markdown("""
<style>
.flashcard {
    border: 1px solid rgba(150,150,150,0.25);
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 16px;
    background-color: var(--background-color);
    color: var(--text-color);
}
.flashcard-title {
    font-weight: 600;
    margin-bottom: 8px;
}
.mermaid {
    background-color: var(--background-color);
    border: 1px solid rgba(150,150,150,0.25);
    border-radius: 8px;
    padding: 18px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Mermaid Cleaner & Formatter
# -------------------------------------------------
def clean_and_format_mermaid(raw: str) -> str:
    raw = re.sub(r"```mermaid|```", "", raw, flags=re.IGNORECASE).strip()
    lines = raw.splitlines()
    formatted = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"\|\>\s*", "|", line)
        line = re.sub(r"\s*-->\s*", " --> ", line)
        line = re.sub(r"\s*-\.\->\s*", " -.-> ", line)

        if " --> " in line and line.count(" --> ") > 1:
            parts = line.split(" --> ")
            for i in range(len(parts) - 1):
                formatted.append(f"{parts[i]} --> {parts[i+1]}")
        else:
            formatted.append(line)

    if not formatted or not formatted[0].lower().startswith("graph"):
        formatted.insert(0, "graph TD")

    return "\n".join(formatted)

# -------------------------------------------------
# Sidebar (Menu Bar)
# -------------------------------------------------
st.sidebar.title("Application Menu")

mode = st.sidebar.selectbox(
    "Study Mode",
    [
        "Explain Topic",
        "Summarize Notes",
        "Generate Quiz",
        "Generate Flashcards",
        "Generate Flowchart"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("History")

if not st.session_state.history:
    st.sidebar.caption("No history available")
else:
    for i, item in enumerate(st.session_state.history):
        with st.sidebar.expander(f"{i + 1}. {item['mode']}"):
            st.caption(item["input"][:120])
            if st.button("Open", key=f"open_{i}"):
                st.session_state.selected_history = i

if st.sidebar.button("Clear History"):
    st.session_state.history.clear()
    st.session_state.selected_history = None

# -------------------------------------------------
# Main Header
# -------------------------------------------------
st.title("AI-Powered Study Buddy")
st.caption(
    "Explain concepts, summarize notes, generate quizzes, flashcards, and easy-to-understand flowcharts"
)

# -------------------------------------------------
# Show History Item
# -------------------------------------------------
if st.session_state.selected_history is not None:
    record = st.session_state.history[st.session_state.selected_history]

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

    elif record["mode"] == "Generate Flowchart":
        st.markdown(record["output"], unsafe_allow_html=True)
        st.markdown("### Explanation")
        st.write(record["explanation"])

    else:
        st.write(record["output"])

    st.stop()

# -------------------------------------------------
# New Request
# -------------------------------------------------
st.subheader("New Request")

user_input = st.text_area(
    "Enter study content",
    height=180,
    placeholder="Example: Explain the data analysis lifecycle"
)

# -------------------------------------------------
# Generate Output
# -------------------------------------------------
if st.button("Generate Output"):
    if not user_input.strip():
        st.warning("Input cannot be empty.")
        st.stop()

    # ---------------- PROMPTS ----------------
    if mode == "Explain Topic":
        prompt = f"Explain the following topic clearly for a student:\n{user_input}"

    elif mode == "Summarize Notes":
        prompt = f"Summarize the following notes concisely:\n{user_input}"

    elif mode == "Generate Quiz":
        prompt = f"Create 5 quiz questions with answers:\n{user_input}"

    elif mode == "Generate Flashcards":
        prompt = f"""
        Create exactly 5 study flashcards.
        Format:
        Q: Question
        A: Answer

        Content:
        {user_input}
        """

    else:  # Flowchart
        prompt = f"""
        Convert the following content into a clean flowchart.

        Rules:
        - Use Mermaid flowchart syntax only
        - Start with: graph TD
        - One concept per node
        - Unique node IDs
        - Use --> for main flow
        - Use -.-> for sub-steps
        - No markdown code blocks
        - No explanations

        Content:
        {user_input}
        """

    # ---------------- MODEL CALL ----------------
    with st.spinner("Generating response"):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional academic assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )

        raw_output = response.choices[0].message.content.strip()

        # ---------------- RENDER ----------------
        if mode == "Generate Flashcards":
            cards = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n|$)", raw_output, re.S)

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

        elif mode == "Generate Flowchart":
            cleaned = clean_and_format_mermaid(raw_output)

            st.subheader("Generated Flowchart")
            st.markdown(f"<div class='mermaid'>{cleaned}</div>", unsafe_allow_html=True)

            explanation_prompt = f"""
            Explain the following process in simple, step-by-step language for a beginner:

            {user_input}
            """

            explanation_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You explain technical processes simply."},
                    {"role": "user", "content": explanation_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )

            explanation = explanation_response.choices[0].message.content

            st.subheader("Explanation")
            st.write(explanation)

            st.session_state.history.append({
                "mode": mode,
                "input": user_input,
                "output": f"<div class='mermaid'>{cleaned}</div>",
                "explanation": explanation
            })

        else:
            st.subheader("Result")
            st.write(raw_output)

            st.session_state.history.append({
                "mode": mode,
                "input": user_input,
                "output": raw_output
            })
