"""
frontend_styles.py
------------------
Import this file in app.py and call inject_styles() once at the top
after st.set_page_config().

Usage in app.py:
    from frontend_styles import inject_styles, render_header
    inject_styles()
    render_header()
"""

import streamlit as st

# ─────────────────────────────────────────────
# MASTER CSS
# ─────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ══════════════════════════════════════════════
   ROOT TOKENS
══════════════════════════════════════════════ */
:root {
    --bg-deep:       #070b14;
    --bg-card:       #0d1321;
    --bg-card-hover: #121929;
    --border:        #1c2640;
    --border-bright: #2a3a5e;

    --accent-blue:   #3d7fff;
    --accent-cyan:   #00d4ff;
    --accent-green:  #00e5a0;
    --accent-red:    #ff4d6d;
    --accent-gold:   #ffd166;

    --text-primary:  #e8edf8;
    --text-secondary:#8899bb;
    --text-muted:    #445577;

    --pro-bg:        #001f14;
    --pro-border:    #00e5a0;
    --pro-text:      #b3fff0;
    --con-bg:        #1f0009;
    --con-border:    #ff4d6d;
    --con-text:      #ffd0d8;

    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-xl: 28px;

    --shadow-glow-blue:  0 0 30px rgba(61,127,255,0.15);
    --shadow-glow-green: 0 0 20px rgba(0,229,160,0.12);
    --shadow-glow-red:   0 0 20px rgba(255,77,109,0.12);

    --font-display: 'Syne', sans-serif;
    --font-body:    'DM Sans', sans-serif;
}

/* ══════════════════════════════════════════════
   GLOBAL RESETS & BASE
══════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }

/* Remove Streamlit default padding */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem !important;
    max-width: 1200px !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }

/* ══════════════════════════════════════════════
   ANIMATED BACKGROUND GRID
══════════════════════════════════════════════ */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(61,127,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(61,127,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
}

/* ══════════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════════ */
.hero-wrapper {
    position: relative;
    text-align: center;
    padding: 4rem 2rem 3rem;
    margin-bottom: 2rem;
    overflow: hidden;
}

.hero-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 600px;
    height: 300px;
    background: radial-gradient(ellipse, rgba(61,127,255,0.12) 0%, transparent 70%);
    pointer-events: none;
}

.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(61,127,255,0.15), rgba(0,212,255,0.1));
    border: 1px solid rgba(61,127,255,0.3);
    border-radius: 50px;
    padding: 6px 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent-cyan);
    margin-bottom: 1.2rem;
    animation: fadeSlideDown 0.6s ease both;
}

.hero-title {
    font-family: var(--font-display) !important;
    font-size: clamp(2.2rem, 5vw, 3.5rem) !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
    margin-bottom: 1rem !important;
    background: linear-gradient(135deg, #e8edf8 0%, var(--accent-cyan) 50%, var(--accent-blue) 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    animation: fadeSlideDown 0.7s ease 0.1s both;
}

.hero-subtitle {
    font-size: 1rem !important;
    color: var(--text-secondary) !important;
    max-width: 500px;
    margin: 0 auto 2rem !important;
    line-height: 1.6 !important;
    animation: fadeSlideDown 0.7s ease 0.2s both;
}

.hero-divider {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
    margin: 0 auto;
    border-radius: 2px;
    animation: fadeSlideDown 0.7s ease 0.3s both;
}

/* ══════════════════════════════════════════════
   SEARCH BAR
══════════════════════════════════════════════ */
.stTextInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-lg) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 1rem !important;
    padding: 0.9rem 1.5rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 2px 20px rgba(0,0,0,0.3) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: var(--shadow-glow-blue), 0 2px 20px rgba(0,0,0,0.3) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-muted) !important; }

/* ══════════════════════════════════════════════
   SELECTBOX
══════════════════════════════════════════════ */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

/* ══════════════════════════════════════════════
   SIMILAR PRODUCT CHIPS
══════════════════════════════════════════════ */
.sim-chips-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 16px; }
.sim-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-card);
    border: 1px solid var(--border-bright);
    border-radius: 50px;
    padding: 6px 16px;
    font-size: 0.82rem;
    color: var(--text-secondary);
    transition: all 0.2s ease;
    cursor: default;
}
.sim-chip:hover {
    border-color: var(--accent-blue);
    color: var(--text-primary);
    background: rgba(61,127,255,0.08);
}
.sim-chip-dot {
    width: 6px; height: 6px;
    background: var(--accent-blue);
    border-radius: 50%;
    flex-shrink: 0;
}

