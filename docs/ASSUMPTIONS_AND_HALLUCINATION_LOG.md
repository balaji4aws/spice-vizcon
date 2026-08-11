# Assumptions, Caveats & Hallucination Log

This file exists so that **every claim in the visualization can be traced to either (a) the
dataset, or (b) a cited external source.** Anything that is our own interpretation,
estimate, or external knowledge is written down here. If a reader ever wonders "did the
data actually say that?", the answer is in this file.

Maintained by: the project team, with AI/LLM assistance during the build. Any reliance on
knowledge **outside** the provided datasets, or any assumption, is recorded here.

---

## 1. The cloves → cigarettes link is EXTERNAL knowledge, not in the data (most important)

**What the dataset shows (verifiable in the file):** Indonesia produces the large majority
of the world's cloves and, unusually, *consumes almost all of its own clove crop
domestically* instead of exporting it — the opposite of nearly every other major
spice-producing country. This "self-consumption anomaly" is computed directly from the
FAOSTAT columns (Production, Import, Export, Consumption).

**What the dataset does NOT contain:** There is **no** field about cigarettes, tobacco,
*kretek*, or end-use of any kind. The dataset is purely tonnage.

**The explanation** — that most of Indonesia's cloves are used to make *kretek* clove
cigarettes rather than eaten as food — is **well-documented real-world knowledge from
outside this dataset.** In the app it is clearly labelled "Outside the data" and carries an
external citation. We never imply the FAOSTAT file itself proves the cigarette usage.

Status: **Handled by design** — hard visual/textual separation between "what the data
shows" and "why (external, cited)."

---

## 2. Population data is a REFERENCE layer, and year-alignment is approximate

- The spice dataset is annual, 1993–2023. The population dataset only has **snapshot years**
  (1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022) — it has **no 2023 value.**
- For any 2023 per-capita figure we use **2022 population as a proxy for 2023** and label it
  as such. Population changes ~1%/yr, so this is a minor approximation, not a fabrication.
- Population is used only for context (per-capita consumption, density framing). The spice
  data remains primary.

Status: **Handled** — proxy year is labelled wherever used.

---

## 3. Population data provenance (honest note)

- The population file used is the one supplied by the team, **downloaded from Kaggle**
  ("World Population Dataset"). Its upstream source is the **UN World Population Prospects /
  World Population Review**.
- The AI did **not** independently download a separate "official UN" file. We cite the
  Kaggle dataset as used, and name the UN/World Population Review upstream source in the
  appendix. We do not claim provenance we cannot verify.

Status: **Handled** — cited honestly in the appendix.

---

## 4. "China" double-count removed

- The FAOSTAT file contains both `China` (a rollup) and `China, mainland` + `China, Taiwan
  Province of` + `China, Hong Kong SAR` + `China, Macao SAR`. Summing all of them
  double-counts China.
- **Decision:** we drop the `China` rollup row everywhere and keep the component territories
  (primarily `China, mainland`). This is a standard FAOSTAT handling choice.

Status: **Handled** in data prep.

---

## 5. "Chillies, green" behaves like a vegetable, not a dried spice

- Green chillies (~50M tonnes/yr) dwarf every dried spice by 1–2 orders of magnitude and are
  really a fresh vegetable crop. Leaving them in visually crushes the actual spice story.
- **Decision:** green chillies are separated out / de-emphasized in the main narrative and
  flagged when shown, so scale comparisons among *dried* spices stay legible.

Status: **Handled** — noted wherever green chillies appear.

---

## 6. Negative "consumption" values are a known artifact of the apparent-consumption formula

- Consumption = Production + Import − Export can go **negative** for a country/year when
  recorded exports exceed production + imports (re-exports, stock draw-down, or reporting
  gaps). This is a real limitation of "apparent consumption," not an error we introduced.
- **Decision:** we do not hide these; where they matter we explain them, and for per-capita
  "who eats the most" rankings we guard against negative/implausible values.

Status: **Handled** — explained in methodology.

---

## 6b. Part of the 30-year "boom" may be improved reporting, not only real growth

FAOSTAT country coverage and estimation methods have improved over three decades. Some of the
measured increase in world spice output (1995→2023) may therefore reflect **better accounting**
(more countries/commodities reported, revised estimates) rather than purely real production growth.

