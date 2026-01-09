import streamlit as st
from groq import Groq
import os
import re

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="AI Study Buddy", layout="wide")

# -----------------------------
# Load API Key
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not configured.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# Helper: Clean Mermaid
# -----------------------------
def clean_mermaid(raw: str) -> str:
    raw = re.sub(r"```mermaid|```", "", raw, flags=re.IGNORECASE).strip()
    raw = raw.replace(" --> ", "\n--> ").replace(" -.-> ", "\n-.-> ")
    lines = ["graph TD"]

    for line in raw.splitlines():
        line = line.strip()
        if line and not line.lower().startswith("graph"):
            lines.append(line)

    return "\n".join(lines)

# -----------------------------
# Helper: Extract Main Steps
# -----------------------------
def extract_main_steps(mermaid_code: str):
    """
    Extracts only the MAIN --> flow (ignores -.-> branches)
    """
    steps = []
    seen = set()

    for line in mermaid_code.splitlines():
        if "-->" in line and "-.->" not in line:
            parts = line.split("-->")
            left = parts[0].strip()
            right = parts[1].strip()

            left_label = re.findall(r"\[(.*?)\]", left)
            right_label = re.findall(r"\[(.*?)\]", right)

            if left_label and left_label[0] not in seen:
                steps.append(left_label[0])
                seen.add(left_label[0])

            if right_label and right_label[0] not in seen:
                steps.append(right_label[0])
                seen.add(right_label[0])

    return steps

# -----------------------------
# UI
# -----------------------------
st.title("AI-Powered Study Buddy")
st.caption("Flowcharts with simple, user-friendly step view")

user_input = st.text_area(
    "Enter topic",
    height=150,
    placeholder="Example: Data science process"
)

# -----------------------------
# Generate Flowchart
# -----------------------------
if st.button("Generate Flowchart"):
    prompt = f"""
    Convert the following topic into a Mermaid flowchart.

    Rules:
    - Start with graph TD
    - Use --> for main steps
    - Use -.-> for optional or method branches
    - One concept per node
    - No explanations

    Topic:
    {user_input}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You generate clean technical flowcharts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=600
    )

    raw_flow = response.choices[0].message.content
    cleaned_flow = clean_mermaid(raw_flow)

    # -------- Visual Flowchart --------
    st.subheader("Visual Flowchart")
    st.markdown(f"<div class='mermaid'>{cleaned_flow}</div>", unsafe_allow_html=True)

    # -------- Step-by-Step View --------
    steps = extract_main_steps(cleaned_flow)

    st.subheader("Step-by-Step Flow (Easy to Understand)")

    for i, step in enumerate(steps, 1):
        st.markdown(f"**{i}. {step}**")
        if i < len(steps):
            st.markdown("⬇️")
