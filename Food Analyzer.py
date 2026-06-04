import streamlit as st
import requests
import base64
import json
import time
from PIL import Image
import io
import os

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")

st.set_page_config(
    page_title="NutriLens · AI Food Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #0e0f11 !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, header, footer, .stDeployButton { display: none !important; }

/* Remove ALL default Streamlit padding */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
.stApp > div { padding: 0 !important; }
section.main > div { padding: 0 !important; }
section[data-testid="stSidebar"] { display: none; }
div[data-testid="stToolbar"] { display: none; }

/* Background gradients */
.stApp {
    background: #0e0f11 !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,90,20,0.08) 0%, transparent 50%) !important;
}

p, span, div, li { color: #e8e4dc; }

/* ── Two-column layout ── */
[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    align-items: flex-start !important;
    min-height: calc(100vh - 80px);
}

[data-testid="column"]:first-child {
    border-right: 1px solid rgba(255,255,255,0.08) !important;
    padding: 2rem 1.75rem 3rem 1.75rem !important;
    min-height: calc(100vh - 80px);
    background: rgba(255,255,255,0.01);
}

[data-testid="column"]:last-child {
    padding: 2.5rem 3rem 3rem 3rem !important;
    min-height: calc(100vh - 80px);
    overflow-y: auto;
}

/* ── Header ── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 2.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 0;
}
.logo-group { display: flex; align-items: baseline; gap: 0.5rem; flex-wrap: wrap; }
.logo-word {
    font-family: 'DM Serif Display', serif;
    font-size: 1.85rem;
    letter-spacing: -0.03em;
    color: #fff !important;
}
.logo-word em { font-style: italic; color: #ff7a38 !important; }
.logo-tag {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.14em;
    text-transform: uppercase; color: rgba(255,255,255,0.35) !important;
    padding: 3px 9px; border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px; margin-left: 0.4rem;
}
.header-status {
    display: flex; align-items: center; gap: 7px;
    font-size: 0.78rem; color: rgba(255,255,255,0.4) !important;
}
.status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #3ec97a; box-shadow: 0 0 8px #3ec97a;
    animation: pulse-dot 2s infinite; flex-shrink: 0;
}
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.45} }

/* ── Panel labels ── */
.panel-label {
    font-size: 0.66rem !important; font-weight: 700 !important;
    letter-spacing: 0.16em; text-transform: uppercase;
    color: rgba(255,255,255,0.3) !important;
    margin-bottom: 0.75rem; margin-top: 1.75rem; display: block;
}
.panel-label:first-child { margin-top: 0; }

/* ── Model card ── */
.model-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 12px; padding: 1rem 1.25rem; margin-top: 0.75rem;
}
.model-name { font-size: 0.9rem; font-weight: 500; color: #e8e4dc !important; }
.model-id   { font-size: 0.71rem; color: rgba(255,255,255,0.28) !important; font-family: monospace; margin-top: 4px; }
.model-badge {
    display: inline-block; font-size: 0.64rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase; padding: 2px 8px;
    border-radius: 4px; background: rgba(62,201,122,0.12);
    color: #3ec97a !important; border: 1px solid rgba(62,201,122,0.22);
    margin-top: 8px;
}

/* ── Buttons ── */
.stButton { margin-top: 0.5rem !important; }
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important; font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    border-radius: 10px !important; padding: 0.72rem 1.5rem !important;
    width: 100% !important; cursor: pointer !important;
    transition: all 0.2s ease !important;
    border: none !important;
}

/* Analyze — primary orange */
[data-testid="column"]:first-child div[data-testid="stButton"]:nth-of-type(1) > button,
[data-testid="column"]:first-child .stButton:nth-of-type(1) > button {
    background: linear-gradient(135deg, #ff7a38 0%, #ff4e0d 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 20px rgba(255,78,13,0.3), 0 1px 0 rgba(255,255,255,0.1) inset !important;
    margin-top: 1rem !important;
}
[data-testid="column"]:first-child div[data-testid="stButton"]:nth-of-type(1) > button:hover,
[data-testid="column"]:first-child .stButton:nth-of-type(1) > button:hover {
    box-shadow: 0 6px 28px rgba(255,78,13,0.45), 0 1px 0 rgba(255,255,255,0.1) inset !important;
    transform: translateY(-1px) !important;
}

/* Clear — ghost red */
[data-testid="column"]:first-child div[data-testid="stButton"]:nth-of-type(2) > button,
[data-testid="column"]:first-child .stButton:nth-of-type(2) > button {
    background: rgba(255,255,255,0.04) !important;
    color: rgba(255,255,255,0.4) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    box-shadow: none !important;
    margin-top: 0.5rem !important;
}
[data-testid="column"]:first-child div[data-testid="stButton"]:nth-of-type(2) > button:hover,
[data-testid="column"]:first-child .stButton:nth-of-type(2) > button:hover {
    background: rgba(255,80,80,0.08) !important;
    color: #ff8080 !important;
    border-color: rgba(255,80,80,0.22) !important;
}

.stButton > button:active { transform: translateY(0) !important; opacity: 0.85 !important; }

/* ── File uploader ── */
.stFileUploader { background: transparent !important; }
.stFileUploader > div { background: transparent !important; border: none !important; }
[data-testid="stFileUploadDropzone"] {
    background: rgba(255,122,56,0.03) !important;
    border: 2px dashed rgba(255,122,56,0.28) !important;
    border-radius: 14px !important; color: rgba(255,255,255,0.45) !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: rgba(255,122,56,0.55) !important;
    background: rgba(255,122,56,0.06) !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; color: #e8e4dc !important;
}

/* ── Misc ── */
[data-testid="stImage"] { margin-top: 1rem !important; }
[data-testid="stImage"] img { border-radius: 14px; width: 100%; }
.stSpinner > div { color: #ff7a38 !important; }
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    margin-top: 1.5rem !important;
}

/* ── Section heading ── */
.section-heading {
    font-size: 0.66rem !important; font-weight: 700 !important;
    letter-spacing: 0.16em; text-transform: uppercase;
    color: rgba(255,255,255,0.3) !important;
    margin-bottom: 1rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.06); display: block;
}

/* ── Meal hero ── */
.meal-hero { margin-bottom: 2.5rem; }
.meal-name-big {
    font-family: 'DM Serif Display', serif; font-size: 2.6rem; line-height: 1.1;
    letter-spacing: -0.02em; color: #fff !important; margin-bottom: 0.6rem;
}
.meal-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 1rem; align-items: center; }
.meta-pill {
    font-size: 0.73rem; font-weight: 500; padding: 5px 12px; border-radius: 20px;
    background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.6) !important;
    border: 1px solid rgba(255,255,255,0.1);
}
.meta-pill.orange { background: rgba(255,122,56,0.14); color: #ff9a68 !important; border-color: rgba(255,122,56,0.25); }
.conf-high { color: #3ec97a !important; background: rgba(62,201,122,0.1) !important; border-color: rgba(62,201,122,0.2) !important; }
.conf-med  { color: #f5c842 !important; background: rgba(245,200,66,0.1) !important; border-color: rgba(245,200,66,0.2) !important; }
.conf-low  { color: #ff5a5a !important; background: rgba(255,90,90,0.1) !important; border-color: rgba(255,90,90,0.2) !important; }

/* ── Nutrition grid ── */
.nutrition-section { margin-bottom: 2.5rem; }
.nutrition-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 12px; margin-top: 1rem; }
.nut-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.1rem 0.5rem; text-align: center;
    transition: border-color 0.2s, background 0.2s;
}
.nut-card:hover { border-color: rgba(255,122,56,0.3); background: rgba(255,122,56,0.04); }
.nut-val   { font-size: 1.55rem; font-weight: 700; color: #ff7a38 !important; line-height: 1; }
.nut-unit  { font-size: 0.6rem; color: rgba(255,255,255,0.25) !important; margin-top: 3px; }
.nut-label { font-size: 0.67rem; color: rgba(255,255,255,0.42) !important; margin-top: 7px; font-weight: 600; letter-spacing: 0.04em; }

/* ── Health bar ── */
.health-bar-wrap {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 1.4rem 1.75rem; margin-bottom: 2.5rem;
    margin-top: 1rem;
    display: flex; align-items: center; gap: 1.75rem;
}
.health-score-num {
    font-family: 'DM Serif Display', serif; font-size: 3.2rem;
    line-height: 1; min-width: 68px; text-align: center;
}
.health-bar-track { flex:1; height:6px; background:rgba(255,255,255,0.09); border-radius:3px; overflow:hidden; }
.health-bar-fill  { height:100%; border-radius:3px; transition: width 0.6s ease; }
.health-notes { font-size: 0.83rem; color: rgba(255,255,255,0.42) !important; margin-top: 10px; line-height: 1.5; }

/* ── Detail grid ── */
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; margin-top: 1rem; }
.detail-block {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px; padding: 1.25rem 1.5rem;
}
.detail-block ul { list-style: none; padding: 0; margin: 0.75rem 0 0 0; }
.detail-block ul li {
    font-size: 0.84rem; color: rgba(255,255,255,0.58) !important;
    padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
    display: flex; align-items: center; gap: 9px;
}
.detail-block ul li::before { content: "·"; color: #ff7a38; font-size: 1.2em; }
.detail-block ul li:last-child { border-bottom: none; }
.tag-chip {
    display: inline-block; font-size: 0.72rem; font-weight: 600;
    padding: 4px 11px; border-radius: 20px;
    background: rgba(62,201,122,0.09); color: #5edd98 !important;
    border: 1px solid rgba(62,201,122,0.18); margin: 4px 4px 0 0;
}
.allergen-chip {
    display: inline-block; font-size: 0.72rem; font-weight: 600;
    padding: 4px 11px; border-radius: 20px;
    background: rgba(255,90,90,0.09); color: #ff8080 !important;
    border: 1px solid rgba(255,90,90,0.18); margin: 4px 4px 0 0;
}

/* ── Agent log ── */
.agent-log {
    background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 1.1rem 1.4rem; margin-bottom: 2rem;
    font-family: monospace; font-size: 0.78rem;
}
.agent-step        { padding: 4px 0; color: rgba(255,255,255,0.4) !important; }
.agent-step.done   { color: #3ec97a !important; }
.agent-step.active { color: #f5c842 !important; }
.agent-step.error  { color: #ff5a5a !important; }

/* ── Fallback notice ── */
.fallback-notice {
    background: rgba(245,200,66,0.07); border: 1px solid rgba(245,200,66,0.2);
    border-radius: 10px; padding: 0.7rem 1.1rem;
    font-size: 0.8rem; color: #f5c842 !important; margin-bottom: 1.75rem;
}

/* ── Empty states ── */
.empty-state-title { font-family:'DM Serif Display',serif; font-size:2rem; color:rgba(255,255,255,0.13) !important; margin-bottom: 0.5rem; }
.empty-state-sub   { font-size:0.85rem; color:rgba(255,255,255,0.2) !important; max-width:300px; line-height: 1.6; }

/* ── Mobile responsive ── */
@media (max-width: 768px) {
    .app-header {
        flex-direction: column; align-items: flex-start;
        gap: 0.75rem; padding: 1.25rem 1.25rem;
    }
    .header-status { align-self: flex-start; }
    [data-testid="column"]:first-child {
        border-right: none !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        padding: 1.5rem 1.25rem 2rem !important;
    }
    [data-testid="column"]:last-child {
        padding: 1.75rem 1.25rem 2rem !important;
    }
    .nutrition-grid { grid-template-columns: repeat(3,1fr) !important; }
    .detail-grid    { grid-template-columns: 1fr !important; }
    .meal-name-big  { font-size: 1.9rem !important; }
    .health-bar-wrap { flex-direction: column; gap: 1rem; padding: 1.25rem; }
    .health-score-num { font-size: 2.5rem; }
}
</style>
""", unsafe_allow_html=True)

# ── Models ────────────────────────────────────────────────────────────────────
FREE_VISION_MODELS = {
    "Kimi K2.6":                "moonshotai/kimi-k2.6:free",
    "Nemotron Nano 12B VL":     "nvidia/nemotron-nano-12b-v2-vl:free",
    "Nemotron Nano Omni 30B":   "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "Gemma 4 31B":              "google/gemma-4-31b-it:free",
    "Gemma 4 26B (MoE)":       "google/gemma-4-26b-a4b-it:free",
    "Auto-Router":              "openrouter/free",
}

FALLBACK_ORDER = [
    "moonshotai/kimi-k2.6:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "openrouter/free",
]

SYSTEM_PROMPT = """You are an expert nutritionist and culinary analyst.
When given a food image, analyze it and return ONLY valid JSON — no markdown, no code fences, no extra text.
Use exactly this structure:
{
  "meal_name": "string",
  "description": "1-2 sentence description",
  "cuisine_type": "string",
  "meal_type": ["breakfast|lunch|dinner|snack|dessert"],
  "ingredients": ["ingredient1", "ingredient2"],
  "nutrition_per_serving": {
    "calories": 0,
    "protein_g": 0,
    "carbs_g": 0,
    "fat_g": 0,
    "fiber_g": 0,
    "sugar_g": 0
  },
  "serving_size": "e.g. 1 plate ~400g",
  "health_score": 7,
  "health_notes": "string",
  "allergens": ["gluten", "dairy"],
  "diet_tags": ["vegetarian", "gluten-free"],
  "preparation_time": "~20 mins",
  "confidence": "high|medium|low"
}
Return ONLY the JSON object."""

# ── Session state ─────────────────────────────────────────────────────────────
if "result"       not in st.session_state: st.session_state.result       = None
if "used_model"   not in st.session_state: st.session_state.used_model   = None
if "clear_flag"   not in st.session_state: st.session_state.clear_flag   = False

# ── Helpers ───────────────────────────────────────────────────────────────────
def image_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def call_model(model_id: str, img_b64: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://nutrilens.app",
        "X-Title": "NutriLens Food Analyzer",
    }
    payload = {
        "model": model_id.strip(),
        "max_tokens": 1200,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    {"type": "text", "text": "Analyze this food image and return the JSON."},
                ],
            },
        ],
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers, json=payload, timeout=60
    )
    if resp.status_code in (400, 404):
        raise ValueError(f"Model unavailable ({resp.status_code}): {model_id}")
    if resp.status_code == 429:
        raise ValueError(f"Rate limited: {model_id}")
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                raw = part; break
    s, e = raw.find("{"), raw.rfind("}") + 1
    if s != -1 and e > s:
        raw = raw[s:e]
    return json.loads(raw)

def analyze_agentic(primary_model: str, img_b64: str, log_placeholder):
    models = [primary_model.strip()] + [m for m in FALLBACK_ORDER if m != primary_model.strip()]
    steps  = []

    def render():
        html = '<div class="agent-log">'
        for cls, txt in steps:
            html += f'<div class="agent-step {cls}">{txt}</div>'
        html += '</div>'
        log_placeholder.markdown(html, unsafe_allow_html=True)

    steps.append(("done",   "▶ NutriLens agentic analysis started"))
    steps.append(("done",   "✓ Image encoded and pre-processed"))
    render()

    for i, model in enumerate(models):
        steps.append(("active", f"→ Trying model [{i+1}/{len(models)}]: {model}"))
        render()
        try:
            data = call_model(model, img_b64)
            steps[-1] = ("done", f"✓ Success with: {model}")
            steps.append(("done", "✓ JSON parsed and validated"))
            steps.append(("done", "✓ Analysis complete"))
            render()
            return data, model
        except (ValueError, requests.HTTPError, json.JSONDecodeError) as ex:
            steps[-1] = ("error", f"✗ {model} — {str(ex)[:60]}")
            render()
            time.sleep(1.5)
        except Exception as ex:
            steps[-1] = ("error", f"✗ {model} — unexpected: {str(ex)[:60]}")
            render()
            time.sleep(1.5)

    steps.append(("error", "✗ All models exhausted"))
    render()
    raise RuntimeError("All models failed. Check API key or try again later.")

def render_results(data: dict, used_model: str, primary_model: str):
    if used_model != primary_model:
        st.markdown(
            f'<div class="fallback-notice">⚡ Fallback used: <b>{used_model}</b></div>',
            unsafe_allow_html=True
        )

    conf       = data.get("confidence", "medium")
    conf_class = {"high":"conf-high","medium":"conf-med","low":"conf-low"}.get(conf,"conf-med")
    conf_icon  = {"high":"🟢","medium":"🟡","low":"🔴"}.get(conf,"🟡")
    meal_types = " · ".join(data.get("meal_type", []))
    cuisine    = data.get("cuisine_type", "—")
    prep       = data.get("preparation_time", "")
    serving    = data.get("serving_size", "")

    st.markdown(f"""
    <div class="meal-hero">
      <div class="meal-name-big">{data.get("meal_name","Unknown")}</div>
      <div style="font-size:0.88rem;color:rgba(255,255,255,0.42);margin-top:8px;line-height:1.55;">
        {data.get("description","")}
      </div>
      <div class="meal-meta">
        <span class="meta-pill orange">{cuisine}</span>
        <span class="meta-pill">{meal_types}</span>
        {"<span class='meta-pill'>⏱ "+prep+"</span>" if prep else ""}
        {"<span class='meta-pill'>🍽 "+serving+"</span>" if serving else ""}
        <span class="meta-pill {conf_class}">{conf_icon} {conf} confidence</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    n = data.get("nutrition_per_serving", {})
    st.markdown('<div class="nutrition-section"><span class="section-heading">Nutrition per serving</span>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="nutrition-grid">
      <div class="nut-card"><div class="nut-val">{n.get("calories","—")}</div><div class="nut-unit">kcal</div><div class="nut-label">Calories</div></div>
      <div class="nut-card"><div class="nut-val">{n.get("protein_g","—")}</div><div class="nut-unit">g</div><div class="nut-label">Protein</div></div>
      <div class="nut-card"><div class="nut-val">{n.get("carbs_g","—")}</div><div class="nut-unit">g</div><div class="nut-label">Carbs</div></div>
      <div class="nut-card"><div class="nut-val">{n.get("fat_g","—")}</div><div class="nut-unit">g</div><div class="nut-label">Fat</div></div>
      <div class="nut-card"><div class="nut-val">{n.get("fiber_g","—")}</div><div class="nut-unit">g</div><div class="nut-label">Fiber</div></div>
      <div class="nut-card"><div class="nut-val">{n.get("sugar_g","—")}</div><div class="nut-unit">g</div><div class="nut-label">Sugar</div></div>
    </div></div>
    """, unsafe_allow_html=True)

    score = data.get("health_score", 5)
    try:    score_int = int(score)
    except: score_int = 5
    bar_pct = score_int * 10
    if   score_int >= 8: bar_color = score_hex = "#3ec97a"
    elif score_int >= 5: bar_color = score_hex = "#f5c842"
    else:                bar_color = score_hex = "#ff5a5a"

    st.markdown(f"""
    <span class="section-heading" style="margin-top:2rem;display:block;">Health Assessment</span>
    <div class="health-bar-wrap">
      <div>
        <div class="health-score-num" style="color:{score_hex};">{score}</div>
        <div style="font-size:0.63rem;color:rgba(255,255,255,0.22);text-align:center;margin-top:3px;">/10</div>
      </div>
      <div style="flex:1;">
        <div class="health-bar-track">
          <div class="health-bar-fill" style="width:{bar_pct}%;background:{bar_color};"></div>
        </div>
        <div class="health-notes">{data.get("health_notes","")}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    ings_html      = "".join([f"<li>{i}</li>" for i in data.get("ingredients", [])])
    tags_html      = "".join([f'<span class="tag-chip">{t}</span>' for t in data.get("diet_tags", [])])
    allergens      = data.get("allergens", [])
    allergens_html = "".join([f'<span class="allergen-chip">⚠ {a}</span>' for a in allergens])

    st.markdown(f"""
    <span class="section-heading" style="margin-top:2rem;display:block;">Details</span>
    <div class="detail-grid">
      <div class="detail-block">
        <span class="section-heading">Ingredients</span>
        <ul>{ings_html}</ul>
      </div>
      <div class="detail-block">
        <span class="section-heading">Diet Tags</span>
        <div style="margin-top:0.6rem;">{tags_html if tags_html else '<span style="color:rgba(255,255,255,0.18)">—</span>'}</div>
        {"<span class='section-heading' style='margin-top:1.25rem;display:block;'>Allergens</span><div>"+allergens_html+"</div>" if allergens else ""}
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("{ } Raw JSON"):
        st.json(data)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="logo-group">
    <span class="logo-word">Nutri<em>Lens</em></span>
    <span class="logo-tag">AI · Free</span>
  </div>
  <div class="header-status">
    <div class="status-dot"></div>
    <span>Models online</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([5, 8], gap="small")

# ═══════════════ LEFT COLUMN ═══════════════
with col_left:
    st.markdown('<span class="panel-label">Upload Image</span>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "food_img", type=["jpg","jpeg","png","webp"],
        label_visibility="collapsed",
        key="uploader" if not st.session_state.clear_flag else "uploader_cleared"
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        max_dim = 1024
        if max(image.size) > max_dim:
            ratio = max_dim / max(image.size)
            image = image.resize(
                (int(image.width*ratio), int(image.height*ratio)), Image.LANCZOS
            )
        st.image(image, use_container_width=True)

    st.markdown('<span class="panel-label">Vision Model</span>', unsafe_allow_html=True)

    model_label = st.selectbox(
        "model", list(FREE_VISION_MODELS.keys()),
        index=0, label_visibility="collapsed"
    )
    model_id = FREE_VISION_MODELS[model_label].strip()

    st.markdown(f"""
    <div class="model-card">
      <div class="model-name">{model_label}</div>
      <div class="model-id">{model_id}</div>
      <span class="model-badge">✓ Free · Vision</span>
    </div>
    """, unsafe_allow_html=True)

    if uploaded:
        analyze_btn = st.button("🔬 Analyze with AI", key="btn_analyze")
        clear_btn   = st.button("✕ Clear Results",    key="btn_clear")
    else:
        st.markdown("""
        <div style="color:rgba(255,255,255,0.18);font-size:0.82rem;text-align:center;
                    padding:2rem 0;letter-spacing:0.02em;">
            Upload a photo to begin
        </div>
        """, unsafe_allow_html=True)
        analyze_btn = False
        clear_btn   = False

    if clear_btn:
        st.session_state.result     = None
        st.session_state.used_model = None
        st.session_state.clear_flag = not st.session_state.clear_flag
        st.rerun()

# ═══════════════ RIGHT COLUMN ═══════════════
with col_right:

    if not uploaded:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:72vh;text-align:center;gap:1.25rem;">
          <div style="font-size:4rem;opacity:0.1">🔬</div>
          <div class="empty-state-title">Ready to analyze</div>
          <div class="empty-state-sub">
            Upload a food photo on the left to get instant AI-powered
            nutrition analysis, ingredients &amp; health scoring
          </div>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.result is not None and not analyze_btn:
        render_results(st.session_state.result, st.session_state.used_model, model_id)

    elif not analyze_btn:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:62vh;text-align:center;gap:1rem;">
          <div style="font-size:3rem;opacity:0.2">⬅</div>
          <div style="font-size:0.9rem;color:rgba(255,255,255,0.28);line-height:1.5;">
            Click <b style="color:#ff7a38">Analyze with AI</b> to start
          </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        if OPENROUTER_API_KEY == "YOUR_API_KEY_HERE":
            st.error("⚠️ No API key configured.")
        else:
            log_area = st.empty()
            with st.spinner(""):
                try:
                    img_b64 = image_to_base64(image)
                    data, used_model = analyze_agentic(model_id, img_b64, log_area)
                    st.session_state.result     = data
                    st.session_state.used_model = used_model
                    log_area.empty()
                    render_results(data, used_model, model_id)
                except RuntimeError as ex:
                    log_area.empty()
                    st.error(f"❌ {ex}")
                    st.markdown("""
                    <div style="font-size:0.82rem;color:rgba(255,255,255,0.35);margin-top:0.75rem;">
                      Try again in a few minutes — free models have rate limits per day.
                    </div>""", unsafe_allow_html=True)
                except Exception as ex:
                    log_area.empty()
                    st.error(f"❌ Unexpected error: {ex}")
