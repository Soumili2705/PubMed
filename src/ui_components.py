"""Knowway AI — UI Components. ASK → UNDERSTAND → DISCOVER → TRUST → ACT."""
from __future__ import annotations
import html
import streamlit as st


# ─────────────────────────────────────────────────────────────────
# HERO HEADER — Navy version (kept as primary visual anchor)
# ─────────────────────────────────────────────────────────────────
def render_hero_header():
    st.markdown("""<div class="kw-hero">
  <div class="kw-hero-left">
    <div class="kw-hero-icon">🧬</div>
    <div>
      <div class="kw-hero-title">Knowway AI<span class="kw-hero-badge">Biomedical Discovery</span></div>
      <div class="kw-hero-sub">Find your knowledge in the right way. · Biomedical Literature Intelligence</div>
    </div>
  </div>
  <div class="kw-pipe">
    <span class="kw-pipe-step">ASK</span>
    <span class="kw-pipe-arrow">→</span>
    <span class="kw-pipe-step">UNDERSTAND</span>
    <span class="kw-pipe-arrow">→</span>
    <span class="kw-pipe-step">DISCOVER</span>
    <span class="kw-pipe-arrow">→</span>
    <span class="kw-pipe-step">TRUST</span>
    <span class="kw-pipe-arrow">→</span>
    <span class="kw-pipe-step">ACT</span>
  </div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# INTRO CARD — Live NCBI PubMed + 3 knowledge feature cards
# ─────────────────────────────────────────────────────────────────
def render_intro_card():
    st.markdown("""<div class="kw-card">
  <div class="kw-eyebrow">LIVE EVIDENCE DISCOVERY</div>
  <div class="kw-intro-title">From research question to verified evidence.</div>
  <p class="kw-intro-desc">
    Search live PubMed literature with <strong>MeSH-informed retrieval</strong> and semantic ranking.
    Every result keeps its PMID, so the evidence remains easy to verify.
  </p>
  <div class="kw-features">
    <div class="kw-feature">
      <div class="kw-feature-title">Understand</div>
      <p class="kw-feature-text">Maps clinical language into searchable concepts.</p>
    </div>
    <div class="kw-feature">
      <div class="kw-feature-title">Retrieve</div>
      <p class="kw-feature-text">Finds live PubMed records with verified PMIDs.</p>
    </div>
    <div class="kw-feature">
      <div class="kw-feature-title">Prioritize</div>
      <p class="kw-feature-text">Ranks abstracts by estimated semantic relevance.</p>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# UNDERSTOOD SECTION
# ─────────────────────────────────────────────────────────────────
def _derive_intent(query: str, mesh_terms: list, clinical_terms: list) -> str:
    q = query.lower()
    tags = []
    if any(w in q for w in ["early", "detection", "biomarker", "screen"]):
        tags.append("Early Detection & Biomarkers")
    if any(w in q for w in ["treatment", "therapy", "trial", "efficacy", "drug"]):
        tags.append("Therapeutic Efficacy")
    if any(w in q for w in ["guideline", "management", "acute", "protocol"]):
        tags.append("Clinical Management")
    if any(w in q for w in ["mechanism", "pathophysiology", "pathway", "damage"]):
        tags.append("Pathophysiology")
    return " · ".join(tags) if tags else (
        f"{mesh_terms[0]} Investigation" if mesh_terms else "Literature Investigation"
    )


def render_understood_section(query, mesh_terms, clinical_terms, facets=None, pubmed_query=None):
    seen, unique = set(), []
    for t in mesh_terms + clinical_terms:
        if t.lower() not in seen and len(t.strip()) > 1:
            seen.add(t.lower()); unique.append(t)
    if not unique:
        unique = [w.capitalize() for w in query.split() if len(w) > 3][:5]

    visible, hidden_count = unique[:8], max(0, len(unique) - 8)
    tags = "".join(f"<span class='kw-tag'>🏷 {html.escape(c)}</span>" for c in visible)
    if hidden_count:
        tags += f"<span class='kw-tag'>+{hidden_count} more</span>"
    intent = (facets or {}).get("intent") or _derive_intent(query, mesh_terms, clinical_terms)

    facet_html = ""
    if facets:
        chips = []
        for key, label in [
            ("condition", "Condition"),
            ("intervention_or_biomarker", "Biomarker/Tool"),
            ("population", "Population"),
            ("outcome_or_intent", "Outcome"),
        ]:
            if facets.get(key):
                chips.append(
                    f"<span class='kw-facet'><strong>{label}:</strong>&nbsp;"
                    f"{html.escape(str(facets[key]))}</span>"
                )
        if chips:
            facet_html = f"<div style='margin-top:7px;'>{''.join(chips)}</div>"

    query_html = ""
    if pubmed_query:
        query_html = (
            f"<div style='margin-top:9px;background:rgba(255,255,255,0.80);"
            f"border:1px solid rgba(203,213,225,0.65);border-radius:8px;padding:6px 11px;'>"
            f"<span style='font-size:10px;font-weight:700;color:#64748B;text-transform:uppercase;"
            f"letter-spacing:0.07em;'>📡 Generated PubMed Boolean</span><br>"
            f"<code style='font-size:11.5px;color:#1D4ED8;word-break:break-all;"
            f"font-family:var(--mono);'>{html.escape(pubmed_query)}</code></div>"
        )

    st.markdown(f"""<div class="kw-understood">
<div class="kw-understood-title">✅ We Understood Your Research Focus</div>
<div style="margin-bottom:5px;">{tags}</div>
{facet_html}
<div style="font-size:12.5px;color:#334155;margin-top:9px;">
  <strong>🎯 Inferred Intent:</strong><span class="kw-intent">{html.escape(intent)}</span>
</div>
{query_html}
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PAPER CARD
# ─────────────────────────────────────────────────────────────────
def _why_matches(paper: dict, concepts: list) -> str:
    text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()
    matched = [c for c in concepts if c.lower() in text]
    if not matched:
        for tok in ["biomarker","trial","therapy","clinical","mechanism","cohort","pediatric","elderly"]:
            if tok in text: matched.append(tok.capitalize())
    return " · ".join(matched[:4]) if matched else "Direct semantic alignment with study concepts & endpoints"


def render_paper_card(paper: dict, index: int, all_concepts: list | None = None):
    c        = all_concepts or []
    score    = paper.get("raw_score", paper.get("similarity_score", 0.0))
    pmid     = paper.get("pmid", "N/A")
    title    = paper.get("title", "Untitled")
    journal  = paper.get("journal", "PubMed Indexed")
    year     = str(paper.get("year", "Recent"))
    author   = paper.get("author", "")
    abstract = paper.get("abstract", "No abstract available.")
    url      = (f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                if pmid != "N/A" else "https://pubmed.ncbi.nlm.nih.gov/")
    why      = _why_matches(paper, c)
    rel      = ("🟢 High Relevance" if score >= 0.65
                else ("🟡 Moderate Relevance" if score >= 0.45 else "⚪ Baseline Relevance"))
    auth_chip = f'<span class="kw-chip">👤 {html.escape(author)}</span>' if author else ""

    st.markdown(f"""<div class="kw-paper">
  <span class="kw-paper-rank">#{index}</span>
  <a href="{url}" target="_blank" class="kw-paper-title">{html.escape(title)}</a>
  <div class="kw-why"><span class="kw-why-lbl">💡 Why this matches:</span>{html.escape(why)}</div>
  <div>
    <span class="kw-sim">{rel} &nbsp;·&nbsp; <span class="kw-sim-score">Semantic Relevance {score:.3f}</span></span>
    <span class="kw-chip">📚 {html.escape(journal)}</span>
    <span class="kw-chip">📅 {html.escape(year)}</span>
    {auth_chip}
    <span class="kw-chip">🆔 PMID {pmid}</span>
  </div>
</div>""", unsafe_allow_html=True)

    citation = f"{author + ' ' if author else ''}{title}. {journal} ({year}). PMID: {pmid}."
    with st.expander(f"📖 Abstract & Citation — #{index} · PMID {pmid}"):
        st.markdown(f"**Abstract:**\n\n{abstract}\n\n---\n**Citation:** `{citation}`")
        st.link_button("🔗 View on PubMed", url, use_container_width=True)


# ─────────────────────────────────────────────────────────────────
# RESEARCHER IMPACT
# ─────────────────────────────────────────────────────────────────
def render_researcher_impact():
    st.markdown("""<div class="kw-card" style="margin-top:16px;">
<div style="font-size:10px;font-weight:700;letter-spacing:0.10em;text-transform:uppercase;
color:var(--faint);margin-bottom:10px;">💡 Researcher Impact</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:9px;">
  <div style="background:rgba(248,250,252,0.9);border:1px solid var(--border);border-radius:9px;
  padding:12px;text-align:center;">
    <div style="font-size:9.5px;font-weight:700;color:var(--faint);text-transform:uppercase;letter-spacing:.07em;">Before</div>
    <div style="font-size:12.5px;font-weight:600;color:var(--ink);margin-top:4px;line-height:1.4;">Hours of manual keyword &amp; Boolean screening</div>
  </div>
  <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:9px;padding:12px;text-align:center;">
    <div style="font-size:9.5px;font-weight:700;color:#1D4ED8;text-transform:uppercase;letter-spacing:.07em;">With Knowway AI</div>
    <div style="font-size:12.5px;font-weight:600;color:#1E3A8A;margin-top:4px;line-height:1.4;">Concept-aware discovery + ranked evidence</div>
  </div>
  <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:9px;padding:12px;text-align:center;">
    <div style="font-size:9.5px;font-weight:700;color:#0D9488;text-transform:uppercase;letter-spacing:.07em;">Outcome</div>
    <div style="font-size:12.5px;font-weight:600;color:#14532D;margin-top:4px;line-height:1.4;">Faster, more focused research decisions</div>
  </div>
</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# HOW IT WORKS
# ─────────────────────────────────────────────────────────────────
def render_how_it_works():
    with st.expander("⚙ How Knowway AI Works — Architecture & Scope"):
        st.markdown("""<div style="font-size:13px;color:#475569;line-height:1.7;padding:4px 0;">
<div style="font-size:13px;font-weight:700;color:#1D4ED8;margin-bottom:8px;">
Question → Concept Understanding → PubMed Retrieval → Semantic Ranking → Evidence Synthesis
</div>
<b>Concept Understanding:</b> MeSH-informed concept mapping and clinical synonyms via PICO facet extraction.<br>
<b>PubMed Retrieval:</b> NCBI Entrez API queries live PubMed repository records with title/abstract Boolean precision.<br>
<b>Semantic Ranking:</b> 384-dim MiniLM dense vector embeddings calculate cosine similarities against research intent.<br>
<b>Evidence Synthesis:</b> Groq LLaMA models generate concise briefings grounded in verified PMIDs.<br><br>
<div style="font-size:11px;color:#64748B;border-top:1px solid #E2E8F0;padding-top:6px;">
🛡 <em>Knowway AI accelerates literature discovery and triage; it does not replace researcher judgment or systematic clinical review.</em>
</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# DOSSIER EXPORT
# ─────────────────────────────────────────────────────────────────
def generate_dossier_markdown(query, translation, papers, ai_report, latency, timings=None):
    mesh_str     = ", ".join(translation.get("mesh_terms", []))
    clinical_str = ", ".join(translation.get("clinical_terms", []))
    bool_query   = translation.get("pubmed_query", "")
    papers_md    = "\n---\n".join([
        f"### {i}. {p.get('title')}\n"
        f"- **Semantic Relevance**: {p.get('raw_score', p.get('similarity_score', 0.0)):.3f} | "
        f"**Journal**: {p.get('journal','PubMed')} ({p.get('year','N/A')}) | "
        f"**PMID**: [{p.get('pmid')}](https://pubmed.ncbi.nlm.nih.gov/{p.get('pmid')}/)\n"
        f"- **Abstract Summary**: {p.get('abstract','')[:350]}..."
        for i, p in enumerate(papers, 1)
    ])
    return f"""# 🧬 Evidence Dossier: {query}
**Knowway AI** | Latency: {latency:.2f}s | PubMed-verified

---
## Research Focus
- **Question**: {query}
- **MeSH Terms**: {mesh_str}
- **Clinical Synonyms**: {clinical_str}
- **PubMed Boolean**: `{bool_query}`

---
## Evidence Summary
{ai_report}

---
## Discovered Literature ({len(papers)} studies)
{papers_md}

*Knowway AI — Find your knowledge in the right way.*"""
