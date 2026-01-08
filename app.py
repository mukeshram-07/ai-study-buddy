import streamlit as st
import os
from openai import OpenAI

# Create OpenAI client (NEW METHOD)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="AI Study Buddy", layout="centered")

# Animated background
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #141e30, #243b55);
    background-size: 400% 400%;
    animation: bg 10s ease infinite;
}
@keyframes bg {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}
</style>
""", unsafe_allow_html=True)

# UI
st.title("AI-Powered Study Buddy")
st.write("Explain topics • Summarize notes • Generate quizzes")

option = st.selectbox(
    "Choose an option",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

user_input = st.text_area("Enter your text")

if st.button("Generate"):
    if user_input.strip() == "":
        st.warning("Please enter some text")
    else:
        if option == "Explain Topic":
            prompt = f"Explain this topic in simple student language:\n{user_input}"
        elif option == "Summarize Notes":
            prompt = f"Summarize these notes clearly:\n{user_input}"
        else:
            prompt = f"Create 5 quiz questions with answers from:\n{user_input}"

        with st.spinner("AI is thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

        st.success("Result")
        st.write(response.choices[0].message.content)
