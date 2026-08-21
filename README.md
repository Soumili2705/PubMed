# 🧬 Knowway AI — Semantic Literature Discovery

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Groq Cloud](https://img.shields.io/badge/Groq-LLaMA--3.3--70B-F55036.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://groq.com/)
[![NCBI Entrez](https://img.shields.io/badge/NCBI-PubMed%20E--Utilities-326CE5.svg?style=for-the-badge)](https://eutils.ncbi.nlm.nih.gov/)
[![HuggingFace](https://img.shields.io/badge/MiniLM--L6-384--dim%20Dense%20Embeddings-FFD21E.svg?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)

> **Knowway AI — Find your knowledge in the right way.**  
> *Turn complex research questions into relevant, evidence-backed literature — so researchers spend less time searching and more time discovering.*

---

## 🌟 The Product Story: ASK ➔ UNDERSTAND ➔ DISCOVER ➔ TRUST ➔ ACT

1. **ASK**: The researcher inputs a complex natural-language inquiry (e.g. *"early detection biomarkers in Alzheimer's disease"*).
2. **UNDERSTAND**: Knowway uses **MeSH-informed concept mapping** and clinical synonyms to infer the core research intent.
3. **DISCOVER**: NCBI PubMed retrieves candidate trials and dense vector embeddings re-rank abstracts by conceptual alignment.
4. **TRUST**: Every paper features a concise **"Why this matches"** breakdown and honest vector cosine similarity metrics, grounded in verified PMIDs.
5. **ACT**: Researchers can explore literature, read query-dependent evidence summaries, inspect visual analytics, and interact with papers via RAG Q&A.

---

## 🏛️ System Architecture

```
User Research Question 
          │
          ▼
[ 1. Concept Understanding ]  ──► MeSH-Informed Mapping & Clinical Synonyms
          │
          ▼
[ 2. PubMed Retrieval ]       ──► NCBI ESearch & EFetch Live Records
          │
          ▼
[ 3. Semantic Ranking ]       ──► 384-dim SentenceTransformer (Cosine Similarity)
          │
          ▼
[ 4. Evidence Synthesis ]     ──► Query-Dependent LLaMA-3.3 Evidence Briefing
          │
          ▼
[ 5. Knowledge Path UI ]      ──► Evidence Explorer, RAG Q&A, Dossier Export
```

---

## ⚡ Quickstart

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Soumili2705/PubMed.git
cd PubMed
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create or edit `.env` in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
NCBI_EMAIL=your_email@domain.com
```

### 3. Launch the Application
```bash
streamlit run app.py
```