/* ══════════════════════════════════════════════
   METRIC CARDS — supports 4 or 6 columns
══════════════════════════════════════════════ */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 1.5rem 0;
}
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.2rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s ease, transform 0.2s ease;
    animation: fadeSlideUp 0.5s ease both;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--card-accent, linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)));
}
.metric-card:hover { border-color: var(--border-bright); transform: translateY(-2px); }
.metric-val {
    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--card-color, var(--text-primary));
    display: block;
    line-height: 1;
    margin-bottom: 6px;
}
.metric-lbl {
    font-size: 0.73rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}

/* Verified badge inside metric */
.verified-badge {
    display: inline-block;
    background: rgba(0,229,160,0.1);
    border: 1px solid rgba(0,229,160,0.3);
    border-radius: 50px;
    padding: 2px 10px;
    font-size: 0.72rem;
    color: var(--accent-green);
    font-weight: 600;
    letter-spacing: 0.06em;
    margin-top: 4px;
}

/* ══════════════════════════════════════════════
   ANALYZE BUTTON
══════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue), #1a4fd4) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-lg) !important;
    padding: 0.75rem 2.5rem !important;
    font-family: var(--font-display) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 24px rgba(61,127,255,0.35) !important;
    width: auto !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(61,127,255,0.5) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ══════════════════════════════════════════════
   VERDICT BANNER
══════════════════════════════════════════════ */
.verdict-banner {
    display: flex;
    align-items: center;
    gap: 14px;
    border-radius: var(--radius-md);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    border: 1px solid;
    animation: fadeSlideUp 0.5s ease both;
}
.verdict-banner.positive {
    background: linear-gradient(135deg, rgba(0,229,160,0.07), rgba(0,229,160,0.03));
    border-color: rgba(0,229,160,0.25);
}
.verdict-banner.negative {
    background: linear-gradient(135deg, rgba(255,77,109,0.07), rgba(255,77,109,0.03));
    border-color: rgba(255,77,109,0.25);
}
.verdict-banner.mixed {
    background: linear-gradient(135deg, rgba(255,209,102,0.07), rgba(255,209,102,0.03));
    border-color: rgba(255,209,102,0.25);
}
.verdict-icon { font-size: 1.8rem; flex-shrink: 0; }
.verdict-text { flex: 1; }
.verdict-title {
    font-family: var(--font-display);
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 2px;
}
.verdict-title.positive { color: var(--accent-green); }
.verdict-title.negative { color: var(--accent-red); }
.verdict-title.mixed    { color: var(--accent-gold); }
.verdict-sub { font-size: 0.84rem; color: var(--text-secondary); }

/* ══════════════════════════════════════════════
   PROS / CONS CARDS
══════════════════════════════════════════════ */
.aspect-card {
    display: flex;
    align-items: center;
    gap: 12px;
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin-bottom: 10px;
    border: 1px solid;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    animation: fadeSlideUp 0.4s ease both;
}
.aspect-card:hover { transform: translateX(4px); }

.aspect-card.pro {
    background: var(--pro-bg);
    border-color: rgba(0,229,160,0.2);
    box-shadow: var(--shadow-glow-green);
}
.aspect-card.pro:hover { box-shadow: 0 0 30px rgba(0,229,160,0.2); }

.aspect-card.con {
    background: var(--con-bg);
    border-color: rgba(255,77,109,0.2);
    box-shadow: var(--shadow-glow-red);
}
.aspect-card.con:hover { box-shadow: 0 0 30px rgba(255,77,109,0.2); }

.aspect-icon {
    font-size: 1.5rem;
    width: 42px; height: 42px;
    display: flex; align-items: center; justify-content: center;
    border-radius: var(--radius-sm);
    flex-shrink: 0;
}
.pro .aspect-icon { background: rgba(0,229,160,0.1); }
.con .aspect-icon { background: rgba(255,77,109,0.1); }

.aspect-label {
    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.pro .aspect-label { color: var(--pro-text); }
.con .aspect-label { color: var(--con-text); }

/* ══════════════════════════════════════════════
   ASPECT OVERVIEW PILLS
══════════════════════════════════════════════ */
.pills-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 20px; }
.pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 50px;
    padding: 6px 14px;
    font-size: 0.80rem;
    font-weight: 600;
    border: 1px solid;
    transition: transform 0.15s ease;
}
.pill:hover { transform: scale(1.05); }
.pill.pos {
    background: rgba(0,229,160,0.08);
    border-color: rgba(0,229,160,0.25);
    color: var(--accent-green);
}
.pill.neg {
    background: rgba(255,77,109,0.08);
    border-color: rgba(255,77,109,0.25);
    color: var(--accent-red);
}

