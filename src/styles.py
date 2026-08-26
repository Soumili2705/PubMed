"""Knowway AI — Professional Biomedical Research Design System."""

CUSTOM_CSS = """
<style id="knowway-css-v10">
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700&display=swap');

/* ── TOKENS ── */
:root {
  --bg:       #EEF2F7;
  --card:     rgba(255,255,255,0.97);
  --border:   rgba(203,213,225,0.65);
  --shadow:   0 1px 3px rgba(15,23,42,0.05), 0 3px 12px rgba(15,23,42,0.04);
  --blue:     #1D4ED8;
  --blue-lt:  #EFF6FF;
  --teal:     #0D9488;
  --ink:      #0F172A;
  --sub:      #334155;
  --muted:    #64748B;
  --faint:    #94A3B8;
  --radius:   14px;
  --f:        'Inter', -apple-system, sans-serif;
  --mono:     'JetBrains Mono', monospace;
}

html, body, [class*="css"], .stApp {
  font-family: var(--f) !important;
  background-color: var(--bg) !important;
  color: var(--ink) !important;
  font-size: 13.5px !important;
}
.stApp {
  background-image:
    radial-gradient(ellipse 60% 35% at 0% 0%, rgba(29,78,216,0.07) 0%, transparent 55%),
    radial-gradient(ellipse 45% 25% at 100% 0%, rgba(13,148,136,0.05) 0%, transparent 50%) !important;
  background-attachment: fixed !important;
}

/* ── HIDE STREAMLIT CHROME ── */
header[data-testid="stHeader"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

.block-container {
  padding-top: 0.9rem !important;
  padding-bottom: 2.5rem !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  max-width: 1600px !important;
}

/* ══════════════════════════════════
   NAVY HERO HEADER
   ══════════════════════════════════ */
.kw-hero {
  background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 60%, #0C2A3A 100%);
  border-radius: 16px;
  padding: 18px 26px;
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  box-shadow: 0 4px 24px rgba(15,23,42,0.18);
}
.kw-hero-left { display: flex; align-items: center; gap: 14px; }
.kw-hero-icon {
  width: 46px; height: 46px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; flex-shrink: 0;
}
.kw-hero-title {
  font-size: 32px; font-weight: 900; color: #fff;
  margin: 0; letter-spacing: -0.035em; line-height: 1.15;
}
.kw-hero-badge {
  font-size: 9px; font-weight: 700; letter-spacing: 0.10em;
  font-family: var(--mono); color: #7DD3FC;
  background: rgba(125,211,252,0.12);
  border: 1px solid rgba(125,211,252,0.28);
  padding: 2px 8px; border-radius: 20px;
  text-transform: uppercase; vertical-align: middle; margin-left: 8px;
}
.kw-hero-sub {
  font-size: 12px; color: rgba(255,255,255,0.50); margin: 3px 0 0;
}
.kw-pipe {
  display: flex; align-items: center; gap: 5px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 50px; padding: 7px 16px;
  font-size: 11px; font-weight: 700; font-family: var(--mono);
}
.kw-pipe-step { color: rgba(255,255,255,0.90); letter-spacing: 0.02em; }
.kw-pipe-arrow { color: rgba(255,255,255,0.22); font-size: 9px; }

/* ══════════════════════════════════
   SIDEBAR PANEL
   ══════════════════════════════════ */
.kw-sidebar {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 14px;
}
.kw-section-label {
  font-size: 9.5px; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--faint);
  margin-bottom: 8px; display: flex; align-items: center; gap: 5px;
}
.kw-divider { height: 1px; background: var(--border); margin: 12px 0; }

/* Grounding stack list */
.kw-stack-row {
  font-size: 12px; color: var(--sub); padding: 3px 0;
  line-height: 1.5;
}
.kw-stack-row strong { color: var(--ink); }

/* History */
.kw-no-history {
  font-size: 12px; color: var(--faint); font-style: italic; margin-bottom: 8px;
}

/* ── INPUTS ── */
.stTextInput > div > div > input {
  background: rgba(248,250,252,0.96) !important;
  color: var(--ink) !important;
  border: 1.5px solid rgba(203,213,225,0.80) !important;
  border-radius: 10px !important;
  padding: 12px 16px !important;
  font-size: 14.5px !important;
  font-weight: 500 !important;
  font-family: var(--f) !important;
  transition: border-color 0.18s, box-shadow 0.18s !important;
}
.stTextInput > div > div > input:focus {
  background: #fff !important;
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3.5px rgba(29,78,216,0.10) !important;
}

/* ── PRIMARY BUTTON ── */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
  color: #fff !important; border: none !important;
  padding: 0.70rem 1.5rem !important;
  font-size: 13.5px !important; font-weight: 700 !important;
  font-family: var(--f) !important;
  border-radius: 10px !important;
  box-shadow: 0 2px 10px rgba(29,78,216,0.26) !important;
  transition: transform 0.12s, box-shadow 0.12s !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 18px rgba(29,78,216,0.36) !important;
}

/* ── SECONDARY BUTTONS ── */
.stButton > button:not([kind="primary"]) {
  background: rgba(255,255,255,0.92) !important;
  color: var(--sub) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
  font-size: 12px !important; font-weight: 600 !important;
  font-family: var(--f) !important;
  padding: 6px 10px !important;
  transition: all 0.12s !important;
}
.stButton > button:not([kind="primary"]):hover {
  border-color: #93C5FD !important;
  color: var(--blue) !important;
  background: var(--blue-lt) !important;
  transform: translateY(-1px) !important;
}

/* ── SLIDERS ── */
div[data-testid="stSlider"] { padding-top: 2px !important; padding-bottom: 4px !important; }
div[data-testid="stSlider"] label p,
div[data-testid="stSlider"] label,
div[data-testid="stSlider"] > label,
div[data-testid="stSlider"] > div > label,
.stSlider label, .stSlider p {
  font-size: 14px !important; font-weight: 700 !important; color: var(--ink) !important;
}

/* ══════════════════════════════════
   MAIN CONTENT CARDS
   ══════════════════════════════════ */
.kw-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 20px;
  margin-bottom: 12px;
}

/* Intro card */
.kw-intro-title {
  font-size: 22px; font-weight: 800; color: var(--ink);
  margin-bottom: 7px; letter-spacing: -0.03em;
  display: flex; align-items: center; gap: 7px;
}
.kw-intro-desc {
  font-size: 15px; line-height: 1.7; color: var(--sub); margin-bottom: 16px;
}
.kw-eyebrow {
  font-size: 11px; font-weight: 800; letter-spacing: 0.12em;
  color: var(--blue); margin-bottom: 6px;
}
.kw-features {
  display: grid; grid-template-columns: repeat(3,1fr); gap: 12px;
}
@media (max-width:860px) { .kw-features { grid-template-columns: 1fr; } }
.kw-feature {
  background: rgba(248,250,252,0.95);
  border: 1px solid rgba(203,213,225,0.70);
  border-radius: 11px; padding: 12px 15px;
}
.kw-feature-title {
  font-size: 15.5px; font-weight: 800; color: var(--ink);
  margin-bottom: 5px; display: flex; align-items: center; gap: 6px;
}
.kw-feature-text {
  font-size: 13.5px; color: var(--sub); line-height: 1.55; margin: 0;
}

/* Templates card */
.kw-tmpl-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 12px 20px 14px;
  margin-bottom: 12px;
}
.kw-tmpl-title {
  font-size: 10px; font-weight: 700; letter-spacing: 0.10em;
  text-transform: uppercase; color: var(--faint); margin-bottom: 9px;
  display: flex; align-items: center; gap: 5px;
}

/* Research Question card */
.kw-search-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 20px 14px;
  margin-bottom: 0;
}
.kw-search-section-label {
  font-size: 10px; font-weight: 700; letter-spacing: 0.10em;
  text-transform: uppercase; color: var(--faint);
  margin-bottom: 5px;
}
.kw-search-heading {
  font-size: 22px; font-weight: 800; color: var(--ink);
  letter-spacing: -0.025em; margin-bottom: 12px; line-height: 1.3;
}

/* ══════════════════════════════════
   RESULTS
   ══════════════════════════════════ */
div[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 13px 16px !important;
  box-shadow: var(--shadow) !important;
}
div[data-testid="stMetricLabel"] > p {
  font-size: 10px !important; font-weight: 700 !important;
  text-transform: uppercase !important; letter-spacing: 0.08em !important;
  color: var(--faint) !important;
}
div[data-testid="stMetricValue"] > div {
  font-size: 26px !important; font-weight: 900 !important;
  font-family: var(--mono) !important; color: var(--ink) !important;
  letter-spacing: -0.03em !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 3px !important;
  background: rgba(226,232,240,0.55) !important;
  padding: 4px !important; border-radius: 11px !important;
  margin-bottom: 16px !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px !important;
  padding: 8px 16px !important;
  color: var(--faint) !important;
  font-weight: 600 !important; font-size: 12.5px !important;
  font-family: var(--f) !important;
  border: none !important; background: transparent !important;
}
.stTabs [aria-selected="true"] {
  background: #fff !important; color: var(--ink) !important;
  box-shadow: 0 1px 4px rgba(15,23,42,0.09) !important;
}

/* Understood box */
.kw-understood {
  background: linear-gradient(135deg, rgba(239,246,255,0.96) 0%, rgba(240,253,250,0.96) 100%);
  border: 1px solid rgba(147,197,253,0.45);
  border-left: 4px solid var(--blue);
  border-radius: var(--radius);
  padding: 15px 20px;
  margin: 12px 0 14px;
  box-shadow: var(--shadow);
}
.kw-understood-title {
  font-size: 10px; font-weight: 700; letter-spacing: 0.10em;
  text-transform: uppercase; color: var(--blue); margin-bottom: 9px;
}
.kw-tag {
  display: inline-flex; align-items: center; gap: 3px;
  background: rgba(255,255,255,0.92);
  border: 1px solid rgba(147,197,253,0.45);
  color: var(--ink); font-size: 12px; font-weight: 600;
  padding: 3px 10px; border-radius: 14px; margin: 0 4px 5px 0;
}
.kw-facet {
  display: inline-flex; align-items: center; gap: 3px;
  background: rgba(255,255,255,0.80);
  border: 1px solid var(--border);
  color: var(--sub); font-size: 11.5px;
  padding: 3px 8px; border-radius: 6px; margin: 0 4px 4px 0;
}
.kw-intent {
  display: inline-flex;
  background: #1D4ED8; color: #fff;
  font-size: 10.5px; font-weight: 700; font-family: var(--mono);
  padding: 2px 10px; border-radius: 14px; margin-left: 6px;
}

/* Paper cards */
.kw-paper {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 17px 21px;
  margin-bottom: 10px;
  box-shadow: var(--shadow);
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
  position: relative;
}
.kw-paper:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(15,23,42,0.09) !important;
  border-color: rgba(147,197,253,0.55) !important;
}
.kw-paper-rank {
  position: absolute; top: 14px; right: 14px;
  font-size: 10px; font-weight: 700; font-family: var(--mono);
  color: var(--faint); background: rgba(248,250,252,0.95);
  border: 1px solid var(--border); padding: 2px 7px; border-radius: 5px;
}
.kw-paper-title {
  font-size: 15px; font-weight: 700; color: var(--ink) !important;
  text-decoration: none; display: block;
  margin-bottom: 8px; line-height: 1.45; padding-right: 55px;
}
.kw-paper-title:hover { color: var(--blue) !important; }
.kw-why {
  background: rgba(240,253,250,0.80);
  border-left: 3px solid var(--teal);
  border-radius: 0 7px 7px 0;
  padding: 6px 12px; font-size: 12px; color: var(--sub);
  margin-bottom: 10px; line-height: 1.5;
}
.kw-why-lbl { font-weight: 700; color: var(--teal); margin-right: 5px; }
.kw-sim {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--blue-lt); border: 1px solid rgba(147,197,253,0.45);
  padding: 3px 10px; border-radius: 7px;
  font-size: 11.5px; font-weight: 700; color: var(--blue);
  margin-right: 5px;
}
.kw-sim-score { font-family: var(--mono); font-size: 12px; }
.kw-chip {
  display: inline-flex; align-items: center; gap: 3px;
  background: rgba(248,250,252,0.9); border: 1px solid var(--border);
  color: var(--muted); font-size: 11.5px;
  padding: 3px 9px; border-radius: 6px; margin-right: 4px;
}

/* Summary */
.kw-summary {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 24px; margin-bottom: 14px;
  box-shadow: var(--shadow); line-height: 1.75;
}
.kw-summary h3 {
  font-size: 14.5px !important; font-weight: 700 !important;
  color: var(--ink) !important;
  border-bottom: 1px solid var(--border);
  padding-bottom: 4px; margin-top: 1.1rem !important;
}
.kw-summary p, .kw-summary li {
  font-size: 13.5px !important; color: var(--sub) !important; line-height: 1.75 !important;
}

/* Expanders */
details[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 11px !important;
  margin-bottom: 9px !important;
  box-shadow: var(--shadow) !important;
}

/* Section result header */
.kw-result-header {
  font-size: 17px; font-weight: 800; color: var(--ink);
  letter-spacing: -0.02em; margin: 14px 0 10px;
  display: flex; align-items: center; gap: 8px;
}
.kw-result-header span {
  font-size: 12.5px; font-weight: 500; color: var(--muted);
}
</style>
"""
