"""
The Secret Life of Spices - data preparation pipeline
=====================================================
Reads the two raw datasets and emits clean, join-ready files + a verified
key_figures.json that the Streamlit app consumes. NOTHING in the narrative is
hand-typed: every headline number is computed here and written to disk.

Primary dataset : FAOSTAT spices (Production/Import/Export/Consumption, tonnes)
Reference layer : World population (Kaggle / UN World Population Prospects)

Run:  python3 build_data.py            # writes data/processed/, prints a short summary
      python3 build_data.py --verbose  # also dumps the full key_figures.json
"""
import argparse
import csv
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "data", "processed")

# ---------------------------------------------------------------- domain constants
# FAOSTAT item names are long and inconsistent; map them once to display labels.
SHORT = {
    "Anise, badian, coriander, cumin, caraway, fennel and juniper berries, raw": "Anise/Cumin/Coriander",
    "Chillies and peppers, dry (Capsicum spp., Pimenta spp.), raw": "Chillies (dry)",
    "Chillies and peppers, green (Capsicum spp. and Pimenta spp.)": "Chillies (green)",
    "Cinnamon and cinnamon-tree flowers, raw": "Cinnamon",
    "Cloves (whole stems), raw": "Cloves",
    "Ginger, raw": "Ginger",
    "Nutmeg, mace, cardamoms, raw": "Nutmeg/Mace/Cardamom",
    "Pepper (Piper spp.), raw": "Pepper",
    "Vanilla, raw": "Vanilla",
}
# Dried "true" spices for the core narrative (green chillies excluded - it is a fresh veg crop)
GREEN = "Chillies (green)"
DRIED_SPICES = [v for v in SHORT.values() if v != GREEN]

# China rollup to drop (keep component territories, primarily China, mainland)
CHINA_ROLLUP = "China"

BASE = 1995  # boom baseline; the file starts in 1993 but the first two years are thin

# Re-export hub thresholds: ships real volume, grows almost none of it.
HUB_MIN_EXPORT_T = 10_000
HUB_MAX_PROD_SHARE_OF_EXPORT = 0.15

# A country must consume this much to count as a "big eater" in the self-sufficiency ranking.
BIG_CONSUMER_MIN_T = 50_000

# ---------------------------------------------------------------- helpers
_unparseable = 0


def num(x):
    """Coerce a raw CSV cell to float.

    Blanks and non-numeric cells become 0.0 - FAOSTAT leaves a cell empty when a
    country reports nothing for that spice/year, which we read as zero. Occurrences
    are counted and reported at the end so a genuinely malformed file is visible
    rather than silently zeroed.
    """
    global _unparseable
    try:
        return float(x)
    except (TypeError, ValueError):
        _unparseable += 1
        return 0.0


def write_csv(name, header, rows):
    """Write a list of row-sequences to data/processed/<name>."""
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def pct(part, whole, digits=1):
    """part/whole as a percentage, or None when whole is zero/absent."""
    return round(part / whole * 100, digits) if whole else None


def pct0(part, whole, digits=1):
    """part/whole as a percentage, falling back to 0.0 when whole is zero/absent."""
    return round(part / whole * 100, digits) if whole else 0.0


# ---------------------------------------------------------------- load spices
def load_spice_rows():
    """Read + clean the FAOSTAT spice export into a flat list of dicts."""
    rows = []
    with open(os.path.join(RAW, "faostat_spices.csv"), encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            # 'Export ' ships with a trailing space in the header; values can carry
            # stray whitespace too, so normalise both sides of the mapping.
            rec = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in raw.items()}
            if rec["Area"] == CHINA_ROLLUP:
                continue  # drop double-counting rollup
            rows.append({
                "area": rec["Area"],
                "spice": SHORT[rec["Item"]],
                "year": int(rec["Year"]),
                "import": num(rec["Import"]),
                "export": num(rec["Export"]),
                "production": num(rec["Production"]),
                "consumption": num(rec["Consumption"]),
            })
    return rows


