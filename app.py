import streamlit as st
from pathlib import Path
import time
from io import BytesIO, StringIO

MODEL_LOADED = False

# ---------- Page config ----------
st.set_page_config(
    page_title="Turbo-Study AI ✨",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- STYLES (AESTHETIC + GLASS + MYTHIC) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Share+Tech+Mono&display=swap');

body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #e6edf3;
    font-family: 'Roboto', sans-serif;
}
h1, h2, h3, h4 {
    font-family: 'Share Tech Mono', monospace;
}
.card {
    backdrop-filter: blur(10px);
    background: rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0,0,0,0.37);
    border: 1px solid rgba(255,255,255,0.12);
    transition: transform 0.2s ease-in-out;
}
.card:hover {
    transform: translateY(-4px);
}
.hero {
    padding: 25px;
    border-radius: 25px;
    margin-bottom: 15px;
    background: linear-gradient(90deg, rgba(255,200,124,0.08), rgba(180,200,255,0.04));
    text-align: center;
}
.small { font-size: 14px; color: #bcd2e8; }
.vignette { font-style: italic; color: #ffd9a8; font-weight:600; text-align: center; margin-top: 15px;}
.icon { width: 30px; height: 30px; margin-right: 6px; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Greek_Vase_Muse.svg/128px-Greek_Vase_Muse.svg.png")
    st.title("Turbo-Study AI ✨")
    backend = st.radio("Backend", ("Local (free)", "OpenAI"))
    openai_key = None
    if backend == "OpenAI":
        openai_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("---")
    st.checkbox("Greek Mythology Mode 🏛️", value=True, key="mythic")

# ---------- Helper Functions ----------
def read_uploaded(file):
    name = file.name.lower()
    if name.endswith((".txt", ".md")):
        return file.getvalue().decode("utf-8")
    elif name.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file)
            text = []
            for p in reader.pages:
                text.append(p.extract_text() or "")
            return "\n".join(text)
        except Exception as e:
            return f"PDF ERROR: {e}"
    return file.getvalue().decode("utf-8", errors="ignore")


def ensure_models():
    global MODEL_LOADED, generator
    if MODEL_LOADED:
        return
    st.info("Loading AI model… first time may take 10–15 seconds.")
    from transformers import pipeline
    generator = pipeline("text2text-generation", model="google/flan-t5-small")
    MODEL_LOADED = True


def call_generate(prompt, max_length=256):
    if backend == "OpenAI" and openai_key:
        import openai
        openai.api_key = openai_key
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_length
        )
        return response.choices[0].message["content"]
    ensure_models()
    out = generator(prompt, max_length=max_length, do_sample=False)
    return out[0]["generated_text"]


def mythic_prefix(text):
    if st.session_state.get("mythic", True):
        return "Hermes whispers: " + text
    return text

# ---------- Top Hero ----------
st.markdown('<div class="hero card"><h1>📚 Turbo-Study AI</h1><div class="small">Aesthetic Summaries, Flashcards, Quizzes & Explanations</div></div>', unsafe_allow_html=True)

# ---------- Tabs ----------
tabs = st.tabs(["Notes", "Summarize", "Explain", "Flashcards", "Quiz"])

# -------- Tab 1: Notes ----------
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Upload or Paste Notes ✍️")
    uploaded = st.file_uploader("Upload (.txt / .md / .pdf)", type=["txt","md","pdf"])
    pasted = st.text_area("Or paste text here", height=200)
    if st.button("Save Notes"):
        if uploaded:
            st.session_state["notes"] = read_uploaded(uploaded)
        else:
            st.session_state["notes"] = pasted
        st.success("Notes saved!")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Tab 2: Summarize ----------
with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Summarize Your Notes ✨")
    notes = st.session_state.get("notes", "")
    if not notes:
        st.warning("No notes found.")
    else:
        size = st.selectbox("Summary length", ["Short", "Medium", "Long"])
        if st.button("Generate Summary"):
            prompt = mythic_prefix(f"Summarize this in a {size} way:\n\n{notes}")
            with st.spinner("Summarizing…"):
                summary = call_generate(prompt, max_length=300)
            st.markdown(f'<div class="card">{summary}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Tab 3: Explain ----------
with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Explain a Concept 🧠")
    question = st.text_input("Enter concept or question")
    level = st.selectbox("Level", ["ELI5", "High school", "College", "Expert"])
    if st.button("Explain"):
        prompt = mythic_prefix(f"Explain {question} at {level} level with examples.")
        ans = call_generate(prompt, max_length=300)
        st.markdown(f'<div class="card">{ans}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Tab 4: Flashcards ----------
with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Generate Flashcards 🃏")
    notes = st.session_state.get("notes", "")
    if not notes:
        st.warning("Save notes first.")
    else:
        count = st.slider("Number of flashcards", 3, 25, 6)
        if st.button("Generate Flashcards"):
            prompt = mythic_prefix(f"Generate {count} flashcards from this text. Format: Q: ... A: ...\n\n{notes}")
            out = call_generate(prompt, max_length=350)
            st.markdown(f'<div class="card">{out}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Tab 5: Quiz ----------
with tabs[4]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Multiple Choice Quiz 📝")
    notes = st.session_state.get("notes", "")
    if not notes:
        st.warning("Save notes first.")
    else:
        qn = st.slider("Number of questions", 3, 15, 5)
        if st.button("Generate Quiz"):
            prompt = mythic_prefix(f"Create {qn} MCQs from this text. Include 4 options each and mark correct answers.")
            quiz = call_generate(prompt, max_length=500)
            st.markdown(f'<div class="card">{quiz}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="vignette">Hermes says: Study like a hero ✨</div>', unsafe_allow_html=True)
