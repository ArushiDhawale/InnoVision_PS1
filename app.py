"""
Green-Truth Auditor — Streamlit Frontend
All decision-making logic lives in the notebook backend (Synapse_3.ipynb).
This file is display-only: it calls backend functions and renders results.
"""

import re
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

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
# FORCE LIGHT THEME — overrides system dark mode completely
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

/* ── FORCE LIGHT on every Streamlit layer ── */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="block-container"],
section[data-testid="stSidebar"],
.main, .block-container,
div[class*="css"] {
    background-color: #F7F6F2 !important;
    color: #1A1A18 !important;
}

/* ── Root palette ── */
:root {
    --bg:           #F7F6F2;
    --surface:      #FFFFFF;
    --border:       #E5E3DC;
    --text-primary: #1A1A18;
    --text-muted:   #6B6B63;
    --green:        #2D6A4F;
    --green-light:  #E8F4F0;
    --amber:        #B45309;
    --amber-light:  #FEF3C7;
    --red:          #9B1C1C;
    --red-light:    #FEE2E2;
    --blue:         #1E3A5F;
    --blue-light:   #DBEAFE;
    --grey-light:   #F3F4F6;
}

/* ── Typography ── */
html, body, p, div, span, label, input, textarea, button {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Layout ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2.5rem 3rem 4rem !important;
    max-width: 1100px !important;
}

/* ── Hero ── */
.hero-title {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2.4rem;
    color: #1A1A18 !important;
    line-height: 1;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.hero-badge {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #2D6A4F;
    background: #E8F4F0;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    vertical-align: middle;
    margin-left: 0.4rem;
}
.hero-sub {
    color: #6B6B63 !important;
    font-size: 0.95rem;
    font-weight: 300;
    margin: 0.4rem 0 2rem;
}

/* ── Cards / surfaces ── */
.card {
    background: #FFFFFF !important;
    border: 1.5px solid #E5E3DC;
    border-radius: 16px;
    padding: 1.8rem 2rem 1.5rem;
    margin-bottom: 1.6rem;
}
.card-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #6B6B63;
    margin-bottom: 1rem;
}

