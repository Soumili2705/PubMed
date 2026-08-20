from __future__ import annotations
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st


@st.cache_resource(show_spinner="🧬 Loading 384-dim Dense Vector Model...")
def get_embedding_model():
  """Loads and caches the all-MiniLM-L6-v2 model for instant vector inference."""
  return SentenceTransformer("all-MiniLM-L6-v2")


def rank_papers(
    query: str, papers: list[dict], clinical_terms: list[str] | None = None
) -> list[dict]:
  """Ranks retrieved PubMed papers using lightweight, medically-sharp title & ontology intent weighting."""
  if not papers:
    return []

  model = get_embedding_model()

  # Build an enriched clinical intent query
  clinical_context = ", ".join(clinical_terms) if clinical_terms else query
  target_intent = (
      f"Clinical Topic: {query}. Target Pathology & Focus: {clinical_context}."
      " Primary human trial outcomes and treatment endpoints."
  )

  query_embedding = model.encode([target_intent])

  # Medically Sharp Structuring: Puts Title & Core Medical Focus first so primary endpoints rank highest
  paper_texts = []
  for p in papers:
    title = p.get("title", "Untitled Study")
    abstract = p.get("abstract", "")
    paper_texts.append(
        f"Title: {title}. Focus: {clinical_context}. Abstract: {abstract}"
    )

  paper_embeddings = model.encode(paper_texts)

  raw_similarities = cosine_similarity(query_embedding, paper_embeddings)[0]

  ranked_papers = []
  for paper, raw_score in zip(papers, raw_similarities):
    ranked = paper.copy()
    # Calibrate cosine score to standard 0-100% confidence curve
    calibrated = float(
        np.clip(1.0 / (1.0 + np.exp(-12 * (raw_score - 0.40))), 0.10, 0.98)
    )
    ranked["similarity_score"] = calibrated
    ranked["raw_score"] = float(raw_score)
    ranked_papers.append(ranked)

  # Sort by highest semantic relevance
  ranked_papers.sort(key=lambda p: p["similarity_score"], reverse=True)
  return ranked_papers