**Decision:** the growth is presented as a real and large trend (it is), but this caveat is stated
in the app's "Where this analysis could be wrong" section so we don't over-claim precision.

Status: **Handled** — caveat surfaced in-app.

---

## 6c. FAOSTAT item groupings hide sub-spice detail

Two headline items are **groups**, not single spices:
- **"Nutmeg, mace and cardamoms"** — Guatemala leads this item, but that is really about
  **cardamom** (Guatemala is a top cardamom grower; it grows little nutmeg). We say the *group*,
  not "nutmeg."
- **"Cinnamon and cinnamon-tree flowers"** — mixes true cinnamon and cassia, which is why
  China/Indonesia/Vietnam lead by volume rather than Sri Lanka (true cinnamon).

**Decision:** we always name the group and avoid implying a country dominates a specific sub-spice
it doesn't actually grow.

Status: **Handled** — noted in-app and here.

---

## 7. Equivalences and comparisons are computed from the data, never invented

- Any "X times more / less than Y" statement in the app is calculated from the FAOSTAT
  tonnage itself (e.g. comparing world vanilla output to world chilli output). We do **not**
  use invented real-world equivalences (e.g. "= N billion cigarettes") unless a specific
  external figure is cited.

Status: **Handled** — all comparisons trace to the data prep script.

---

## 7b. Per-capita consumption is a ROUGH proxy with known outlier artifacts

Per-capita = (apparent consumption in tonnes ÷ population). Because apparent consumption
inherits the re-export / reporting artifacts from item #6, some countries show impossible
values and must NOT be presented as fact:
- **Guyana ≈ 64 kg/person/yr** — clearly an artifact (trade recording), not real eating.
- **Nepal ≈ 13 kg/person/yr** — inflated because Nepal is a big *ginger producer*; apparent
  consumption ≠ dietary intake.
- Small nations (pop < ~10M) are the most distorted.

**Decision:** per-capita is shown only as a caveated "explore" layer with a population
filter, never as a hero number. The defensible, believable signal we do surface: among
large nations, spice-heavy cuisines (Nepal, Sri Lanka, Thailand, Bangladesh, Malaysia,
India, Türkiye, Nigeria, Ghana) rank highest — consistent with real culinary reality.
Population is used mainly for context/density, per the team's instruction.

Status: **Handled** — caveat shown in-app; per-capita never used as a standalone claim.

---

## VERIFIED HEADLINE FIGURES (computed from data, latest year = 2023, base = 1995)

All numbers below are produced by `build_data.py` into `data/processed/key_figures.json`.
The app reads them from that file; they are **not** hand-typed into the narrative.

- World dried-spice production: **3.28M t (1995) → 15.02M t (2023)** ≈ **4.6×**.
- Ginger: **+552%** (0.75M → 4.86M t). Anise/cumin/coriander group: **+820%**.
- Top producers (2023 share of world output): India — Anise/Cumin group **69%**, dry
  chillies **48%**, ginger **45%**; Indonesia — cloves **73%**; Madagascar — vanilla **45%**;
  Guatemala — nutmeg/mace/cardamom **43%**; Viet Nam — pepper **30%**.
- USA self-sufficiency: grows **0.2%** of the dried spice it consumes (produces 662 t,
  consumes ~398,652 t). Germany, Saudi Arabia, UK ≈ **0%**.
- Re-export hubs (grow <15% of what they export, >10k t exported): **12** countries; largest
  is the **UAE** (exported ~107,212 t, grew ~0 t).
- Cloves: Indonesia = **73%** of world production and consumes **~107%** of its own crop
  (self-consumption anomaly — see item #1). World cloves 2023 ≈ **185,691 t**.
- Vanilla: world total 2023 ≈ **6,922 t**; Madagascar share **23% (2000) → 45% (2023)**. The
  world grows **~841×** more dried chilli than vanilla.

Cross-check note: earlier exploratory numbers (before dropping the `China` rollup and before
fixing the base year / dried-only scope) differed slightly. The figures above — post-clean —
are the authoritative ones.

---

## 8. Open items / to re-verify before final submission

- [ ] Confirm the exact public FAOSTAT download URL/citation the team used originally.
- [ ] Confirm the exact Kaggle dataset URL for the population file.
- [ ] Add the external citation(s) for the kretek/clove-cigarette explanation (Finding 3 / "Up in Smoke").

(These are placeholders to fill with the team's real source links — not fabricated URLs.)
