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
# CUSTOM CSS — clean light theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root palette ── */
:root {
    --bg:          #F7F6F2;
    --surface:     #FFFFFF;
    --border:      #E5E3DC;
    --text-primary:#1A1A18;
    --text-muted:  #6B6B63;
    --green:       #2D6A4F;
    --green-light: #E8F4F0;
    --amber:       #B45309;
    --amber-light: #FEF3C7;
    --red:         #9B1C1C;
    --red-light:   #FEE2E2;
    --blue:        #1E3A5F;
    --blue-light:  #DBEAFE;
    --grey-light:  #F3F4F6;
    --score-high:  #2D6A4F;
    --score-mid:   #B45309;
    --score-low:   #9B1C1C;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text-primary);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem; max-width: 1100px; }

/* ── Hero header ── */
.hero {
    display: flex;
    align-items: baseline;
    gap: 0.6rem;
    margin-bottom: 0.25rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: var(--text-primary);
    line-height: 1;
}
.hero-badge {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--green);
    background: var(--green-light);
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    margin-bottom: 0.15rem;
}
.hero-sub {
    color: var(--text-muted);
    font-size: 0.95rem;
    font-weight: 300;
    margin-bottom: 2.2rem;
    margin-top: 0.4rem;
}

/* ── Input card ── */
.input-card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 1.8rem 2rem 1.5rem;
    margin-bottom: 1.8rem;
}
.input-card-title {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 1rem;
}

/* ── Score card ── */
.score-card {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    height: 100%;
}
.score-number {
    font-family: 'DM Serif Display', serif;
    font-size: 3.6rem;
    line-height: 1;
}
.score-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    color: var(--text-muted);
}
.verdict-pill {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-top: 0.5rem;
}
.verdict-green  { background: var(--green-light); color: var(--green); }
.verdict-amber  { background: var(--amber-light); color: var(--amber); }
.verdict-red    { background: var(--red-light);   color: var(--red);   }

