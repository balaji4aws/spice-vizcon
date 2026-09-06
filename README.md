# 🌶️ The Secret Life of Spices — *Grown There, Eaten Here*

**An interactive data-visualization story about where the world's flavour is grown versus where
it's eaten**, built on 30 years of UN food-and-agriculture data covering 9 spices across nearly
200 countries.

> **The hook:** you have never grown a single spice you eat — and neither has almost any country
> on Earth. Your spice rack is a map of somewhere else.

Built with Python, Streamlit, and Plotly. Every number in the story is computed from source data
by a reproducible pipeline — nothing in the narrative is hand-typed.

---

## Live demo

Deployed on Streamlit Community Cloud: **`https://<app-name>.streamlit.app`**
*(fill in your deployed URL here once published — see [Deploying](#deploying-your-own-copy) below)*

<!-- Optional: drop a screenshot or GIF of the app here once you have one, e.g.
     ![App screenshot](docs/screenshot.png) -->

---

## The three findings

| # | Finding | The number that sells it |
|---|---|---|
| 1 | **The Great Spice Boom** — the world's palate is globalising. | World dried-spice output grew **~4.6×** in 30 years; ginger alone is up **+552%**. |
| 2 | **Grown There, Eaten Here** — the biggest eaters barely grow any of it. | The USA grows just **0.2%** of the dried spice it consumes; Germany, Saudi Arabia, and the UK sit near **0%**. |
| 3 | **Up in Smoke** — some spices belong to one country. | Indonesia grows **73%** of the world's cloves and eats almost all of them — because most go into *kretek* clove cigarettes, not food. |

The app also includes an interactive **"Trace your spice"** map (pick any spice, watch its
*grown* vs. *eaten* footprint split across the globe) and a full **Assumptions & analysis**
chapter that documents the analytical workflow — including, honestly, where the analysis could
be wrong.

---

## How it works

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────────┐
│   data/raw/       │ ───▶ │  build_data.py    │ ───▶ │   data/processed/     │
│  FAOSTAT spice    │      │  clean, reshape,   │      │  small purpose-built  │
│  + population CSV │      │  compute figures   │      │  CSVs + key_figures   │
└──────────────────┘      └──────────────────┘      │  .json                │
                                                       └──────────┬───────────┘
                                                                  ▼
                                                       ┌──────────────────────┐
                                                       │       app.py          │
                                                       │  Streamlit story,     │
                                                       │  6 chapters, Plotly   │
                                                       │  charts + maps        │
                                                       └──────────────────────┘
```

`build_data.py` is the single source of truth for every statistic in the story: it cleans the raw
FAOSTAT export (fixing a duplicated `China` rollup, a stray header space, and negative
consumption artifacts), derives **apparent consumption = Production + Imports − Exports**, and
writes verified figures to `data/processed/key_figures.json`. `app.py` only ever *reads* those
numbers — it never recomputes or hand-types a statistic, so the pipeline and the narrative can
never drift apart.

---

## Run it locally

Requires Python 3.10+.

```bash
git clone https://github.com/balaji4aws/spice-vizcon.git
cd spice-vizcon
python3 -m pip install -r requirements.txt

python3 build_data.py     # optional — regenerates data/processed/ from data/raw/; already built
streamlit run app.py
```

Then open the local URL Streamlit prints (typically http://localhost:8501).

## Test it

A headless smoke test drives every chapter via Streamlit's `AppTest` framework and asserts no
exceptions are raised:

```bash
python3 test_app.py
```

Expect `ALL PASS` across all 6 chapters (🏠 Start here, ① The Great Spice Boom,
② Grown There Eaten Here, ③ Up in Smoke, 🧭 Assumptions & analysis, 📎 Sources & credits).

## Deploying your own copy

1. Fork or push this repo to your own GitHub account.
2. Go to **https://share.streamlit.io** → sign in with GitHub → **New app**.
3. Pick the repo, branch `main`, main file `app.py` → **Deploy**.
4. Streamlit gives you a public URL like `https://<app-name>.streamlit.app`.

The processed data in `data/processed/` is committed to the repo, so the cloud deploy runs with
no build step. Raw data in `data/raw/` is also committed, for full transparency and
reproducibility.

---

## Project structure

```
spice-vizcon/
├── app.py                      # the Streamlit story — 6 chapters, Plotly charts + choropleth maps
├── build_data.py               # reproducible pipeline: raw data → processed CSVs + key_figures.json
├── test_app.py                 # headless smoke test (Streamlit AppTest) — every chapter, no exceptions
├── requirements.txt            # streamlit, pandas, plotly
├── .streamlit/config.toml      # spice-warm, accessible theme (contrast-checked palette)
├── data/
│   ├── raw/                    # faostat_spices.csv, world_population.csv — as received, untouched
│   └── processed/              # cleaned aggregates + key_figures.json — what app.py actually reads
└── docs/
    ├── SOURCES.md                             # full data provenance + external citations
    ├── ASSUMPTIONS_AND_HALLUCINATION_LOG.md   # every non-data claim in the app, traced and logged
    └── GENAI_WORKFLOW.md                      # how AI assisted the build, and what stayed human-owned
```

---

## Data & honesty

- **Primary (as used):** Kaggle — [Global Spice Consumption (harishthakur995)](https://www.kaggle.com/datasets/harishthakur995/global-spice-consumption), a FAOSTAT-derived table with apparent consumption pre-computed as Production + Import − Export, 1995–2023.
- **Upstream origin:** [FAOSTAT](https://www.fao.org/faostat/en/) (Food and Agriculture Organization of the UN) — crops & livestock [production (QCL)](https://www.fao.org/faostat/en/#data/QCL) and [trade (TCL)](https://www.fao.org/faostat/en/#data/TCL).
- **Reference layer:** world population ([Kaggle](https://www.kaggle.com/datasets/iamsouravbanerjee/world-population-dataset) / UN World Population Prospects) — used only for per-capita/density context, never as a primary measure.
- Every headline number is computed by `build_data.py` into `data/processed/key_figures.json` and
  read from there — **nothing in the narrative is hand-typed.**
- The cloves → cigarettes explanation is clearly labelled **external knowledge**, separated from
  what the dataset itself proves, and cited. Full provenance, every external citation, and a
  complete log of assumptions and judgement calls live in [`docs/SOURCES.md`](docs/SOURCES.md)
  and [`docs/ASSUMPTIONS_AND_HALLUCINATION_LOG.md`](docs/ASSUMPTIONS_AND_HALLUCINATION_LOG.md).

## Design notes

- **Spice-warm, accessible palette** (parchment background, clove-brown text) defined once in
  `.streamlit/config.toml` and reused as a Python constant dict in `app.py`, so every chart shares
  one identity.
- **Colour is never the only cue.** Every chart carries direct data labels, and every chart has a
  descriptive caption that doubles as alt text for screen readers.
- **Sequential, colour-vision-safe scales** (`YlOrBr` / `OrRd`) for the choropleth maps.

## Tech stack

Python · [Streamlit](https://streamlit.io/) (app framework) · [Plotly](https://plotly.com/python/) (charts & choropleth maps) · [pandas](https://pandas.pydata.org/) (data prep, in `build_data.py`'s underlying logic) — with AI/LLM assistance for data profiling, code, and drafting; analysis, editorial calls, and validation of every figure were led by the author. See [`docs/GENAI_WORKFLOW.md`](docs/GENAI_WORKFLOW.md) for the full breakdown.

## Team

Built by **Ashish Chauhan**, **KP Bhat**, and **Balaji Venkatesh**.

## License

No license file is currently included, which under default copyright law means all rights are
reserved by the author. Add an [OSI-approved license](https://choosealicense.com/) here if you'd
like to allow reuse.
