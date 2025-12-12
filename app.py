# app.py
import streamlit as st
from pathlib import Path
import time
import os
from typing import List
from io import StringIO, BytesIO

# ML imports (lazy load)
MODEL_LOADED = False

st.set_page_config(page_title="Turbo-Study — Aesthetic Study AI", layout="wide", initial_sidebar_state="expanded")

# ---------- Styles (aesthetic + mythic) ----------
st.markdown(
    """
    <style>
    :root{
      --bg1: linear-gradient(135deg, #0f172a, #04293a);
      --card: rgba(255,255,255,0.03);
      --accent: rgba(255,200,124,0.12);
      --glass: rgba(255,255,255,0.03);
    }
    .main-container {
      background: var(--bg1);
      color: #e6edf3;
      font-family: 'Inter', sans-serif;
    }
    .card {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 4px 30px rgba(2,6,23,0.6);
      border: 1px solid rgba(255,255,255,0.03);
    }
    .hero {
      padding: 18px;
      border-radius: 12px;
      margin-bottom: 10px;
      background: linear-gradient(90deg, rgba(255,200,124,0.06), rgba(180,200,255,0.02));
    }
    .small {
      font-size: 14px;
      color: #bcd2e8;
    }
    .vignette {
      font-style: italic; color: #ffd9a8; font-weight:600;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Greek_Vase_Muse.svg/512px-Greek_Vase_Muse.svg.png", width=80)
    st.title("Turbo-Study")
    st.markdown("Aesthetic study helper — mythic vibes, modern brains ✨")
    backend = st.radio("Backend", ("Local (free, downloads models)", "OpenAI (optional)"))
    if backend.startswith("OpenAI"):
        openai_key = st.text_input("OpenAI API Key (optional)", type="password")
    st.markdown("---")
    st.markdown("Study mode")
    study_mode = st.selectbox("Focus Mode", ["Pomodoro", "Deep Work (90m)", "Quick Review (15m)"])
    st.markdown("---")
    st.markdown("Theme")
    st.checkbox("Enable Mythic Prompts (greek gods flavor)", value=True, key="mythic")

# ---------- Top hero ----------
st.markdown('<div class="hero card"><h1>Turbo-Study — aesthetic study AI</h1><div class="small">Upload notes, summarize, generate flashcards & quizzes. Powered by local or OpenAI models.</div></div>', unsafe_allow_html=True)

# ---------- Helper functions ----------
def read_uploaded(file) -> str:
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
            return f"[Could not parse PDF: {e}]"
    else:
        return file.getvalue().decode("utf-8", errors="ignore")

# ML lazy loader
def ensure_models():
    global MODEL_LOADED, generator, embedder
    if MODEL_LOADED:
        return
    st.info("Loading models (one-time). This downloads transformer weights; please be patient.")
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    # generator: summarization & Q/A style generation
    try:
        # flan-t5-small or t5-small
        gen_model_name = "google/flan-t5-small"
        generator = pipeline("text2text-generation", model=gen_model_name, device=-1, tokenizer=gen_model_name)
    except Exception:
        generator = pipeline("text2text-generation", model="t5-small", device=-1)
    # sentence transformer for embeddings
    try:
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        embedder = None
    MODEL_LOADED = True

def call_generate(prompt: str, max_length=256) -> str:
    if backend.startswith("OpenAI") and openai_key:
        # optional OpenAI fallback (user provided key)
        import openai
        openai.api_key = openai_key
        resp = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens= max_length//2)
        return resp.choices[0].text.strip()
    else:
        ensure_models()
        out = generator(prompt, max_length=max_length, do_sample=False)
        return out[0]["generated_text"].strip()

def make_mythic_prefix(text: str) -> str:
    if st.session_state.get("mythic", True):
        return f"Ancient scholar Hermes whispers: {text}"
    return text

# ---------- Main UI: Tabs ----------
tabs = st.tabs(["Notes", "Summarize", "Explain", "Flashcards", "Quiz", "Pomodoro"])

# Notes tab
with tabs[0]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Upload your notes / paste text")
    uploaded = st.file_uploader("Upload .txt .md .pdf (or drag & drop)", accept_multiple_files=False)
    paste = st.text_area("Or paste text here", height=200)
    if uploaded:
        raw_text = read_uploaded(uploaded)
    else:
        raw_text = paste
    st.write("")    
    if raw_text and st.button("Save as session notes"):
        st.session_state["notes"] = raw_text
        st.success("Saved to session!")
    st.markdown("</div>", unsafe_allow_html=True)

# Summarize tab
with tabs[1]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Summarize")
    notes = st.session_state.get("notes", "")
    if not notes:
        st.warning("No notes saved. Upload or paste text in the Notes tab.")
    else:
        form = st.form("summarize_form")
        length = form.selectbox("Summary length", ["Short (3-4 lines)", "Medium (1 paragraph)", "Long (detailed)"])
        tone = form.selectbox("Tone", ["Neutral", "Motivational", "Exam-focused"])
        submit = form.form_submit_button("Generate summary")
        if submit:
            prompt = f"summarize the following text into a {length} tone:{tone}:\n\n{notes}"
            prompt = make_mythic_prefix(prompt)
            with st.spinner("Summarizing..."):
                summary = call_generate(prompt, max_length=300)
            st.markdown("**Summary**")
            st.write(summary)
    st.markdown("</div>", unsafe_allow_html=True)

# Explain tab
with tabs[2]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Explain a concept")
    query = st.text_input("Enter concept or question (e.g., 'What is Fourier transform?')", "")
    level = st.selectbox("Explain level", ["Eli5", "High-school", "College", "Expert"])
    if st.button("Explain"):
        if not query:
            st.warning("Type a topic first.")
        else:
            prompt = f"Explain '{query}' at {level} level with analogies and 3 examples."
            prompt = make_mythic_prefix(prompt)
            with st.spinner("Thinking like Athena..."):
                resp = call_generate(prompt, max_length=300)
            st.write(resp)
    st.markdown("</div>", unsafe_allow_html=True)

# Flashcards tab
with tabs[3]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Auto flashcards")
    notes = st.session_state.get("notes", "")
    fc_count = st.slider("Number of flashcards", 3, 30, 8)
    if st.button("Generate flashcards"):
        if not notes:
            st.warning("No notes — save some notes first.")
        else:
            prompt = f"Create {fc_count} concise question-answer flashcards from this text. Format each as Q: ... A: ...\n\n{notes}"
            prompt = make_mythic_prefix(prompt)
            with st.spinner("Forging tablets..."):
                out = call_generate(prompt, max_length=700)
            # parse simple Q/A blocks
            cards = [c.strip() for c in out.split("\n") if c.strip()]
            for idx, c in enumerate(cards[:fc_count]):
                st.markdown(f"**Card {idx+1}**")
                st.text(c)
    st.markdown("</div>", unsafe_allow_html=True)

# Quiz tab
with tabs[4]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Quick multiple-choice quiz")
    notes = st.session_state.get("notes", "")
    qcount = st.number_input("Questions", 3, 15, 5)
    if st.button("Make quiz"):
        if not notes:
            st.warning("Save notes first.")
        else:
            prompt = f"Make a {qcount}-question multiple choice quiz (4 options each) from the text. Mark the correct answer. Provide questions, options labeled A-D, and answer letter."
            prompt = make_mythic_prefix(prompt)
            with st.spinner("Summoning riddles..."):
                out = call_generate(prompt, max_length=800)
            st.markdown("**Quiz**")
            st.write(out)
    st.markdown("</div>", unsafe_allow_html=True)

# Pomodoro tab
with tabs[5]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Pomodoro & session tracker")
    pomodoro_mins = st.number_input("Minutes per Pomodoro", min_value=5, max_value=90, value=25)
    short_break = st.number_input("Short break (mins)", min_value=1, max_value=30, value=5)
    long_break = st.number_input("Long break (mins)", min_value=5, max_value=60, value=20)
    if st.button("Start Pomodoro"):
        st.info("Starting Pomodoro — focus mode on.")
        # simple countdown (keeps UI busy)
        placeholder = st.empty()
        total = pomodoro_mins * 60
        for remaining in range(total, -1, -1):
            mins, secs = divmod(remaining, 60)
            placeholder.markdown(f"⏳ **Focus** — {mins:02d}:{secs:02d}")
            time.sleep(1)
        st.balloons()
        st.success("Pomodoro complete! Take a short break.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("<div class='small vignette'>Hermes says: Learn like a hero. ✨</div>", unsafe_allow_html=True)
