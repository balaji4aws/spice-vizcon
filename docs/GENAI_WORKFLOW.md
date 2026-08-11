# How We Used AI (optional GenAI documentation)

The analysis, editorial decisions, and validation for this entry were done **by the team**. We
used AI/LLM tools as an *assistant* along the way — for speed on repetitive work — while keeping
every decision and every number under human control.

**Guiding principle:** AI can accelerate the work, but every claim must trace to the data or a
cited source, and a human makes the call.

## Where AI assisted
- **Data profiling.** Helped quickly scan the raw FAOSTAT extract and flag data-quality issues to
  check — a duplicated `China` total, a trailing space in the `Export ` header, negative apparent
  consumption, and green chillies sitting at a different scale. The team confirmed each one.
- **Exploration.** Helped compute and compare candidate angles across the nine spices; the team
  chose the three findings and the narrative.
- **Code.** Assisted with the data-prep script and the Streamlit/Plotly app code, which the team
  reviewed and tested.
- **Drafting.** Helped draft copy, which the team edited.

## What the team owned
- The story, the framing, and every editorial choice.
- The decision to make the pipeline **reproducible** (`build_data.py` recomputes all figures into
  `key_figures.json`, so nothing is hand-typed).
- The **honesty guardrails**: the assumptions/analysis notes and the strict separation between
  *what the data shows* and *outside-the-data* context (e.g. the cloves→cigarette explanation).
- Validation of every figure against the source data.

## Tools
Python · Streamlit · Plotly · pandas, with AI/LLM assistance as described above.
