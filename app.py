st.markdown("""
<style>

/* IMPORTANT: Target Streamlit root */
.stApp {
    background: linear-gradient(-45deg, #141e30, #243b55, #1f4037, #99f2c8);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

/* Gradient animation */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Remove default white blocks */
section[data-testid="stSidebar"] {
    background: transparent;
}

/* Glass effect main container */
.block-container {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 2rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 25px;
    padding: 0.6rem 1.8rem;
    border: none;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 8px 20px rgba(0,0,0,0.3);
}

/* Inputs */
textarea, select {
    border-radius: 12px !important;
}

/* Alerts */
.stAlert {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)