os.makedirs(OUT, exist_ok=True)
spice_rows = load_spice_rows()

LATEST = max(r["year"] for r in spice_rows)  # expected 2023

# Index once by (spice, year). Every downstream slice reads this instead of
# re-scanning all ~45k rows, which the previous version did ~50 times over.
by_spice_year = defaultdict(list)
for r in spice_rows:
    by_spice_year[(r["spice"], r["year"])].append(r)


def rows_for(spice, year):
    return by_spice_year.get((spice, year), [])


# Apparent consumption (Production + Import - Export) can come out negative when a
# country re-exports from stock. Those rows are real data, not corruption, so we keep
# them in the cleaned file and exclude them at the point of use (every consumption
# ratio below is guarded on consumption > 0). Count them so the scale stays visible.
negative_consumption_rows = sum(1 for r in spice_rows if r["consumption"] < 0)

# write cleaned long file
write_csv(
    "spice_clean.csv",
    ["area", "spice", "year", "import", "export", "production", "consumption", "is_dried_spice"],
    [[r["area"], r["spice"], r["year"], r["import"], r["export"],
      r["production"], r["consumption"], int(r["spice"] != GREEN)] for r in spice_rows],
)

# ---------------------------------------------------------------- load population + crosswalk
with open(os.path.join(RAW, "world_population.csv"), encoding="utf-8-sig") as f:
    pop_rows = list(csv.DictReader(f))

pop_by_name = {r["Country/Territory"]: r for r in pop_rows}

# explicit aliases: FAOSTAT area name -> population Country/Territory name
ALIAS = {
    "China, mainland": "China",
    "China, Taiwan Province of": "Taiwan",
    "China, Hong Kong SAR": "Hong Kong",
    "China, Macao SAR": "Macau",
    "Türkiye": "Turkey",
    "Viet Nam": "Vietnam",
    "United States of America": "United States",
    "Iran (Islamic Republic of)": "Iran",
    "Russian Federation": "Russia",
    "Republic of Korea": "South Korea",
    "Democratic People's Republic of Korea": "North Korea",
    "Bolivia (Plurinational State of)": "Bolivia",
    "Venezuela (Bolivarian Republic of)": "Venezuela",
    "United Republic of Tanzania": "Tanzania",
    "Lao People's Democratic Republic": "Laos",
    "Syrian Arab Republic": "Syria",
    "Republic of Moldova": "Moldova",
    "Brunei Darussalam": "Brunei",
    "Democratic Republic of the Congo": "DR Congo",
    "Congo": "Republic of the Congo",
    "Côte d'Ivoire": "Ivory Coast",
    "Czechia": "Czech Republic",
    "Netherlands (Kingdom of the)": "Netherlands",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Republic of North Macedonia": "North Macedonia",
    "Cabo Verde": "Cape Verde",
    "State of Palestine": "Palestine",
    "Micronesia (Federated States of)": "Micronesia",
}


def pop_lookup(area):
    """Return population row for a FAOSTAT area name, or None."""
    alias = ALIAS.get(area)
    if alias and alias in pop_by_name:
        return pop_by_name[alias]
    return pop_by_name.get(area)


spice_areas = sorted({r["area"] for r in spice_rows})
crosswalk = []
unmatched = []
for area_name in spice_areas:
    p = pop_lookup(area_name)
    if p:
        crosswalk.append({"spice_area": area_name, "pop_name": p["Country/Territory"],
                          "cca3": p["CCA3"], "continent": p["Continent"],
                          "pop_2022": int(p["2022 Population"])})
    else:
        unmatched.append(area_name)

write_csv(
    "country_crosswalk.csv",
    ["spice_area", "pop_name", "cca3", "continent", "pop_2022"],
    [[c["spice_area"], c["pop_name"], c["cca3"], c["continent"], c["pop_2022"]] for c in crosswalk],
)

cw_by_area = {c["spice_area"]: c for c in crosswalk}

# ---------------------------------------------------------------- Act 1: global production by spice by year
gby = defaultdict(float)
for r in spice_rows:
    gby[(r["spice"], r["year"])] += r["production"]

