# 🌶️ The Secret Life of Spices — *Grown There, Eaten Here*

A **VizCon 2026** data-visualization contest entry (theme: *"How the world lives, thrives, and connects"*).

A three-act data story about where the world's flavour is **born** versus where it is **eaten**,
built on 30 years of UN food-and-agriculture data covering **9 spices** across **~200 countries**.

> **The hook:** You have never grown a single spice you eat — and neither has almost any country
> on Earth. Your spice rack is a map of somewhere else.

---

## The three findings
1. **The Great Spice Boom** — the world's dried-spice output grew ~**4.6×** in 30 years
   (ginger alone **+552%**). The whole planet's palate is globalising.
2. **Grown There, Eaten Here** — the USA grows **0.2%** of the dried spice it eats; Germany,
   Saudi Arabia and the UK ~0%. An interactive **"Trace your spice"** map splits *grown* vs *eaten*.
3. **Up in Smoke** — Indonesia grows **73%** of the world's cloves and eats almost all of them.
   *(Why? External, clearly-cited context: kretek clove cigarettes.)* Plus vanilla's fragility:
   the world grows ~**841×** more chilli than vanilla, and Madagascar's share climbed 23%→45%.

Plus an **Assumptions & analysis** chapter that documents the full analytical workflow and, honestly,
where the analysis could be wrong.

---

## Run it locally
```bash
cd spice-vizcon
python3 -m pip install -r requirements.txt
python3 build_data.py          # regenerates data/processed/ from data/raw/ (optional; already built)
streamlit run app.py
```
Then open the local URL Streamlit prints (e.g. http://localhost:8501).

## Test it
```bash
python3 test_app.py            # headless AppTest: runs all 5 chapters, asserts no exceptions
```

---

## Publish a public URL (Streamlit Community Cloud) — required for submission
1. A local commit is already prepared. Create an **empty public repo** on GitHub named
   `spice-vizcon`, then add the remote and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/balaji4aws/spice-vizcon.git
   git push -u origin main
   ```
   *(The processed data in `data/processed/` is committed so the app runs on the cloud without a
   build step. Raw data in `data/raw/` is included for transparency.)*
2. Go to **https://share.streamlit.io** → sign in with GitHub → **New app**.
3. Pick the repo, branch `main`, main file `app.py` → **Deploy**.
4. You'll get a public URL like `https://<app-name>.streamlit.app` — **that's your submission link.**

---

## Project structure
```
spice-vizcon/
├── app.py                      # the Streamlit story (5 chapters)
├── build_data.py               # reproducible pipeline: raw → processed + key_figures.json
├── test_app.py                 # headless smoke test (AppTest)
├── requirements.txt
├── .streamlit/config.toml      # spice-warm accessible theme
├── data/
│   ├── raw/                    # faostat_spices.csv, world_population.csv (as received)
│   └── processed/              # cleaned aggregates + key_figures.json (app reads these)
└── docs/
    ├── ASSUMPTIONS_AND_HALLUCINATION_LOG.md   # every non-data claim, logged
    ├── SOURCES.md                             # data sources + citations
    ├── GENAI_WORKFLOW.md                      # how AI was used (Best-Use-of-GenAI doc)
    └── SUBMISSION_BRIEF.md                    # ready-to-paste submission text + checklist
```

---

## Data & honesty
- **Primary (as used):** Kaggle — ["Global Spice Consumption" (harishthakur995)](https://www.kaggle.com/datasets/harishthakur995/global-spice-consumption), a FAOSTAT-derived table (consumption pre-computed as Production + Import − Export), 1995–2023.
- **Upstream origin:** FAOSTAT (FAO of the UN) — crops & livestock production & trade.
- **Reference:** World population (Kaggle / UN World Population Prospects) — context/density only.
- **Consumption = Production + Imports − Exports** (apparent consumption).
- Every headline number is computed by `build_data.py` into `data/processed/key_figures.json` and
  read from there — **nothing in the narrative is hand-typed.**
- The **cloves → cigarettes** link is **external knowledge**, clearly separated from what the data
  shows and cited. See `docs/ASSUMPTIONS_AND_HALLUCINATION_LOG.md`.

**Tools:** Python · Streamlit · Plotly · pandas (with AI/LLM assistance for profiling, code and drafting; team-led analysis and validation).
