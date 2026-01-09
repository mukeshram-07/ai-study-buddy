import streamlit as st
from groq import Groq
import os
import re

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(page_title="AI Study Buddy", layout="wide")

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
# Styling (Theme Safe)
# -------------------------------------------------
st.markdown("""
<style>
.flashcard {
    border: 1px solid rgba(150,150,150,0.25);
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 16px;
    background-color: var(--background-color);
}
.flashcard-title {
    font-weight: 600;
    margin-bottom: 6px;
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
# Mermaid Cleaner & Formatter (CRITICAL FIX)
# -------------------------------------------------
def clean_and_format_mermaid(raw: str) -> str:
    raw = re.sub(r"```mermaid|```", "", raw, flags=re.IGNORECASE).strip()

    # Insert line breaks before arrows
    raw = raw.replace(" --> ", "\n--> ").replace(" -.-> ", "\n-.-> ")

    lines = raw.splitlines()
    formatted = ["graph TD"]

    for line in lines:
        line = line.strip()
        if not line or line.lower().startswith("graph"):
            continue

        # Fix -->|Yes|> mistake
        line = re.sub(r"\|\>\s*", "|", line)

        formatted.append(line)

    return "\n".join(formatted)

# -------------------------------------------------
# Sidebar
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
        with st.sidebar.expander(f"{i+1}. {item['mode']}"):
            st.caption(item["input"][:100])
            if st.button("Open", key=f"h_{i}"):
                st.session_state.selected_history = i

if st.sidebar.button("Clear History"):
    st.session_state.history.clear()
    st.session_state.selected_history = None

# -------------------------------------------------
# Main Header
# -------------------------------------------------
st.title("AI-Powered Study Buddy")
st.caption("Explain concepts, summarize notes, generate quizzes, flashcards, and easy-to-understand flowcharts")

# -------------------------------------------------
# History View
# -------------------------------------------------
if st.session_state.selected_history is not None:
    record = st.session_state.history[st.session_state.selected_history]
    st.subheader("Previous Result")
    st.write(record["output"])
    st.stop()

# -------------------------------------------------
# Input
# -------------------------------------------------
st.subheader("New Request")
user_input = st.text_area("Enter study content", height=160)

# -------------------------------------------------
# Generate
# -------------------------------------------------
if st.button("Generate Output"):
    if not user_input.strip():
        st.warning("Input cannot be empty.")
        st.stop()

    if mode == "Generate Flowchart":
        flow_prompt = f"""
        Convert the following topic into a clean Mermaid flowchart.

        Rules:
        - Start with: graph TD
        - One step per node
        - Use --> for main flow
        - Use -.-> for decision or subflow
        - No explanations

        Topic:
        {user_input}
        """

        flow_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You generate clean technical flowcharts."},
                {"role": "user", "content": flow_prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )

        cleaned_flow = clean_and_format_mermaid(
            flow_response.choices[0].message.content
        )

        st.subheader("Generated Flowchart")
        st.markdown(f"<div class='mermaid'>{cleaned_flow}</div>", unsafe_allow_html=True)

        # ---------- Explanation (FIXED TOKEN LIMIT) ----------
        explanation_prompt = f"""
        Explain the following process in simple, beginner-friendly steps.
        Use numbered steps and complete sentences.

        Topic:
        {user_input}
        """

        explanation_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You explain concepts clearly and fully."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )

        explanation = explanation_response.choices[0].message.content

        st.subheader("Explanation")
        st.write(explanation)

        st.session_state.history.append({
            "mode": mode,
            "input": user_input,
            "output": cleaned_flow + "\n\n" + explanation
        })

    else:
        st.info("Other modes already implemented earlier.")
