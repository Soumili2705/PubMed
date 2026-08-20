"""
Knowway AI — UI Components Module.
Story-driven biomedical research interface: ASK → UNDERSTAND → DISCOVER → TRUST → ACT.
"""
from __future__ import annotations
import html
import streamlit as st

def render_hero_header():
  """Renders the Google AI Studio-inspired top banner."""
  st.markdown("""<div class="studio-top-header">
<div class="studio-logo-group">
  <div class="studio-logo-icon">🧬</div>
  <div>
    <h1 class="studio-title-main">Knowway AI <span class="studio-badge-sub">Biomedical Discovery</span></h1>
    <p class="studio-tagline">Find your knowledge in the right way.</p>
  </div>
</div>
<div class="studio-pipeline-pill">
  <span>🧭 Path:</span>
  <span style="color:#2563EB;">ASK</span> ➔ <span style="color:#0D9488;">UNDERSTAND</span> ➔ <span style="color:#4F46E5;">DISCOVER</span> ➔ <span style="color:#059669;">TRUST</span> ➔ <span style="color:#0F172A; font-weight:700;">ACT</span>
</div>
</div>""", unsafe_allow_html=True)


def derive_research_intent(query: str, mesh_terms: list, clinical_terms: list) -> str:
  """Derives concise, honest research intent label from query concepts."""
  q = query.lower()
  intents = []
  if any(w in q for w in ["early", "detection", "detect", "biomarker", "screen"]): intents.append("Early Detection & Biomarkers")
  if any(w in q for w in ["treatment", "therapy", "trial", "efficacy", "drug", "inhibitor"]): intents.append("Therapeutic Efficacy & Clinical Trials")
  if any(w in q for w in ["guideline", "management", "acute", "protocol"]): intents.append("Clinical Management & Guidelines")
  if any(w in q for w in ["mechanism", "pathophysiology", "pathway", "damage", "cause"]): intents.append("Pathophysiology & Disease Progression")
  return " · ".join(intents) if intents else (f"{mesh_terms[0]} Investigation" if mesh_terms else "Targeted Literature Investigation")


def render_understood_section(query: str, mesh_terms: list, clinical_terms: list):
  """Renders the '1. WE UNDERSTOOD YOUR QUESTION' concept understanding card."""
  unique = []
  seen = set()
  for t in mesh_terms + clinical_terms:
    if t.lower() not in seen and len(t.strip()) > 1:
      seen.add(t.lower()); unique.append(t)
  if not unique: unique = [w.capitalize() for w in query.split() if len(w) > 3][:4]
  tags_html = "".join([f"<span class='concept-tag'>🏷️ {html.escape(c)}</span>" for c in unique])
  intent = derive_research_intent(query, mesh_terms, clinical_terms)
  st.markdown(f"""<div class="understood-box">
<div class="understood-header">1. We Understood Your Research Focus</div>
<div style="margin-bottom:8px;">{tags_html}</div>
<div style="font-size:13px; color:#475569; margin-top:8px;"><strong>🎯 Inferred Intent:</strong> <span class="intent-tag">{html.escape(intent)}</span></div>
</div>""", unsafe_allow_html=True)


def derive_why_this_matches(paper: dict, concepts: list[str]) -> str:
  """Derives non-hallucinated 'Why this matches' explanation from paper abstract."""
  text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()
  matched = [c for c in concepts if c.lower() in text]
  if not matched:
    for tok in ["biomarker", "trial", "therapy", "clinical", "mechanism", "cohort", "pediatric", "elderly"]:
      if tok in text: matched.append(tok.capitalize())
  return " · ".join(matched[:4]) if matched else "Direct semantic alignment with inquiry concepts & study endpoints"


def render_paper_card(paper: dict, index: int, all_concepts: list[str] | None = None):
  """Renders a paper card: Title → Why this matches → Similarity → Metadata."""
  concepts = all_concepts or []
  raw_cosine = paper.get("raw_score", paper.get("similarity_score", 0.0))
  pmid = paper.get("pmid", "N/A")
  title, journal, year, author, abstract = paper.get("title", "Untitled"), paper.get("journal", "PubMed Indexed"), paper.get("year", "Recent"), paper.get("author", ""), paper.get("abstract", "No abstract available.")
  url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid != "N/A" else "https://pubmed.ncbi.nlm.nih.gov/"
  why = derive_why_this_matches(paper, concepts)
  rel = "High relevance" if raw_cosine >= 0.65 else ("Moderate relevance" if raw_cosine >= 0.45 else "Baseline relevance")
  author_chip = f'<span class="meta-chip-clean">👤 {html.escape(author)}</span>' if author else ""
  
  st.markdown(f"""<div class="paper-card-clean">
<a href="{url}" target="_blank" class="paper-title-link">#{index}. {html.escape(title)}</a>
<div class="why-matches-box"><span class="why-matches-label">💡 Why this matches:</span><span>{html.escape(why)}</span></div>
<div style="margin-bottom:6px;">
  <span class="sim-badge">🎯 {rel} · <span class="sim-badge-score">{raw_cosine:.3f} similarity</span></span>
  <span class="meta-chip-clean">📚 {html.escape(journal)}</span>
  <span class="meta-chip-clean">📅 {html.escape(str(year))}</span>
  {author_chip}
  <span class="meta-chip-clean">🆔 PMID: {pmid}</span>
</div>
</div>""", unsafe_allow_html=True)
  
  citation = f"{author + ' ' if author else ''}{title}. {journal} ({year}). PMID: {pmid}."
  with st.expander(f"📖 Read Full Abstract & Citation for #{index} (PMID {pmid})"):
    st.markdown(f"**Abstract:**\n\n{abstract}\n\n---\n**APA Citation:** `{citation}`")
    st.link_button("🔗 View on PubMed", url, use_container_width=True)


