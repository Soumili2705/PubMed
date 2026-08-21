from __future__ import annotations
import os
import re
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

load_dotenv()

FAST_MODELS = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
DEEP_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]


def _get_groq_client() -> Groq | None:
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and api_key.strip():
        try:
            return Groq(api_key=api_key.strip())
        except Exception:
            return None
    return None


def _format_context(papers: list[dict], max_papers: int = 5, max_abstract_len: int = 650) -> str:
    """Formats retrieved papers into structured prompt context."""
    blocks: list[str] = []
    for i, p in enumerate(papers[:max_papers], start=1):
        pmid = p.get("pmid", "N/A")
        title = p.get("title", "No Title")
        journal = p.get("journal", "PubMed")
        year = p.get("year", "N/A")
        abstract = p.get("abstract", "No abstract available.")
        if len(abstract) > max_abstract_len:
            abstract = abstract[:max_abstract_len] + "..."
        blocks.append(
            f"STUDY #{i} [PMID: {pmid}]\nTitle: {title}\nJournal: {journal} ({year})\nAbstract: {abstract}"
        )
    return "\n\n".join(blocks)


def _call_groq(system_prompt: str, user_prompt: str, models: list[str], max_tokens: int = 950) -> str | None:
    """Executes completion with fallback across candidate models."""
    client = _get_groq_client()
    if not client:
        return None

    for model_id in models:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=max_tokens,
            )
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
        except Exception:
            continue
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def generate_summary(query: str, papers: list[dict], fast_mode: bool = True) -> str:
    """Synthesizes an evidence-grounded clinical briefing strictly from retrieved abstracts."""
    if not papers:
        return "No candidate papers available for clinical synthesis."

    context = _format_context(papers, max_papers=5, max_abstract_len=650)
    prompt = f"""You are an elite biomedical evidence synthesist.
Synthesize a precise, evidence-grounded clinical briefing to directly answer the user's research query.

USER RESEARCH QUERY: "{query}"

RETRIEVED LITERATURE (Grounding Evidence):
{context}

CRITICAL INSTRUCTIONS:
1. Ground every claim STRICTLY in the provided study excerpts above. Do NOT introduce external medical facts.
2. Adapt your answer specifically to the nature of the query (diagnostics, trials, or guidelines).
3. Always cite the exact PubMed ID like [PMID: XXXXXXXX] for every scientific claim.

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
### 💡 Evidence Synthesis
(2-3 precise sentences directly answering the question using study data. Cite PMIDs.)

### 🔬 Key Findings from Retrieved Evidence
- **Finding 1**: (Specific finding with [PMID: XXXXXXXX])
- **Finding 2**: (Specific finding with [PMID: XXXXXXXX])
- **Finding 3**: (Specific finding with [PMID: XXXXXXXX])

### 📊 Evidence Matrix
| PMID | Primary Study | Year | Key Supported Finding |
| :--- | :--- | :--- | :--- |
(Rows for top 3-4 papers citing exact PMIDs with Markdown links: [PMID: XXXXXXXX](https://pubmed.ncbi.nlm.nih.gov/XXXXXXXX/))

### ⚠️ Evidence Gaps & Study Limitations
- (1-2 specific limitations mentioned or inherent in the abstracts)
"""

    models = FAST_MODELS if fast_mode else DEEP_MODELS
    sys_prompt = "You are an evidence-grounded biomedical research assistant. Strictly cite PMIDs and avoid hallucination."
    
    if result := _call_groq(sys_prompt, prompt, models, max_tokens=950):
        return result

    # Extractive Fallback
    top_papers = papers[:4]
    rows, key_bullets = [], []
    for p in top_papers:
        pmid, title, year = p.get("pmid", "N/A"), p.get("title", "Clinical Study"), p.get("year", "Recent")
        abstract = p.get("abstract", "")
        sentences = [
            s.strip() for s in re.split(r"\. |\n", abstract)
            if len(s.strip()) > 30 and not s.lower().startswith("background")
        ]
        finding = sentences[0][:117] + "..." if sentences else "Clinical evidence evaluated."
        rows.append(f"| [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) | {title[:45]}... | {year} | {finding} |")
        key_bullets.append(f"- **{title[:60]}...**: {finding} [PMID: {pmid}]")

    first_p = top_papers[0]
    return f"""### 💡 Evidence Synthesis
Extractive overview of retrieved PubMed abstracts for *"{query}"*. Top study: **{first_p.get('title')}** [PMID: {first_p.get('pmid')}].

### 🔬 Key Findings from Retrieved Evidence
{"".join(key_bullets[:3])}

### 📊 Evidence Matrix
| PMID | Primary Study | Year | Key Supported Finding |
| :--- | :--- | :--- | :--- |
{"".join(rows)}

### ⚠️ Evidence Gaps & Study Limitations
- Limitations are not consistently available in abstracts; review full publications before drawing conclusions.
"""


def answer_rag_question(
    question: str, papers: list[dict], chat_history: list[dict] | None = None
) -> str:
    """Answers interactive follow-up questions strictly grounded in the retrieved PubMed study abstracts."""
    if not papers:
        return "Please execute a search first to retrieve clinical literature for Q&A."

    context = _format_context(papers, max_papers=6, max_abstract_len=800)
    prompt = f"""You are a clinical AI research assistant. Answer the question using ONLY the retrieved studies below.
Cite exact PMIDs (e.g. [PMID: 12345678]). If not present, state: "The retrieved studies do not contain specific data regarding this question."

Retrieved Literature:
{context}

User Question: {question}"""

    sys_prompt = "You are an evidence-based clinical literature assistant. Strictly ground answers in the provided text and cite PMIDs."
    if result := _call_groq(sys_prompt, prompt, FAST_MODELS, max_tokens=650):
        return result

    top_p = papers[0]
    return (
        f"According to *'{top_p.get('title')}'* [PMID: {top_p.get('pmid')}], the retrieved evidence addresses "
        f"aspects of '{question}'. Inspect the Evidence Explorer for complete quantitative metrics."
    )
