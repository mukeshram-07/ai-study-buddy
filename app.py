import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="AI Study Buddy", layout="wide")

@st.cache_resource
def load_model():
    return pipeline(
        "text2text-generation",
        model="study_buddy_model"
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
            prompt = f"Explain the following topic in simple terms for a student:\n{text}"

        elif option == "Summarize Notes":
            prompt = f"Summarize the following content in clear, simple sentences:\n{text}"

        else:
            prompt = f"Create 5 quiz questions with answers from the following content:\n{text}"

        output = model(
            prompt,
            max_length=200,
            min_length=30,
            num_beams=4,
            repetition_penalty=2.0,
            early_stopping=True
        )

        st.success("Done!")
        st.write(output[0]["generated_text"])
