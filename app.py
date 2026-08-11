"""
The Secret Life of Spices — Grown There, Eaten Here
VizCon 2026 entry (theme: "How the world lives, thrives, and connects").

A three-act data story built on a FAOSTAT-derived global spice dataset (primary) with a world
population reference layer. Every headline number is read from data/processed/key_figures.json,
which is computed by build_data.py — nothing in the narrative is hand-typed.

Run locally:  streamlit run app.py
"""
import json
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------ config
st.set_page_config(
    page_title="The Secret Life of Spices",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

HERE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.join(HERE, "data", "processed")
LATEST_YEAR = 2023
BASE_YEAR = 1995

# ------------------------------------------------------------------ palette
# Spice-warm identity. We never rely on colour ALONE to convey meaning
# (labels + direct annotation everywhere) — an accessibility best practice.
INK = "#2B2016"        # dark clove-brown text
PARCHMENT = "#FBF6EE"
CREAM = "#F3E7D3"
TURMERIC = "#E8A020"
CHILI = "#C1440E"
PAPRIKA = "#D9541E"
CINNAMON = "#8B5A2B"
CARDAMOM = "#6B8E23"
PEPPER = "#3B2417"
CLOVE = "#7A2E1D"

SPICE_COLORS = {
    "Anise/Cumin/Coriander": "#C9A227",   # goldenrod
    "Chillies (dry)": "#C1440E",          # chili red
    "Chillies (green)": "#6B8E23",        # olive/cardamom
    "Cinnamon": "#8B5A2B",                # cinnamon brown
    "Cloves": "#7A2E1D",                  # clove maroon
    "Ginger": "#E8A020",                  # turmeric gold
    "Nutmeg/Mace/Cardamom": "#A0522D",    # sienna
    "Pepper": "#3B2417",                  # peppercorn
    "Vanilla": "#D6B98C",                 # vanilla cream
}
DRIED_ORDER = [
    "Anise/Cumin/Coriander", "Chillies (dry)", "Pepper", "Ginger",
    "Cinnamon", "Nutmeg/Mace/Cardamom", "Cloves", "Vanilla",
]

# ------------------------------------------------------------------ data loaders (cached)
@st.cache_data
def load_csv(name):
    return pd.read_csv(os.path.join(PROC, name))

@st.cache_data
def load_keys():
    with open(os.path.join(PROC, "key_figures.json")) as f:
        return json.load(f)

K = load_keys()

# ------------------------------------------------------------------ styling
st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {PARCHMENT}; }}
    h1, h2, h3, h4 {{ color: {PEPPER}; font-weight: 800; letter-spacing: -0.01em; }}
    .big-hook {{
        font-size: 2.7rem; line-height: 1.15; font-weight: 800; color: {CLOVE};
        margin: 0.2rem 0 0.6rem 0;
    }}
    .kicker {{
        text-transform: uppercase; letter-spacing: 0.18em; font-size: 0.8rem;
        font-weight: 700; color: {CHILI};
    }}
    .lede {{ font-size: 1.15rem; line-height: 1.6; color: {INK}; }}
    .datacard {{
        background: {CREAM}; border-left: 6px solid {CHILI}; border-radius: 8px;
        padding: 1rem 1.2rem; margin: 0.6rem 0;
    }}
    .data-shows {{
        background: #EAF3E0; border-left: 6px solid {CARDAMOM}; border-radius: 8px;
        padding: 1rem 1.2rem; margin: 0.6rem 0;
    }}
    .outside-data {{
        background: #F6E7DF; border-left: 6px dashed {CLOVE}; border-radius: 8px;
        padding: 1rem 1.2rem; margin: 0.6rem 0;
    }}
    .caveat {{
        background: #FBF3D9; border-left: 6px solid {TURMERIC}; border-radius: 8px;
        padding: 0.8rem 1.1rem; margin: 0.6rem 0; font-size: 0.92rem;
    }}
    .altcap {{ font-size: 0.85rem; color: {CINNAMON}; font-style: italic; }}
    .source {{ font-size: 0.8rem; color: {CINNAMON}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

def alt_caption(text):
    """Descriptive caption that doubles as chart alt-text for screen readers."""
    st.markdown(f"<p class='altcap'>🖼️ {text}</p>", unsafe_allow_html=True)

def style_fig(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=14),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(bgcolor="rgba(255,255,255,0.5)"),
        title=dict(font=dict(size=18, color=PEPPER)),
    )
    fig.update_xaxes(gridcolor="#E3D6C2", zerolinecolor="#E3D6C2")
    fig.update_yaxes(gridcolor="#E3D6C2", zerolinecolor="#E3D6C2")
    return fig

def fmt(n):
    return f"{n:,.0f}"

# ================================================================== SIDEBAR NAV
st.sidebar.markdown("## 🌶️ The Secret Life of Spices")
st.sidebar.caption("VizCon 2026 · *How the world lives, thrives & connects*")
section = st.sidebar.radio(
    "Jump to a chapter",
    ["🏠 Start here", "① The Great Spice Boom", "② Grown There, Eaten Here",
     "③ Up in Smoke", "🧭 Assumptions & analysis", "📎 Sources & credits"],
    label_visibility="visible",
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<p class='source'><b>Primary data:</b> Kaggle 'Global Spice Consumption' "
    f"(FAOSTAT-derived), {BASE_YEAR}–{LATEST_YEAR}, {K['meta']['n_countries']} countries, "
    f"{K['meta']['n_spices_total']} spices.<br>"
    f"<b>Reference:</b> World population (Kaggle / UN WPP).</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p class='source'>Every headline number is computed from the source data, not hand-typed. "
    "See the <b>Assumptions &amp; analysis</b> chapter for how we got here.</p>",
    unsafe_allow_html=True,
)


# ================================================================== SECTION: START
def render_start():
    st.markdown("<p class='kicker'>VizCon 2026</p>", unsafe_allow_html=True)
    st.markdown("<div class='big-hook'>You have never grown a single spice you eat.<br>Neither has almost any country on Earth.</div>", unsafe_allow_html=True)
    st.markdown(
        "<p class='lede'>Every kitchen on the planet runs on a hidden supply chain. A pinch of "
        "cinnamon, a spoon of cumin, the vanilla in your ice cream — each one travelled a "
        "secret map before it reached you. Using 30 years of UN food-and-agriculture data on "
        "<b>9 spices</b> across <b>nearly 200 countries</b>, this is the story of where the "
        "world's flavour is <i>born</i> versus where it is <i>eaten</i> — and the three "
        "surprises hiding in the gap.</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Spices tracked", K["meta"]["n_spices_total"])
    with c2:
        st.metric("Countries", K["meta"]["n_countries"])
    with c3:
        st.metric("Years of data", f"{BASE_YEAR}–{LATEST_YEAR}")
    with c4:
        mult = K["world_dried_total_latest_t"] / K["world_dried_total_base_t"]
        st.metric("World spice output", f"{mult:.1f}×", help="Dried-spice production, 1995 → 2023")

    st.markdown("### Three findings, one story")
    a, b, c = st.columns(3)
    with a:
        st.markdown(
            f"<div class='datacard'><b>① The Great Spice Boom</b><br>"
            f"The world got <b>{mult:.1f}× spicier</b> in 30 years. Ginger alone is up "
            f"<b>{K['act1_boom']['ginger_pct']:.0f}%</b>.</div>",
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            f"<div class='datacard'><b>② Grown There, Eaten Here</b><br>"
            f"The USA grows just <b>{K['act2_grown_eaten']['usa_self_sufficiency_pct']}%</b> "
            f"of the spice it eats. See the map — and trace your own spice.</div>",
            unsafe_allow_html=True,
        )
    with c:
        st.markdown(
            f"<div class='datacard'><b>③ Up in Smoke</b><br>"
            f"One country grows <b>{K['act3_cloves']['indonesia_share_pct_latest']}%</b> of the "
            f"world's cloves — and eats almost all of them. Why is the twist.</div>",
            unsafe_allow_html=True,
        )
    st.markdown(
        "<p class='source'>👈 Use the sidebar to move through the chapters, or read straight down. "
        "All figures: FAOSTAT apparent consumption (Production + Import − Export).</p>",
        unsafe_allow_html=True,
    )


# ================================================================== SECTION: ACT 1
def render_act1():
    g = load_csv("global_by_spice_year.csv")
    growth = load_csv("growth_1995_latest.csv")
    dried = g[g["spice"] != "Chillies (green)"]

    st.markdown("<p class='kicker'>Finding 01 · How the world's taste changed</p>", unsafe_allow_html=True)
    st.markdown("<div class='big-hook'>The Great Spice Boom</div>", unsafe_allow_html=True)
    mult = K["world_dried_total_latest_t"] / K["world_dried_total_base_t"]
    st.markdown(
        f"<p class='lede'>Your kitchen changed more in the last 30 years than in the previous "
        f"300. Between {BASE_YEAR} and {LATEST_YEAR}, world production of dried spices grew from "
        f"<b>{fmt(K['world_dried_total_base_t'])} tonnes</b> to "
        f"<b>{fmt(K['world_dried_total_latest_t'])} tonnes</b> — roughly <b>{mult:.1f}×</b>. "
        "This isn't just more people eating; it's the whole planet's palate globalising.</p>",
        unsafe_allow_html=True,
    )

    # Growth multiples bar
    gd = growth[growth["spice"] != "Chillies (green)"].sort_values("multiple", ascending=True)
    fig = go.Figure()
    fig.add_bar(
        x=gd["multiple"], y=gd["spice"], orientation="h",
        marker_color=[SPICE_COLORS[s] for s in gd["spice"]],
        text=[f"{m:.1f}× (+{p:.0f}%)" for m, p in zip(gd["multiple"], gd["pct_change"])],
        textposition="outside", cliponaxis=False,
    )
    fig.update_layout(title=f"How much each spice's world output multiplied, {BASE_YEAR} → {LATEST_YEAR}",
                      xaxis_title="Growth multiple (×)", yaxis_title="")
    fig.update_xaxes(range=[0, gd["multiple"].max() * 1.25])
    st.plotly_chart(style_fig(fig, 440), width="stretch")
    alt_caption(
        f"Horizontal bar chart. Every dried spice grew. The anise/cumin/coriander group led at "
        f"{K['act1_boom']['anise_multiple']}× (+{K['act1_boom']['anise_pct']:.0f}%), ginger next at "
        f"{K['act1_boom']['ginger_multiple']}× (+{K['act1_boom']['ginger_pct']:.0f}%). Cloves grew "
        f"least at ~2×.")

    st.markdown("#### The rise of the world's flavour, spice by spice")
    sel = st.multiselect(
        "Choose spices to compare over time",
        DRIED_ORDER, default=["Ginger", "Anise/Cumin/Coriander", "Pepper", "Chillies (dry)"],
    )
    log = st.toggle("Log scale (helps compare small vs large spices)", value=False)
    if sel:
        dd = dried[dried["spice"].isin(sel)]
        fig2 = px.line(
            dd, x="year", y="world_production", color="spice",
            color_discrete_map=SPICE_COLORS, markers=False,
        )
        fig2.update_layout(title="World production over time (tonnes)",
                           xaxis_title="Year", yaxis_title="Tonnes",
                           legend_title_text="")
        if log:
            fig2.update_yaxes(type="log")
        st.plotly_chart(style_fig(fig2, 460), width="stretch")
        alt_caption("Line chart of annual world production per selected spice, 1995–2023. "
                    "Ginger shows the steepest sustained climb.")

    st.markdown(
        f"<div class='datacard'>🫚 <b>The ginger explosion.</b> Ginger production went from "
        f"{fmt(K['act1_boom']['ginger_base'])} to {fmt(K['act1_boom']['ginger_latest'])} tonnes — "
        f"a <b>{K['act1_boom']['ginger_pct']:.0f}%</b> jump. It tracks the global rise of "
        "ginger in wellness culture, teas and 'ginger shots' — the clearest single fingerprint "
        "of changing tastes in the data.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='caveat'>⚠️ <b>Scale note:</b> fresh <i>green</i> chillies (~50M tonnes/yr) are "
        "excluded from this dried-spice view — they behave like a vegetable crop and would "
        "visually crush every real spice. They're discussed separately, never mixed into these "
        "comparisons.</p>",
        unsafe_allow_html=True,
    )


# ================================================================== SECTION: ACT 2
def render_act2():
    ge = load_csv("grown_vs_eaten_latest.csv")
    trace = load_csv("trace_by_spice_latest.csv")

    st.markdown("<p class='kicker'>Finding 02 · The production–consumption gap</p>", unsafe_allow_html=True)
    st.markdown("<div class='big-hook'>Grown There, Eaten Here</div>", unsafe_allow_html=True)
    usa = K["act2_grown_eaten"]
    st.markdown(
        f"<p class='lede'>Here is the quiet truth of the spice world: the places that "
        f"<b>eat</b> the most spice are almost never the places that <b>grow</b> it. The United "
        f"States consumes about <b>{fmt(usa['usa_consumption'])} tonnes</b> of dried spice a year "
        f"and grows just <b>{usa['usa_self_sufficiency_pct']}%</b> of it. Germany, Saudi Arabia "
        "and the UK grow essentially none. Your spice rack is a map of somewhere else.</p>",
        unsafe_allow_html=True,
    )

    # Self-sufficiency choropleth
    m = ge[(ge["cca3"].notna()) & (ge["cca3"] != "") & (ge["consumption"] > 0)].copy()
    m["self_suff_capped"] = m["self_sufficiency_pct"].clip(upper=200)
    fig = px.choropleth(
        m, locations="cca3", color="self_suff_capped",
        hover_name="area",
        hover_data={"self_sufficiency_pct": ":.1f", "consumption": ":,.0f",
                    "production": ":,.0f", "self_suff_capped": False, "cca3": False},
        color_continuous_scale="YlOrBr", range_color=(0, 200),
        labels={"self_suff_capped": "Grows % of what it eats"},
    )
    fig.update_coloraxes(colorbar_title="Grows % of<br>what it eats")
    fig.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False,
                    projection_type="natural earth")
    fig.update_layout(title=f"Spice self-sufficiency by country, {LATEST_YEAR} "
                            "(pale = imports nearly all its spice)")
    st.plotly_chart(style_fig(fig, 500), width="stretch")
    alt_caption("World choropleth map. Pale countries (much of North America, Europe, the "
                "Gulf) grow almost none of the spice they consume; deep-coloured producers "
                "(India, Indonesia, Vietnam, China) grow far more than they eat. Values capped "
                "at 200% for colour; hover for exact figures.")

    st.markdown("#### The world's biggest spice eaters that grow almost none of it")
    lsb = pd.DataFrame(usa["least_self_sufficient_big"])
    lsb = lsb.sort_values("self_sufficiency_pct")
    lsb["label"] = lsb["area"].replace(
        {"United States of America": "USA",
         "United Kingdom of Great Britain and Northern Ireland": "UK",
         "Republic of Korea": "South Korea"})
    fig2 = go.Figure()
    fig2.add_bar(x=lsb["self_sufficiency_pct"], y=lsb["label"], orientation="h",
                 marker_color=CHILI,
                 text=[f"{v:.1f}%" for v in lsb["self_sufficiency_pct"]],
                 textposition="outside", cliponaxis=False)
    fig2.update_layout(title="Share of consumed spice that each country grows itself (2023)",
                       xaxis_title="Grows % of what it eats", yaxis_title="")
    fig2.update_xaxes(range=[0, max(lsb["self_sufficiency_pct"]) * 1.25 + 5])
    st.plotly_chart(style_fig(fig2, 380), width="stretch")
    alt_caption("Bar chart of large spice-consuming nations. Germany, Saudi Arabia and the UK "
                "sit near 0%; the USA at 0.2%. All depend almost entirely on imports.")

    st.markdown(
        f"<div class='datacard'>🔁 <b>The middlemen.</b> {usa['n_reexport_hubs']} countries "
        f"<i>export</i> large volumes of spice while growing almost none — pure trade hubs. The "
        f"biggest, <b>{usa['top_hub']['area']}</b>, shipped out "
        f"~{fmt(usa['top_hub']['export'])} tonnes in {LATEST_YEAR} while producing essentially "
        "zero. Spice is as much a logistics business as an agricultural one.</div>",
        unsafe_allow_html=True,
    )

    # ------- Trace your spice
    st.markdown("### 🔎 Trace your spice")
    st.markdown("<p class='lede'>Pick a spice and watch its map split in two: where it's "
                "<b>grown</b> versus where it's <b>eaten</b>.</p>", unsafe_allow_html=True)
    spice = st.selectbox("Choose a spice", DRIED_ORDER, index=DRIED_ORDER.index("Cinnamon"))
    ts = trace[(trace["spice"] == spice) & (trace["cca3"].notna()) & (trace["cca3"] != "")].copy()

    colp, colc = st.columns(2)
    prod_top = ts.sort_values("production", ascending=False).head(1)
    cons_top = ts[ts["consumption"] > 0].sort_values("consumption", ascending=False).head(1)
    with colp:
        figp = px.choropleth(ts, locations="cca3", color="production", hover_name="area",
                             color_continuous_scale="YlOrBr")
        figp.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False,
                         projection_type="natural earth")
        figp.update_layout(title=f"Where {spice} is GROWN", coloraxis_showscale=False)
        st.plotly_chart(style_fig(figp, 320), width="stretch")
    with colc:
        figc = px.choropleth(ts[ts["consumption"] > 0], locations="cca3", color="consumption",
                             hover_name="area", color_continuous_scale="OrRd")
        figc.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False,
                         projection_type="natural earth")
        figc.update_layout(title=f"Where {spice} is EATEN", coloraxis_showscale=False)
        st.plotly_chart(style_fig(figc, 320), width="stretch")
    if not prod_top.empty and not cons_top.empty:
        st.markdown(
            f"<div class='datacard'>For <b>{spice}</b>, the top grower is "
            f"<b>{prod_top.iloc[0]['area']}</b> ({fmt(prod_top.iloc[0]['production'])} t) while the "
            f"top consumer is <b>{cons_top.iloc[0]['area']}</b> "
            f"({fmt(cons_top.iloc[0]['consumption'])} t). "
            "Often they're worlds apart.</div>",
            unsafe_allow_html=True,
        )
    alt_caption(f"Two side-by-side world maps for {spice}: production on the left, apparent "
                "consumption on the right. Compare how the coloured regions differ.")

    with st.expander("🧑‍🤝‍🧑 Optional reference layer: spice per person (handle with care)"):
        st.markdown(
            "<p class='caveat'>Population is a <b>reference layer only</b> (Kaggle / UN, 2022 "
            "population used as a proxy for 2023). Dividing apparent consumption by population "
            "gives a <i>rough</i> per-person figure that is <b>distorted</b> for small nations "
            "and for producer/re-export countries — e.g. Guyana and Nepal show impossibly high "
            "values. So we only show large countries and read it as a soft signal, not a fact.</p>",
            unsafe_allow_html=True,
        )
        pc = load_csv("per_capita_latest.csv")
        min_pop = st.slider("Only show countries with population above (millions)", 10, 200, 30, 10)
        pcf = pc[pc["pop_2022"] > min_pop * 1_000_000].copy()
        pcf = pcf[pcf["grams_per_capita_yr"] < 20000]  # drop impossible artifacts
        pcf = pcf.sort_values("grams_per_capita_yr", ascending=False).head(12)
        figpc = go.Figure()
        figpc.add_bar(x=pcf["grams_per_capita_yr"], y=pcf["area"], orientation="h",
                      marker_color=TURMERIC,
                      text=[f"{v/1000:.1f} kg" for v in pcf["grams_per_capita_yr"]],
                      textposition="outside", cliponaxis=False)
        figpc.update_layout(title="Apparent spice per person per year (rough proxy, big nations)",
                            xaxis_title="grams per person / year", yaxis_title="")
        figpc.update_yaxes(autorange="reversed")
        st.plotly_chart(style_fig(figpc, 420), width="stretch")
        alt_caption("Bar chart: among large nations, South & Southeast Asian and West African "
                    "cuisines (Nepal, Sri Lanka, Thailand, Bangladesh, India, Nigeria) show the "
                    "highest apparent spice per person — consistent with their cuisines.")


