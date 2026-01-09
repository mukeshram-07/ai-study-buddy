import streamlit as st
from groq import Groq
import os
import re
import requests

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

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "home"   # home | history

# -------------------------------------------------
# Load API Keys
# -------------------------------------------------
groq_key = os.getenv("GROQ_API_KEY")
pexels_key = os.getenv("PEXELS_API_KEY")

if not groq_key:
    st.error("GROQ_API_KEY not configured.")
    st.stop()

client = Groq(api_key=groq_key)

# -------------------------------------------------
# Styling
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
# Helper Functions
# -------------------------------------------------
def fetch_images_pexels(topic, count=4):
    if not pexels_key:
        return []
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": pexels_key}
    params = {"query": topic, "per_page": count}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        data = r.json()
        return [photo["src"]["medium"] for photo in data.get("photos", [])]
    except Exception:
        return []

def show_images(topic):
    images = fetch_images_pexels(topic)
    if images:
        st.subheader("Related Visuals")
        cols = st.columns(len(images))
        for col, img in zip(cols, images):
            col.image(img, use_container_width=True)

def parse_flashcards(text):
    cards = re.findall(r"Q\s*:\s*(.*?)\nA\s*:\s*(.*?)(?=\nQ|\Z)", text, re.S)
    if cards:
        return cards
    lines = [l for l in text.split("\n") if l.strip()]
    return [(lines[i], lines[i+1]) for i in range(0, len(lines)-1, 2)]

def clean_mermaid(raw):
    raw = re.sub(r"```mermaid|```", "", raw, flags=re.IGNORECASE)
    raw = raw.replace(" --> ", "\n--> ").replace(" -.-> ", "\n-.-> ")
    lines = ["graph TD"]
    for line in raw.splitlines():
        if line and not line.lower().startswith("graph"):
            lines.append(line.strip())
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
    ["Explain Topic", "Summarize Notes", "Generate Quiz", "Generate Flashcards", "Generate Flowchart"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("History")

for i, h in enumerate(st.session_state.history):
    with st.sidebar.expander(f"{i+1}. {h['mode']}"):
        st.caption(h["input"][:100])
        if st.button("Open", key=f"h{i}"):
            st.session_state.selected_history = i
            st.session_state.view_mode = "history"

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("AI-Powered Study Buddy")
st.caption("Explain topics, summarize notes, generate quizzes, flashcards, flowcharts, and related visuals")

# -------------------------------------------------
# HISTORY VIEW (FIXED)
# -------------------------------------------------
if st.session_state.view_mode == "history":
    rec = st.session_state.history[st.session_state.selected_history]

    st.subheader("Previous Result")
    st.markdown(f"**Mode:** {rec['mode']}")
    st.markdown(f"**Input:** {rec['input']}")
    st.divider()
    st.write(rec["output"])

    if st.button("Back to Home"):
        st.session_state.view_mode = "home"
        st.session_state.selected_history = None

    st.stop()

# -------------------------------------------------
# HOME VIEW
# -------------------------------------------------
user_input = st.text_area("Enter study content", height=160)

if st.button("Generate Output"):
    if not user_input.strip():
        st.warning("Input cannot be empty.")
        st.stop()

    if mode == "Explain Topic":
        prompt = f"Explain the following topic clearly with examples:\n{user_input}"
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=900
        )
        output = res.choices[0].message.content
        st.write(output)
        show_images(user_input)

    elif mode == "Summarize Notes":
        prompt = f"Summarize the following notes:\n{user_input}"
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700
        )
        output = res.choices[0].message.content
        st.write(output)

    elif mode == "Generate Quiz":
        prompt = f"Create 5 quiz questions with answers strictly about: {user_input}"
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        output = res.choices[0].message.content
        st.write(output)

    elif mode == "Generate Flashcards":
        prompt = f"Create 5 flashcards in Q/A format on: {user_input}"
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        cards = parse_flashcards(res.choices[0].message.content)
        for q, a in cards:
            st.markdown(f"<div class='flashcard'><b>Q:</b> {q}<br><b>A:</b> {a}</div>", unsafe_allow_html=True)
        output = cards

    else:
        prompt = f"Create a Mermaid flowchart for: {user_input}"
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700
        )
        flow = clean_mermaid(res.choices[0].message.content)
        st.markdown(f"<div class='mermaid'>{flow}</div>", unsafe_allow_html=True)
        steps = extract_steps(flow)
        for i, s in enumerate(steps, 1):
            st.write(f"{i}. {s}")
        output = flow

    st.session_state.history.append({
        "mode": mode,
        "input": user_input,
        "output": output
    })
