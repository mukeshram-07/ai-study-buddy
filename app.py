import streamlit as st
from groq import Groq
import os
import re

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="AI Study Buddy – Flowchart Generator",
    layout="wide"
)

# -------------------------------------------------
# Load API Key
# -------------------------------------------------
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY not configured.")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------------------------------
# Styling (Professional, Theme Aware)
# -------------------------------------------------
st.markdown("""
<style>
.mermaid {
    background-color: var(--background-color);
    color: var(--text-color);
    border-radius: 8px;
    padding: 18px;
    border: 1px solid rgba(150,150,150,0.25);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Helper: Clean & Format Mermaid
# -------------------------------------------------
def clean_and_format_mermaid(raw: str) -> str:
    # Remove markdown fences
    raw = re.sub(r"```mermaid|```", "", raw, flags=re.IGNORECASE).strip()

    lines = raw.splitlines()
    formatted = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Fix invalid arrow labels like -->|Data|>
        line = re.sub(r"\|\>\s*", "|", line)

        # Normalize arrows
        line = re.sub(r"\s*-->\s*", " --> ", line)
        line = re.sub(r"\s*-\.\->\s*", " -.-> ", line)

        formatted.append(line)

    # Ensure graph TD exists
    if not formatted or not formatted[0].lower().startswith("graph"):
        formatted.insert(0, "graph TD")

    return "\n".join(formatted)

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("AI-Powered Flowchart Generator")
st.caption("Convert any concept, process, or system into a clean, formatted flowchart")

user_input = st.text_area(
    "Enter topic or process description",
    height=180,
    placeholder="Example: Explain the software development life cycle"
)

# -------------------------------------------------
# Generate Flowchart
# -------------------------------------------------
if st.button("Generate Flowchart"):
    if not user_input.strip():
        st.warning("Input cannot be empty.")
        st.stop()

    prompt = f"""
    Convert the following content into a clear, well-formatted flowchart.

    Strict rules:
    - Use Mermaid flowchart syntax only
    - Start with: graph TD
    - One concept per node
    - Short, readable node labels
    - Unique node IDs
    - Use --> for main flow
    - Use -.-> for control or decision flow
    - Do NOT use markdown code blocks
    - Do NOT add explanations or text

    Content:
    {user_input}
    """

    with st.spinner("Generating formatted flowchart"):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional system design assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            raw_output = response.choices[0].message.content
            cleaned_mermaid = clean_and_format_mermaid(raw_output)

            st.subheader("Generated Flowchart")
            st.markdown(
                f"<div class='mermaid'>{cleaned_mermaid}</div>",
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error("Flowchart generation failed.")
            st.code(str(e))
