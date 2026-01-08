import streamlit as st
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Study Buddy", layout="centered")

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

st.title("AI-Powered Study Buddy")
st.write("Explain • Summarize • Quiz")

choice = st.selectbox(
    "Select option",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area("Enter text")

if st.button("Generate"):
    if text:
        if choice == "Explain Topic":
            prompt = f"Explain simply: {text}"
        elif choice == "Summarize Notes":
            prompt = f"Summarize: {text}"
        else:
            prompt = f"Create 5 quiz questions with answers: {text}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        st.success("Result")
        st.write(response.choices[0].message["content"])
    else:
        st.warning("Enter some text")
