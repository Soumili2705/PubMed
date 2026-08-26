"""Knowway AI — PubMed Biomedical Intelligence Platform."""
from __future__ import annotations
import time
import streamlit as st

from src._ai_summary      import answer_rag_question, generate_summary
from src._fetch_papers    import fetch_papers, search_pubmed
from src._rank_papers     import rank_papers
from src._translate_query import translate_to_mesh_query
from src.analytics        import render_analytics_dashboard
from src.styles           import CUSTOM_CSS
from src.ui_components    import (
    generate_dossier_markdown, render_hero_header, render_how_it_works,
    render_intro_card, render_paper_card, render_researcher_impact,
    render_understood_section,
)

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Knowway AI — Biomedical Discovery",
    page_icon="🧬", layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in [("results",None),("query",""),("chat",[]),("history",[]),("ikey",0)]:
    if k not in st.session_state: st.session_state[k] = v

# ── HERO HEADER ───────────────────────────────────────────────────────────────
render_hero_header()

# ── LAYOUT ───────────────────────────────────────────────────────────────────
left, right = st.columns([1, 2.9], gap="large")

# ══════════════════════════════════════════════════════════════════
# LEFT SIDEBAR — All controls, full grounding stack, history, reset
# ══════════════════════════════════════════════════════════════════
with left:
    st.markdown('<div class="kw-sidebar">', unsafe_allow_html=True)

    # ── Retrieval Settings ────────────────────────────────
    st.markdown('<div class="kw-section-label">🎛 Retrieval Settings</div>', unsafe_allow_html=True)

    fast_mode = st.toggle(
        "⚡ Fast mode", value=True,
        help="Uses deterministic query mapping, fewer candidates, and Groq's faster model.",
    )
    st.caption("Fast: quicker results · Deep: broader AI-assisted query mapping")
    fetch_limit = st.slider(
        "Candidate Pool Size", 5, 30, 8, 1,
        help="Number of candidate records retrieved from NCBI PubMed.",
    )
    min_sim = st.slider(
        "Min Similarity Threshold", 0.20, 0.85, 0.35, 0.05,
        help="Filter out candidates below this cosine similarity score.",
    )
    st.markdown(
        f"<div style='font-size:11px;color:#1D4ED8;font-family:var(--mono);"
        f"margin:-2px 0 10px;'>▶ {fetch_limit} candidates · ≥ {min_sim:.2f} similarity</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="kw-divider"></div>', unsafe_allow_html=True)

    # ── Grounding Stack (full labels like screenshot 2) ───
    st.markdown('<div class="kw-section-label">🔬 Grounding Stack</div>', unsafe_allow_html=True)
    for label, value in [
        ("Ontology",   "MeSH-informed mapping"),
        ("Retrieval",  "NCBI E-Utilities"),
        ("Embeddings", "MiniLM 384-dim"),
        ("Synthesis",  "Groq LLaMA 3.3"),
    ]:
        st.markdown(
            f'<div class="kw-stack-row">• <strong>{label}:</strong> {value}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="kw-divider"></div>', unsafe_allow_html=True)

    # ── Recent Searches ───────────────────────────────────
    st.markdown('<div class="kw-section-label">🕐 Recent Searches</div>', unsafe_allow_html=True)

    if st.session_state.history:
        for i, item in enumerate(st.session_state.history):
            lbl = item["query"][:24] + ("…" if len(item["query"]) > 24 else "")
            if st.button(f"🔍 {lbl}", key=f"h{i}", use_container_width=True,
                         help=item["query"]):
                st.session_state.query   = item["query"]
                st.session_state.results = item["results"]
                st.session_state.chat    = []
                st.session_state.ikey   += 1
                st.rerun()
        if st.button("✕ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown(
            '<div class="kw-no-history">No searches yet this session.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="kw-divider"></div>', unsafe_allow_html=True)

    # ── Reset Session ─────────────────────────────────────
    if st.button("🗑 Reset Session", use_container_width=True):
        st.session_state.results = None
        st.session_state.chat    = []
        st.session_state.query   = ""
        st.session_state.ikey   += 1
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# RIGHT CANVAS — Intro + Templates + Search + Results
# ══════════════════════════════════════════════════════════════════
with right:

    # ── 1. Intro card (Live NCBI PubMed + 3 knowledge cards) ──
    render_intro_card()

    # ── 2. Quick Research Templates ───────────────────────────
    st.markdown("""<div class="kw-tmpl-card">
  <div class="kw-tmpl-title">💡 Quick Research Templates — Select a Research Inquiry</div>""",
                unsafe_allow_html=True)

    PRESETS = [
        ("🧪 Oncology",   "lung cancer immunotherapy clinical trials efficacy"),
        ("👶 Pediatrics", "pediatric asthma acute management guidelines"),
        ("🧠 Neurology",  "early detection biomarkers in alzheimers disease"),
        ("💉 Nephrology", "sugar disease causing kidney damage in old people"),
    ]
    pc = st.columns(len(PRESETS))
    for col, (lbl, qry) in zip(pc, PRESETS):
        with col:
            if st.button(lbl, use_container_width=True):
                st.session_state.query = qry
                st.session_state.ikey += 1
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 3. Research Question + Search ─────────────────────────
    st.markdown("""<div class="kw-search-card">
  <div class="kw-search-section-label">🔍 Research Question</div>
  <div class="kw-search-heading">What biomedical question are you trying to explore?</div>
</div>""", unsafe_allow_html=True)

    query_input = st.text_input(
        "Query",
        value=st.session_state.query,
        key=f"q_{st.session_state.ikey}",
        placeholder="e.g., early detection biomarkers in Alzheimer's disease",
        label_visibility="collapsed",
    )

    btn_col, hint_col = st.columns([1.4, 2.2])
    with btn_col:
        run = st.button("🚀 Find Relevant Evidence", type="primary", use_container_width=True)
    with hint_col:
        st.markdown(
            "<div style='padding-top:10px;font-size:12px;color:#94A3B8;'>"
            "PubMed-verified &nbsp;·&nbsp; Semantically ranked &nbsp;·&nbsp; AI-synthesised</div>",
            unsafe_allow_html=True,
        )

    # ── 4. Pipeline Execution ─────────────────────────────────
    if run:
        if not query_input.strip():
            st.warning("⚠️ Enter a research question or select a template above.")
        else:
            st.session_state.query = query_input
            t_start, timings = time.time(), {}

            with st.status("🔍 Searching PubMed and synthesising evidence…", expanded=True) as status:
                t0 = time.time()
                st.write("🧠 Mapping biomedical concepts & MeSH terms…")
                tr = translate_to_mesh_query(query_input, use_llm=True, fast_mode=fast_mode)
                timings["mesh"] = time.time() - t0

                t0 = time.time()
                st.write(f"📡 Querying PubMed for {fetch_limit} candidates…")
                candidate_limit = min(fetch_limit, 8) if fast_mode else fetch_limit
                pmids = search_pubmed(tr["pubmed_query"], max_results=candidate_limit)
                if not pmids:
                    st.write("🔄 Broadening search query…")
                    pmids = search_pubmed(query_input, max_results=candidate_limit)
                if not pmids:
                    status.update(label="❌ No records found on PubMed.", state="error", expanded=False)
                    st.stop()
                st.write(f"📥 Fetching metadata for {len(pmids)} records…")
                raw = fetch_papers(pmids)
                timings["ncbi"] = time.time() - t0

                t0 = time.time()
                st.write("🎯 Ranking by semantic relevance…")
                ranked   = rank_papers(query_input, raw, tr["clinical_terms"])
                filtered = [p for p in ranked
                            if p.get("raw_score", p.get("similarity_score", 0)) >= min_sim]
                timings["vector"] = time.time() - t0

                t0 = time.time()
                st.write("🤖 Synthesising AI evidence briefing…")
                pool   = filtered if filtered else ranked[:5]
                report = generate_summary(query_input, pool, fast_mode=fast_mode)
                timings["groq"] = time.time() - t0

                total = time.time() - t_start
                status.update(label=f"✅ Complete — {total:.2f}s", state="complete", expanded=False)

            res = dict(
                query=query_input, translation=tr, raw_papers=raw,
                ranked_papers=ranked, filtered_papers=filtered,
                ai_report=report, timings=timings, latency=total,
            )
            st.session_state.results = res

            # History (deduplicated, max 8)
            st.session_state.history = [h for h in st.session_state.history
                                         if h["query"].lower() != query_input.lower()]
            st.session_state.history.insert(0, {
                "query": query_input,
                "time": time.strftime("%H:%M"),
                "results": res,
            })
            st.session_state.history = st.session_state.history[:8]

    # ── 5. Results Dashboard ──────────────────────────────────
    if st.session_state.results:
        res      = st.session_state.results
        ranked   = res["ranked_papers"]
        active   = [p for p in ranked
                    if p.get("raw_score", p.get("similarity_score", 0)) >= min_sim]
        tr       = res["translation"]
        mesh     = tr.get("mesh_terms", [])
        clin     = tr.get("clinical_terms", [])
        concepts = list(dict.fromkeys(mesh + clin))

        # Understood section
        render_understood_section(
            res["query"], mesh, clin,
            facets=tr.get("facets"),
            pubmed_query=tr.get("pubmed_query"),
        )

        # Section header + KPIs
        top_score = (
            round(ranked[0].get("raw_score", ranked[0].get("similarity_score", 0)), 3)
            if ranked else 0.0
        )
        st.markdown(
            f"<div class='kw-result-header'>🧭 Your Knowledge Path "
            f"<span>{len(active)} studies discovered · ranked by semantic relevance</span></div>",
            unsafe_allow_html=True,
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("📄 Studies Retrieved",  len(res["raw_papers"]))
        k2.metric("🏷 Concepts Identified", len(mesh) + len(clin))
        k3.metric("🎯 Top Relevance",      f"{top_score:.3f}")
        k4.metric("⚡ Total Latency",      f"{res['latency']:.2f}s")

        # Tabs
        t1, t2, t3, t4 = st.tabs([
            f"📚 Evidence Explorer ({len(active)})",
            "📝 Evidence Summary",
            "📊 Biomedical Analytics",
            "💬 Chat with Literature",
        ])

        with t1:
            if active:
                if len(active) <= 3:
                    st.info("Only a few closely related studies were found. Try a broader question or lower the relevance threshold.")
                for i, paper in enumerate(active, 1):
                    render_paper_card(paper, i, concepts)
            else:
                st.warning(
                    f"No papers above {min_sim:.2f} threshold. "
                    "Lower 'Min Similarity' in the left panel to see all candidates."
                )

        with t2:
            hdr_col, dl_col = st.columns([3, 1])
            hdr_col.markdown(
                "<div style='font-size:15px;font-weight:800;color:#0F172A;"
                "letter-spacing:-0.02em;padding-top:4px;'>📝 AI Evidence Briefing</div>",
                unsafe_allow_html=True,
            )
            with dl_col:
                dossier = generate_dossier_markdown(
                    res["query"], tr, active or ranked[:5],
                    res["ai_report"], res["latency"], res["timings"],
                )
                st.download_button(
                    "📥 Export Dossier", dossier,
                    file_name=f"KnowwayAI_{int(time.time())}.md",
                    mime="text/markdown", use_container_width=True,
                )
            st.markdown(f'<div class="kw-summary">{res["ai_report"]}</div>',
                        unsafe_allow_html=True)
            with st.expander("🔍 View Raw Boolean Query sent to PubMed"):
                st.code(tr.get("pubmed_query", ""), language="sql")

        with t3:
            render_analytics_dashboard(
                papers=ranked, timings=res["timings"],
                mesh_terms=mesh, min_threshold=min_sim,
            )

        with t4:
            st.caption(
                "Ask targeted follow-up questions. Responses are strictly grounded "
                "in the retrieved study abstracts and cite verified PMIDs."
            )
            for msg in st.session_state.chat:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            if q := st.chat_input("Ask a specific question about the retrieved studies…"):
                st.session_state.chat.append({"role": "user", "content": q})
                with st.chat_message("user"): st.markdown(q)
                with st.chat_message("assistant"):
                    with st.spinner("Cross-referencing retrieved abstracts…"):
                        ans = answer_rag_question(q, active or ranked[:5], st.session_state.chat)
                        st.markdown(ans)
                        st.session_state.chat.append({"role": "assistant", "content": ans})

        render_researcher_impact()
        render_how_it_works()
        st.caption("For biomedical literature discovery only — not medical advice or a clinical decision tool.")
