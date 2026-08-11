"""
The Secret Life of Spices - data preparation pipeline
=====================================================
Reads the two raw datasets and emits clean, join-ready files + a verified
key_figures.json that the Streamlit app consumes. NOTHING in the narrative is
hand-typed: every headline number is computed here and written to disk.

Primary dataset : FAOSTAT spices (Production/Import/Export/Consumption, tonnes)
Reference layer : World population (Kaggle / UN World Population Prospects)

Run:  python3 build_data.py
"""
import csv, json, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "data", "processed")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- helpers
def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0

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

# ---------------------------------------------------------------- load spices
spice_rows = []
with open(os.path.join(RAW, "faostat_spices.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        r = {k.strip(): v for k, v in r.items()}  # 'Export ' has a trailing space
        area = r["Area"]
        if area == CHINA_ROLLUP:
            continue  # drop double-counting rollup
        spice_rows.append({
            "area": area,
            "spice": SHORT[r["Item"]],
            "year": int(r["Year"]),
            "import": num(r["Import"]),
            "export": num(r["Export"]),
            "production": num(r["Production"]),
            "consumption": num(r["Consumption"]),
        })

LATEST = max(r["year"] for r in spice_rows)   # expected 2023
BASE = 1995                                    # boom baseline

# write cleaned long file
with open(os.path.join(OUT, "spice_clean.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["area", "spice", "year", "import", "export", "production", "consumption", "is_dried_spice"])
    for r in spice_rows:
        w.writerow([r["area"], r["spice"], r["year"], r["import"], r["export"],
                    r["production"], r["consumption"], int(r["spice"] != GREEN)])

# ---------------------------------------------------------------- load population + crosswalk
pop_rows = []
with open(os.path.join(RAW, "world_population.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        pop_rows.append(r)

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
    "Netherlands (Kingdom of the) ": "Netherlands",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Republic of North Macedonia": "North Macedonia",
    "Cabo Verde": "Cape Verde",
    "Eswatini": "Eswatini",
    "State of Palestine": "Palestine",
    "Timor-Leste": "Timor-Leste",
    "Micronesia (Federated States of)": "Micronesia",
    "Saint Kitts and Nevis": "Saint Kitts and Nevis",
    "Bahamas": "Bahamas",
    "Bolivia": "Bolivia",
}

def pop_lookup(area):
    """Return population row for a FAOSTAT area name, or None."""
    if area in ALIAS and ALIAS[area] in pop_by_name:
        return pop_by_name[ALIAS[area]]
    if area in pop_by_name:
        return pop_by_name[area]
    return None

spice_areas = sorted(set(r["area"] for r in spice_rows))
crosswalk = []
unmatched = []
for a in spice_areas:
    p = pop_lookup(a)
    if p:
        crosswalk.append({"spice_area": a, "pop_name": p["Country/Territory"],
                          "cca3": p["CCA3"], "continent": p["Continent"],
                          "pop_2022": int(p["2022 Population"])})
    else:
        unmatched.append(a)

with open(os.path.join(OUT, "country_crosswalk.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["spice_area", "pop_name", "cca3", "continent", "pop_2022"])
    for c in crosswalk:
        w.writerow([c["spice_area"], c["pop_name"], c["cca3"], c["continent"], c["pop_2022"]])

cw_by_area = {c["spice_area"]: c for c in crosswalk}

# ---------------------------------------------------------------- Act 1: global production by spice by year
gby = defaultdict(float)
for r in spice_rows:
    gby[(r["spice"], r["year"])] += r["production"]
with open(os.path.join(OUT, "global_by_spice_year.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["spice", "year", "world_production"])
    for (sp, y), v in sorted(gby.items()):
        w.writerow([sp, y, round(v, 2)])

# growth 1995 -> latest, per spice
growth = []
for sp in SHORT.values():
    a = gby.get((sp, BASE), 0.0)
    b = gby.get((sp, LATEST), 0.0)
    growth.append({"spice": sp, "base": round(a, 1), "latest": round(b, 1),
                   "multiple": round(b / a, 2) if a else None,
                   "pct": round((b / a - 1) * 100, 1) if a else None})
with open(os.path.join(OUT, "growth_1995_latest.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["spice", f"prod_{BASE}", f"prod_{LATEST}", "multiple", "pct_change"])
    for g in growth:
        w.writerow([g["spice"], g["base"], g["latest"], g["multiple"], g["pct"]])

# ---------------------------------------------------------------- Act 3 support: concentration latest year
concentration = []
for sp in SHORT.values():
    prod = defaultdict(float)
    for r in spice_rows:
        if r["spice"] == sp and r["year"] == LATEST:
            prod[r["area"]] += r["production"]
    tot = sum(prod.values())
    top = sorted(prod.items(), key=lambda x: -x[1])
    for rank, (area, v) in enumerate(top[:10], 1):
        concentration.append({"spice": sp, "rank": rank, "area": area,
                              "production": round(v, 1),
                              "share_pct": round(v / tot * 100, 1) if tot else 0})
with open(os.path.join(OUT, "concentration_latest.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["spice", "rank", "area", "production", "share_pct"])
    for c in concentration:
        w.writerow([c["spice"], c["rank"], c["area"], c["production"], c["share_pct"]])

# ---------------------------------------------------------------- Act 2: grown vs eaten (per country, all dried spices, latest)
agg = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])  # area -> prod, imp, exp, cons
for r in spice_rows:
    if r["year"] == LATEST and r["spice"] != GREEN:
        a = agg[r["area"]]
        a[0] += r["production"]; a[1] += r["import"]; a[2] += r["export"]; a[3] += r["consumption"]
grown_eaten = []
for area, (p, i, e, c) in agg.items():
    cw = cw_by_area.get(area)
    grown_eaten.append({
        "area": area, "cca3": cw["cca3"] if cw else "", "continent": cw["continent"] if cw else "",
        "production": round(p, 1), "import": round(i, 1), "export": round(e, 1),
        "consumption": round(c, 1),
        "import_dependence_pct": round((i / c * 100), 1) if c > 0 else None,
        # self-sufficiency = how much of what a country consumes it grows itself (clean, unambiguous)
        "self_sufficiency_pct": round((p / c * 100), 1) if c > 0 else None,
    })
with open(os.path.join(OUT, "grown_vs_eaten_latest.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["area", "cca3", "continent", "production", "import", "export", "consumption",
                "import_dependence_pct", "self_sufficiency_pct"])
    for r in sorted(grown_eaten, key=lambda x: -x["consumption"]):
        w.writerow([r["area"], r["cca3"], r["continent"], r["production"], r["import"],
                    r["export"], r["consumption"], r["import_dependence_pct"], r["self_sufficiency_pct"]])

# ---------------------------------------------------------------- Trace-your-spice: production & consumption by country/spice (latest)
trace = []
for sp in SHORT.values():
    for r in spice_rows:
        if r["spice"] == sp and r["year"] == LATEST:
            cw = cw_by_area.get(r["area"])
            trace.append({"spice": sp, "area": r["area"], "cca3": cw["cca3"] if cw else "",
                          "continent": cw["continent"] if cw else "",
                          "production": round(r["production"], 1),
                          "consumption": round(r["consumption"], 1)})
with open(os.path.join(OUT, "trace_by_spice_latest.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["spice", "area", "cca3", "continent", "production", "consumption"])
    for r in trace:
        w.writerow([r["spice"], r["area"], r["cca3"], r["continent"], r["production"], r["consumption"]])

# ---------------------------------------------------------------- per-capita (reference layer, 2022 pop proxy for 2023)
percap = []
for area, (p, i, e, c) in agg.items():
    cw = cw_by_area.get(area)
    if not cw or c <= 0:
        continue
    pop = cw["pop_2022"]
    if pop <= 0:
        continue
    grams = c * 1000 * 1000 / pop  # tonnes -> grams per person per year
    percap.append({"area": area, "cca3": cw["cca3"], "continent": cw["continent"],
                   "consumption_t": round(c, 1), "pop_2022": pop,
                   "grams_per_capita_yr": round(grams, 1)})
with open(os.path.join(OUT, "per_capita_latest.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["area", "cca3", "continent", "consumption_t", "pop_2022", "grams_per_capita_yr"])
    for r in sorted(percap, key=lambda x: -x["grams_per_capita_yr"]):
        w.writerow([r["area"], r["cca3"], r["continent"], r["consumption_t"], r["pop_2022"], r["grams_per_capita_yr"]])

# ---------------------------------------------------------------- Cloves: Indonesia self-consumption anomaly over time
cloves = []
for y in range(BASE, LATEST + 1):
    prod = defaultdict(float)
    ind_cons = 0.0
    for r in spice_rows:
        if r["spice"] == "Cloves" and r["year"] == y:
            prod[r["area"]] += r["production"]
            if r["area"] == "Indonesia":
                ind_cons += r["consumption"]
    tot = sum(prod.values())
    ind = prod.get("Indonesia", 0.0)
    cloves.append({"year": y, "world_production": round(tot, 1),
                   "indonesia_production": round(ind, 1),
                   "indonesia_share_pct": round(ind / tot * 100, 1) if tot else 0,
                   "indonesia_consumption": round(ind_cons, 1),
                   "self_consumption_pct": round(ind_cons / ind * 100, 1) if ind else None})
with open(os.path.join(OUT, "cloves_indonesia.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "world_production", "indonesia_production", "indonesia_share_pct",
                "indonesia_consumption", "self_consumption_pct"])
    for r in cloves:
        w.writerow([r["year"], r["world_production"], r["indonesia_production"],
                    r["indonesia_share_pct"], r["indonesia_consumption"], r["self_consumption_pct"]])

# ---------------------------------------------------------------- Vanilla: Madagascar share over time
vanilla = []
for y in range(BASE, LATEST + 1):
    prod = defaultdict(float)
    for r in spice_rows:
        if r["spice"] == "Vanilla" and r["year"] == y:
            prod[r["area"]] += r["production"]
    tot = sum(prod.values())
    mad = prod.get("Madagascar", 0.0)
    vanilla.append({"year": y, "world_production": round(tot, 1),
                    "madagascar_production": round(mad, 1),
                    "madagascar_share_pct": round(mad / tot * 100, 1) if tot else 0})
with open(os.path.join(OUT, "vanilla_madagascar.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "world_production", "madagascar_production", "madagascar_share_pct"])
    for r in vanilla:
        w.writerow([r["year"], r["world_production"], r["madagascar_production"], r["madagascar_share_pct"]])

# ---------------------------------------------------------------- Re-export hubs (grow ~nothing, export a lot), latest
hubs = []
for area, (p, i, e, c) in agg.items():
    if e > 10000 and p < 0.15 * e:
        hubs.append({"area": area, "export": round(e, 1), "production": round(p, 1),
                     "import": round(i, 1),
                     "grows_pct_of_exports": round(p / e * 100, 1) if e else 0})
with open(os.path.join(OUT, "reexport_hubs_latest.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["area", "export", "production", "import", "grows_pct_of_exports"])
    for r in sorted(hubs, key=lambda x: -x["export"]):
        w.writerow([r["area"], r["export"], r["production"], r["import"], r["grows_pct_of_exports"]])

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
conc_top = {}
for c in concentration:
    if c["rank"] == 1:
        conc_top[c["spice"]] = {"area": c["area"], "share_pct": c["share_pct"]}

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
        "top_hub": (sorted(hubs, key=lambda x: -x["export"])[0] if hubs else None),
        # big consumers that grow the least of what they eat (self-sufficiency), consumption > 50k t
        "least_self_sufficient_big": sorted(
            [r for r in grown_eaten if r["consumption"] and r["consumption"] > 50000
             and r["self_sufficiency_pct"] is not None],
            key=lambda x: x["self_sufficiency_pct"])[:8],
    },
    "act3_cloves": {
        "indonesia_share_pct_latest": cloves_latest["indonesia_share_pct"],
        "indonesia_self_consumption_pct_latest": cloves_latest["self_consumption_pct"],
        "world_cloves_latest": cloves_latest["world_production"],
        "cloves_top_producer": conc_top.get("Cloves"),
    },
    "vanilla": {
        "world_vanilla_latest_t": round(van_world, 1),
        "madagascar_share_pct_latest": vanilla_latest["madagascar_share_pct"],
        "madagascar_share_pct_2000": next((v["madagascar_share_pct"] for v in vanilla if v["year"] == 2000), None),
        "chilli_dry_world_latest_t": round(chilli_dry_world, 1),
        "chilli_vs_vanilla_multiple": round(chilli_dry_world / van_world, 0) if van_world else None,
    },
    "concentration_top1": conc_top,
    "world_dried_total_latest_t": round(world_dried_total(LATEST), 1),
    "world_dried_total_base_t": round(world_dried_total(BASE), 1),
}
with open(os.path.join(OUT, "key_figures.json"), "w") as f:
    json.dump(key, f, indent=2)

print("DONE. latest_year =", LATEST, "| countries =", len(spice_areas),
      "| crosswalk matched =", len(crosswalk), "unmatched =", len(unmatched))
print("Unmatched (reference layer only):", unmatched)
print("\n--- KEY FIGURES ---")
print(json.dumps(key, indent=2))