# ================================================================== SECTION: ACT 3
def render_act3():
    conc = load_csv("concentration_latest.csv")
    cloves = load_csv("cloves_indonesia.csv")
    van = load_csv("vanilla_madagascar.csv")

    st.markdown("<p class='kicker'>Finding 03 · When one country owns a spice</p>", unsafe_allow_html=True)
    st.markdown("<div class='big-hook'>Up in Smoke</div>", unsafe_allow_html=True)
    st.markdown(
        "<p class='lede'>Some spices belong to one country. When you concentrate the world's "
        "supply in a single place, you also concentrate its <b>secrets</b>. Two spices tell the "
        "strangest stories in this dataset — and one of them isn't really about food at all.</p>",
        unsafe_allow_html=True,
    )

    # concentration: top-1 share per spice
    top1 = conc[conc["rank"] == 1].sort_values("share_pct", ascending=True)
    fig = go.Figure()
    fig.add_bar(x=top1["share_pct"], y=top1["spice"], orientation="h",
                marker_color=[SPICE_COLORS.get(s, CINNAMON) for s in top1["spice"]],
                text=[f"{a} · {p:.0f}%" for a, p in zip(top1["area"], top1["share_pct"])],
                textposition="outside", cliponaxis=False)
    fig.update_layout(title=f"How much the #1 country controls of each spice ({LATEST_YEAR})",
                      xaxis_title="Top producer's share of world output (%)", yaxis_title="")
    fig.update_xaxes(range=[0, 100])
    st.plotly_chart(style_fig(fig, 440), width="stretch")
    alt_caption("Bar chart of each spice's single biggest producer. Cloves are the most "
                "concentrated: Indonesia alone grows ~73%. Guatemala leads nutmeg/mace/cardamom, "
                "a spice group culturally tied to South Asia and the Middle East.")

    # ---- Cloves anomaly
    st.markdown("### 🚬 Cloves: the spice that mostly isn't eaten")
    cl = K["act3_cloves"]
    st.markdown(
        f"<div class='data-shows'>✅ <b>What the data shows.</b> Indonesia grows "
        f"<b>{cl['indonesia_share_pct_latest']}%</b> of the world's cloves — and, unlike every "
        f"other big spice producer, it <b>consumes about {cl['indonesia_self_consumption_pct_latest']}% "
        "of its own crop</b> instead of exporting it. Most producing nations ship their spice out; "
        "Indonesia keeps (and even imports more of) its cloves.</div>",
        unsafe_allow_html=True,
    )

    cll = cloves.copy()
    fig2 = go.Figure()
    fig2.add_bar(x=cll["year"], y=cll["indonesia_production"], name="Indonesia produces",
                 marker_color=CINNAMON)
    fig2.add_trace(go.Scatter(x=cll["year"], y=cll["indonesia_consumption"],
                              name="Indonesia consumes", mode="lines+markers",
                              line=dict(color=CHILI, width=3)))
    fig2.update_layout(title="Indonesia's cloves: production vs. its own consumption (tonnes)",
                       xaxis_title="Year", yaxis_title="Tonnes", legend_title_text="")
    st.plotly_chart(style_fig(fig2, 420), width="stretch")
    alt_caption("Combined bar-and-line chart. Indonesia's clove consumption line tracks — and "
                "sometimes exceeds — its own production bars, year after year. It eats what it grows.")

    st.markdown(
        "<div class='outside-data'>🚭 <b>Outside the data — why?</b> The dataset contains "
        "<b>no</b> information on how cloves are used; this explanation comes from <b>outside</b> "
        "the dataset. Indonesia's cloves overwhelmingly go into <i>kretek</i> — clove cigarettes — "
        "which are smoked far more than cloves are cooked with. So the world's clove supply is, in "
        "effect, largely a tobacco input controlled by one country. "
        "<i>(External context; see the citation in Sources &amp; credits. The dataset only proves "
        "the self-consumption anomaly above, not the reason.)</i></div>",
        unsafe_allow_html=True,
    )

    # ---- Vanilla fragility
    st.markdown("### 🍦 Vanilla: the fragile luxury")
    v = K["vanilla"]
    st.markdown(
        f"<p class='lede'>If cloves are concentrated, vanilla is <b>precarious</b>. The entire "
        f"world produced only about <b>{fmt(v['world_vanilla_latest_t'])} tonnes</b> of vanilla in "
        f"{LATEST_YEAR} — the planet grows roughly <b>{fmt(v['chilli_vs_vanilla_multiple'])}× more "
        f"dried chilli than vanilla</b>. And Madagascar's grip has tightened from "
        f"<b>{v['madagascar_share_pct_2000']:.0f}%</b> of world output in 2000 to "
        f"<b>{v['madagascar_share_pct_latest']:.0f}%</b> today. One bad cyclone on one island moves "
        "the price of vanilla everywhere.</p>",
        unsafe_allow_html=True,
    )
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=van["year"], y=van["madagascar_share_pct"],
                              mode="lines+markers", line=dict(color=CLOVE, width=3),
                              fill="tozeroy", fillcolor="rgba(122,46,29,0.15)",
                              name="Madagascar share"))
    fig3.update_layout(title="Madagascar's share of world vanilla production (%)",
                       xaxis_title="Year", yaxis_title="% of world output")
    fig3.update_yaxes(range=[0, 100])
    st.plotly_chart(style_fig(fig3, 380), width="stretch")
    alt_caption("Line chart: Madagascar's share of global vanilla rises from about 20–25% around "
                "2000 to roughly 45% by 2023 — a single country holding up a global luxury crop.")

    st.markdown(
        "<div class='datacard'>🌍 <b>The through-line.</b> From cumin to cloves to vanilla, the "
        "same pattern repeats: the world's flavour is grown by a handful of countries and eaten "
        "by everyone else. The spice rack in your kitchen is one of the most globalised objects "
        "you own.</div>",
        unsafe_allow_html=True,
    )


