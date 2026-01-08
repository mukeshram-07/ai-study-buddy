import streamlit as st
from openai import OpenAI

client = OpenAI()

st.set_page_config(page_title="AI Study Buddy", layout="centered")
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
            prompt = f"Explain the following topic in simple student-friendly language:\n{text}"
        elif option == "Summarize Notes":
            prompt = f"Summarize the following notes in bullet points:\n{text}"
        else:
            prompt = f"Create 5 MCQs with answers from the following content:\n{text}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.success("Done!")
        st.write(response.choices[0].message.content)
