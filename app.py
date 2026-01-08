import streamlit as st
import requests
import os
import time

# ---------------------------------
# Hugging Face Router API details
# ---------------------------------
MODEL_ID = "google/flan-t5-base"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}",
    "Content-Type": "application/json"
}

# ---------------------------------
# Page configuration
# ---------------------------------
st.set_page_config(
    page_title="AI-Powered Study Buddy",
    layout="centered"
)

# ---------------------------------
# Animated background
# ---------------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(-45deg, #141e30, #243b55);
    background-size: 400% 400%;
    animation: gradientBG 10s ease infinite;
}
@keyframes gradientBG {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# UI
# ---------------------------------
st.title("🤖 AI-Powered Study Buddy")
st.write("Explain topics • Summarize notes • Generate quizzes")

option = st.selectbox(
    "Choose a feature",
    ["Explain Topic", "Summarize Notes", "Generate Quiz"]
)

text = st.text_area(
    "Enter your content",
    height=180,
    placeholder="Example: What is Artificial Intelligence?"
)

# ---------------------------------
# Button action
# ---------------------------------
if st.button("Generate"):
    if not text.strip():
        st.warning("Please enter some text.")
        st.stop()

    if len(text) > 800:
        st.warning("Please limit input to 800 characters.")
        st.stop()

    # Prompt preparation
    if option == "Explain Topic":
        prompt = f"Explain in simple words: {text}"
    elif option == "Summarize Notes":
        prompt = f"Summarize clearly: {text}"
    else:
        prompt = f"Create 5 quiz questions with answers: {text}"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.5
        }
    }

    with st.spinner("Generating response..."):
        try:
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json=payload,
                timeout=30
            )

            result = response.json()

            # SUCCESS CASE
            if isinstance(result, list) and "generated_text" in result[0]:
                st.success("Result")
                st.write(result[0]["generated_text"])

            # MODEL LOADING CASE
            elif isinstance(result, dict) and "error" in result:
                if "loading" in result["error"].lower():
                    st.warning("Model is warming up. Please click Generate again.")
                else:
                    st.error("AI error: " + result["error"])

            else:
                st.error("Unexpected AI response format.")

        except Exception as e:
            st.error("AI service unreachable. Please try again later.")