write_csv(
    "global_by_spice_year.csv",
    ["spice", "year", "world_production"],
    [[sp, y, round(v, 2)] for (sp, y), v in sorted(gby.items())],
)

# growth 1995 -> latest, per spice
growth = []
for sp in SHORT.values():
    a = gby.get((sp, BASE), 0.0)
    b = gby.get((sp, LATEST), 0.0)
    growth.append({"spice": sp, "base": round(a, 1), "latest": round(b, 1),
                   "multiple": round(b / a, 2) if a else None,
                   "pct": round((b / a - 1) * 100, 1) if a else None})

write_csv(
    "growth_1995_latest.csv",
    ["spice", f"prod_{BASE}", f"prod_{LATEST}", "multiple", "pct_change"],
    [[g["spice"], g["base"], g["latest"], g["multiple"], g["pct"]] for g in growth],
)

# ---------------------------------------------------------------- Act 3 support: concentration latest year
concentration = []
for sp in SHORT.values():
    prod = defaultdict(float)
    for r in rows_for(sp, LATEST):
        prod[r["area"]] += r["production"]
    tot = sum(prod.values())
    top = sorted(prod.items(), key=lambda x: -x[1])
    for rank, (area_name, v) in enumerate(top[:10], 1):
        concentration.append({"spice": sp, "rank": rank, "area": area_name,
                              "production": round(v, 1),
                              "share_pct": pct0(v, tot)})

write_csv(
    "concentration_latest.csv",
    ["spice", "rank", "area", "production", "share_pct"],
    [[c["spice"], c["rank"], c["area"], c["production"], c["share_pct"]] for c in concentration],
)

# ---------------------------------------------------------------- Act 2: grown vs eaten (per country, all dried spices, latest)
agg = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])  # area -> prod, imp, exp, cons
for r in spice_rows:
    if r["year"] == LATEST and r["spice"] != GREEN:
        totals = agg[r["area"]]
        totals[0] += r["production"]
        totals[1] += r["import"]
        totals[2] += r["export"]
        totals[3] += r["consumption"]

grown_eaten = []
for area_name, (p, imp, exp, cons) in agg.items():
    cw = cw_by_area.get(area_name)
    grown_eaten.append({
        "area": area_name,
        "cca3": cw["cca3"] if cw else "",
        "continent": cw["continent"] if cw else "",
        "production": round(p, 1), "import": round(imp, 1), "export": round(exp, 1),
        "consumption": round(cons, 1),
        # Both ratios are None when consumption <= 0 (a re-export-from-stock artifact),
        # which keeps those countries out of every downstream ranking and map.
        "import_dependence_pct": pct(imp, cons) if cons > 0 else None,
        # self-sufficiency = how much of what a country consumes it grows itself
        "self_sufficiency_pct": pct(p, cons) if cons > 0 else None,
    })

write_csv(
    "grown_vs_eaten_latest.csv",
    ["area", "cca3", "continent", "production", "import", "export", "consumption",
     "import_dependence_pct", "self_sufficiency_pct"],
    [[r["area"], r["cca3"], r["continent"], r["production"], r["import"], r["export"],
      r["consumption"], r["import_dependence_pct"], r["self_sufficiency_pct"]]
     for r in sorted(grown_eaten, key=lambda x: -x["consumption"])],
)

# ---------------------------------------------------------------- Trace-your-spice: production & consumption by country/spice (latest)
trace = []
for sp in SHORT.values():
    for r in rows_for(sp, LATEST):
        cw = cw_by_area.get(r["area"])
        trace.append({"spice": sp, "area": r["area"], "cca3": cw["cca3"] if cw else "",
                      "continent": cw["continent"] if cw else "",
                      "production": round(r["production"], 1),
                      "consumption": round(r["consumption"], 1)})

write_csv(
    "trace_by_spice_latest.csv",
    ["spice", "area", "cca3", "continent", "production", "consumption"],
    [[r["spice"], r["area"], r["cca3"], r["continent"], r["production"], r["consumption"]]
     for r in trace],
)