def render_researcher_impact():
  """Renders the value-oriented story section."""
  st.markdown("""<div style="background:var(--bg-card); border:1px solid var(--glass-border); border-radius:16px; padding:20px 24px; margin:22px 0;">
<h4 style="margin:0 0 4px 0; font-size:16px; font-weight:800; color:#0F172A;">💡 Researcher Impact</h4>
<p style="margin:0 0 12px 0; font-size:13px; color:#64748B;">How Knowway AI transforms scientific literature exploration:</p>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px;">
  <div style="background:rgba(255,255,255,0.6); border:1px solid #E2E8F0; border-radius:10px; padding:12px; text-align:center;">
    <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Before</div>
    <div style="font-size:12.5px; font-weight:600; color:#0F172A; margin-top:3px;">Hours of manual keyword & Boolean screening</div>
  </div>
  <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px; padding:12px; text-align:center;">
    <div style="font-size:11px; font-weight:700; color:#2563EB; text-transform:uppercase;">With Knowway AI</div>
    <div style="font-size:12.5px; font-weight:600; color:#1E3A8A; margin-top:3px;">Concept-aware discovery + ranked evidence</div>
  </div>
  <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:12px; text-align:center;">
    <div style="font-size:11px; font-weight:700; color:#0D9488; text-transform:uppercase;">Outcome</div>
    <div style="font-size:12.5px; font-weight:600; color:#14532D; margin-top:3px;">Faster discovery and more focused research</div>
  </div>
</div>
</div>""", unsafe_allow_html=True)


def render_how_it_works():
  """Renders the architecture dropdown."""
  with st.expander("⚙ How Knowway AI Works — Architecture & Retrieval Pipeline"):
    st.markdown("""<div style="padding:6px 0; font-size:12.5px; color:#64748B; line-height:1.6;">
<div style="font-size:13.5px; font-weight:600; color:#2563EB; margin-bottom:8px;">Question ➔ Concept Understanding ➔ PubMed Retrieval ➔ Semantic Ranking ➔ Evidence Synthesis</div>
• <strong>Concept Understanding:</strong> Mapped against NLM MeSH ontology descriptors and clinical synonyms.<br>
• <strong>PubMed Retrieval:</strong> NCBI Entrez API queries live PubMed repository records with title/abstract precision.<br>
• <strong>Semantic Ranking:</strong> 384-dim dense vector embeddings calculate cosine similarities against intent.<br>
• <strong>Evidence Synthesis:</strong> Groq LLaMA models generate concise briefings grounded in verified PMIDs.
</div>""", unsafe_allow_html=True)


def generate_dossier_markdown(query: str, translation: dict, papers: list, ai_report: str, latency: float, timings: dict | None = None) -> str:
  """Generates structured literature dossier in clean Markdown for export."""
  mesh_str, clinical_str = ", ".join(translation.get("mesh_terms", [])), ", ".join(translation.get("clinical_terms", []))
  bool_query = translation.get("pubmed_query", "")
  papers_md = "\n---\n".join([f"### {i}. {p.get('title')}\n- **Similarity**: {p.get('raw_score', p.get('similarity_score', 0.0)):.3f} | **Journal**: {p.get('journal', 'PubMed')} ({p.get('year', 'N/A')}) | **PMID**: [{p.get('pmid')}](https://pubmed.ncbi.nlm.nih.gov/{p.get('pmid')}/)\n- **Abstract Summary**: {p.get('abstract', '')[:350]}..." for i, p in enumerate(papers, 1)])
  return f"""# 🧬 Evidence Dossier: {query}
**Generated by Knowway AI**  
*Pipeline Latency: {latency:.2f}s | Verified PubMed records*

---
## 📋 Interpreted Research Focus
- **Research Question**: {query}
- **Concepts**: {mesh_str} | **Synonyms**: {clinical_str}
- **PubMed Boolean Query**: `{bool_query}`

---
## 📝 Evidence Summary
{ai_report}

---
## 📚 Discovered Literature ({len(papers)} Studies)
{papers_md}

*Knowway AI — Find your knowledge in the right way.*"""

