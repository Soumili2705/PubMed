from __future__ import annotations
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

MODEL_NAME = "all-MiniLM-L6-v2"
SIGMOID_MIDPOINT = 0.40
SIGMOID_STEEPNESS = -12.0
SCORE_MIN_CLIP = 0.10
SCORE_MAX_CLIP = 0.98


@st.cache_resource(show_spinner="🧬 Loading 384-dim Dense Vector Model...")
def get_embedding_model() -> SentenceTransformer:
    """Loads, caches, and warms up the dense vector model for instant inference."""
    model = SentenceTransformer(MODEL_NAME)
    try:
        model.encode(["Biomedical literature warmup query"])
    except Exception:
        pass
    return model


def _calibrate_similarity(raw_score: float) -> float:
    """Non-linear sigmoid transformation to calibrate raw cosine score into confidence percentage."""
    scaled = 1.0 / (1.0 + np.exp(SIGMOID_STEEPNESS * (raw_score - SIGMOID_MIDPOINT)))
    return float(np.clip(scaled, SCORE_MIN_CLIP, SCORE_MAX_CLIP))


def rank_papers(
    query: str, papers: list[dict], clinical_terms: list[str] | None = None
) -> list[dict]:
    """Ranks retrieved PubMed papers using dense semantic embeddings and intent calibration."""
    if not papers:
        return []

    model = get_embedding_model()
    clinical_context = ", ".join(clinical_terms) if clinical_terms else query
    target_intent = (
        f"Clinical Topic: {query}. Target Pathology & Focus: {clinical_context}."
        " Primary human trial outcomes and treatment endpoints."
    )

    query_embedding = model.encode([target_intent])
    paper_texts = [
        f"Title: {p.get('title', 'Untitled Study')}. Abstract: {p.get('abstract', '')}"
        for p in papers
    ]
    paper_embeddings = model.encode(paper_texts)
    raw_similarities = cosine_similarity(query_embedding, paper_embeddings)[0]

    ranked_papers: list[dict] = []
    for paper, raw_score in zip(papers, raw_similarities):
        ranked = paper.copy()
        ranked["similarity_score"] = _calibrate_similarity(float(raw_score))
        ranked["raw_score"] = float(raw_score)
        ranked_papers.append(ranked)

    ranked_papers.sort(key=lambda p: p["similarity_score"], reverse=True)
    return ranked_papers