/* ══════════════════════════════════════════════
   RECOMMENDATION CARDS
══════════════════════════════════════════════ */
.rec-card {
    background: linear-gradient(135deg, rgba(61,127,255,0.06), rgba(0,212,255,0.03));
    border: 1px solid rgba(61,127,255,0.18);
    border-radius: var(--radius-md);
    padding: 12px 18px;
    margin-bottom: 8px;
    font-size: 0.93rem;
    color: #a8c0ff;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: border-color 0.2s ease;
}
.rec-card:hover { border-color: rgba(61,127,255,0.35); }

/* ══════════════════════════════════════════════
   EVIDENCE EXPANDERS
══════════════════════════════════════════════ */
div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
    transition: border-color 0.2s ease !important;
}
div[data-testid="stExpander"]:hover {
    border-color: var(--border-bright) !important;
}
div[data-testid="stExpander"] summary {
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 14px 18px !important;
    color: var(--text-primary) !important;
}

.ev-sentence {
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    margin: 5px 0;
    font-size: 0.86rem;
    line-height: 1.5;
    border-left: 3px solid;
    position: relative;
}
.ev-sentence.pos {
    background: rgba(0,229,160,0.05);
    border-color: var(--accent-green);
    color: #9af0d0;
}
.ev-sentence.neg {
    background: rgba(255,77,109,0.05);
    border-color: var(--accent-red);
    color: #ffb3c1;
}
.ev-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.ev-label.pos { color: var(--accent-green); }
.ev-label.neg { color: var(--accent-red); }

/* ══════════════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════════════ */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 2rem 0 1rem;
}
.section-header-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border-bright), transparent);
}
.section-header-text {
    font-family: var(--font-display);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--text-secondary);
    white-space: nowrap;
}
.section-header-icon { font-size: 1rem; }

/* ══════════════════════════════════════════════
   SPINNER & PROGRESS
══════════════════════════════════════════════ */
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

/* ══════════════════════════════════════════════
   BAR CHART
══════════════════════════════════════════════ */
div[data-testid="stVegaLiteChart"] canvas,
div[data-testid="stArrowVegaLiteChart"] { border-radius: var(--radius-md); }

/* ══════════════════════════════════════════════
   COLUMNS GAP
══════════════════════════════════════════════ */
div[data-testid="column"] { padding: 0 8px !important; }

/* ══════════════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════════════ */
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.6; }
}

/* Stagger animation delays for cards */
.aspect-card:nth-child(1) { animation-delay: 0.05s; }
.aspect-card:nth-child(2) { animation-delay: 0.10s; }
.aspect-card:nth-child(3) { animation-delay: 0.15s; }
.aspect-card:nth-child(4) { animation-delay: 0.20s; }
.aspect-card:nth-child(5) { animation-delay: 0.25s; }
.aspect-card:nth-child(6) { animation-delay: 0.30s; }
.metric-card:nth-child(1) { animation-delay: 0.05s; }
.metric-card:nth-child(2) { animation-delay: 0.10s; }
.metric-card:nth-child(3) { animation-delay: 0.15s; }
.metric-card:nth-child(4) { animation-delay: 0.20s; }
.metric-card:nth-child(5) { animation-delay: 0.25s; }
.metric-card:nth-child(6) { animation-delay: 0.30s; }
"""

# ─────────────────────────────────────────────
# HTML COMPONENT BUILDERS
# ─────────────────────────────────────────────

def inject_styles():
    """Call once at top of app.py after st.set_page_config()"""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def render_header():
    """Renders the animated hero header"""
    st.markdown("""
    <div class="hero-wrapper">
        <div class="hero-glow"></div>
        <div class="hero-badge">⚡ 100K+ Reviews Analyzed</div>
        <h1 class="hero-title">SmartBuy</h1>
        <p class="hero-subtitle">
            Deep aspect-level sentiment analysis across 100,000+ reviews from
            Amazon, Flipkart, Snapdeal &amp; more — discover what users really think.
        </p>
        <div class="hero-divider"></div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(icon, label):
    """Renders a styled section divider with label"""
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon">{icon}</span>
        <span class="section-header-text">{label}</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)


def render_similar_chips(similar_products):
    """Renders similar product chips"""
    if not similar_products:
        return
    chips = "".join([
        f'<span class="sim-chip"><span class="sim-chip-dot"></span>{p.title()}</span>'
        for p in similar_products
    ])
    st.markdown(f'<div class="sim-chips-wrap">{chips}</div>', unsafe_allow_html=True)


