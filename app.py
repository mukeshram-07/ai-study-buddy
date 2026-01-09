import streamlit as st
from groq import Groq
import os
import re

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    layout="centered"
)

# -----------------------------
# Session State Initialization
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "selected_history" not in st.session_state:
    st.session_state.selected_history = None

# -----------------------------
# Basic Styling
# -----------------------------
st.markdown("""
<style>
.flashcard {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 14px;
    background-color: #ffffff;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.05);
}
.flashcard h4 {
    color: #1e3c72;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar - History Menu
# -----------------------------
st.sidebar.title("📚 History")

if not st.session_state.history:
    st.sidebar.info("No history yet.")
else:
    for idx, item in enumerate(st.session_state.history):
        label = f"{idx + 1}. {item['mode']}"
        if st.sidebar.button(label, key=f"hist_{idx}"):
            st.session_state.selected_history = idx

st.sidebar.divider()
if st.sidebar.button("🗑️ Clear History"):
    st.session_state.history.clear()
    st.session_state.selected_history = None

# -----------------------------
# Load API Key
# -----------------------------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# Main UI
# -----------------------------
st.title("AI-Powered Study Buddy")
st.caption("Explain • Summarize • Quiz • Flashcards")

option = st.selectbox(
    "Select a learning mode",
    [
        "Explain Topic",
        "Summarize Notes",
        "Generate Quiz",
        "Generate Flashcards"
    ]
)

text = st.text_area(
    "Enter your study content",
    height=170,
    placeholder="Example: Artificial Intelligence"
)

# -----------------------------
# Show Selected History
# -----------------------------
if st.session_state.selected_history is not None:
    item = st.session_state.history[st.session_state.selected_history]
    st.subheader("📖 History Preview")
    st.markdown(f"**Mode:** {item['mode']}")
    st.markdown(f"**Input:** {item['input']}")
    st.divider()

    if item["mode"] == "Generate Flashcards":
        for i, (q, a) in enumerate(item["output"], 1):
            st.markdown(f"""
            <div class="flashcard">
                <h4>Flashcard {i}</h4>
                <p><strong>Q:</strong> {q}</p>
                <p><strong>A:</strong> {a}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write(item["output"])

    st.stop()

# -----------------------------
# Generate Button
# -----------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some content.")
        st.stop()

    if option == "Generate Flashcards":
        prompt = f"""
        Create exactly 5 study flashcards.
        Format:
        Q: Question
        A: Answer

        Content:
        {text}
        """
    elif option == "Explain Topic":
        prompt = f"Explain this topic clearly for a student:\n{text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize the following notes:\n{text}"
    else:
        prompt = f"Create 5 quiz questions with answers:\n{text}"

    with st.spinner("Generating..."):
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

            result = response.choices[0].message.content

            # -----------------------------
            # Flashcard Handling
            # -----------------------------
            if option == "Generate Flashcards":
                cards = re.findall(r"Q:\s*(.*?)\nA:\s*(.*?)(?:\n|$)", result, re.S)

                if not cards:
                    st.warning("Could not format flashcards.")
                else:
                    st.subheader("Flashcards")
                    for i, (q, a) in enumerate(cards, 1):
                        st.markdown(f"""
                        <div class="flashcard">
                            <h4>Flashcard {i}</h4>
                            <p><strong>Q:</strong> {q.strip()}</p>
                            <p><strong>A:</strong> {a.strip()}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.session_state.history.append({
                        "mode": option,
                        "input": text,
                        "output": [(q.strip(), a.strip()) for q, a in cards]
                    })
            else:
                st.success("Result")
                st.write(result)

                st.session_state.history.append({
                    "mode": option,
                    "input": text,
                    "output": result
                })

        except Exception as e:
            st.error("Groq API Error")
            st.code(str(e))
