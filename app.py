import streamlit as st
from io import BytesIO
import time

MODEL_LOADED = False

st.set_page_config(
    page_title="⚡Turbo-Study AI✨",
    page_icon="📚",
    layout="wide"
)

# ---------- ULTRA AESTHETIC CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Share+Tech+Mono&display=swap');

body {
    margin:0;
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #e6edf3;
    font-family: 'Roboto', sans-serif;
    overflow-x: hidden;
}

/* Hero Section */
.hero {
    padding: 30px;
    text-align: center;
    border-radius: 30px;
    background: linear-gradient(120deg, rgba(255,200,124,0.15), rgba(180,200,255,0.08));
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    animation: pulse 3s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 10px rgba(255,255,255,0.1);}
    50% { box-shadow: 0 0 30px rgba(255,255,255,0.3);}
    100% { box-shadow: 0 0 10px rgba(255,255,255,0.1);}
}

/* Cards */
.card {
    backdrop-filter: blur(12px);
    background: rgba(255,255,255,0.05);
    border-radius: 25px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    border: 1px solid rgba(255,255,255,0.12);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 60px rgba(255,255,255,0.3);
}

/* Floating Greek Gods icons */
.floating-icon {
    position: absolute;
    width: 50px;
    opacity: 0.15;
    animation: floaty 15s infinite;
}
@keyframes floaty {
    0% { transform: translateY(0px);}
    50% { transform: translateY(-20px);}
    100% { transform: translateY(0px);}
}

/* Thunder animations */
.thunder {
    position: absolute;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: repeating-linear-gradient(
        rgba(255,255,255,0.03),
        rgba(255,255,255,0.03) 1px,
        transparent 1px,
        transparent 2px
    );
    animation: lightning 0.2s infinite;
    mix-blend-mode: lighten;
}
@keyframes lightning {
    0%, 80%, 100% { opacity: 0;}
    81%, 82% { opacity: 1;}
}

/* Footer */
.vignette {
    font-style: italic;
    color: #ffd9a8;
    font-weight:600;
    text-align: center;
    margin-top: 20px;
}

/* Fonts */
h1,h2,h3,h4 { font-family: 'Share Tech Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Greek_Vase_Muse.svg/128px-Greek_Vase_Muse.svg.png")
    st.title("⚡ Turbo-Study AI ✨")
    backend = st.radio("Backend", ("Local (free)", "OpenAI"))
    openai_key = None
    if backend == "OpenAI":
        openai_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("---")
    st.checkbox("Enable Mythic Mode 🏛️", value=True, key="mythic")

# ---------- Floating Greek Gods Icons ----------
st.markdown("""
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Greek_Vase_Muse.svg/64px-Greek_Vase_Muse.svg.png" class="floating-icon" style="top:50px; left:20px;">
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Greek_Vase_Muse.svg/64px-Greek_Vase_Muse.svg.png" class="floating-icon" style="top:200px; right:50px;">
<div class="thunder"></div>
""", unsafe_allow_html=True)

# ---------- Helper Functions ----------
def mythic_prefix(text):
    if st.session_state.get("mythic", True):
        return "Hermes whispers: " + text
    return text

# (Use the same ensure_models, call_generate, read_uploaded functions as before)
# ...

# ---------- Hero ----------
st.markdown('<div class="hero card"><h1>⚡ Turbo-Study AI ✨</h1><div class="small">Summaries • Flashcards • Quizzes • Explanations</div></div>', unsafe_allow_html=True)

# ---------- Tabs ----------
tabs = st.tabs(["Notes", "Summarize", "Explain", "Flashcards", "Quiz"])

# Tabs code same as previous app.py but wrap outputs in:
# st.markdown(f'<div class="card">{output}</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown('<div class="vignette">Hermes says: Study like a god ⚡📚</div>', unsafe_allow_html=True)
