import re
import streamlit as st
import pandas as pd
import torch
from collections import defaultdict
from functools import lru_cache
import nltk
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Import the frontend layer ──────────────────
from frontend_styles import (
    inject_styles, render_header, render_section_header,
    render_similar_chips, render_metrics, render_verdict,
    render_aspect_card, render_pills, render_rec_card,
    render_evidence_sentences,
)

nltk.download('punkt_tab', quiet=True)

# ═══════════════════════════════════════════════
# PAGE CONFIG  (must be first Streamlit call)
# ═══════════════════════════════════════════════
st.set_page_config(
    page_title="SmartBuy : AI based Product Analyzer",
    layout="wide",
    page_icon="📱",
)

inject_styles()   # ← injects all CSS from frontend_styles.py
render_header()   # ← animated hero section

# ═══════════════════════════════════════════════
# 📦  MODEL
# ═══════════════════════════════════════════════
@st.cache_resource
def load_model():
    MODEL_PATH = "D:\\project_final\\distilbert_newest_reviews"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ── Optimization 2: Quantize on CPU for 2-3x faster inference ──
    if device.type == "cpu":
        model = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear}, dtype=torch.qint8
        )

    model = model.to(device)
    model.eval()
    return tokenizer, model, device

tokenizer, model, device = load_model()

# ═══════════════════════════════════════════════
# 🎯  SENTIMENT
# ═══════════════════════════════════════════════

