# 🌶️ The Secret Life of Spices — *Grown There, Eaten Here*

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://spice-vizcon.streamlit.app)
[![CI](https://github.com/balaji4aws/spice-vizcon/actions/workflows/ci.yml/badge.svg)](https://github.com/balaji4aws/spice-vizcon/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

### ▶️ **[Open the live app → spice-vizcon.streamlit.app](https://spice-vizcon.streamlit.app)**

*No install, no signup — it runs in your browser.*

<!-- Optional: drop a screenshot or GIF of the app here once you have one, e.g.
     ![App screenshot](docs/screenshot.png) -->

---

## What is this?

An interactive web app that tells one story with data: **the countries that eat the most spice
are almost never the countries that grow it.**

It's built on 30 years of United Nations food data — 9 spices, 198 countries, 1995 to 2023, about
45,000 rows. The app walks you through three findings, one chapter at a time, with charts and
world maps you can click around in.

> **The hook:** you have never grown a single spice you eat — and neither has almost any country
> on Earth. Your spice rack is a map of somewhere else.

---

## The three findings

| # | Finding | The headline number |
|---|---|---|
| 1 | **The Great Spice Boom** — the world is eating far more spice than it used to. | World dried-spice production grew **4.6× in 30 years**. Ginger alone is up **552%**. |
| 2 | **Grown There, Eaten Here** — the big eaters barely grow any of it. | The USA grows just **0.2%** of the spice it eats. Germany, Saudi Arabia and the UK are near **0%**. |
| 3 | **Up in Smoke** — some spices belong to a single country. | Indonesia grows **73%** of the world's cloves and keeps almost all of them — because most go into clove *cigarettes*, not food. |

Plus an interactive **"Trace your spice"** map: pick any spice and watch two world maps appear
side by side — where it's grown, and where it's eaten. They rarely look the same.

---

## First, some plain English

The data uses a few terms that are worth knowing before you dive in. None of them are complicated.

| Term | What it actually means |
|---|---|
| **FAOSTAT** | The UN's Food and Agriculture Organization database. Countries report their farm production and trade to it every year. It's the standard public source for this kind of question. |
| **Apparent consumption** | How much of a spice *stayed inside* a country, worked out as **what it grew + what it imported − what it exported**. Nobody surveys the world's kitchens, so this is the standard stand-in for "how much a country eats". |
| **Self-sufficiency** | Of everything a country eats, the share it grew itself. The USA at 0.2% means it grows about 1 kg for every 500 kg it consumes. |
| **Choropleth** | A map where each country is shaded by a value — darker means more. Two of them side by side is how Finding 2 works. |
| **Tonnes** | Metric tonnes: 1,000 kg. All quantities in this project are in tonnes. |

**One honest caveat, up front:** apparent consumption measures what's *available* in a country,
not what people literally put on their plates. Food that gets industrially processed, stockpiled,
or shipped back out is still counted. That's exactly why Finding 3 works — Indonesia's cloves
show up as "eaten" when they're really being smoked.

---

## What this project demonstrates

If you're reviewing this as work sample, here's what's in it:

- **Data cleaning on messy real-world data** — a duplicated `China` total that would have
  double-counted, a column header with a stray trailing space, 2,448 rows with negative values,
  and one crop so much larger than the rest that it flattened every chart it appeared in.
- **Joining datasets that don't agree on names** — FAOSTAT says *"Türkiye"* and
  *"Viet Nam"*; the population data says *"Turkey"* and *"Vietnam"*. A name-matching layer
  reconciles 195 of 198 countries; the 3 that fail are countries that no longer exist.
- **A reproducible pipeline** — one script (`build_data.py`) computes every number in the story
  and writes it to a file. The app only ever *reads* that file, so no statistic is ever typed by
  hand into the narrative.
- **Automated tests and CI** — a test opens every chapter of the app and fails if any of them
  crashes. GitHub Actions runs it, plus a linter, on every push.
- **Accessibility as a requirement, not an afterthought** — see [Design choices](#design-choices).
- **Documented judgement calls** — [`docs/`](docs/) records where the analysis relies on
  interpretation, where it could be wrong, and which claims come from outside the data.

---

## How it's built

Three pieces, in order:

```
data/raw/  →  build_data.py  →  data/processed/  →  app.py
(the UN         (cleans and       (small, tidy        (the Streamlit
 CSVs, as        calculates)       result files)       web app)
 downloaded)
```

1. **`data/raw/`** holds the source CSVs exactly as downloaded. Never edited.
2. **`build_data.py`** cleans them, works out apparent consumption, and calculates every figure
   in the story. It saves small summary files plus one `key_figures.json` holding every headline
   number.
3. **`app.py`** is the web app. It reads those files and draws the charts. It never does its own
   maths.

**Why split it that way?** If the app calculated its own numbers, the text and the charts could
quietly disagree with each other. Keeping one script as the only place numbers are produced means
the story and the data can't drift apart. The CI check enforces it: if the processed files don't
match what `build_data.py` produces, the build fails.

---

## Run it on your own machine

You'll need Python 3.10 or newer.

```bash
git clone https://github.com/balaji4aws/spice-vizcon.git
cd spice-vizcon
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens at `http://localhost:8501`. That's it — the processed data is already in the
repo, so there's no build step.

Want to regenerate the data from the raw CSVs yourself? `python3 build_data.py`. It takes about a
second and should leave the files unchanged, which is the point.

---

## Quality checks

```bash
python3 test_app.py    # opens all 6 chapters, fails if any of them errors
ruff check .           # code style (pip install ruff first)
```

`test_app.py` uses Streamlit's own testing tools to load each chapter without a browser and check
that nothing crashes. It exits with an error code on failure, so CI can catch it.

[GitHub Actions](.github/workflows/ci.yml) runs both of these on every push, and also re-runs
`build_data.py` to confirm the committed data still matches what the code produces.

---

## Project structure

```
spice-vizcon/
├── app.py                      # the web app — 6 chapters of charts and maps
├── build_data.py               # the pipeline: raw CSVs → processed data + key_figures.json
├── test_app.py                 # loads every chapter and checks none of them crash
├── requirements.txt            # streamlit, pandas, plotly
├── pyproject.toml              # code style rules
├── .github/workflows/ci.yml    # runs tests, style checks, and the data check on every push
├── .streamlit/config.toml      # the warm colour theme, defined in one place
├── data/
│   ├── raw/                    # the UN CSVs, exactly as downloaded — never edited
│   └── processed/              # cleaned results + key_figures.json — what the app reads
└── docs/
    ├── SOURCES.md                             # where every number comes from
    ├── ASSUMPTIONS_AND_HALLUCINATION_LOG.md   # every judgement call, and where it could be wrong
    └── GENAI_WORKFLOW.md                      # how AI helped, and what stayed human-owned
```

---

## Where the data comes from

- **Main dataset:** [Global Spice Consumption](https://www.kaggle.com/datasets/harishthakur995/global-spice-consumption)
  on Kaggle — a table built from FAOSTAT covering production, trade and consumption per country,
  1995–2023.
- **Original source:** [FAOSTAT](https://www.fao.org/faostat/en/), the UN's Food and Agriculture
  Organization — [production](https://www.fao.org/faostat/en/#data/QCL) and
  [trade](https://www.fao.org/faostat/en/#data/TCL) data.
- **Population figures:** a [world population dataset](https://www.kaggle.com/datasets/iamsouravbanerjee/world-population-dataset)
  (originally UN World Population Prospects), used only for rough per-person context — never for
  a headline claim.

Two things worth calling out. First, the Kaggle table is what was actually used; FAOSTAT is where
it originally came from, and the README names both rather than claiming a direct UN download.
Second, the clove-cigarette explanation in Finding 3 is **not** in the data — the dataset only
proves that Indonesia keeps its own cloves. The *reason* comes from outside sources (World Bank,
Cornell), is labelled as such inside the app, and is cited in [`docs/SOURCES.md`](docs/SOURCES.md).

Full provenance and every judgement call: [`docs/SOURCES.md`](docs/SOURCES.md) and
[`docs/ASSUMPTIONS_AND_HALLUCINATION_LOG.md`](docs/ASSUMPTIONS_AND_HALLUCINATION_LOG.md).

---

## Design choices

- **Colour is never the only signal.** Every chart also labels its values directly, and every
  chart has a written caption describing what it shows — which doubles as alt text for screen
  readers.
- **One palette, defined once.** The warm parchment-and-brown theme lives in
  `.streamlit/config.toml` and is reused in `app.py`, so every chart matches.
- **Map colours chosen for colour blindness.** The scales run light-to-dark in a single hue, so
  the ordering survives most forms of colour vision deficiency.
- **Green chillies are excluded from comparisons.** Fresh green chillies behave like a vegetable
  crop, not a spice: at 34 million tonnes a year they outweigh all eight dried spices *combined*
  by more than 2×, and outweigh vanilla by around 5,000×. Leaving them in would squash every
  other spice into a flat line. They're discussed separately instead of mixed in.

---

## Built with

[Python](https://www.python.org/) · [Streamlit](https://streamlit.io/) (the web app) ·
[Plotly](https://plotly.com/python/) (charts and maps) · [pandas](https://pandas.pydata.org/)
(data handling)

AI/LLM tools assisted with data profiling, code, and drafting. The analysis, the editorial
decisions, and the validation of every figure against the source data were author-led — see
[`docs/GENAI_WORKFLOW.md`](docs/GENAI_WORKFLOW.md) for the honest breakdown.

## Deploy your own copy

1. Fork this repo to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, click **New app**.
3. Choose the repo, branch `main`, main file `app.py`, then **Deploy**.

Because the processed data is committed, there's no build step — it just runs.

## Author

Built by **Balaji Venkatesh**.

## License

No licence file yet, which by default means all rights reserved. If you'd like to reuse any of
this, please get in touch.