def render_metrics(avg_stars, total_reviews, pos_pct, category,
                   avg_price=None, verified_pct=None):
    """
    Renders a responsive metric card row.
    Shows 4 base cards; if avg_price or verified_pct are provided,
    adds up to 2 extra cards (price & verified %).
    """
    star_str = "⭐" * round(avg_stars)

    # Base 4 cards
    cards = f"""
        <div class="metric-card" style="--card-accent: linear-gradient(90deg, #ffd166, #ffaa00); --card-color: #ffd166;">
            <span class="metric-val">{star_str}</span>
            <span class="metric-lbl">Avg Rating · {avg_stars:.1f} / 5</span>
        </div>
        <div class="metric-card" style="--card-accent: linear-gradient(90deg, #3d7fff, #00d4ff); --card-color: #7eb8f7;">
            <span class="metric-val">{total_reviews:,}</span>
            <span class="metric-lbl">Total Reviews</span>
        </div>
        <div class="metric-card" style="--card-accent: linear-gradient(90deg, #00e5a0, #00b894); --card-color: #00e5a0;">
            <span class="metric-val">{pos_pct:.0f}%</span>
            <span class="metric-lbl">Positive Ratings</span>
        </div>
        <div class="metric-card" style="--card-accent: linear-gradient(90deg, #a29bfe, #6c5ce7); --card-color: #c8b4fe;">
            <span class="metric-val" style="font-size:1.2rem;">{category.title()}</span>
            <span class="metric-lbl">Category</span>
        </div>
    """

    # Optional: avg price card
    if avg_price is not None and not __import__('math').isnan(avg_price):
        price_display = f"₹{avg_price:,.0f}"
        cards += f"""
        <div class="metric-card" style="--card-accent: linear-gradient(90deg, #ffeaa7, #fdcb6e); --card-color: #ffeaa7;">
            <span class="metric-val" style="font-size:1.3rem;">{price_display}</span>
            <span class="metric-lbl">Avg Price (INR)</span>
        </div>
        """

    # Optional: verified purchase card
    if verified_pct is not None:
        cards += f"""
        <div class="metric-card" style="--card-accent: linear-gradient(90deg, #55efc4, #00b894); --card-color: #55efc4;">
            <span class="metric-val">{verified_pct:.0f}%</span>
            <span class="metric-lbl">Verified Purchases</span>
        </div>
        """

    st.markdown(f'<div class="metrics-row">{cards}</div>', unsafe_allow_html=True)


def render_verdict(n_pros, n_cons):
    """Renders the overall verdict banner"""
    if n_pros > n_cons:
        vtype, icon = "positive", "✅"
        title = "Mostly Positive"
        sub = f"{n_pros} positive aspects vs {n_cons} negatives — a solid choice."
    elif n_cons > n_pros:
        vtype, icon = "negative", "⚠️"
        title = "Mostly Negative"
        sub = f"{n_cons} negative aspects vs {n_pros} positives — approach with caution."
    else:
        vtype, icon = "mixed", "⚖️"
        title = "Mixed Reviews"
        sub = f"Equal split — {n_pros} pros and {n_cons} cons. Read the evidence carefully."

    st.markdown(f"""
    <div class="verdict-banner {vtype}">
        <div class="verdict-icon">{icon}</div>
        <div class="verdict-text">
            <div class="verdict-title {vtype}">{title}</div>
            <div class="verdict-sub">{sub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_aspect_card(aspect, verdict, icon):
    """Renders a single pro or con card"""
    cls = "pro" if verdict == "positive" else "con"
    st.markdown(f"""
    <div class="aspect-card {cls}">
        <div class="aspect-icon">{icon}</div>
        <div class="aspect-label">{aspect}</div>
    </div>
    """, unsafe_allow_html=True)


def render_pills(final_aspects, aspect_icons):
    """Renders aspect overview pills"""
    pills = ""
    for aspect, verdict in sorted(final_aspects.items()):
        icon = aspect_icons.get(aspect, "•")
        cls = "pos" if verdict == "positive" else "neg"
        pills += f'<span class="pill {cls}">{icon} {aspect.title()}</span>'
    st.markdown(f'<div class="pills-wrap">{pills}</div>', unsafe_allow_html=True)


def render_rec_card(text):
    """Renders a single recommendation card"""
    st.markdown(f'<div class="rec-card">{text}</div>', unsafe_allow_html=True)


def render_evidence_sentences(ev_pros, ev_cons, aspect):
    """Renders evidence sentences inside an expander"""
    html = ""
    if aspect in ev_pros:
        html += '<div class="ev-label pos">✔ Positive Mentions</div>'
        for s in ev_pros[aspect]:
            html += f'<div class="ev-sentence pos">"{s}"</div>'
    if aspect in ev_cons:
        html += '<div class="ev-label neg" style="margin-top:12px;">✘ Negative Mentions</div>'
        for s in ev_cons[aspect]:
            html += f'<div class="ev-sentence neg">"{s}"</div>'
    st.markdown(html, unsafe_allow_html=True)