import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader

MODEL_LOADED = False

st.set_page_config(
    page_title="⚡Turbo-Study AI✨",
    page_icon="📚",
    layout="wide"
)

# ---------- STYLES ----------
st.markdown("""
<style>
body {background: linear-gradient(135deg, #0f172a, #1e293b); color: #e6edf3; font-family: 'Roboto', sans-serif;}
.hero {padding:30px;text-align:center;border-radius:30px;background:linear-gradient(120deg, rgba(255,200,124,0.15), rgba(180,200,255,0.08)); box-shadow:0 8px 32px rgba(0,0,0,0.4);}
.card {backdrop-filter:blur(12px); background: rgba(255,255,255,0.05); border-radius:25px; padding:25px; margin-bottom:20px; box-shadow:0 12px 40px rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.12);}
.card:hover {transform: translateY(-6px); box-shadow:0 20px 60px rgba(255,255,255,0.3);}
.vignette {font-style: italic; color: #ffd9a8; font-weight:600; text-align:center; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚡ Turbo-Study AI ✨")
    backend = st.radio("Backend", ("Local (free)", "OpenAI"))
    openai_key = None
    if backend == "OpenAI":
        openai_key = st.text_input("OpenAI API Key", type="password")
    st.checkbox("Enable Mythic Mode 🏛️", value=True, key="mythic")

# ---------- Helper Functions ----------
def read_uploaded(file):
    name = file.name.lower()
    if name.endswith((".txt", ".md")):
        return file.getvalue().decode("utf-8")
    elif name.endswith(".pdf"):
        reader = PdfReader(file)
        text = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(text)
    return file.getvalue().decode("utf-8", errors="ignore")

def mythic_prefix(text):
    if st.session_state.get("mythic", True):
        return "Hermes whispers: " + text
    return text

# Dummy generator (replace with your call_generate)
def call_generate(prompt, max_length=256):
    return f"[AI OUTPUT] {prompt[:200]}..."  # For testing

# ---------- Hero ----------
st.markdown('<div class="hero card"><h1>⚡ Turbo-Study AI ✨</h1><div class="small">Summaries • Flashcards • Quizzes • Explanations</div></div>', unsafe_allow_html=True)

# ---------- Tabs ----------
tabs = st.tabs(["Notes", "Summarize", "Explain", "Flashcards", "Quiz"])

# ---------- Tab 1: Notes ----------
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

    if "notes" in st.session_state:
        st.markdown("**Current Notes Preview:**")
        st.write(st.session_state["notes"][:500] + ("..." if len(st.session_state["notes"])>500 else ""))
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Tab 2: Summarize ----------
with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Summarize Your Notes ✨")
    notes = st.session_state.get("notes", "")
    if not notes:
        st.warning("No notes found. Upload or paste notes first.")
    else:
        size = st.selectbox("Summary length", ["Short", "Medium", "Long"], key="sum_size")
        if st.button("Generate Summary", key="sum_btn"):
            prompt = mythic_prefix(f"Summarize this in a {size} way:\n\n{notes}")
            summary = call_generate(prompt, max_length=300)
            st.markdown(f'<div class="card">{summary}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Tab 3: Explain ----------
with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Explain a Concept 🧠")
    question = st.text_input("Enter concept or question", key="ex_input")
    level = st.selectbox("Level", ["ELI5", "High school", "College", "Expert"], key="ex_level")
    if st.button("Explain", key="ex_btn"):
        if question.strip() == "":
            st.warning("Please enter a concept.")
        else:
            prompt = mythic_prefix(f"Explain {question} at {level} level with examples.")
            ans = call_generate(prompt, max_length=300)
            st.markdown(f'<div class="card">{ans}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Tab 4: Flashcards ----------
with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Generate Flashcards 🃏")
    notes = st.session_state.get("notes", "")
    if not notes:
        st.warning("Save notes first.")
    else:
        count = st.slider("Number of flashcards", 3, 25, 6, key="fc_count")
        if st.button("Generate Flashcards", key="fc_btn"):
            prompt = mythic_prefix(f"Generate {count} flashcards from this text. Format: Q: ... A: ...\n\n{notes}")
            out = call_generate(prompt, max_length=350)
            st.markdown(f'<div class="card">{out}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Tab 5: Quiz ----------
with tabs[4]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Multiple Choice Quiz 📝")
    notes = st.session_state.get("notes", "")
    if not notes:
        st.warning("Save notes first.")
    else:
        qn = st.slider("Number of questions", 3, 15, 5, key="quiz_qn")
        if st.button("Generate Quiz", key="quiz_btn"):
            prompt = mythic_prefix(f"Create {qn} MCQs from this text. Include 4 options each and mark correct answers.")
            quiz = call_generate(prompt, max_length=500)
            st.markdown(f'<div class="card">{quiz}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="vignette">Hermes says: Study like a god ⚡📚</div>', unsafe_allow_html=True)
