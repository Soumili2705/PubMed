from __future__ import annotations
import time
import streamlit as st

# Internal core modules (preserving all working backend functionality)
from src._ai_summary import answer_rag_question, generate_summary
from src._fetch_papers import fetch_papers, search_pubmed
from src._rank_papers import rank_papers
from src._translate_query import translate_to_mesh_query
from src.analytics import render_analytics_dashboard
from src.styles import CUSTOM_CSS
from src.ui_components import (
    generate_dossier_markdown,
    render_hero_header,
    render_how_it_works,
    render_paper_card,
    render_researcher_impact,
    render_understood_section,
)

# --- 1. PAGE CONFIGURATION & INJECT MINIMAL-CONTRAST FROSTED GLASS THEME ---
st.set_page_config(
    page_title="Knowway AI — Find your knowledge in the right way.",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- 2. INITIALIZE SESSION STATE ---
if "pipeline_results" not in st.session_state:
  st.session_state.pipeline_results = None
if "selected_query" not in st.session_state:
  st.session_state.selected_query = ""
if "chat_messages" not in st.session_state:
  st.session_state.chat_messages = []

# --- 3. TOP OF PAGE: STUDIO HERO & BREADCRUMB ---
render_hero_header()

# --- 4. 2-COLUMN STUDIO WORKBENCH (PERSISTENT LEFT SIDEBAR + RIGHT SEARCH CANVAS) ---
col_sidebar, col_main = st.columns([1, 2.8], gap="medium")

# ==============================================================================
# LEFT SIDEBAR PANEL (RETRIEVAL SETTINGS & GROUNDING STACK)
# ==============================================================================
with col_sidebar:
  st.markdown(
      """<div class="sidebar-panel-container">
<div class="sidebar-section-title">🎛️ Retrieval Settings</div>
<div class="sidebar-section-sub">Configure candidate pool depth and semantic vector cutoffs.</div>
""",
      unsafe_allow_html=True,
  )

  fetch_limit = st.slider(
      "Candidate Pool Size",
      min_value=5,
      max_value=30,
      value=12,
      step=1,
      help="Number of candidate records retrieved from NCBI PubMed.",
  )
  st.markdown(
      f"<div style='font-size:11px; color:#2563EB; font-weight:700;"
      f" font-family:var(--font-mono); margin-top:-6px; margin-bottom:10px;'>"
      f"▶ {fetch_limit} candidate studies</div>",
      unsafe_allow_html=True,
  )

  min_similarity = st.slider(
      "Minimum Similarity Threshold",
      min_value=0.20,
      max_value=0.85,
      value=0.35,
      step=0.05,
      help="Filter out candidate records below this vector cosine similarity.",
  )
  st.markdown(
      f"<div style='font-size:11px; color:#0D9488; font-weight:700;"
      f" font-family:var(--font-mono); margin-top:-6px; margin-bottom:12px;'>"
      f"▶ {min_similarity:.2f} cosine similarity</div>",
      unsafe_allow_html=True,
  )

  st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

  st.markdown(
      """<div class="sidebar-section-title">🎯 System Objectives</div>
<div style="font-size: 11.5px; color: #475569; line-height: 1.6; margin-bottom: 8px;">
• <strong>Precision:</strong> MeSH & synonym ontology<br>
• <strong>Recall:</strong> Surface related clinical trials<br>
• <strong>Ranking:</strong> 384-dim dense vector cosine<br>
• <strong>Grounding:</strong> Verified PubMed PMIDs
</div>
""",
      unsafe_allow_html=True,
  )

  st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

  st.markdown(
      """<div class="sidebar-section-title">🔬 Grounding Stack</div>
<div class="sidebar-status-box">
  <div style="font-weight:700; color:#0F172A; margin-bottom:4px;">NLM & NCBI Live Pipeline</div>
  • <strong>Ontology:</strong> MeSH 2026 Tree<br>
  • <strong>Retrieval:</strong> PubMed E-Utilities<br>
  • <strong>Embeddings:</strong> MiniLM 384-dim<br>
  • <strong>Synthesis:</strong> Groq LLaMA 3.3
</div>
""",
      unsafe_allow_html=True,
  )

  st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

  if st.button("🗑️ Reset Session", use_container_width=True):
    st.session_state.pipeline_results = None
    st.session_state.chat_messages = []
    st.session_state.selected_query = ""
    st.rerun()

  st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# RIGHT MAIN CANVAS (PUBMED INTRO + PRESETS + SEARCH PROMPT + RESULTS)
# ==============================================================================
with col_main:
  # 1. LIVE NCBI PUBMED & BIOMEDICAL KNOWLEDGE FETCHING INTRO CARD
  st.markdown(
      """<div class="pubmed-intro-card">
<div class="pubmed-intro-title">📡 Live NCBI PubMed & Biomedical Knowledge Fetching</div>
<p class="pubmed-intro-desc">
Knowway AI connects directly to the <strong>National Center for Biotechnology Information (NCBI PubMed)</strong> live repository of over 36 million peer-reviewed biomedical records. Natural-language inquiries are mapped to standardized <strong>NLM MeSH descriptors</strong>, retrieving active clinical literature and ranking candidate abstracts using <strong>384-dimensional dense semantic vector similarity</strong> to synthesize grounded, transparent evidence briefings.
</p>
<div class="intro-features-grid">
  <div class="intro-feature-item">
    <div class="intro-feature-label">🧠 Concept Ontology</div>
    <p class="intro-feature-text">Translates conversational clinical queries into standardized MeSH terms and synonyms.</p>
  </div>
  <div class="intro-feature-item">
    <div class="intro-feature-label">📡 Real-Time Entrez</div>
    <p class="intro-feature-text">Fetches authentic, live PubMed research records and verified PMID citations.</p>
  </div>
  <div class="intro-feature-item">
    <div class="intro-feature-label">🎯 Honest Vectors</div>
    <p class="intro-feature-text">SentenceTransformer embeddings rank papers by genuine semantic alignment.</p>
  </div>
</div>
</div>""",
      unsafe_allow_html=True,
  )

  # 2. EXPLORATION PRESETS CARD (ABOVE THE SEARCH BOX)
  st.markdown(
      """<div class="preset-card-container">
<div class="preset-card-title">💡 Exploration Presets — Select a Research Inquiry Template</div>
""",
      unsafe_allow_html=True,
  )

  pr1, pr2, pr3, pr4 = st.columns(4)
  with pr1:
    if st.button("🧪 Oncology (NSCLC)", use_container_width=True, help="Lung cancer immunotherapy clinical trials efficacy"):
      st.session_state.selected_query = "lung cancer immunotherapy clinical trials efficacy"
      st.rerun()
  with pr2:
    if st.button("👶 Pediatrics (Asthma)", use_container_width=True, help="Pediatric acute asthma management guidelines"):
      st.session_state.selected_query = "pediatric asthma acute management guidelines"
      st.rerun()
  with pr3:
    if st.button("🧠 Neurology (Alzheimer's)", use_container_width=True, help="Early detection biomarkers in Alzheimer's disease"):
      st.session_state.selected_query = "early detection biomarkers in alzheimers disease"
      st.rerun()
  with pr4:
    if st.button("💉 Nephrology (Diabetes)", use_container_width=True, help="Diabetic kidney damage in elderly patients"):
      st.session_state.selected_query = "sugar disease causing kidney damage in old people"
      st.rerun()

  st.markdown("</div>", unsafe_allow_html=True)

  # 3. SEARCH ENGINE PROMPT INPUT CARD
  st.markdown(
      """<div class="main-search-card">
<div class="main-search-label">🔍 What biomedical question are you trying to explore?</div>
""",
      unsafe_allow_html=True,
  )

  query_input = st.text_input(
      "Search Query",
      value=st.session_state.selected_query,
      placeholder="e.g., early detection biomarkers in Alzheimer's disease",
      label_visibility="collapsed",
  )

  btn_col, info_col = st.columns([1.2, 2])
  with btn_col:
    execute_btn = st.button(
        "🚀 Find Relevant Evidence", type="primary", use_container_width=True
    )
  with info_col:
    st.markdown(
        "<div style='padding-top: 6px; font-size: 12.5px; color: #64748B;'>"
        "Evidence-grounded synthesis · PubMed-verified PMIDs"
        "</div>",
        unsafe_allow_html=True,
    )

  st.markdown("</div>", unsafe_allow_html=True)

  # 2. PIPELINE EXECUTION (RUNS IN-STREAM INSIDE RIGHT COLUMN)
  if execute_btn:
    if not query_input.strip():
      st.warning("⚠️ Please enter a research question or select a preset from the sidebar.")
    else:
      st.session_state.selected_query = query_input
      timings = {}
      total_start = time.time()

      with st.status(
          "🔍 Discovering and synthesizing relevant literature...", expanded=True
      ) as status:
        # Step 1: Concept Understanding & MeSH Translation
        t0 = time.time()
        st.write("🧠 Interpreting clinical intent & mapping biomedical concepts...")
        translation = translate_to_mesh_query(query_input)
        pubmed_query = translation["pubmed_query"]
        mesh_terms = translation["mesh_terms"]
        clinical_terms = translation["clinical_terms"]
        timings["mesh"] = time.time() - t0

        # Step 2: PubMed Retrieval
        t0 = time.time()
        st.write(
            f"📡 Retrieving top {fetch_limit} candidate studies from PubMed..."
        )
        pmids = search_pubmed(pubmed_query, max_results=fetch_limit)

        if not pmids:
          st.write("🔄 Broadening search with conceptual synonyms...")
          pmids = search_pubmed(query_input, max_results=fetch_limit)

        if not pmids:
          status.update(
              label="❌ No matching records found on PubMed.",
              state="error",
              expanded=False,
          )
          st.stop()

        # Step 3: XML Metadata Fetch
        st.write(f"📥 Fetching structured metadata for {len(pmids)} records...")
        raw_papers = fetch_papers(pmids)
        timings["ncbi"] = time.time() - t0

        # Step 4: Semantic Ranking
        t0 = time.time()
        st.write("🎯 Ranking literature by research relevance and intent...")
        ranked_papers = rank_papers(query_input, raw_papers, clinical_terms)
        timings["vector"] = time.time() - t0

        filtered_papers = [
            p
            for p in ranked_papers
            if p.get("raw_score", p.get("similarity_score", 0.0))
            >= min_similarity
        ]

        # Step 5: Evidence Synthesis
        t0 = time.time()
        st.write("🤖 Synthesizing query-grounded evidence summary...")
        papers_for_synthesis = (
            filtered_papers if filtered_papers else ranked_papers[:5]
        )
        ai_report = generate_summary(query_input, papers_for_synthesis)
        timings["groq"] = time.time() - t0

        total_latency = time.time() - total_start
        status.update(
            label=f"✅ Discovery Complete in {total_latency:.2f}s!",
            state="complete",
            expanded=False,
        )

        # Store in session state
        st.session_state.pipeline_results = {
            "query": query_input,
            "translation": translation,
            "raw_papers": raw_papers,
            "ranked_papers": ranked_papers,
            "filtered_papers": filtered_papers,
            "ai_report": ai_report,
            "timings": timings,
            "latency": total_latency,
        }

  # 3. RESULTS DASHBOARD (FLOWS IN-LINE DIRECTLY BENEATH PROMPT IN RIGHT COLUMN)
  if st.session_state.pipeline_results:
    res = st.session_state.pipeline_results
    ranked_papers = res["ranked_papers"]
    active_filtered = [
        p
        for p in ranked_papers
        if p.get("raw_score", p.get("similarity_score", 0.0)) >= min_similarity
    ]
    translation = res["translation"]
    timings = res["timings"]
    latency = res["latency"]
    mesh_terms = translation.get("mesh_terms", [])
    clinical_terms = translation.get("clinical_terms", [])
    all_concepts = list(dict.fromkeys(mesh_terms + clinical_terms))

    # A. WE UNDERSTOOD YOUR QUESTION
    render_understood_section(res["query"], mesh_terms, clinical_terms)

    # B. YOUR KNOWLEDGE PATH HEADER
    st.markdown(
        f"""<div class="knowledge-path-header">
  <h2 class="knowledge-path-title">🧭 Your Knowledge Path</h2>
  <p class="knowledge-path-subtitle"><strong>{len(active_filtered)} studies discovered</strong> · ranked by research relevance</p>
</div>""",
        unsafe_allow_html=True,
    )

    # C. METRICS ROW
    top_raw_score = (
        round(
            ranked_papers[0].get(
                "raw_score", ranked_papers[0].get("similarity_score", 0.0)
            ),
            3,
        )
        if ranked_papers
        else 0.0
    )
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
      st.metric(label="Studies Retrieved", value=len(res["raw_papers"]))
    with kpi2:
      st.metric(
          label="Concepts Identified", value=len(mesh_terms) + len(clinical_terms)
      )
    with kpi3:
      st.metric(label="Top Vector Sim", value=f"{top_raw_score:.3f}")
    with kpi4:
      st.metric(label="Latency", value=f"{latency:.2f}s")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # D. 4 WORKBENCH TABS
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📚 Evidence Explorer ({len(active_filtered)})",
        "📝 Evidence Summary",
        "📊 Biomedical Analysis",
        "💬 Chat with Literature",
    ])

    # TAB 1: EVIDENCE EXPLORER
    with tab1:
      st.markdown("### 📚 Discovered Literature Records")
      if active_filtered:
        for i, paper in enumerate(active_filtered, start=1):
          render_paper_card(paper, i, all_concepts)
      else:
        st.warning(
            f"No papers met the {min_similarity:.2f} threshold. Lower the slider"
            " in the control panel to inspect all retrieved candidate papers."
        )

    # TAB 2: EVIDENCE SUMMARY BRIEFING
    with tab2:
      col_syn_left, col_syn_right = st.columns([3, 1])
      with col_syn_left:
        st.markdown("### 📝 Evidence Summary Briefing")
      with col_syn_right:
        dossier_content = generate_dossier_markdown(
            res["query"],
            translation,
            active_filtered if active_filtered else ranked_papers[:5],
            res["ai_report"],
            latency,
            timings,
        )
        st.download_button(
            label="📥 Export Evidence Dossier",
            data=dossier_content,
            file_name=f"PubMedAI_Dossier_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True,
        )

      st.markdown(
          f'<div class="summary-container-clean">{res["ai_report"]}</div>',
          unsafe_allow_html=True,
      )

      with st.expander("🔍 View Raw Boolean Query sent to PubMed"):
        st.code(translation.get("pubmed_query", ""), language="sql")

    # TAB 3: BIOMEDICAL ANALYSIS
    with tab3:
      st.markdown("### 📊 Retrieval & Concept Analytics")
      render_analytics_dashboard(
          papers=ranked_papers,
          timings=timings,
          mesh_terms=translation.get("mesh_terms", []),
          min_threshold=min_similarity,
      )

    # TAB 4: CHAT WITH LITERATURE (INTERACTIVE RAG)
    with tab4:
      st.markdown("### 💬 Chat with Literature")
      st.caption(
          "Ask targeted follow-up questions. Responses are strictly grounded in"
          " the retrieved study abstracts and cite verified PMIDs."
      )

      for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
          st.markdown(msg["content"])

      user_rag_query = st.chat_input(
          "Ask a specific question about the retrieved studies..."
      )
      if user_rag_query:
        st.session_state.chat_messages.append(
            {"role": "user", "content": user_rag_query}
        )
        with st.chat_message("user"):
          st.markdown(user_rag_query)

        with st.chat_message("assistant"):
          with st.spinner("🤖 Cross-referencing retrieved study abstracts..."):
            answer = answer_rag_question(
                user_rag_query,
                active_filtered if active_filtered else ranked_papers[:5],
                st.session_state.chat_messages,
            )
            st.markdown(answer)
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": answer}
            )

    # E. RESEARCHER IMPACT SECTION
    render_researcher_impact()

    # F. HOW IT WORKS SECTION
    render_how_it_works()