# ---------------------------------------------------------------- per-capita (reference layer, 2022 pop proxy for latest year)
percap = []
for area_name, (_p, _imp, _exp, cons) in agg.items():
    cw = cw_by_area.get(area_name)
    if not cw or cons <= 0:
        continue
    pop = cw["pop_2022"]
    if pop <= 0:
        continue
    grams = cons * 1000 * 1000 / pop  # tonnes -> grams per person per year
    percap.append({"area": area_name, "cca3": cw["cca3"], "continent": cw["continent"],
                   "consumption_t": round(cons, 1), "pop_2022": pop,
                   "grams_per_capita_yr": round(grams, 1)})

write_csv(
    "per_capita_latest.csv",
    ["area", "cca3", "continent", "consumption_t", "pop_2022", "grams_per_capita_yr"],
    [[r["area"], r["cca3"], r["continent"], r["consumption_t"], r["pop_2022"],
      r["grams_per_capita_yr"]]
     for r in sorted(percap, key=lambda x: -x["grams_per_capita_yr"])],
)


# ---------------------------------------------------------------- single-country share of one spice, over time
def country_share_series(spice, country):
    """Yearly world total, one country's production, and that country's share."""
    series = []
    for y in range(BASE, LATEST + 1):
        prod = defaultdict(float)
        country_cons = 0.0
        for r in rows_for(spice, y):
            prod[r["area"]] += r["production"]
            if r["area"] == country:
                country_cons += r["consumption"]
        tot = sum(prod.values())
        own = prod.get(country, 0.0)
        series.append({"year": y, "world_production": round(tot, 1),
                       "country_production": round(own, 1),
                       "country_share_pct": pct0(own, tot),
                       "country_consumption": round(country_cons, 1),
                       "self_consumption_pct": pct(country_cons, own)})
    return series


# Cloves: Indonesia self-consumption anomaly over time
cloves = country_share_series("Cloves", "Indonesia")
write_csv(
    "cloves_indonesia.csv",
    ["year", "world_production", "indonesia_production", "indonesia_share_pct",
     "indonesia_consumption", "self_consumption_pct"],
    [[r["year"], r["world_production"], r["country_production"], r["country_share_pct"],
      r["country_consumption"], r["self_consumption_pct"]] for r in cloves],
)

# Vanilla: Madagascar share over time
vanilla = country_share_series("Vanilla", "Madagascar")
write_csv(
    "vanilla_madagascar.csv",
    ["year", "world_production", "madagascar_production", "madagascar_share_pct"],
    [[r["year"], r["world_production"], r["country_production"], r["country_share_pct"]]
     for r in vanilla],
)

# ---------------------------------------------------------------- Re-export hubs (grow ~nothing, export a lot), latest
hubs = []
for area_name, (p, imp, exp, _cons) in agg.items():
    if exp > HUB_MIN_EXPORT_T and p < HUB_MAX_PROD_SHARE_OF_EXPORT * exp:
        hubs.append({"area": area_name, "export": round(exp, 1), "production": round(p, 1),
                     "import": round(imp, 1),
                     "grows_pct_of_exports": pct0(p, exp)})

write_csv(
    "reexport_hubs_latest.csv",
    ["area", "export", "production", "import", "grows_pct_of_exports"],
    [[r["area"], r["export"], r["production"], r["import"], r["grows_pct_of_exports"]]
     for r in sorted(hubs, key=lambda x: -x["export"])],
)


# ---------------------------------------------------------------- KEY FIGURES (verified, single source of truth for narrative)
def world_dried_total(year):
    return sum(r["production"] for r in spice_rows if r["year"] == year and r["spice"] != GREEN)


top_ginger = next(g for g in growth if g["spice"] == "Ginger")
top_anise = next(g for g in growth if g["spice"] == "Anise/Cumin/Coriander")
cloves_latest = cloves[-1]
vanilla_latest = vanilla[-1]
van_world = gby.get(("Vanilla", LATEST), 0.0)
chilli_dry_world = gby.get(("Chillies (dry)", LATEST), 0.0)

