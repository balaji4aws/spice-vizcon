# Data Sources & Citations

## Primary dataset — FAOSTAT (Food and Agriculture Organization of the United Nations)
- **What:** Production and trade (import/export) quantities, in tonnes, by country and year, for
  9 spice items; apparent domestic consumption derived as Production + Import − Export.
- **Coverage:** ~200 countries/territories, 1993–2023 (this story uses 1995–2023).
- **Public portals:**
  - Crops & livestock production: https://www.fao.org/faostat/en/#data/QCL
  - Crops & livestock trade: https://www.fao.org/faostat/en/#data/TCL
- **TO CONFIRM before final submit:** paste the exact FAOSTAT query/download URL (or the Kaggle
  mirror) your team originally used, so the citation is the precise source.

## Reference layer — World Population dataset (Kaggle)
- **What:** Population by country for snapshot years 1970–2022, plus area, density, growth rate,
  continent, ISO CCA3 code.
- **Use in this project:** context/density only (per-capita is shown as a caveated proxy — see
  the assumptions log). 2022 population is used as a proxy for 2023.
- **Source as used:** Kaggle "World Population Dataset."
  https://www.kaggle.com/datasets/iamsouravbanerjee/world-population-dataset
- **Upstream origin:** UN World Population Prospects / World Population Review.
- **Honest note:** we used the Kaggle file the team supplied; we did **not** separately download a
  distinct "official UN" file and do not claim to.

## External context (NOT from the datasets) — cited where used
- **Finding 3 ("Up in Smoke"), cloves → *kretek* clove cigarettes.** The datasets contain no
  end-use information. The explanation that the bulk of Indonesia's cloves go into kretek cigarettes
  is external knowledge, labelled "Outside the data" in the app. Public supporting sources:
  - World Bank, *The Economics of Clove Farming in Indonesia* — the Indonesian tobacco (kretek)
    industry buys the bulk of the country's clove crop.
    http://documents1.worldbank.org/curated/en/166181507538499946/pdf/120318-REVISED-WP-WBGIndoCloveFarmingweb.pdf
  - Cornell University news (2024), "Why kretek — 'no ordinary cigarette' — thrives in Indonesia":
    kretek clove cigarettes dominate the Indonesian cigarette market.
    https://news.cornell.edu/stories/2024/04/why-kretek-no-ordinary-cigarette-thrives-indonesia
  - Campaign for Tobacco-Free Kids — kretek composition (tobacco + cut clove buds).
    https://assets.tobaccofreekids.org/global/pdfs/en/IW_facts_products_Kreteks.pdf
  - *Sources summarised/paraphrased for licensing compliance.*

---
*All numeric claims in the visualization are computed by `build_data.py` into
`data/processed/key_figures.json`. See `ASSUMPTIONS_AND_HALLUCINATION_LOG.md` for every point where
we relied on interpretation or outside knowledge.*
