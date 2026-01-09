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
# Styling (Theme-aware + Step Timeline)
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

.flashcard-title {
    font-weight: 600;
    margin-bottom: 6px;
}

.mermaid {
    background-color: var(--background-color);
    border: 1px solid rgba(150,150,150,0.25);
    border-radius: 8px;
    padding: 16px;
}

/* Step timeline */
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
# Mermaid Cleaner
# -------------------------------------------------
def clean_mermaid(raw: str) -> str:
    raw = re.sub(r"```mermaid|```", "", raw, flags=re.IGNORECASE).strip()
    raw = raw.replace(" --> ", "\n--> ").replace(" -.-> ", "\n-.-> ")
    lines = ["graph TD"]

    for line in raw.splitlines():
        line = line.strip()
        if line and not line.lower().startswith("graph"):
            line = re.sub(r"\|\>\s*", "|", line)
            lines.append(line)

    return "\n".join(lines)

# -------------------------------------------------
# Extract Main Steps
# -------------------------------------------------
def extract_steps(mermaid_code: str):
    steps = []
    seen = set()

    for line in mermaid_code.splitlines():
        if "-->" in line and "-.->" not in line:
            parts = line.split("-->")
            for part in parts:
                labels = re.findall(r"\[(.*?)\]", part)
                for lbl in labels:
                    if lbl not in seen:
                        steps.append(lbl)
                        seen.add(lbl)

    return steps

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
st.caption("Explain concepts, summarize notes, generate quizzes, flashcards, and structured flowcharts")

# -------------------------------------------------
# History View
# -------------------------------------------------
if st.session_state.selected_history is not None:
    record = st.session_state.history[st.session_state.selected_history]

    st.subheader("Previous Result")
    st.markdown(f"**Mode:** {record['mode']}")
    st.markdown(f"**Input:** {record['input']}")
    st.divider()

    if record["mode"] == "Generate Flowchart":
        st.markdown(record["flowchart"], unsafe_allow_html=True)
        st.subheader("Step-by-Step Flow")
        st.markdown(record["steps"], unsafe_allow_html=True)
        st.subheader("Explanation")
        st.write(record["explanation"])

    elif record["mode"] == "Generate Flashcards":
        for q, a in record["output"]:
            st.markdown(f"""
            <div class="flashcard">
                <div class="flashcard-title">{q}</div>
                <div>{a}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write(record["output"])

    st.stop()

# -------------------------------------------------
# New Request
# -------------------------------------------------
st.subheader("New Request")

user_input = st.text_area(
    "Enter study content",
    height=170,
    placeholder="Example: Data science lifecycle"
)

# -------------------------------------------------
# Generate Output
# -------------------------------------------------
if st.button("Generate Output"):
    if not user_input.strip():
        st.warning("Input cannot be empty.")
        st.stop()

    if mode == "Generate Flowchart":
        flow_prompt = f"""
        Convert the following topic into a clean Mermaid flowchart.

        Rules:
        - Start with graph TD
        - Use --> for main steps
        - Use -.-> for optional methods
        - One concept per node
        - No explanations

        Topic:
        {user_input}
        """

        flow_res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You generate clean flowcharts."},
                {"role": "user", "content": flow_prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )

        cleaned_flow = clean_mermaid(flow_res.choices[0].message.content)

        st.subheader("Visual Flowchart")
        st.markdown(f"<div class='mermaid'>{cleaned_flow}</div>", unsafe_allow_html=True)

        steps = extract_steps(cleaned_flow)

        st.subheader("Step-by-Step Flow (Easy to Understand)")
        timeline_html = "<div class='timeline'>"
        for i, step in enumerate(steps, 1):
            timeline_html += f"<div class='step'><strong>{i}. {step}</strong></div>"
        timeline_html += "</div>"

        st.markdown(timeline_html, unsafe_allow_html=True)

        explanation_prompt = f"""
        Explain the following process in simple, numbered steps for a beginner:

        {user_input}
        """

        exp_res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You explain processes simply."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )

        explanation = exp_res.choices[0].message.content
        st.subheader("Explanation")
        st.write(explanation)

        st.session_state.history.append({
            "mode": mode,
            "input": user_input,
            "flowchart": f"<div class='mermaid'>{cleaned_flow}</div>",
            "steps": timeline_html,
            "explanation": explanation
        })

    elif mode == "Generate Flashcards":
        prompt = f"Create 5 flashcards.\nQ and A format.\n{user_input}"
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400
        )

        cards = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n|$)", res.choices[0].message.content, re.S)
        for q, a in cards:
            st.markdown(f"""
            <div class="flashcard">
                <div class="flashcard-title">{q.strip()}</div>
                <div>{a.strip()}</div>
            </div>
            """, unsafe_allow_html=True)

        st.session_state.history.append({
            "mode": mode,
            "input": user_input,
            "output": [(q.strip(), a.strip()) for q, a in cards]
        })

    else:
        prompt = user_input
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        st.write(res.choices[0].message.content)

        st.session_state.history.append({
            "mode": mode,
            "input": user_input,
            "output": res.choices[0].message.content
        })