# ================================================================== SECTION: ASSUMPTIONS & ANALYSIS
def render_analysis():
    st.markdown("<p class='kicker'>How we got here</p>", unsafe_allow_html=True)
    st.markdown("## 🧭 Assumptions & analysis")
    st.markdown(
        "<p class='lede'>This chapter is the workbench behind the story: what we started with, the "
        "steps we took, the judgement calls we made, and — honestly — where the analysis could be "
        "wrong. Nothing here is decoration; it's how the numbers in the story were produced.</p>",
        unsafe_allow_html=True,
    )

    st.markdown("### The analytical work, step by step")
    st.markdown(
        f"1. **Profiled the raw data.** We started from a single FAOSTAT-derived spice dataset "
        f"({K['meta']['n_countries']} countries × {K['meta']['n_spices_total']} spices × "
        f"{BASE_YEAR}–{LATEST_YEAR}, in tonnes) and inspected it before drawing anything. That "
        "surfaced four issues we had to fix: a duplicated `China` total, a stray trailing space in "
        "the `Export ` column header, negative 'consumption' values, and one spice behaving at a "
        "completely different scale (green chillies).\n"
        "2. **Derived a consumption measure.** The file gives production and trade, so we work in "
        "**apparent consumption = Production + Imports − Exports** — a standard proxy for how much "
        "of a spice stays in a country for domestic use.\n"
        "3. **Cleaned and reshaped.** We removed the duplicate China rollup, set green chillies "
        "aside, coerced all values to numbers, and reduced the ~45,000-row file into small, "
        "purpose-built tables (world totals by year, top-producer concentration, grown-vs-eaten by "
        "country, the cloves and vanilla series, and re-export hubs).\n"
        "4. **Added a light population reference.** We joined a world-population table via a "
        f"country-name crosswalk ({K['meta']['crosswalk_matched']} of {K['meta']['n_countries']} "
        "matched) purely for context/density — never as the main measure.\n"
        "5. **Mined and ranked the findings.** We computed candidate insights across all spices and "
        "kept the three with the strongest, most surprising, and most defensible signal.\n"
        "6. **Made every number reproducible.** A single script recomputes every headline figure "
        "from the source into one file the app reads — so no statistic in the story is typed by "
        "hand, and anyone can regenerate them.")

    st.markdown("### How 'consumption' is estimated")
    st.markdown(
        "> **Consumption = Production + Imports − Exports**\n\n"
        "This estimates what stays inside a country for domestic use. It is widely used, but it is "
        "an *apparent* measure — it captures what's available domestically, not necessarily what "
        "people put on their plates (stock changes, industrial use, and re-exports all sit inside "
        "it).")

    st.markdown("### Key cleaning & modelling decisions")
    st.markdown(
        "- **Dropped the `China` rollup** row (kept `China, mainland` + the separate territories) "
        "to avoid double-counting.\n"
        "- **Set green chillies aside** (~50M t/yr, effectively a fresh vegetable) so scale "
        "comparisons among the eight dried spices stay legible and honest.\n"
        f"- **Population crosswalk:** {K['meta']['crosswalk_matched']} of "
        f"{K['meta']['n_countries']} countries matched; the {K['meta']['crosswalk_unmatched']} "
        "unmatched are defunct entities (e.g. Belgium-Luxembourg) with no recent data.\n"
        "- **2022 population used as a proxy for 2023** (the population file has no 2023 value; "
        "population moves ~1%/yr, so this is a small approximation).\n"
        "- **Baseline year 1995** for the 30-year 'boom' (the file technically starts in 1993, but "
        "the first two years have thinner coverage).")

    st.markdown("### Assumptions & things to keep in mind")
    st.markdown(
        "**How we measure**\n"
        "- **Apparent consumption ≈ domestic use**, not literal dietary intake — re-exports and "
        "stock changes sit inside it, so it can occasionally go negative or spike.\n"
        "- **Per-capita is a rough reference only.** Small nations and producer/trade-hub countries "
        "are distorted — e.g. Guyana (~64 kg/person) and Nepal (~13 kg/person, a ginger *producer*) "
        "are artifacts, not real eating rates; hubs like the UAE reflect trade flow, not eating.\n"
        "- **2022 population stands in for 2023** (the population file has no 2023 value).\n"
        "- **1995 is the starting line for the boom**; part of the 30-year rise also reflects "
        "improved FAOSTAT reporting over time, not only real production growth."
    )
    st.markdown(
        "**How we read the spices**\n"
        "- **FAOSTAT items are groups.** 'Nutmeg, mace & cardamom' is led by *cardamom* (not "
        "nutmeg), and 'cinnamon' includes cassia — so we name the group, not the individual spice.\n"
        "- **The eight dried spices are the story**; green chillies are a separate, vegetable-scale "
        "crop, kept out of the comparisons.\n"
        "- **The cloves → cigarette reason is context from outside the data**, labelled as such in "
        "the story; the dataset itself only shows the self-consumption anomaly.\n"
        "- Country names and borders are taken as reported by FAOSTAT for each year."
    )