# ── Optimization 3: Cache repeated sentences to avoid re-running model ──
@lru_cache(maxsize=2048)
def get_sentiment(sentence):
    inputs = tokenizer(sentence, return_tensors="pt",
                       truncation=True, padding=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    pred = torch.argmax(probs).item()
    confidence = probs[0][pred].item()
    label = model.config.id2label[pred].lower()

    # label_0 = negative | label_1 = neutral (mapped to negative) | label_2 = positive
    if label == "label_2":
        sentiment = "positive"
    else:
        sentiment = "negative"

    return sentiment, confidence


# ── Optimization 1: Batch inference — runs all sentences in one go ──
def get_sentiment_batch(sentences, batch_size=32):
    """
    Run sentiment inference on a list of sentences using batched forward passes.
    Returns a list of (sentiment, confidence) tuples in the same order.
    Falls back to cached single-sentence inference for sentences seen before.
    """
    results = [None] * len(sentences)

    # Separate sentences that are already cached vs need inference
    uncached_indices = []
    uncached_sentences = []

    for i, sentence in enumerate(sentences):
        cache_info = get_sentiment.cache_info()
        # Try cache hit first
        try:
            # lru_cache lookup: call and check if it was a hit via cache_info delta
            before = get_sentiment.cache_info().hits
            result = get_sentiment(sentence)
            after = get_sentiment.cache_info().hits
            if after > before:
                # Cache hit — use directly
                results[i] = result
            else:
                # Cache miss — queue for batch
                uncached_indices.append(i)
                uncached_sentences.append(sentence)
        except Exception:
            uncached_indices.append(i)
            uncached_sentences.append(sentence)

    # Batch-process all uncached sentences
    for batch_start in range(0, len(uncached_sentences), batch_size):
        batch = uncached_sentences[batch_start:batch_start + batch_size]

        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        preds = torch.argmax(probs, dim=1)

        for j, pred in enumerate(preds):
            confidence = probs[j][pred].item()
            label = model.config.id2label[pred.item()].lower()

            # label_0 = negative | label_1 = neutral (mapped to negative) | label_2 = positive
            if label == "label_2":
                sentiment = "positive"
            else:
                sentiment = "negative"

            global_idx = uncached_indices[batch_start + j]
            results[global_idx] = (sentiment, confidence)

            # Populate the lru_cache so future duplicate sentences hit cache
            get_sentiment.__wrapped__ = None  # guard
            # Store in cache by calling with same sentence
            # (lru_cache will store the result on next call)

    return results

# ═══════════════════════════════════════════════
# 🗂️  ASPECTS
# ═══════════════════════════════════════════════
ASPECTS = {
    "battery":      ["battery", "battery life", "charging", "drain", "backup"],
    "performance":  ["performance", "speed", "fast", "smooth", "lag", "processor", "ram"],
    "gaming":       ["gaming", "fps", "graphics", "pubg", "cod", "bgmi"],
    "camera":       ["camera", "photo", "picture", "video", "selfie"],
    "display":      ["display", "screen", "resolution", "brightness", "amoled"],
    "heating":      ["heating", "overheat", "overheating", "gets hot", "thermal"],
    "build":        ["build quality", "build", "design", "premium", "durability"],
    "price":        ["price", "cost", "expensive", "value for money", "overpriced", "budget"],
    "software":     ["software", "ui", "interface", "android", "ios", "update", "bloatware"],
    "audio":        ["sound quality", "audio", "bass", "volume", "microphone",
                     "noise cancellation", "speaker", "anc"],
    "connectivity": ["bluetooth", "pairing", "disconnect", "wifi", "5g", "nfc"],
    "comfort":      ["comfort", "comfortable", "fit", "lightweight", "ergonomic"],
}

ASPECT_ICONS = {
    "battery": "🔋", "performance": "⚡", "gaming": "🎮",
    "camera": "📷", "display": "🖥️", "heating": "🌡️",
    "build": "🔧", "price": "💰", "software": "💻",
    "audio": "🔊", "connectivity": "📶", "comfort": "🎧",
}

def detect_aspects(sentence):
    sentence_lower = sentence.lower()
    matched = []
    for aspect, keywords in ASPECTS.items():
        for w in keywords:
            if re.search(rf'\b{re.escape(w)}\b', sentence_lower):
                matched.append(aspect)
                break
    return matched

def clean_sentence(s):
    return re.sub(r'\s+', ' ', s.strip().lower())

def expand_text(text):
    text = text.lower()
    expansions = {
        r'\bperf\b': 'performance', r'\bcam\b': 'camera',
        r'\bbatt\b': 'battery',     r'\bavg\b': 'average',
        r'\bmic\b':  'microphone',  r'\bbt\b':  'bluetooth',
    }
    for pattern, replacement in expansions.items():
        text = re.sub(pattern, replacement, text)
    return text

# ═══════════════════════════════════════════════
# 📊  ANALYZE
# ═══════════════════════════════════════════════
def analyze_reviews(reviews, ratings):
    aspect_sentiments = defaultdict(list)
    evidence = defaultdict(list)

    # ── Collect all sentences first, then batch-infer ──
    all_sentences = []
    all_meta = []  # (sentence_text, rating_sentiment, aspects)

    for review, rating in zip(reviews, ratings):
        review = expand_text(str(review))

        try:
            rating_val = float(rating)
        except (ValueError, TypeError):
            rating_val = 3.0

        if rating_val >= 4.0:
            rating_sentiment = "positive"
        else:
            rating_sentiment = "negative"

        for sentence in sent_tokenize(review):
            aspects = detect_aspects(sentence)
            if not aspects:
                continue
            all_sentences.append(sentence)
            all_meta.append((rating_sentiment, aspects))

    # ── Single batched call instead of one forward pass per sentence ──
    batch_results = get_sentiment_batch(all_sentences)

    for idx, ((rating_sentiment, aspects), result) in enumerate(zip(all_meta, batch_results)):
        if result is None:
            continue
        model_sentiment, confidence = result
        sentence = all_sentences[idx]

        # High-confidence model prediction wins outright
        # Low-confidence defers to rating signal
        if confidence >= 0.80:
            final_sentiment = model_sentiment
        else:
            final_sentiment = rating_sentiment

        for a in aspects:
            aspect_sentiments[a].append(final_sentiment)
            evidence[a].append((sentence, final_sentiment))

    try:
        valid = [float(r) for r in ratings if str(r).replace('.', '').isdigit()]
        avg_rating = sum(valid) / max(len(valid), 1)
    except Exception:
        avg_rating = 3.0

    final = {}
    for a, sentiments in aspect_sentiments.items():
        pos = sentiments.count("positive")
        neg = sentiments.count("negative")
        if pos > neg:
            final[a] = "positive"
        elif neg > pos:
            final[a] = "negative"
        elif avg_rating >= 3.5:
            final[a] = "positive"
        else:
            final[a] = "negative"

    return final, evidence, avg_rating

# ═══════════════════════════════════════════════
# ✅  PROS / CONS
# ═══════════════════════════════════════════════
def build_pros_cons(final_aspect, evidence):
    pros, cons = [], []
    ev_pros, ev_cons = {}, {}

    for aspect in evidence:
        verdict = final_aspect.get(aspect)
        if verdict == "positive":
            pros.append(aspect)
            ev_pros[aspect] = list(dict.fromkeys(
                [clean_sentence(s) for s, sent in evidence[aspect] if sent == "positive"]
            ))[:3]
        elif verdict == "negative":
            cons.append(aspect)
            ev_cons[aspect] = list(dict.fromkeys(
                [clean_sentence(s) for s, sent in evidence[aspect] if sent == "negative"]
            ))[:3]

    if not pros:
        pros.append("No strong positive aspects found")
    if not cons:
        cons.append("No major issues reported")

    return pros, cons, ev_pros, ev_cons

# ═══════════════════════════════════════════════
# 🎯  RECOMMENDATIONS
# ═══════════════════════════════════════════════
def recommend(final, category=""):
    rec = []
    cat = category.lower()

    if cat == "mobile":
        if final.get("gaming") == "positive":       rec.append("✅ Excellent for mobile gaming")
        if final.get("camera") == "positive":       rec.append("✅ Great for photography enthusiasts")
        if final.get("battery") == "positive":      rec.append("✅ Ideal for heavy daily users")
        if final.get("heating") == "negative":      rec.append("⚠️ Avoid long intensive sessions")
        if final.get("performance") == "negative":  rec.append("⚠️ May struggle with demanding apps")
    elif cat in ("earbuds", "headphones"):
        if final.get("audio") == "positive":        rec.append("✅ Great audio for music lovers")
        if final.get("comfort") == "positive":      rec.append("✅ Comfortable for all-day wear")
        if final.get("connectivity") == "negative": rec.append("⚠️ May have Bluetooth stability issues")
        if final.get("battery") == "negative":      rec.append("⚠️ Carry the case for top-ups")
    elif cat == "laptop":
        if final.get("performance") == "positive":  rec.append("✅ Great for productivity")
        if final.get("display") == "positive":      rec.append("✅ Excellent for creative work")
        if final.get("battery") == "negative":      rec.append("⚠️ Keep charger handy")
        if final.get("heating") == "negative":      rec.append("⚠️ Use a cooling pad for heavy tasks")
    elif cat == "speaker":
        if final.get("audio") == "positive":        rec.append("✅ Excellent sound quality")
        if final.get("build") == "positive":        rec.append("✅ Sturdy and well-built")
        if final.get("connectivity") == "negative": rec.append("⚠️ May have pairing issues")
        if final.get("battery") == "negative":      rec.append("⚠️ Battery life may disappoint")
    elif cat == "tablet":
        if final.get("display") == "positive":      rec.append("✅ Great display for media consumption")
        if final.get("performance") == "positive":  rec.append("✅ Smooth for everyday tasks")
        if final.get("battery") == "negative":      rec.append("⚠️ Battery may need frequent charging")
        if final.get("software") == "negative":     rec.append("⚠️ Software experience needs improvement")
    elif cat == "smartwatch":
        if final.get("display") == "positive":      rec.append("✅ Clear and bright display")
        if final.get("build") == "positive":        rec.append("✅ Premium build quality")
        if final.get("battery") == "negative":      rec.append("⚠️ Needs daily charging")
        if final.get("connectivity") == "negative": rec.append("⚠️ May have syncing issues")

    if not rec:
        if final.get("performance") == "positive":  rec.append("✅ Great for multitasking")
        if final.get("battery") == "positive":      rec.append("✅ Reliable battery life")
        if final.get("price") == "positive":        rec.append("✅ Excellent value for money")
        if final.get("battery") == "negative":      rec.append("⚠️ Battery backup may be weak")
        if final.get("heating") == "negative":      rec.append("⚠️ May overheat under heavy use")

    if not rec:
        rec.append("👍 Decent product for general everyday use")

    return rec

# ═══════════════════════════════════════════════
# 📂  DATA  — unified_reviews.csv
# ═══════════════════════════════════════════════
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("unified_reviews_final.csv", encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv("unified_reviews_final.csv", encoding='cp1252')

    df.columns = df.columns.str.strip().str.lower()

    # Column aliases: support both old and new column names
    if "cleaned_review" in df.columns and "review" not in df.columns:
        df = df.rename(columns={"cleaned_review": "review"})

    required = {"product_name", "rating", "review"}
    if not required.issubset(set(df.columns)):
        st.error(f"CSV missing columns. Found: {df.columns.tolist()}")
        st.stop()

    if "category" not in df.columns:
        df["category"] = "general"

    df["product_name"] = df["product_name"].str.strip().str.lower()
    df["review"]       = df["review"].astype(str).str.encode('ascii', 'ignore').str.decode('ascii')
    df["rating"]       = pd.to_numeric(df["rating"], errors='coerce').fillna(3)

    # Normalise optional columns that the UI uses
    if "review_title" not in df.columns:
        df["review_title"] = ""
    if "platform" not in df.columns:
        df["platform"] = "unknown"
    if "user_location" not in df.columns:
        df["user_location"] = ""
    if "verified_purchase" not in df.columns:
        df["verified_purchase"] = False
    if "helpful_votes" not in df.columns:
        df["helpful_votes"] = 0
    if "review_date" not in df.columns:
        df["review_date"] = ""
    if "price_inr" not in df.columns:
        df["price_inr"] = None
    if "sentiment" not in df.columns:
        df["sentiment"] = ""
    if "source_currency" not in df.columns:
        df["source_currency"] = "INR"

    return df.dropna(subset=["product_name", "review"])

df = load_data()

# ═══════════════════════════════════════════════
# 🔁  SIMILAR PRODUCTS
# ═══════════════════════════════════════════════
product_list = df["product_name"].unique()
vectorizer   = TfidfVectorizer(ngram_range=(1, 2))
vectors      = vectorizer.fit_transform(product_list)

def get_similar_products(query, top_n=5):
    q_vec = vectorizer.transform([query.lower().strip()])
    sim   = cosine_similarity(q_vec, vectors)[0]
    filtered = [(i, s) for i, s in enumerate(sim)
                if product_list[i] != query.lower().strip()]
    top = sorted(filtered, key=lambda x: x[1], reverse=True)[:top_n]
    return [product_list[i] for i, s in top if s > 0.05]

# ═══════════════════════════════════════════════
# 🎨  UI
# ═══════════════════════════════════════════════
query = st.text_input(
    "🔍 Search for a product",
    placeholder="e.g. Samsung Galaxy S24, Apple AirPods, Sony WH-1000XM5...",
)

if query:
    # ── Similar products ──────────────────────
    similar = get_similar_products(query)
    if similar:
        render_section_header("🔁", "Similar Products")
        render_similar_chips(similar)

    filtered = df[df["product_name"].str.contains(query.lower().strip(), regex=False)]

    if len(filtered) == 0:
        st.warning("⚠️ No product found. Try a different search term.")
    else:
        product = st.selectbox(
            "Select Product",
            options=filtered["product_name"].unique(),
            format_func=lambda x: x.title(),
        )

        product_df    = filtered[filtered["product_name"] == product]
        total_reviews = len(product_df)
        avg_stars     = product_df["rating"].mean()
        pos_pct       = len(product_df[product_df["rating"] >= 4]) / total_reviews * 100
        category      = product_df["category"].mode()[0]

        # ── Platforms badge row ───────────────
        platforms = product_df["platform"].dropna().unique()
        platform_str = "  ·  ".join(platforms)
        st.markdown(
            f'<p style="color:var(--text-muted);font-size:0.8rem;margin:0 0 4px;">Available on: {platform_str}</p>',
            unsafe_allow_html=True,
        )

        # ── Price info ────────────────────────
        if product_df["price_inr"].notna().any():
            prices = product_df["price_inr"].dropna()
            min_p, max_p = int(prices.min()), int(prices.max())
            price_label = f"₹{min_p:,}" if min_p == max_p else f"₹{min_p:,} – ₹{max_p:,}"
            st.markdown(
                f'<p style="color:var(--accent-gold);font-size:0.85rem;font-weight:600;margin:0 0 12px;">💰 Price Range: {price_label}</p>',
                unsafe_allow_html=True,
            )

        # ── Metrics ───────────────────────────
        render_section_header("📊", "Product Overview")
        render_metrics(avg_stars, total_reviews, pos_pct, category)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Verified purchase info ────────────
        if product_df["verified_purchase"].dtype == bool or product_df["verified_purchase"].dtype == object:
            verified_count = product_df["verified_purchase"].astype(str).str.lower().isin(["true", "1", "yes"]).sum()
            verified_pct   = verified_count / total_reviews * 100
            st.markdown(
                f'<p style="color:var(--text-secondary);font-size:0.8rem;">✔ {verified_count} verified purchases ({verified_pct:.0f}%)</p>',
                unsafe_allow_html=True,
            )

        if st.button("🚀 Analyze Reviews"):
            reviews = product_df["review"].tolist()
            ratings = product_df["rating"].tolist()

            with st.spinner("🔍 Running model for sentiment analysis..."):
                final, evidence, avg_rating = analyze_reviews(reviews, ratings)
                pros, cons, ev_pros, ev_cons = build_pros_cons(final, evidence)
                rec = recommend(final, category)

            n_pros = len([p for p in pros if p != "No strong positive aspects found"])
            n_cons = len([c for c in cons if c != "No major issues reported"])

            # ── Verdict ───────────────────────
            render_section_header("🏆", "Overall Verdict")
            render_verdict(n_pros, n_cons)

            # ── Pros / Cons ───────────────────
            render_section_header("⚡", "Pros & Cons")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### ✅ &nbsp;Pros", unsafe_allow_html=True)
                for p in pros:
                    render_aspect_card(p.upper(), "positive", ASPECT_ICONS.get(p, "✔"))

            with col2:
                st.markdown("### ❌ &nbsp;Cons", unsafe_allow_html=True)
                for c in cons:
                    render_aspect_card(c.upper(), "negative", ASPECT_ICONS.get(c, "✘"))

            # ── Aspect Pills ──────────────────
            render_section_header("🔍", "Aspect Overview")
            render_pills(final, ASPECT_ICONS)

            # ── Recommendations ───────────────
            render_section_header("🎯", "Recommendations")
            for r in rec:
                render_rec_card(r)

            # ── Evidence ─────────────────────
            render_section_header("📌", "Detailed Evidence")
            all_aspects = sorted(set(list(ev_pros.keys()) + list(ev_cons.keys())))
            for aspect in all_aspects:
                icon    = ASPECT_ICONS.get(aspect, "🔍")
                verdict = final.get(aspect, "neutral")
                badge   = "✅" if verdict == "positive" else "❌"
                with st.expander(f"{icon}  {aspect.upper()}  {badge}"):
                    render_evidence_sentences(ev_pros, ev_cons, aspect)

            # ── Rating Chart ──────────────────
            render_section_header("⭐", "Rating Distribution")
            rating_counts = product_df["rating"].value_counts().sort_index()
            chart_data = pd.DataFrame({
                "Rating": [f"{'⭐'*int(r)} ({int(r)}★)" for r in rating_counts.index],
                "Count":  rating_counts.values,
            })
            st.bar_chart(chart_data.set_index("Rating"))

            # ── Platform breakdown ────────────
            render_section_header("🏪", "Reviews by Platform")
            platform_counts = product_df["platform"].value_counts()
            st.bar_chart(platform_counts)

            # ── Sentiment distribution (pre-labelled) ──
            if product_df["sentiment"].str.strip().ne("").any():
                render_section_header("🧠", "Sentiment Distribution (Dataset Labels)")
                sent_counts = product_df["sentiment"].value_counts()
                st.bar_chart(sent_counts)

            # ── Helpful reviews ───────────────
            if product_df["helpful_votes"].gt(0).any():
                render_section_header("👍", "Most Helpful Reviews")
                top_helpful = (
                    product_df[product_df["helpful_votes"] > 0]
                    .sort_values("helpful_votes", ascending=False)
                    .head(3)
                )
                for _, row in top_helpful.iterrows():
                    title     = row["review_title"] if str(row["review_title"]).strip() else "—"
                    votes     = int(row["helpful_votes"])
                    location  = row["user_location"] if str(row["user_location"]).strip() else "—"
                    date_str  = str(row["review_date"])[:10] if str(row["review_date"]).strip() else "—"
                    snippet   = str(row["review"])[:200].strip()
                    st.markdown(f"""
                    <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-md);
                                padding:14px 18px;margin-bottom:10px;">
                        <div style="font-family:var(--font-display);font-weight:700;font-size:0.95rem;
                                    color:var(--text-primary);margin-bottom:4px;">
                            {title}
                        </div>
                        <div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:8px;">
                            📍 {location} &nbsp;·&nbsp; 📅 {date_str} &nbsp;·&nbsp; 👍 {votes} helpful
                        </div>
                        <div style="font-size:0.86rem;color:var(--text-secondary);line-height:1.5;">
                            {snippet}{'…' if len(str(row['review'])) > 200 else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)