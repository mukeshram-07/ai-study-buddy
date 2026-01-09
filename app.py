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
# Styling (Theme-aware + Option-2 Timeline)
# -------------------------------------------------
st.markdown("""
<style>
.flashcard {
    border: 1px solid rgba(150,150,150,0.25);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
    background-color: var(--background-color);
}
.flashcard-q {
    font-weight: 600;
    margin-bottom: 6px;
}
.mermaid {
    background-color: var(--background-color);
    border: 1px solid rgba(150,150,150,0.25);
    border-radius: 8px;
    padding: 16px;
}

/* Option-2 Step Timeline */
.timeline {
    position: relative;
    margin-left: 20px;
    padding-left: 20px;
}
.timeline::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 2px;
    height: 100%;
    background-color: rgba(150,150,150,0.4);
}
.step {
    position: relative;
    padding: 10px 12px;
    margin-bottom: 14px;
    border-radius: 6px;
    background-color: var(--background-color);
    border: 1px solid rgba(150,150,150,0.25);
}
.step::before {
    content: "";
    position: absolute;
    left: -26px;
    top: 16px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: rgba(150,150,150,0.9);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def parse_flashcards(text):
    cards = re.findall(
        r"Q\s*[:\-]\s*(.*?)\nA\s*[:\-]\s*(.*?)(?=\nQ|\Z)",
        text, re.S | re.I
    )
    if cards:
        return [(q.strip(), a.strip()) for q, a in cards]

    fallback = re.findall(
        r"\d+[\).\s]+(.*?)\n.*?Answer\s*[:\-]\s*(.*?)(?=\n\d+|\Z)",
        text, re.S | re.I
    )
    if fallback:
        return [(q.strip(), a.strip()) for q, a in fallback]

    parts = [p.strip() for p in text.split("\n") if p.strip()]
    return [(parts[i], parts[i+1]) for i in range(0, len(parts)-1, 2)]

def clean_mermaid(raw):
    raw = re.sub(r"```mermaid|```", "", raw, flags=re.IGNORECASE).strip()
    raw = raw.replace(" --> ", "\n--> ").replace(" -.-> ", "\n-.-> ")
    lines = ["graph TD"]
    for line in raw.splitlines():
        line = line.strip()
        if line and not line.lower().startswith("graph"):
            lines.append(line)
    return "\n".join(lines)

def extract_steps(mermaid):
    steps, seen = [], set()
    for line in mermaid.splitlines():
        if "-->" in line and "-.->" not in line:
            labels = re.findall(r"\[(.*?)\]", line)
            for lbl in labels:
                if lbl not in seen:
                    steps.append(lbl)
                    seen.add(lbl)
    return steps

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

if st.session_state.history:
    for i, item in enumerate(st.session_state.history):
        with st.sidebar.expander(f"{i+1}. {item['mode']}"):
            st.caption(item["input"][:100])
            if st.button("Open", key=f"h{i}"):
                st.session_state.selected_history = i
else:
    st.sidebar.caption("No history available")

if st.sidebar.button("Clear History"):
    st.session_state.history.clear()
    st.session_state.selected_history = None

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("AI-Powered Study Buddy")
st.caption("Explain topics, summarize notes, generate quizzes, flashcards, and structured flowcharts")

# -------------------------------------------------
# History View
# -------------------------------------------------
if st.session_state.selected_history is not None:
    rec = st.session_state.history[st.session_state.selected_history]
    st.subheader("Previous Result")
    st.write(rec["output"])
    st.stop()

# -------------------------------------------------
# Input
# -------------------------------------------------
user_input = st.text_area("Enter study content", height=160)

# -------------------------------------------------
# Generate Output
# -------------------------------------------------
if st.button("Generate Output"):
    if not user_input.strip():
        st.warning("Input cannot be empty.")
        st.stop()

    # -------- PROMPTS --------
    if mode == "Explain Topic":
        prompt = f"Explain the following topic clearly with examples:\n{user_input}"
        max_tokens = 900

    elif mode == "Summarize Notes":
        prompt = f"Summarize the following notes in clear bullet points:\n{user_input}"
        max_tokens = 700

    elif mode == "Generate Quiz":
        prompt = f"""
        Create exactly 5 quiz questions WITH answers.
        The quiz must be strictly based on this topic only.

        Topic: "{user_input}"
        """
        max_tokens = 800

    elif mode == "Generate Flashcards":
        prompt = f"""
        Create exactly 5 flashcards.

        Format strictly as:
        Q: Question
        A: Answer

        Topic: "{user_input}"
        """
        max_tokens = 800

    else:  # Flowchart
        prompt = f"""
        Convert the topic into a Mermaid flowchart.
        Use --> for main steps and -.-> for optional or method steps.
        Start with graph TD.
        Topic: {user_input}
        """
        max_tokens = 700

    # -------- MODEL CALL --------
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=max_tokens
    )

    output = response.choices[0].message.content

    # -------- RENDER --------
    if mode == "Generate Flashcards":
        cards = parse_flashcards(output)
        st.subheader("Flashcards")
        for q, a in cards:
            st.markdown(f"""
            <div class="flashcard">
                <div class="flashcard-q">Q: {q}</div>
                <div>A: {a}</div>
            </div>
            """, unsafe_allow_html=True)
        final_output = cards

    elif mode == "Generate Flowchart":
        flow = clean_mermaid(output)
        st.subheader("Visual Flowchart")
        st.markdown(f"<div class='mermaid'>{flow}</div>", unsafe_allow_html=True)

        steps = extract_steps(flow)
        st.subheader("Step-by-Step Flow")
        timeline = "<div class='timeline'>"
        for i, step in enumerate(steps, 1):
            timeline += f"<div class='step'><strong>{i}. {step}</strong></div>"
        timeline += "</div>"
        st.markdown(timeline, unsafe_allow_html=True)

        explanation_prompt = f"""
        Explain the following process in simple numbered steps for beginners:
        {user_input}
        """

        exp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": explanation_prompt}],
            temperature=0.3,
            max_tokens=900
        )

        st.subheader("Explanation")
        st.write(exp.choices[0].message.content)

        final_output = flow

    else:
        st.write(output)
        final_output = output

    # -------- SAVE HISTORY --------
    st.session_state.history.append({
        "mode": mode,
        "input": user_input,
        "output": final_output
    })