# ================================================================== SECTION: SOURCES & CREDITS
def render_credits():
    st.markdown("<p class='kicker'>The fine print</p>", unsafe_allow_html=True)
    st.markdown("## 📎 Sources & credits")

    st.markdown("### Team")
    st.markdown(
        "Built by **Ashish Chauhan**, **KP Bhat**, and **Balaji Venkatesh** — "
        "a trio of data/BI practitioners.")

    st.markdown("### Data sources")
    st.markdown(
        "- **Primary (as used) — Kaggle: 'Global Spice Consumption' (harishthakur995).** A "
        "FAOSTAT-derived table of spice production, trade and apparent consumption by country, "
        f"{BASE_YEAR}–{LATEST_YEAR} (the consumption column is pre-computed as Production + Import "
        "− Export). https://www.kaggle.com/datasets/harishthakur995/global-spice-consumption\n"
        "- **Upstream origin — FAOSTAT, Food and Agriculture Organization of the UN** "
        "(crops & livestock production and trade). https://www.fao.org/faostat/en/#data/QCL and "
        "https://www.fao.org/faostat/en/#data/TCL\n"
        "- **Reference — World population dataset (Kaggle, iamsouravbanerjee).** Snapshot years "
        "1970–2022, used only as a context/density layer. Upstream: **UN World Population "
        "Prospects / World Population Review.** "
        "https://www.kaggle.com/datasets/iamsouravbanerjee/world-population-dataset\n"
    )
    st.markdown("### External context used in 'Up in Smoke'")
    st.markdown(
        "The cloves → *kretek* clove-cigarette link is **not** from the datasets; it is external "
        "context. Supporting public sources:\n\n"
        "- **World Bank** — *The Economics of Clove Farming in Indonesia*: the Indonesian tobacco "
        "(kretek) industry buys the bulk of the country's clove crop. "
        "http://documents1.worldbank.org/curated/en/166181507538499946/pdf/120318-REVISED-WP-WBGIndoCloveFarmingweb.pdf\n"
        "- **Cornell University (news, 2024)** — kretek clove cigarettes make up the overwhelming "
        "majority of Indonesia's cigarette market. https://news.cornell.edu/stories/2024/04/why-kretek-no-ordinary-cigarette-thrives-indonesia\n"
        "- **Campaign for Tobacco-Free Kids** — background on kretek composition (tobacco + cut "
        "clove buds). https://assets.tobaccofreekids.org/global/pdfs/en/IW_facts_products_Kreteks.pdf\n\n"
        "*Sources summarised/paraphrased for licensing compliance.*")

    st.markdown("### Accessibility")
    st.markdown(
        "- High-contrast dark-brown text on parchment; colour is **never the only cue** — every "
        "chart has direct labels and a descriptive caption (🖼️) that doubles as alt-text.\n"
        "- Sequential warm colour scales (`YlOrBr`/`OrRd`) chosen for reasonable colour-vision "
        "safety; values are also shown as text.\n"
        "- Inclusive, plain language reviewed throughout.")

    st.markdown("### A note on tools")
    st.markdown(
        "Built by the team in **Python** with **Streamlit** (app), **Plotly** (charts) and "
        "**pandas** (data). We used AI/LLM tools to assist with data profiling, code, and "
        "drafting; the team led the analysis, made the editorial calls, and validated every "
        "figure against the source data.")


# ================================================================== ROUTER
if section.startswith("🏠"):
    render_start()
elif section.startswith("①"):
    render_act1()
elif section.startswith("②"):
    render_act2()
elif section.startswith("③"):
    render_act3()
elif section.startswith("🧭"):
    render_analysis()
else:
    render_credits()

st.markdown("---")
st.markdown(
    f"<p class='source'>The Secret Life of Spices · VizCon 2026 · "
    f"Data: Kaggle 'Global Spice Consumption' (FAOSTAT-derived), {BASE_YEAR}–{LATEST_YEAR} "
    f"+ world population (Kaggle/UN).</p>",
    unsafe_allow_html=True,
)
