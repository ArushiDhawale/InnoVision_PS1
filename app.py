import streamlit as st
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title="Green-Truth Auditor", layout="wide", page_icon="🌿")

# --- GREENWASHING DICTIONARIES ---
VAGUE_BUZZWORDS = [
    "eco-friendly", "eco conscious", "green", "natural", "all-natural",
    "sustainable", "sustainability", "ethical", "conscious", "planet-friendly",
    "earth-friendly", "responsible", "clean", "organic", "biodegradable",
    "carbon neutral", "net zero", "cruelty-free", "good for the planet", "mindful"
]

EVIDENCE_KEYWORDS = [
    "b-corp", "bcorp", "gots", "fsc", "oeko-tex", "bluesign", "fair trade", 
    "carbon trust", "ecocert", "eu ecolabel", "%", "percent", "kg", "tonnes",
    "third-party", "independently verified", "audited", "certified", "scope 1", "lca"
]

# --- FUNCTIONS ---
def draw_gauge(score, title="Truth & Transparency Score"):
    """Draws a Plotly gauge chart."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1E1E1E"},
            'steps': [
                {'range': [0, 40], 'color': "#ff4b4b"},    # Red / High Risk
                {'range': [40, 75], 'color': "#ffa500"},   # Orange / Mixed
                {'range': [75, 100], 'color': "#2ecc71"}   # Green / Transparent
            ]}))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def scrape_url(url):
    """Scrapes main paragraph text from a URL, spoofing a real browser."""
    try:
        # Spoofing a standard web browser to bypass basic bot blockers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code in [403, 401]:
            return "BLOCKED"
            
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Strip out scripts, styles, and footers
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
            
        # Get visible paragraph text
        paragraphs = soup.find_all(['p', 'li', 'span', 'h2'])
        text_chunks = [p.get_text(separator=" ", strip=True) for p in paragraphs]
        
        # Filter out tiny UI fragments and join
        valid_text = " ".join([t for t in text_chunks if len(t) > 20])
        return valid_text[:4000] # Limit to first 4000 characters
        
    except Exception as e:
        return None

def analyze_text(text):
    """Audits text for buzzwords vs. evidence."""
    text_lower = text.lower()
    
    found_buzzwords = set(word for word in VAGUE_BUZZWORDS if word in text_lower)
    found_evidence = set(word for word in EVIDENCE_KEYWORDS if word in text_lower)
    
    # Simple Scoring Logic
    base_score = 50
    penalty = len(found_buzzwords) * 15
    bonus = len(found_evidence) * 25
    
    final_score = max(0, min(100, base_score - penalty + bonus))
    
    # Split into sentences for detailed breakdown
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    return {
        "score": final_score,
        "buzzwords": list(found_buzzwords),
        "evidence": list(found_evidence),
        "sentences": sentences
    }

# --- UI LAYOUT ---
st.title("🌿 Green-Truth Auditor")
st.markdown("Analyze product descriptions for greenwashing using structural logic and keyword verification.")

# --- INPUT SECTION ---
input_mode = st.radio("Choose Input Method:", ["🔗 URL Analyzer", "📝 Text Description"], horizontal=True)

source_text = ""
if input_mode == "🔗 URL Analyzer":
    url_input = st.text_input("Paste Brand URL (Note: Amazon/Flipkart may block scrapers):", placeholder="https://www.example.com/product")
    if st.button("🚀 Run Deep Audit", type="primary") and url_input:
        with st.spinner("🕷️ Scraping product webpage..."):
            source_text = scrape_url(url_input)
            if source_text == "BLOCKED":
                st.error("🚨 This website actively blocks automated scrapers (Common with Amazon). Please copy and paste the text manually.")
                source_text = ""
            elif not source_text or len(source_text) < 30:
                st.error("Could not extract enough readable text from this URL. Please paste text manually.")
                source_text = ""

elif input_mode == "📝 Text Description":
    text_input = st.text_area("Paste Product Description:", height=150, placeholder="Our products are 100% eco-friendly and good for the planet...")
    if st.button("🚀 Run Deep Audit", type="primary") and text_input:
        source_text = text_input

# --- RESULTS SECTION ---
if source_text:
    st.divider()
    
    # Run the audit
    audit_results = analyze_text(source_text)
    score = audit_results["score"]
    
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.plotly_chart(draw_gauge(score), width="stretch")
        
    with c2:
        if score >= 75:
            st.success("### ✅ Evidence-Based Claim")
            st.write("This product relies on verifiable data and certifications rather than marketing fluff.")
        elif score >= 40:
            st.warning("### ⚠️ Partial Greenwashing")
            st.write("This description contains some valid claims, but relies heavily on vague environmental buzzwords.")
        else:
            st.error("### ❌ High Greenwashing Risk")
            st.write("This product uses deceptive or highly vague marketing terms with zero measurable proof or certifications.")
            
        st.markdown("**Findings:**")
        if audit_results["buzzwords"]:
            st.markdown(f"🚩 **Vague Buzzwords found:** `{', '.join(audit_results['buzzwords'])}`")
        if audit_results["evidence"]:
            st.markdown(f"✅ **Verifiable Evidence found:** `{', '.join(audit_results['evidence'])}`")
        if not audit_results["evidence"] and not audit_results["buzzwords"]:
            st.markdown("ℹ️ No specific environmental claims detected in this text.")

    st.divider()

    # --- DETAILED BREAKDOWN ---
    st.subheader("🕵️ Detailed Sentence Breakdown")
    
    for sentence in audit_results["sentences"]:
        if len(sentence) < 15: continue
        
        s_lower = sentence.lower()
        has_buzz = any(b in s_lower for b in VAGUE_BUZZWORDS)
        has_evid = any(e in s_lower for e in EVIDENCE_KEYWORDS)
        
        if has_evid:
            with st.expander(f"✅ **PASS:** {sentence[:80]}..."):
                st.write(f"**Full Sentence:** {sentence}")
        elif has_buzz and not has_evid:
            with st.expander(f"❌ **FAIL:** {sentence[:80]}..."):
                st.write(f"**Full Sentence:** {sentence}")
                st.error("Contains vague buzzwords with no supporting evidence.")
