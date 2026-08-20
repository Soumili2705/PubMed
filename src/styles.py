"""
Knowway AI — Frosted Glass Biomedical Workbench Design System (~140 lines).
Matches screenshot: Clean Frosted Glass Canvas, Top Studio Banner, and 2-Column Split.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500;600;700;800&display=swap');

:root {
    --bg-canvas: #EEF2F6;
    --bg-card: rgba(255, 255, 255, 0.82);
    --bg-card-hover: rgba(255, 255, 255, 0.96);
    --bg-sidebar: rgba(255, 255, 255, 0.72);
    --font-heading: 'Space Grotesk', -apple-system, sans-serif;
    --font-body: 'Plus Jakarta Sans', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --text-primary: #0F172A;
    --text-body: #334155;
    --text-muted: #64748B;
    --blue-primary: #2563EB;
    --blue-border: #DBEAFE;
    --teal-primary: #0D9488;
    --glass-blur: blur(16px);
    --glass-border: rgba(255, 255, 255, 0.85);
    --glass-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 1px 3px rgba(15, 23, 42, 0.03);
}

html, body, [class*="css"], .stApp {
    font-family: var(--font-body) !important;
    background-color: var(--bg-canvas) !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em;
}

.stApp {
    background-image: 
        radial-gradient(ellipse at 5% 0%, rgba(37, 99, 235, 0.07) 0%, transparent 45%),
        radial-gradient(ellipse at 95% 10%, rgba(13, 148, 136, 0.06) 0%, transparent 45%),
        radial-gradient(ellipse at 50% 100%, rgba(203, 213, 225, 0.25) 0%, transparent 60%) !important;
    background-attachment: fixed !important;
}

header[data-testid="stHeader"], [data-testid="collapsedControl"], section[data-testid="stSidebar"], #MainMenu, footer, [data-testid="stToolbar"] {
    display: none !important;
    visibility: hidden;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    max-width: 1440px !important;
}

/* Top Studio Banner */
.studio-top-header {
    background: var(--bg-card);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 16px 24px;
    margin-bottom: 16px;
    box-shadow: var(--glass-shadow);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.studio-logo-group { display: flex; align-items: center; gap: 12px; }
.studio-logo-icon { font-size: 28px; background: #EFF6FF; border: 1px solid #DBEAFE; border-radius: 12px; padding: 8px; line-height: 1; }
.studio-title-main { font-family: var(--font-heading) !important; font-size: 22px; font-weight: 700; color: var(--text-primary); margin: 0; display: flex; align-items: center; gap: 8px; }
.studio-badge-sub { font-size: 11px; font-weight: 700; font-family: var(--font-mono); color: var(--blue-primary); background: rgba(239, 246, 255, 0.9); border: 1px solid var(--blue-border); padding: 2px 8px; border-radius: 20px; text-transform: uppercase; }
.studio-tagline { font-size: 13px; color: var(--text-muted); margin: 2px 0 0 0; font-weight: 500; }
.studio-pipeline-pill { display: inline-flex; align-items: center; gap: 8px; background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(226, 232, 240, 0.8); padding: 6px 14px; border-radius: 24px; font-size: 12px; font-weight: 600; color: var(--text-body); font-family: var(--font-mono); }

/* Left Sidebar & Cards */
.sidebar-panel-container, .pubmed-intro-card, .preset-card-container, .main-search-card, .understood-box, .paper-card-clean, .summary-container-clean, div[data-testid="stMetric"], details[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 14px !important;
    box-shadow: var(--glass-shadow) !important;
}
.sidebar-panel-container { padding: 18px 16px; display: flex; flex-direction: column; gap: 14px; }
.sidebar-section-title { font-family: var(--font-heading); font-size: 12.5px; font-weight: 700; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px; margin-bottom: 2px; }
.sidebar-section-sub { font-size: 11.5px; color: var(--text-muted); line-height: 1.4; margin-bottom: 8px; }
.sidebar-divider { height: 1px; background: rgba(226, 232, 240, 0.8); margin: 2px 0; }
.sidebar-status-box { background: rgba(255, 255, 255, 0.65); border: 1px solid rgba(226, 232, 240, 0.7); border-radius: 10px; padding: 10px 12px; font-size: 11.5px; color: var(--text-body); line-height: 1.5; }

/* Right Main Cards */
.pubmed-intro-card { padding: 22px 26px; margin-bottom: 16px; }
.pubmed-intro-title { font-family: var(--font-heading); font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.pubmed-intro-desc { font-size: 14.5px; line-height: 1.65; color: var(--text-body); margin-bottom: 14px; }
.intro-features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
@media (max-width: 900px) { .intro-features-grid { grid-template-columns: 1fr; } }
.intro-feature-item { background: rgba(255, 255, 255, 0.70); border: 1px solid rgba(226, 232, 240, 0.85); border-radius: 12px; padding: 12px 14px; }
.intro-feature-label { font-family: var(--font-heading); font-size: 12.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; display: flex; align-items: center; gap: 5px; }
.intro-feature-text { font-size: 12px; color: var(--text-muted); line-height: 1.45; margin: 0; }

.preset-card-container { padding: 16px 20px; margin-bottom: 16px; }
.preset-card-title { font-family: var(--font-heading); font-size: 12.5px; font-weight: 700; color: var(--text-primary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.main-search-card { padding: 20px 24px; margin-bottom: 18px; }
.main-search-label { font-family: var(--font-heading); font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }

/* Streamlit Inputs & Buttons */
.stTextInput > div > div > input { background: rgba(255, 255, 255, 0.95) !important; color: var(--text-primary) !important; border: 1.5px solid rgba(203, 213, 225, 0.85) !important; border-radius: 12px !important; padding: 13px 18px !important; font-size: 14.5px !important; font-weight: 500 !important; font-family: var(--font-body) !important; transition: all 0.2s ease !important; }
.stTextInput > div > div > input:focus { background: #FFFFFF !important; border-color: var(--blue-primary) !important; box-shadow: 0 0 0 3.5px rgba(37, 99, 235, 0.12) !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%) !important; color: #FFFFFF !important; border: none !important; padding: 0.7rem 1.4rem !important; font-size: 14px !important; font-weight: 700 !important; font-family: var(--font-heading) !important; border-radius: 11px !important; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.16) !important; transition: all 0.15s ease !important; }
.stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #1E293B 0%, #334155 100%) !important; transform: translateY(-1px) !important; }
.stButton > button[kind="secondary"] { background: rgba(255, 255, 255, 0.85) !important; color: var(--text-body) !important; border: 1px solid rgba(226, 232, 240, 0.85) !important; border-radius: 10px !important; font-size: 12px !important; font-weight: 600 !important; padding: 7px 10px !important; transition: all 0.15s ease !important; }
.stButton > button[kind="secondary"]:hover { border-color: #94A3B8 !important; color: var(--text-primary) !important; background: #FFFFFF !important; transform: translateY(-1px) !important; }

/* Understood & Results */
.understood-box { border-left: 4px solid var(--blue-primary) !important; padding: 16px 20px; margin: 14px 0 18px 0; }
.understood-header { font-family: var(--font-heading); font-size: 13.5px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em; }
.concept-tag { display: inline-flex; align-items: center; gap: 4px; background: rgba(255, 255, 255, 0.90); border: 1px solid rgba(226, 232, 240, 0.9); color: var(--text-primary); font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 16px; margin: 0 6px 6px 0; }
.intent-tag { display: inline-flex; align-items: center; gap: 4px; background: rgba(239, 246, 255, 0.9); border: 1px solid var(--blue-border); color: var(--blue-primary); font-size: 12px; font-weight: 700; font-family: var(--font-mono); padding: 3px 10px; border-radius: 16px; margin-left: 6px; }

.knowledge-path-title { font-family: var(--font-heading); font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0; }
div[data-testid="stMetric"] { padding: 12px 16px !important; }
div[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase !important; font-family: var(--font-heading) !important; }
div[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-weight: 800 !important; font-size: 22px !important; font-family: var(--font-mono) !important; }

.stTabs [data-baseweb="tab-list"] { gap: 6px !important; background: rgba(226, 232, 240, 0.70) !important; padding: 5px !important; border-radius: 12px !important; margin-bottom: 12px !important; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; padding: 8px 16px !important; color: var(--text-muted) !important; font-weight: 600 !important; font-size: 13px !important; font-family: var(--font-heading) !important; border: none !important; background: transparent !important; }
.stTabs [aria-selected="true"] { background: #FFFFFF !important; color: var(--text-primary) !important; box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08) !important; }

.paper-card-clean { padding: 18px 22px; margin-bottom: 12px; transition: all 0.2s ease; }
.paper-card-clean:hover { border-color: rgba(186, 230, 253, 0.95) !important; transform: translateY(-1px); background: var(--bg-card-hover) !important; }
.paper-title-link { font-family: var(--font-heading); font-size: 15.5px; font-weight: 700; color: var(--text-primary) !important; text-decoration: none; display: block; margin-bottom: 8px; }
.paper-title-link:hover { color: var(--blue-primary) !important; }
.why-matches-box { background: rgba(240, 253, 250, 0.85); border-left: 3px solid var(--teal-primary); border-radius: 0 8px 8px 0; padding: 7px 12px; font-size: 12px; color: var(--text-body); margin-bottom: 10px; }
.why-matches-label { font-weight: 700; color: var(--teal-primary); margin-right: 6px; font-family: var(--font-heading); }
.sim-badge { display: inline-flex; align-items: center; gap: 5px; background: rgba(255, 255, 255, 0.95); border: 1px solid rgba(226, 232, 240, 0.9); padding: 3px 9px; border-radius: 6px; font-size: 11.5px; font-weight: 600; color: var(--text-body); margin-right: 6px; }
.sim-badge-score { font-weight: 800; font-family: var(--font-mono); color: var(--blue-primary); }
.meta-chip-clean { display: inline-flex; align-items: center; gap: 4px; background: rgba(255, 255, 255, 0.80); border: 1px solid rgba(226, 232, 240, 0.8); color: var(--text-muted); font-size: 11.5px; padding: 3px 9px; border-radius: 6px; margin-right: 6px; }

.summary-container-clean { padding: 22px 26px; margin-bottom: 16px; }
.summary-container-clean h3 { font-family: var(--font-heading) !important; color: var(--text-primary) !important; font-weight: 700 !important; margin-top: 1rem !important; border-bottom: 1px solid rgba(226, 232, 240, 0.8); padding-bottom: 6px; }
.summary-container-clean p, .summary-container-clean li { color: var(--text-body) !important; font-size: 14px !important; line-height: 1.65 !important; }
details[data-testid="stExpander"] { margin-bottom: 8px !important; }
div[data-testid="stSlider"] { padding-top: 4px; padding-bottom: 6px; }
</style>
"""