/* ── Stat grid ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.8rem;
    margin-bottom: 1.8rem;
}
.stat-chip {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.stat-chip-num {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    display: block;
}
.stat-chip-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* ── Brand badges ── */
.brand-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-bottom: 1.8rem;
}
.brand-chip {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 0.85rem;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 500;
    border: 1.5px solid;
}
.brand-chip-ok  { background: var(--green-light); border-color: #A7D5C4; color: var(--green); }
.brand-chip-bad { background: var(--red-light);   border-color: #FCA5A5; color: var(--red);   }

/* ── Section label ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.8rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Sentence row ── */
.sentence-row {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-left: 4px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.15s;
}
.sentence-row:hover { border-color: var(--green); }
.sentence-row-text {
    font-size: 0.92rem;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    line-height: 1.5;
}
.sentence-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;
}
.verdict-tag {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
}
.reason-text {
    font-size: 0.78rem;
    color: var(--text-muted);
}
.flagged-word {
    font-size: 0.72rem;
    background: var(--amber-light);
    color: var(--amber);
    padding: 0.1rem 0.45rem;
    border-radius: 3px;
    font-weight: 500;
}

/* ── Verdict colour map ── */
.v-vague              { background: var(--red-light);   color: var(--red);   border-left-color: var(--red) !important; }
.v-fake-cert          { background: var(--red-light);   color: var(--red);   border-left-color: #7F1D1D !important; }
.v-unverified         { background: var(--amber-light); color: var(--amber); border-left-color: var(--amber) !important; }
.v-future             { background: var(--amber-light); color: var(--amber); border-left-color: #92400E !important; }
.v-pr                 { background: var(--grey-light);  color: #4B5563;      border-left-color: #9CA3AF !important; }
.v-backed             { background: var(--green-light); color: var(--green); border-left-color: var(--green) !important; }
.v-evidence           { background: var(--blue-light);  color: var(--blue);  border-left-color: var(--blue) !important; }
.v-ignored            { background: var(--grey-light);  color: #9CA3AF;      border-left-color: #D1D5DB !important; }

/* ── Progress bar override ── */
.stProgress > div > div > div > div { background-color: var(--green) !important; border-radius: 4px; }

/* ── Button ── */
.stButton > button {
    background: var(--green) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 2.2rem !important;
    letter-spacing: 0.03em !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── Radio pills ── */
.stRadio > div { flex-direction: row; gap: 1rem; }
.stRadio > div > label {
    background: var(--surface);
    border: 1.5px solid var(--border);
    border-radius: 8px;
    padding: 0.4rem 1.1rem;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: border-color 0.15s;
}
.stRadio > div > label:hover { border-color: var(--green); }

/* ── Text inputs ── */
.stTextArea textarea, .stTextInput input {
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--surface) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px rgba(45,106,79,0.1) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.6rem 0 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# BACKEND: All logic imported from notebook (re-declared here
# so the app runs standalone from the same repo folder)
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
LABELS = ["vague marketing or future promises","specific and verifiable environmental evidence"]


@st.cache_resource(show_spinner="Loading AI model…")
def load_model():
    return pipeline("zero-shot-classification", model="cross-encoder/nli-MiniLM2-L6-H768")


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


# ── Pure logic functions (backend, no UI) ───────────────────

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

    res = clf(s, LABELS)
    label, conf = res["labels"][0], res["scores"][0]
    if label == LABELS[1] and conf > 0.6:
        return {"verdict":"Evidence-Based","score":round(conf,2),
                "flagged":[],"reason":"AI found specific environmental evidence."}
    return {"verdict":"Uncertain / PR Speak","score":0.4,
            "flagged":[],"reason":"AI classified this as vague marketing or corporate PR."}


def audit(text, clf, bcorp, gots, india):
    sentences    = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 10]
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
               "Uncertain" if score < 0.7 else "Legitimate Claims")

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
# VERDICT STYLING HELPERS
# ─────────────────────────────────────────────────────────────

VERDICT_META = {
    "Vague":                      {"icon":"❌","class":"v-vague",     "tag_bg":"#FEE2E2","tag_fg":"#9B1C1C"},
    "Fake Certification Claim":   {"icon":"🚨","class":"v-fake-cert", "tag_bg":"#FEE2E2","tag_fg":"#7F1D1D"},
    "Unverified Statistic":       {"icon":"📉","class":"v-unverified","tag_bg":"#FEF3C7","tag_fg":"#B45309"},
    "Future Promise (Not Evidence)":{"icon":"🗓️","class":"v-future",  "tag_bg":"#FEF3C7","tag_fg":"#92400E"},
    "Uncertain / PR Speak":       {"icon":"⚠️","class":"v-pr",       "tag_bg":"#F3F4F6","tag_fg":"#4B5563"},
    "Backed Claim":               {"icon":"✅","class":"v-backed",    "tag_bg":"#E8F4F0","tag_fg":"#2D6A4F"},
    "Evidence-Based":             {"icon":"📊","class":"v-evidence",  "tag_bg":"#DBEAFE","tag_fg":"#1E3A5F"},
    "Ignored (Website Noise)":    {"icon":"⚪","class":"v-ignored",   "tag_bg":"#F3F4F6","tag_fg":"#9CA3AF"},
}

def verdict_class(v):
    return VERDICT_META.get(v, {}).get("class","v-pr")

def verdict_icon(v):
    return VERDICT_META.get(v, {}).get("icon","ℹ️")

def verdict_tag_html(v):
    m = VERDICT_META.get(v, {"tag_bg":"#F3F4F6","tag_fg":"#4B5563"})
    return (f'<span class="verdict-tag" style="background:{m["tag_bg"]};color:{m["tag_fg"]}">'
            f'{verdict_icon(v)} {v}</span>')

def score_color(s):
    if s >= 0.7: return "var(--score-high)"
    if s >= 0.4: return "var(--score-mid)"
    return "var(--score-low)"

def verdict_pill_class(overall):
    if overall == "Legitimate Claims": return "verdict-green"
    if overall == "Uncertain":         return "verdict-amber"
    return "verdict-red"


# ─────────────────────────────────────────────────────────────
# UI — HEADER
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
  <span class="hero-title">🌿 Green-Truth Auditor</span>
  <span class="hero-badge">Beta</span>
</div>
<p class="hero-sub">
  Paste a sustainability claim or enter a product URL — we'll tell you if it's real or greenwashing.
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOAD RESOURCES
# ─────────────────────────────────────────────────────────────

clf           = load_model()
bcorp, gots, india = load_databases()

# ─────────────────────────────────────────────────────────────
# INPUT CARD
# ─────────────────────────────────────────────────────────────

st.markdown('<div class="input-card"><div class="input-card-title">Input</div>', unsafe_allow_html=True)

input_type = st.radio("", ["Paste text", "Enter URL"], horizontal=True, label_visibility="collapsed")

text = ""
if input_type == "Paste text":
    text = st.text_area(
        "Paste claims here",
        placeholder="e.g. Our jacket is made from 100% recycled ocean plastics, certified by GOTS …",
        height=160,
        label_visibility="collapsed",
    )
else:
    url = st.text_input("Product / brand URL", placeholder="https://example.com/sustainability")
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

col_btn, _ = st.columns([1, 4])
with col_btn:
    run = st.button("Run Audit ›", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# AUDIT + RESULTS
# ─────────────────────────────────────────────────────────────

if run:
    if not text.strip():
        st.warning("Please enter some text or a valid URL first.")
        st.stop()

    with st.spinner("Analysing claims…"):
        report = audit(text, clf, bcorp, gots, india)

    # ── Top metrics ─────────────────────────────────────────
    st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)

    col_score, col_stats = st.columns([1, 2], gap="large")

    with col_score:
        sc      = report["final_score"]
        overall = report["overall"]
        pill_cls = verdict_pill_class(overall)
        st.markdown(f"""
        <div class="score-card">
          <span class="score-label">Credibility Score</span>
          <span class="score-number" style="color:{score_color(sc)}">{sc:.0%}</span>
          <div>
            <span class="verdict-pill {pill_cls}">{overall}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_stats:
        verdicts = [r["verdict"] for r in report["sentences"]]
        counts = {
            "Vague / Fake": verdicts.count("Vague") + verdicts.count("Fake Certification Claim"),
            "Future Promises": verdicts.count("Future Promise (Not Evidence)"),
            "Backed / Evidence": verdicts.count("Backed Claim") + verdicts.count("Evidence-Based"),
            "Uncertain": verdicts.count("Uncertain / PR Speak"),
            "Unverified Stats": verdicts.count("Unverified Statistic"),
            "Ignored": verdicts.count("Ignored (Website Noise)"),
        }
        html_chips = '<div class="stat-grid">'
        for label, val in counts.items():
            html_chips += f"""
            <div class="stat-chip">
              <span class="stat-chip-num">{val}</span>
              <span class="stat-chip-label">{label}</span>
            </div>"""
        html_chips += "</div>"
        st.markdown(html_chips, unsafe_allow_html=True)

    # ── Brand matches ────────────────────────────────────────
    if report["brand_matches"]:
        st.markdown('<div class="section-label">Brand Verification</div>', unsafe_allow_html=True)
        html = '<div class="brand-row">'
        for m in report["brand_matches"]:
            if m["certified"]:
                html += (f'<span class="brand-chip brand-chip-ok">'
                         f'✅ <strong>{m["brand"]}</strong> · {m["cert_type"]}</span>')
            else:
                html += (f'<span class="brand-chip brand-chip-bad">'
                         f'❌ <strong>{m["brand"]}</strong> · Not certified</span>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    # ── Progress bar ─────────────────────────────────────────
    st.progress(report["final_score"])

    # ── Sentence breakdown ───────────────────────────────────
    st.markdown('<div class="section-label">Sentence-by-Sentence Breakdown</div>', unsafe_allow_html=True)

    # Filter controls
    filter_col, _ = st.columns([2, 3])
    with filter_col:
        show_ignored = st.checkbox("Show ignored (non-environmental) sentences", value=False)

    for r in report["sentences"]:
        if not show_ignored and r["verdict"] == "Ignored (Website Noise)":
            continue

        vc   = verdict_class(r["verdict"])
        tag  = verdict_tag_html(r["verdict"])

        flagged_html = ""
        if r.get("flagged"):
            flagged_html = " ".join(
                f'<span class="flagged-word">{w}</span>' for w in r["flagged"]
            )

        st.markdown(f"""
        <div class="sentence-row {vc}">
          <div class="sentence-meta">{tag}</div>
          <div class="sentence-row-text" style="margin-top:0.5rem">{r['sentence']}</div>
          <div class="sentence-meta">
            <span class="reason-text">{r['reason']}</span>
            {flagged_html}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Download report ──────────────────────────────────────
    st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)

    df_export = pd.DataFrame([
        {"sentence": r["sentence"], "verdict": r["verdict"],
         "score": r["score"], "reason": r["reason"],
         "flagged_words": ", ".join(r.get("flagged",[]))}
        for r in report["sentences"]
    ])
    csv_bytes = df_export.to_csv(index=False).encode()
    st.download_button(
        "⬇ Download CSV Report",
        data=csv_bytes,
        file_name="green_truth_audit.csv",
        mime="text/csv",
    )

else:
    # Empty-state illustration
    st.markdown("""
    <div style="text-align:center;padding:3.5rem 0 2rem;color:#9CA3AF">
      <div style="font-size:3.5rem;margin-bottom:1rem">🌿</div>
      <div style="font-size:1rem;font-weight:500;color:#6B6B63">
        Enter a sustainability claim above and click <strong>Run Audit</strong>
      </div>
      <div style="font-size:0.82rem;margin-top:0.4rem">
        Powered by cross-encoder/nli-MiniLM2-L6-H768 · B-Corp · GOTS · India Certifications
      </div>
    </div>
    """, unsafe_allow_html=True)
