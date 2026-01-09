import streamlit as st
from groq import Groq
import os
import re
import json
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
.keypoint {
    border-left: 4px solid rgba(100,100,255,0.6);
    padding: 8px 12px;
    margin-bottom: 8px;
    background-color: var(--background-color);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def fetch_images(topic, count=4):
    if not pexels_key:
        return []
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": pexels_key}
    params = {"query": topic, "per_page": count}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=5)
        data = r.json()
        return [p["src"]["medium"] for p in data.get("photos", [])]
    except Exception:
        return []

def show_images(topic):
    images = fetch_images(topic)
    if not images:
        return
    st.subheader("Related Visuals")
    cols = st.columns(len(images))
    for c, img in zip(cols, images):
        c.image(img, use_container_width=True)

def clean_mermaid(raw):
    raw = re.sub(r"```mermaid|```", "", raw, flags=re.I).strip()
    raw = raw.replace(" --> ", "\n--> ").replace(" -.-> ", "\n-.-> ")
    lines = ["graph TD"]
    for l in raw.splitlines():
        if l and not l.lower().startswith("graph"):
            lines.append(l.strip())
    return "\n".join(lines)

def extract_steps(mermaid):
    steps, seen = [], set()
    for line in mermaid.splitlines():
        if "-->" in line and "-.->" not in line:
            for lbl in re.findall(r"\[(.*?)\]", line):
                if lbl not in seen:
                    steps.append(lbl)
                    seen.add(lbl)
    return steps

def parse_flashcards_json(text):
    try:
        return json.loads(text)
    except Exception:
        return []

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
        "Generate Flowchart",
        "Exam Quick Revision"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("History")

if st.session_state.history:
    for i, h in enumerate(st.session_state.history):
        with st.sidebar.expander(f"{i+1}. {h['mode']}"):
            st.caption(h["input"][:100])
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
st.caption("Learning, revision, and exam preparation in one place")

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

    # ---------- Explain Topic ----------
    if mode == "Explain Topic":
        prompt = f"Explain the following topic clearly with examples:\n{user_input}"
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=900
        )
        output = res.choices[0].message.content
        st.subheader("Explanation")
        st.write(output)
        show_images(user_input)

    # ---------- Summarize ----------
    elif mode == "Summarize Notes":
        prompt = f"Summarize the following notes in bullet points:\n{user_input}"
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700
        )
        output = res.choices[0].message.content
        st.write(output)

    # ---------- Quiz ----------
    elif mode == "Generate Quiz":
        prompt = f"""
        Create exactly 5 quiz questions WITH answers.
        Strictly based on the topic: "{user_input}"
        """
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        output = res.choices[0].message.content
        st.write(output)

    # ---------- Flashcards ----------
    elif mode == "Generate Flashcards":
        prompt = f"""
        Generate exactly 5 flashcards.
        Return ONLY JSON:
        [
          {{ "question": "...", "answer": "..." }}
        ]
        Topic: "{user_input}"
        """
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=700
        )
        cards = parse_flashcards_json(res.choices[0].message.content)
        st.subheader("Flashcards")
        for i, c in enumerate(cards, 1):
            st.markdown(f"""
            <div class="flashcard">
                <div class="flashcard-q">Q{i}. {c["question"]}</div>
                <div>A: {c["answer"]}</div>
            </div>
            """, unsafe_allow_html=True)
        output = cards

    # ---------- Flowchart ----------
    elif mode == "Generate Flowchart":
        prompt = f"""
        Convert the topic into a Mermaid flowchart.
        Use --> for main steps and -.-> for optional steps.
        Start with graph TD.
        Topic: {user_input}
        """
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700
        )
        flow = clean_mermaid(res.choices[0].message.content)
        st.subheader("Visual Flowchart")
        st.markdown(f"<div class='mermaid'>{flow}</div>", unsafe_allow_html=True)

        steps = extract_steps(flow)
        st.subheader("Step-by-Step Flow")
        timeline = "<div class='timeline'>"
        for i, s in enumerate(steps, 1):
            timeline += f"<div class='step'><strong>{i}. {s}</strong></div>"
        timeline += "</div>"
        st.markdown(timeline, unsafe_allow_html=True)

        exp_prompt = f"Explain this process in simple numbered steps:\n{user_input}"
        exp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": exp_prompt}],
            temperature=0.3,
            max_tokens=900
        )
        st.subheader("Explanation")
        st.write(exp.choices[0].message.content)
        show_images(user_input + " diagram")
        output = flow

    # ---------- Exam Quick Revision ----------
    else:
        prompt = f"""
        Generate 10 high-yield exam key points for the topic below.
        Rules:
        - One line per point
        - Very short
        - No explanations
        - Exam-oriented language

        Topic: "{user_input}"
        """
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400
        )
        points = res.choices[0].message.content.split("\n")
        st.subheader("Exam Quick Revision – Key Points")
        for p in points:
            if p.strip():
                st.markdown(f"<div class='keypoint'>{p}</div>", unsafe_allow_html=True)
        output = points

    # ---------- Save History ----------
    st.session_state.history.append({
        "mode": mode,
        "input": user_input,
        "output": output
    })
