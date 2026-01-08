import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="AI Study Buddy", layout="wide")

# Load model once
@st.cache_resource
def load_model():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-base"
    )

model = load_model()

st.title("📘 AI-Powered Study Buddy")
st.write("Explain topics, summarize notes, and generate quizzes.")

text = st.text_area("Enter your topic or notes")

option = st.selectbox(
    "Choose what you want to do",
    ["Explain Simply", "Summarize Notes", "Generate Quiz"]
)

if st.button("Generate"):
    with st.spinner("AI is working..."):
        if option == "Explain Simply":
            prompt = f"Explain in simple terms: {text}"
        elif option == "Summarize Notes":
            prompt = f"Summarize: {text}"
        else:
            prompt = f"Create 5 quiz questions with answers: {text}"

        output = model(prompt, max_length=256)
        st.success("Done!")
        st.write(output[0]["generated_text"])