# concentration headline per spice (rank 1)
conc_top = {c["spice"]: {"area": c["area"], "share_pct": c["share_pct"]}
            for c in concentration if c["rank"] == 1}

# USA import dependence
usa = next((r for r in grown_eaten if r["area"] == "United States of America"), None)

key = {
    "meta": {
        "latest_year": LATEST,
        "base_year": BASE,
        "n_countries": len(spice_areas),
        "n_spices_total": len(SHORT),
        "n_dried_spices": len(DRIED_SPICES),
        "crosswalk_matched": len(crosswalk),
        "crosswalk_unmatched": len(unmatched),
        "unmatched_examples": unmatched[:15],
        "negative_consumption_rows": negative_consumption_rows,
    },
    "act1_boom": {
        "ginger_multiple": top_ginger["multiple"], "ginger_pct": top_ginger["pct"],
        "ginger_base": top_ginger["base"], "ginger_latest": top_ginger["latest"],
        "anise_multiple": top_anise["multiple"], "anise_pct": top_anise["pct"],
        "growth_all": {g["spice"]: {"multiple": g["multiple"], "pct": g["pct"]} for g in growth},
    },
    "act2_grown_eaten": {
        "usa_self_sufficiency_pct": usa["self_sufficiency_pct"] if usa else None,
        "usa_production": usa["production"] if usa else None,
        "usa_consumption": usa["consumption"] if usa else None,
        "n_reexport_hubs": len(hubs),
        "top_hub": (max(hubs, key=lambda x: x["export"]) if hubs else None),
        # big consumers that grow the least of what they eat (self-sufficiency)
        "least_self_sufficient_big": sorted(
            [r for r in grown_eaten if r["consumption"] and r["consumption"] > BIG_CONSUMER_MIN_T
             and r["self_sufficiency_pct"] is not None],
            key=lambda x: x["self_sufficiency_pct"])[:8],
    },
    "act3_cloves": {
        "indonesia_share_pct_latest": cloves_latest["country_share_pct"],
        "indonesia_self_consumption_pct_latest": cloves_latest["self_consumption_pct"],
        "world_cloves_latest": cloves_latest["world_production"],
        "cloves_top_producer": conc_top.get("Cloves"),
    },
    "vanilla": {
        "world_vanilla_latest_t": round(van_world, 1),
        "madagascar_share_pct_latest": vanilla_latest["country_share_pct"],
        "madagascar_share_pct_2000": next(
            (v["country_share_pct"] for v in vanilla if v["year"] == 2000), None),
        "chilli_dry_world_latest_t": round(chilli_dry_world, 1),
        "chilli_vs_vanilla_multiple": round(chilli_dry_world / van_world, 0) if van_world else None,
    },
    "concentration_top1": conc_top,
    "world_dried_total_latest_t": round(world_dried_total(LATEST), 1),
    "world_dried_total_base_t": round(world_dried_total(BASE), 1),
}
with open(os.path.join(OUT, "key_figures.json"), "w") as f:
    json.dump(key, f, indent=2)

# ---------------------------------------------------------------- summary
args = argparse.ArgumentParser(description=__doc__)
args.add_argument("--verbose", action="store_true", help="also print the full key_figures.json")
opts = args.parse_args()

print("DONE. latest_year =", LATEST, "| countries =", len(spice_areas),
      "| crosswalk matched =", len(crosswalk), "unmatched =", len(unmatched))
print("Unmatched (reference layer only):", unmatched)
print(f"Negative apparent-consumption rows kept but excluded from ratios: "
      f"{negative_consumption_rows:,} of {len(spice_rows):,}")
if _unparseable:
    print(f"WARNING: {_unparseable:,} non-numeric cells read as 0.0 - check the raw export")
if opts.verbose:
    print("\n--- KEY FIGURES ---")
    print(json.dumps(key, indent=2))
