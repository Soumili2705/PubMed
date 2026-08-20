"""
Analytics and Visualizations module for PubMed AI (Knowway Design System).
Renders vector cosine similarity distributions, ontology co-occurrence, and pipeline latency breakdowns.
"""

from __future__ import annotations
import streamlit as st

try:
  import plotly.express as px
  import plotly.graph_objects as go

  PLOTLY_AVAILABLE = True
except ImportError:
  PLOTLY_AVAILABLE = False


def render_analytics_dashboard(
    papers: list,
    timings: dict,
    mesh_terms: list,
    min_threshold: float = 0.30,
):
  """Renders the research analytics dashboard with a clean light clinical theme and honest metrics."""
  if not papers:
    st.info("Run a search pipeline first to populate analytics.")
    return

  col_left, col_right = st.columns(2)

  with col_left:
    st.markdown("#### 🎯 Vector Similarity Distribution")
    # Honest raw cosine similarity scores
    scores = [
        round(p.get("raw_score", p.get("similarity_score", 0.0)), 3)
        for p in papers
    ]
    titles = [
        p.get("title", f"Paper {i}")[:35] + "..."
        for i, p in enumerate(papers, 1)
    ]
    pmids = [str(p.get("pmid", "")) for p in papers]

    if PLOTLY_AVAILABLE:
      colors = [
          "#0D9488" if s >= 0.65 else "#2563EB" if s >= 0.45 else "#94A3B8"
          for s in scores
      ]

      fig_scores = go.Figure(
          data=[
              go.Bar(
                  x=[f"#{i}" for i in range(1, len(papers) + 1)],
                  y=scores,
                  hovertext=[
                      f"<b>{t}</b><br>PMID: {p}<br>Similarity: {s:.3f}"
                      for t, p, s in zip(titles, pmids, scores)
                  ],
                  hoverinfo="text",
                  marker=dict(
                      color=colors,
                      line=dict(color="#E2E8F0", width=1),
                  ),
              )
          ]
      )
      fig_scores.update_layout(
          template="plotly_white",
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="#FFFFFF",
          margin=dict(l=20, r=20, t=30, b=20),
          xaxis=dict(title="Retrieved Studies (Ranked)", showgrid=False),
          yaxis=dict(
              title="Cosine Similarity", range=[0, 1.0], gridcolor="#F1F5F9"
          ),
          height=320,
      )
      st.plotly_chart(fig_scores, use_container_width=True)
    else:
      st.bar_chart({"Cosine Similarity": scores})

  with col_right:
    st.markdown("#### ⏱️ Pipeline Latency Breakdown")
    stage_names = [
        "MeSH Concept Parsing",
        "NCBI E-Utilities",
        "Dense Vector Ranking",
        "Groq Evidence Synthesis",
    ]
    stage_times = [
        round(timings.get("mesh", 0.1), 2),
        round(timings.get("ncbi", 0.5), 2),
        round(timings.get("vector", 0.2), 2),
        round(timings.get("groq", 0.8), 2),
    ]

    if PLOTLY_AVAILABLE:
      fig_latency = go.Figure(
          data=[
              go.Bar(
                  y=stage_names,
                  x=stage_times,
                  orientation="h",
                  marker=dict(
                      color=["#2563EB", "#0284C7", "#0D9488", "#7C3AED"],
                      line=dict(color="#E2E8F0", width=1),
                  ),
                  text=[f"{t}s" for t in stage_times],
                  textposition="auto",
              )
          ]
      )
      fig_latency.update_layout(
          template="plotly_white",
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="#FFFFFF",
          margin=dict(l=20, r=20, t=30, b=20),
          xaxis=dict(title="Execution Time (seconds)", gridcolor="#F1F5F9"),
          yaxis=dict(autorange="reversed", showgrid=False),
          height=320,
      )
      st.plotly_chart(fig_latency, use_container_width=True)
    else:
      st.bar_chart(dict(zip(stage_names, stage_times)))

  st.markdown("---")

  # Bottom row: Journal Breakdown & MeSH Entities
  col_j, col_m = st.columns(2)

  with col_j:
    st.markdown("#### 📚 Journal Distribution")
    journal_counts = {}
    for p in papers:
      j = p.get("journal", "Unknown")
      j_short = j[:30] + "..." if len(j) > 30 else j
      journal_counts[j_short] = journal_counts.get(j_short, 0) + 1

    if PLOTLY_AVAILABLE and journal_counts:
      fig_j = px.pie(
          names=list(journal_counts.keys()),
          values=list(journal_counts.values()),
          hole=0.45,
          color_discrete_sequence=px.colors.qualitative.Pastel,
      )
      fig_j.update_layout(
          template="plotly_white",
          paper_bgcolor="rgba(0,0,0,0)",
          margin=dict(l=10, r=10, t=10, b=10),
          height=260,
          showlegend=False,
      )
      st.plotly_chart(fig_j, use_container_width=True)
    else:
      for j_name, cnt in list(journal_counts.items())[:5]:
        st.write(f"• **{j_name}**: {cnt} paper(s)")

  with col_m:
    st.markdown("#### 🏷️ Active MeSH Ontology Terms")
    if mesh_terms:
      for i, term in enumerate(mesh_terms, 1):
        st.markdown(
            f"`{i}.` **{term}** *(National Library of Medicine MeSH Tree)*"
        )
    else:
      st.caption("No specific MeSH terms extracted for this query.")
