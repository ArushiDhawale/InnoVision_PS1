import streamlit as st
import pandas as pd

# ── Import everything from the shared backend ──────────────
from backend import (
    load_model,
    load_databases,
    audit_text,
    scrape_url,
)

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Synapse · Green-Truth Auditor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# FORCE LIGHT THEME & CUSTOM STYLING
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

/* Main Background */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], .main {
    background-color: #F7F6F2 !important;
    color: #1A1A18 !important;
}

/* --- RADIO BUTTON TEXT COLOR FIX --- */
/* Targets the text labels of the radio buttons specifically */
[data-testid="stMarkdownContainer"] p {
    color: #000000 !important;
    font-weight: 500 !important;
}

/* Targets the unselected state label color */
div[data-testid="stRadio"] label p {
    color: #000000 !important;
}

/* Targets the selected state (Streamlit often uses primary color) */
div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
    color: #2D6A4F !important; /* Dark Green for the active choice */
}

/* Global Font */
html, body, p, div, span, label, input, textarea, button {
    font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem !important; max-width: 1100px !important; }

/* Hero Section */
.hero-title {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2.4rem; color: #1A1A18 !important;
    line-height: 1; display: flex; align-items: center; gap: 0.5rem;
}
.hero-badge {
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #2D6A4F; background: #E8F4F0;
    padding: 0.2rem 0.65rem; border-radius: 20px; margin-left: 0.4rem;
}
.hero-sub { color: #6B6B63 !important; font-size: 0.95rem; font-weight: 300; margin: 0.4rem 0 2rem; }

/* Card Styling */
.card {
    background: #FFFFFF !important; border: 1.5px solid #E5E3DC;
    border-radius: 16px; padding: 1.8rem 2rem 1.5rem; margin-bottom: 1.6rem;
}
.card-label {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.13em;
    text-transform: uppercase; color: #6B6B63; margin-bottom: 1rem;
}

/* Widgets Styling */
[data-testid="stRadio"] label {
    background:#FFFFFF !important; 
    border:1.5px solid #E5E3DC !important; border-radius:8px !important;
    padding:.38rem 1rem !important; font-size:.85rem !important;
}
[data-testid="stRadio"] label:hover { border-color:#2D6A4F !important; }

[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
    background:#FFFFFF !important; color:#1A1A18 !important;
    border:1.5px solid #E5E3DC !important; border-radius:10px !important;
}

[data-testid="stButton"] > button {
    background:#2D6A4F !important; color:#FFFFFF !important; border:none !important;
    border-radius:10px !important; font-weight:600 !important;
}
</style>
""", unsafe_allow_html=True)

# (Remainder of VERDICT_META and helper functions from your snippet...)

# ─────────────────────────────────────────────────────────────
# LOAD DATA & MODELS
# ─────────────────────────────────────────────────────────────
clf = load_model()
bcorp, gots, india = load_databases()

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-title">🌿 Green-Truth Auditor <span class="hero-badge">Beta</span></div>
<p class="hero-sub">Paste a sustainability claim or enter a product URL — we'll verify it against global standards.</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# INPUT CARD
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-label">Input Source</div>', unsafe_allow_html=True)

# The Radio button with forced black text via CSS above
input_type = st.radio("", ["Paste text", "Enter URL"],
                      horizontal=True, label_visibility="collapsed")

text = ""
if input_type == "Paste text":
    text = st.text_area(
        "Claims",
        placeholder="e.g. Our jacket is made from 100% recycled ocean plastics, certified by GOTS…",
        height=160,
        label_visibility="collapsed",
    )
else:
    url = st.text_input("Product / brand URL",
                        placeholder="https://example.com/sustainability")
    if url:
        with st.spinner("Fetching page content…"):
            scraped = scrape_url(url)
        if scraped:
            st.success("Page scraped successfully.")
            with st.expander("Preview scraped text"):
                st.write(scraped[:1200] + "…")
            text = scraped
        else:
            st.error("Could not fetch that URL. Try pasting the text directly.")

btn_col, _ = st.columns([1, 5])
with btn_col:
    run = st.button("Run Audit ›", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# RUN AUDIT — calls backend, then only renders the result
# ─────────────────────────────────────────────────────────────

if run:
    if not text.strip():
        st.warning("Please enter some text or a valid URL first.")
        st.stop()

    with st.spinner("Analysing claims…"):
        report = audit_text(text, clf, bcorp, gots, india)   # ← backend.audit_text()

    sc      = report["final_score"]
    overall = report["overall"]

    # ── Summary ──────────────────────────────────────────────
    st.markdown('<div class="sec-label">Summary</div>', unsafe_allow_html=True)
    col_score, col_stats = st.columns([1, 2], gap="large")

    with col_score:
        st.markdown(f"""
        <div class="score-card">
          <span class="score-sub">Credibility Score</span>
          <span class="score-number" style="color:{score_color(sc)}">{sc:.0%}</span>
          <div><span class="verdict-pill {pill_class(overall)}">{overall}</span></div>
        </div>""", unsafe_allow_html=True)

    with col_stats:
        verdicts = [r["verdict"] for r in report["sentences"]]
        chips = {
            "Vague / Fake":      verdicts.count("Vague") + verdicts.count("Fake Certification Claim"),
            "Future Promises":   verdicts.count("Future Promise (Not Evidence)"),
            "Backed / Evidence": verdicts.count("Backed Claim") + verdicts.count("Evidence-Based"),
            "Uncertain":         verdicts.count("Uncertain / PR Speak"),
            "Unverified Stats":  verdicts.count("Unverified Statistic"),
            "Ignored":           verdicts.count("Ignored (Website Noise)"),
        }
        html = '<div class="stat-grid">'
        for lbl, val in chips.items():
            html += (f'<div class="stat-chip"><span class="stat-num">{val}</span>'
                     f'<span class="stat-lbl">{lbl}</span></div>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    st.progress(sc)

    # ── Brand verification ───────────────────────────────────
    if report["brand_matches"]:
        st.markdown('<div class="sec-label">Brand Verification</div>', unsafe_allow_html=True)
        html = '<div class="brand-row">'
        for m in report["brand_matches"]:
            cls  = "bc-ok"  if m["certified"] else "bc-bad"
            icon = "✅"     if m["certified"] else "❌"
            html += (f'<span class="brand-chip {cls}">'
                     f'{icon} <strong>{m["brand"]}</strong> · {m["cert_type"]}</span>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    # ── Sentence breakdown ───────────────────────────────────
    st.markdown('<div class="sec-label">Sentence-by-Sentence Breakdown</div>',
                unsafe_allow_html=True)

    show_ignored = st.checkbox("Show ignored (non-environmental) sentences", value=False)

    for r in report["sentences"]:
        if not show_ignored and r["verdict"] == "Ignored (Website Noise)":
            continue
        m     = VERDICT_META.get(r["verdict"], VERDICT_META["Uncertain / PR Speak"])
        tag   = (f'<span class="v-tag" style="background:{m["tbg"]};color:{m["tfg"]}">'
                 f'{m["icon"]} {r["verdict"]}</span>')
        flags = " ".join(f'<span class="flag-word">{w}</span>'
                         for w in r.get("flagged", []))
        st.markdown(f"""
        <div class="s-row {m['div']}">
          <div class="s-text">{r['sentence']}</div>
          <div class="s-meta">{tag} <span class="s-reason">{r['reason']}</span> {flags}</div>
        </div>""", unsafe_allow_html=True)

    # ── Export ───────────────────────────────────────────────
    st.markdown('<div class="sec-label">Export</div>', unsafe_allow_html=True)
    df_export = pd.DataFrame([
        {"sentence": r["sentence"], "verdict": r["verdict"],
         "score": r["score"], "reason": r["reason"],
         "flagged_words": ", ".join(r.get("flagged", []))}
        for r in report["sentences"]
    ])
    st.download_button(
        "⬇ Download CSV Report",
        data=df_export.to_csv(index=False).encode(),
        file_name="green_truth_audit.csv",
        mime="text/csv",
    )

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 0 2.5rem">
      <div style="font-size:3.5rem;margin-bottom:1rem">🌿</div>
      <div style="font-size:1rem;font-weight:500;color:#6B6B63">
        Enter a sustainability claim above and click <strong>Run Audit</strong>
      </div>
      <div style="font-size:.8rem;margin-top:.5rem;color:#9CA3AF">
        Powered by cross-encoder/nli-MiniLM2-L6-H768 · B-Corp · GOTS · India Certifications
      </div>
    </div>""", unsafe_allow_html=True)