/* ── Score card ── */
.score-card {
    background: #FFFFFF !important;
    border: 1.5px solid #E5E3DC;
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
}
.score-number {
    font-family: 'DM Serif Display', serif !important;
    font-size: 3.8rem;
    line-height: 1;
    display: block;
}
.score-sub {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    color: #6B6B63;
    margin-bottom: 0.6rem;
}
.verdict-pill {
    display: inline-block;
    padding: 0.35rem 1.1rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-top: 0.6rem;
    letter-spacing: 0.04em;
}
.pill-green { background: #E8F4F0; color: #2D6A4F; }
.pill-amber { background: #FEF3C7; color: #B45309; }
.pill-red   { background: #FEE2E2; color: #9B1C1C; }

/* ── Stat chips ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 0.75rem;
}
.stat-chip {
    background: #FFFFFF !important;
    border: 1.5px solid #E5E3DC;
    border-radius: 12px;
    padding: 0.9rem 0.8rem;
    text-align: center;
}
.stat-num {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2rem;
    color: #1A1A18;
    display: block;
}
.stat-lbl {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #6B6B63;
    display: block;
    margin-top: 0.1rem;
}

/* ── Brand chips ── */
.brand-row { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-bottom: 1.4rem; }
.brand-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.38rem 0.85rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 500;
    border: 1.5px solid;
}
.bc-ok  { background: #E8F4F0; border-color: #A7D5C4; color: #2D6A4F; }
.bc-bad { background: #FEE2E2; border-color: #FCA5A5; color: #9B1C1C; }

/* ── Section divider label ── */
.sec-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #6B6B63;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.8rem 0 0.85rem;
}
.sec-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #E5E3DC;
}

/* ── Sentence rows ── */
.s-row {
    background: #FFFFFF !important;
    border: 1.5px solid #E5E3DC;
    border-left: 4px solid #E5E3DC;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.55rem;
}
.s-text {
    font-size: 0.91rem;
    color: #1A1A18 !important;
    line-height: 1.55;
    margin-bottom: 0.5rem;
}
.s-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 0.45rem; }
.v-tag {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.18rem 0.55rem;
    border-radius: 4px;
}
.s-reason { font-size: 0.77rem; color: #6B6B63; }
.flag-word {
    font-size: 0.7rem;
    background: #FEF3C7;
    color: #B45309;
    padding: 0.1rem 0.45rem;
    border-radius: 3px;
    font-weight: 600;
}

/* Verdict left-border + tag colours */
.vd-vague    { border-left-color: #EF4444 !important; }
.vd-fake     { border-left-color: #B91C1C !important; }
.vd-unverif  { border-left-color: #F59E0B !important; }
.vd-future   { border-left-color: #D97706 !important; }
.vd-pr       { border-left-color: #9CA3AF !important; }
.vd-backed   { border-left-color: #2D6A4F !important; }
.vd-evidence { border-left-color: #1E3A5F !important; }
.vd-ignored  { border-left-color: #D1D5DB !important; }

/* ── Streamlit widget overrides — force light ── */

/* Radio */
[data-testid="stRadio"] > div { background: transparent !important; }
[data-testid="stRadio"] label {
    background: #FFFFFF !important;
    color: #1A1A18 !important;
    border: 1.5px solid #E5E3DC !important;
    border-radius: 8px !important;
    padding: 0.38rem 1rem !important;
    font-size: 0.85rem !important;
}
[data-testid="stRadio"] label:hover { border-color: #2D6A4F !important; }

/* Text area */
[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    color: #1A1A18 !important;
    border: 1.5px solid #E5E3DC !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #2D6A4F !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.12) !important;
}
[data-testid="stTextArea"] label { color: #6B6B63 !important; }

/* Text input */
[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    color: #1A1A18 !important;
    border: 1.5px solid #E5E3DC !important;
    border-radius: 10px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #2D6A4F !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.12) !important;
}
[data-testid="stTextInput"] label { color: #6B6B63 !important; }

/* Buttons */
[data-testid="stButton"] > button {
    background: #2D6A4F !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.03em !important;
}
[data-testid="stButton"] > button:hover { opacity: 0.85 !important; }

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: #FFFFFF !important;
    color: #2D6A4F !important;
    border: 1.5px solid #2D6A4F !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #E8F4F0 !important; }

/* Checkbox */
[data-testid="stCheckbox"] label { color: #1A1A18 !important; font-size: 0.85rem !important; }

/* Progress bar */
[data-testid="stProgressBar"] > div > div { background: #2D6A4F !important; border-radius: 4px !important; }
[data-testid="stProgressBar"] { background: #E5E3DC !important; border-radius: 4px !important; }

/* Alerts */
[data-testid="stAlert"] { background: #FFFFFF !important; border-radius: 10px !important; }

/* Expander */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1.5px solid #E5E3DC !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: #1A1A18 !important; font-size: 0.85rem !important; }

/* Divider */
hr { border-color: #E5E3DC !important; margin: 1.4rem 0 !important; }

/* Metric */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1.5px solid #E5E3DC !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="stMetricLabel"] { color: #6B6B63 !important; }
[data-testid="stMetricValue"] { color: #1A1A18 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# BACKEND LOGIC (mirrors notebook — single source of truth)
# ─────────────────────────────────────────────────────────────

BUZZWORDS = [
    "eco-friendly","green","natural","sustainable","conscious",
    "ethical","clean","planet-friendly","earth-conscious","non-toxic",
    "biodegradable","organic","eco-conscious","responsible","pure",
    "carbon neutral","net zero","zero waste","environmentally friendly",
    "loved by nature","free from harmful chemicals","toxin-free",
    "chemical-free","nature-inspired","plant-based","earth-friendly",
    "safe for the planet","free from","no harmful","gentle on earth",
    "cruelty-free","vegan","clean beauty","green beauty",
    "sustainability","climate","fossil-free","pre-loved",
    "circular","commitments","ambition","targets","decarbonise",
]
FUTURE_PROMISES = [
    "aim to","committed to","by 2030","by 2040","by 2050","goal is",
    "working towards","our ambition","roadmap","in the future","strive to",
    "mission to","pledge",
]
EVIDENCE_KEYWORDS = [
    'according to','verified by','audited by','reported by',
    'certified','certification','gots','b-corp','oeko-tex',
    'third party','third-party','accredited','iso','standard',
    'control union','bureau veritas','rainforest alliance',
    'bis ecomark','ecomark','greenpro','cii greenpro',
    'asci','isi mark','score of','independently verified',
]
EVIDENCE_PATTERNS = [
    r'\d+%',r'certified',r'certification',r'gots',r'b-corp',r'oeko-tex',
    r'audited',r'audit',r'third[\s\-]?party',r'verified',r'accredited',
    r'iso\s*\d+',r'control union',r'bureau veritas',r'bis ecomark',
    r'ecomark',r'greenpro',r'rainforest alliance',r'score of \d+',
]
CERT_NAMES = [
    'gots','b-corp','oeko-tex','rainforest alliance','fair trade',
    'control union','bureau veritas','bis ecomark','ecomark','greenpro',
    'cii greenpro','asci','isi mark',
]
ENVIRONMENTAL_TOPICS = BUZZWORDS + FUTURE_PROMISES + EVIDENCE_KEYWORDS + [
    "material","fabric","cotton","wool","polyester","plastic","leather",
    "carbon","emissions","water","energy","waste","footprint","impact",
    "supply chain","factory","workers","packaging","recycled","recycling",
    "climate","environment","ingredients","sourcing","agriculture",
    "forestry","biodiversity","renewable","solar","power","manufacturing",
]
LABELS = [
    "vague marketing or future promises",
    "specific and verifiable environmental evidence",
]


@st.cache_resource(show_spinner="Loading AI model…")
def load_model():
    return pipeline("zero-shot-classification",
                    model="cross-encoder/nli-MiniLM2-L6-H768")


@st.cache_data(show_spinner="Loading certification databases…")
def load_databases():
    try:
        bcorp = pd.read_csv("bcorp.csv")
        gots  = pd.read_csv("gots.csv")
        india = pd.read_csv("indian_certifications.csv")
        if 'certification_type' in bcorp.columns:
            bcorp = bcorp.rename(columns={'certification_type': 'cert_type'})
        for df in (bcorp, gots, india):
            df['cert_type'] = df['cert_type'].fillna('None')
        return bcorp, gots, india
    except FileNotFoundError as e:
        st.error(f"Database file missing: {e}")
        st.stop()


def is_relevant(s):
    lo = s.lower()
    return any(t in lo for t in ENVIRONMENTAL_TOPICS)

def has_buzzword(s):
    lo = s.lower()
    found = [w for w in BUZZWORDS if w in lo]
    return bool(found), found

def has_future_promise(s):
    lo = s.lower()
    found = [w for w in FUTURE_PROMISES if w in lo]
    return bool(found), found

def has_evidence(s):
    lo = s.lower()
    return any(re.search(p, lo) for p in EVIDENCE_PATTERNS)

def has_unverified_stat(s):
    lo = s.lower()
    return (bool(re.search(r'\d+\s*(million|billion|ton|tons|kg|lbs)', lo))
            and not any(w in lo for w in EVIDENCE_KEYWORDS))

def check_brands(text, bcorp, gots, india):
    lo = text.lower()
    matches = []
    for db, name in [(bcorp,"B-Corp"),(gots,"GOTS"),(india,"India")]:
        for _, row in db.iterrows():
            bl = str(row["brand"]).lower()
            if re.search(r'\b' + re.escape(bl) + r'\b', lo):
                matches.append({
                    "brand": row["brand"],
                    "certified": bool(row["certified"]),
                    "cert_type": str(row["cert_type"]),
                    "database": name,
                })
    return matches

def verify_cert(sentence, brand_matches):
    lo = sentence.lower()
    for cert in CERT_NAMES:
        if cert in lo:
            ok = any(cert.lower() in str(r["cert_type"]).lower() and r["certified"]
                     for r in brand_matches)
            if not ok:
                return False, cert.upper()
    return True, None

def classify_sentence(s, clf, brand_matches):
    bw_found, bw_list = has_buzzword(s)
    fp_found, fp_list = has_future_promise(s)
    ev = has_evidence(s)

    if fp_found and not ev:
        return {"verdict":"Future Promise (Not Evidence)","score":0.3,
                "flagged":fp_list,"reason":"Corporate goals aren't current verifiable facts."}
    if ev:
        if has_unverified_stat(s):
            return {"verdict":"Unverified Statistic","score":0.2,
                    "flagged":bw_list,"reason":"Numbers used without an auditor or certification."}
        ok, cert = verify_cert(s, brand_matches)
        if not ok:
            return {"verdict":"Fake Certification Claim","score":0.0,
                    "flagged":bw_list,"reason":f"Brand not found in our {cert} database."}
        return {"verdict":"Backed Claim","score":0.9,
                "flagged":bw_list,"reason":"References a certification or verified evidence."}
    if has_unverified_stat(s):
        return {"verdict":"Unverified Statistic","score":0.2,
                "flagged":[],"reason":"Numbers without any source, auditor, or cert."}
    if bw_found:
        return {"verdict":"Vague","score":0.0,
                "flagged":bw_list,"reason":"Uses sustainability buzzwords with no proof."}

    res   = clf(s, LABELS)
    label = res["labels"][0]
    conf  = res["scores"][0]
    if label == LABELS[1] and conf > 0.6:
        return {"verdict":"Evidence-Based","score":round(conf,2),
                "flagged":[],"reason":"AI found specific environmental evidence."}
    return {"verdict":"Uncertain / PR Speak","score":0.4,
            "flagged":[],"reason":"AI classified this as vague marketing or corporate PR."}


def audit(text, clf, bcorp, gots, india):
    sentences     = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 10]
    brand_matches = check_brands(text, bcorp, gots, india)
    all_res, valid = [], []

    for s in sentences:
        if not is_relevant(s):
            all_res.append({"verdict":"Ignored (Website Noise)","score":0.0,
                            "flagged":[],"reason":"Non-environmental text.","sentence":s})
            continue
        r = classify_sentence(s, clf, brand_matches)
        r["sentence"] = s
        all_res.append(r)
        valid.append(r)

    score = round(sum(r["score"] for r in valid)/len(valid), 2) if valid else 0.0
    if any(m["certified"] is False for m in brand_matches):
        score = round(max(0.0, score - 0.40), 2)

    overall = ("Greenwashing Likely" if score < 0.4 else
               "Uncertain"           if score < 0.7 else "Legitimate Claims")

    return {"sentences":all_res,"final_score":score,"overall":overall,
            "brand_matches":brand_matches,"total_valid":len(valid)}


def scrape_url(url):
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script","style","nav","footer"]): tag.decompose()
        return soup.get_text(separator=". ", strip=True)[:3000]
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# VERDICT STYLE MAP
# ─────────────────────────────────────────────────────────────

VERDICT_META = {
    "Vague":                        {"icon":"❌","div":"vd-vague",   "tbg":"#FEE2E2","tfg":"#9B1C1C"},
    "Fake Certification Claim":     {"icon":"🚨","div":"vd-fake",    "tbg":"#FEE2E2","tfg":"#7F1D1D"},
    "Unverified Statistic":         {"icon":"📉","div":"vd-unverif", "tbg":"#FEF3C7","tfg":"#B45309"},
    "Future Promise (Not Evidence)":{"icon":"🗓️","div":"vd-future",  "tbg":"#FEF3C7","tfg":"#92400E"},
    "Uncertain / PR Speak":         {"icon":"⚠️","div":"vd-pr",      "tbg":"#F3F4F6","tfg":"#4B5563"},
    "Backed Claim":                 {"icon":"✅","div":"vd-backed",   "tbg":"#E8F4F0","tfg":"#2D6A4F"},
    "Evidence-Based":               {"icon":"📊","div":"vd-evidence", "tbg":"#DBEAFE","tfg":"#1E3A5F"},
    "Ignored (Website Noise)":      {"icon":"⚪","div":"vd-ignored",  "tbg":"#F3F4F6","tfg":"#9CA3AF"},
}

def score_color(s):
    return "#2D6A4F" if s >= 0.7 else "#B45309" if s >= 0.4 else "#9B1C1C"

def pill_class(overall):
    return ("pill-green" if overall == "Legitimate Claims" else
            "pill-amber" if overall == "Uncertain" else "pill-red")


# ─────────────────────────────────────────────────────────────
# UI — HEADER
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-title">
  🌿 Green-Truth Auditor
  <span class="hero-badge">Beta</span>
</div>
<p class="hero-sub">
  Paste a sustainability claim or enter a product URL — we'll tell you if it's real or greenwashing.
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOAD RESOURCES
# ─────────────────────────────────────────────────────────────

clf            = load_model()
bcorp, gots, india = load_databases()

# ─────────────────────────────────────────────────────────────
# INPUT CARD
# ─────────────────────────────────────────────────────────────

st.markdown('<div class="card"><div class="card-label">Input</div>', unsafe_allow_html=True)

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
# RESULTS
# ─────────────────────────────────────────────────────────────

if run:
    if not text.strip():
        st.warning("Please enter some text or a valid URL first.")
        st.stop()

    with st.spinner("Analysing claims…"):
        report = audit(text, clf, bcorp, gots, india)

    sc      = report["final_score"]
    overall = report["overall"]

    # ── Summary ──────────────────────────────────────────────
    st.markdown('<div class="sec-label">Summary</div>', unsafe_allow_html=True)

    col_score, col_stats = st.columns([1, 2], gap="large")

    with col_score:
        pclass = pill_class(overall)
        st.markdown(f"""
        <div class="score-card">
          <span class="score-sub">Credibility Score</span>
          <span class="score-number" style="color:{score_color(sc)}">{sc:.0%}</span>
          <div><span class="verdict-pill {pclass}">{overall}</span></div>
        </div>
        """, unsafe_allow_html=True)

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
            html += (f'<div class="stat-chip">'
                     f'<span class="stat-num">{val}</span>'
                     f'<span class="stat-lbl">{lbl}</span></div>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    # ── Progress ─────────────────────────────────────────────
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

        m    = VERDICT_META.get(r["verdict"], VERDICT_META["Uncertain / PR Speak"])
        dcls = m["div"]
        tag  = (f'<span class="v-tag" style="background:{m["tbg"]};color:{m["tfg"]}">'
                f'{m["icon"]} {r["verdict"]}</span>')
        flags = " ".join(f'<span class="flag-word">{w}</span>'
                         for w in r.get("flagged", []))

        st.markdown(f"""
        <div class="s-row {dcls}">
          <div class="s-text">{r['sentence']}</div>
          <div class="s-meta">{tag} <span class="s-reason">{r['reason']}</span> {flags}</div>
        </div>
        """, unsafe_allow_html=True)

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
      <div style="font-size:0.8rem;margin-top:0.5rem;color:#9CA3AF">
        Powered by cross-encoder/nli-MiniLM2-L6-H768 · B-Corp · GOTS · India Certifications
      </div>
    </div>
    """, unsafe_allow_html=True)
