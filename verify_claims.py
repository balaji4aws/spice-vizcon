"""Cross-verify every factual claim made in the app and the README.

This deliberately does NOT import build_data.py or read data/processed/. It
recomputes each figure straight from data/raw/ using pandas, whereas the pipeline
uses the stdlib csv module. Two independent implementations agreeing is real
corroboration; re-running the same code would just be a tautology.

Usage:  python3 verify_claims.py     (exits 0 if every claim checks out, 1 otherwise)
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw" / "faostat_spices.csv"
POP = HERE / "data" / "raw" / "world_population.csv"

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
GREEN = "Chillies (green)"

df = pd.read_csv(RAW, encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]
raw_row_count = len(df)
df["Area"] = df["Area"].str.strip()
df = df[df["Area"] != "China"]           # drop the double-counting rollup
df["spice"] = df["Item"].map(SHORT)
for col in ["Import", "Export", "Production", "Consumption"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

dried = df[df["spice"] != GREEN]
L, B = int(df["Year"].max()), 1995

results = []


def check(label, claimed, actual, tol=0.05, note=""):
    """Compare a claim against an independently computed value.

    Booleans compare by truthiness, strings and sets by their text form, and
    numbers within `tol` to absorb float rounding.
    """
    if isinstance(claimed, bool):
        ok = bool(claimed) == bool(actual)
    elif isinstance(claimed, str) or isinstance(actual, (str, set, frozenset)):
        ok = str(claimed) == str(actual)
    else:
        ok = abs(claimed - actual) <= tol
    results.append((ok, label, claimed, actual, note))


# ---------------------------------------------------------------- scope claims
check("Spices tracked = 9", 9, df["spice"].nunique())
check("Countries = 198", 198, df["Area"].nunique())
check("Raw rows ~45,000", 45320, raw_row_count, tol=400)
check("Data range starts 1993", 1993, int(df["Year"].min()))
check("Latest year = 2023", 2023, L)
check("Dried spices = 8", 8, dried["spice"].nunique())

# ---------------------------------------------------------------- the dataset's own consumption column
# Both README and app state: apparent consumption = Production + Imports - Exports.
recomputed = df["Production"] + df["Import"] - df["Export"]
max_dev = (recomputed - df["Consumption"]).abs().max()
check("Consumption == Prod + Imp - Exp (max deviation)", 0.0, round(max_dev, 4), tol=0.51)

neg = int((df["Consumption"] < 0).sum())
check("Negative consumption rows = 2,448", 2448, neg, tol=0)

# ---------------------------------------------------------------- FINDING 1: the boom
wd_latest = dried[dried["Year"] == L]["Production"].sum()
wd_base = dried[dried["Year"] == B]["Production"].sum()
check("World dried-spice growth = 4.6x", 4.6, round(wd_latest / wd_base, 1), tol=0.05)
check("World dried total 1995 = 3,282,754.7 t (in app)", 3282754.7, round(wd_base, 1), tol=1.0)
check("World dried total 2023 = 15,018,402.1 t (in app)", 15018402.1, round(wd_latest, 1), tol=1.0)
# The copy used to round this span to "30 years". It is 28. Both app and README now say 28.
check("Boom span = 28 years (not 30)", 28, L - B, tol=0)

gprod = df.groupby(["spice", "Year"])["Production"].sum()


def growth(sp):
    a, b = gprod.get((sp, B), 0), gprod.get((sp, L), 0)
    return b / a, (b / a - 1) * 100


gm, gp = growth("Ginger")
check("Ginger 1995 = 745,109.7 t (in app)", 745109.7, round(gprod.get(("Ginger", B)), 1), tol=1.0)
check("Ginger 2023 = 4,861,254.3 t (in app)", 4861254.3, round(gprod.get(("Ginger", L)), 1), tol=1.0)
check("Ginger up 552%", 552.4, round(gp, 1), tol=0.5)
check("Ginger multiple 6.52x", 6.52, round(gm, 2), tol=0.01)
am, ap = growth("Anise/Cumin/Coriander")
check("Anise multiple 9.2x", 9.2, round(am, 2), tol=0.01)
check("Anise up 819.8%", 819.8, round(ap, 1), tol=0.5)

# "Every dried spice grew" + "Cloves grew least at ~2x"
mults = {sp: growth(sp)[0] for sp in dried["spice"].unique()}
check("Every dried spice grew (min multiple > 1)", True, bool(min(mults.values()) > 1))
check("Cloves grew least among dried spices", "Cloves", min(mults, key=mults.get))
check("Cloves multiple ~2x", 2.0, round(mults["Cloves"], 1), tol=0.05)
check("Anise led all dried spices", "Anise/Cumin/Coriander", max(mults, key=mults.get))
# "ginger next" after anise
ranked = sorted(mults, key=mults.get, reverse=True)
check("Ginger is 2nd-fastest growing dried spice", "Ginger", ranked[1])

# ---------------------------------------------------------------- FINDING 2: grown vs eaten
agg = dried[dried["Year"] == L].groupby("Area")[
    ["Production", "Import", "Export", "Consumption"]].sum()
agg["self_suff"] = agg["Production"] / agg["Consumption"] * 100

usa = agg.loc["United States of America"]
check("USA self-sufficiency = 0.2%", 0.2, round(usa["self_suff"], 1), tol=0.05)
check("USA consumption = 398,652.4 t (in app)", 398652.4, round(usa["Consumption"], 1), tol=1.0)
check("USA production = 661.8 t (in app)", 661.8, round(usa["Production"], 1), tol=0.5)

for country, label in [("Germany", "Germany"), ("Saudi Arabia", "Saudi Arabia"),
                       ("United Kingdom of Great Britain and Northern Ireland", "UK")]:
    v = agg.loc[country, "self_suff"]
    check(f"{label} near 0% self-sufficient (<1%)", True, bool(v < 1.0),
          note=f"actual {v:.2f}%")

# "big eaters that grow the least" - the 8 shown in the app
big = agg[agg["Consumption"] > 50000].sort_values("self_suff").head(8)
check("USA is among the 8 least self-sufficient big eaters", True,
      "United States of America" in big.index)

# re-export hubs
hubs = agg[(agg["Export"] > 10000) & (agg["Production"] < 0.15 * agg["Export"])]
check("Re-export hubs = 12", 12, len(hubs), tol=0)
check("Top hub = United Arab Emirates", "United Arab Emirates",
      hubs["Export"].idxmax())
check("UAE exports ~107,212 t", 107211.6, round(hubs["Export"].max(), 1), tol=1.0)

# "deep-coloured producers (India, Indonesia, Vietnam, China) grow far more than they eat"
for c, label in [("India", "India"), ("Indonesia", "Indonesia"),
                 ("Viet Nam", "Vietnam"), ("China, mainland", "China")]:
    v = agg.loc[c, "self_suff"]
    check(f"{label} grows more than it eats (>100%)", True, bool(v > 100),
          note=f"actual {v:.0f}%")

# ---------------------------------------------------------------- FINDING 3: cloves
cl = df[(df["spice"] == "Cloves") & (df["Year"] == L)]
cl_world = cl["Production"].sum()
cl_ind = cl[cl["Area"] == "Indonesia"]["Production"].sum()
cl_ind_cons = cl[cl["Area"] == "Indonesia"]["Consumption"].sum()
check("Indonesia grows 73% of world cloves", 72.8, round(cl_ind / cl_world * 100, 1), tol=0.15)
check("Indonesia clove self-consumption = 107.4%", 107.4,
      round(cl_ind_cons / cl_ind * 100, 1), tol=0.15)
check("Indonesia is #1 clove producer", "Indonesia",
      cl.groupby("Area")["Production"].sum().idxmax())

# "Cloves are the most concentrated spice"
conc = {}
for sp in df["spice"].unique():
    d = df[(df["spice"] == sp) & (df["Year"] == L)].groupby("Area")["Production"].sum()
    conc[sp] = d.max() / d.sum() * 100
check("Cloves are the most concentrated spice", "Cloves", max(conc, key=conc.get))

nmc = df[(df["spice"] == "Nutmeg/Mace/Cardamom") & (df["Year"] == L)]
check("Guatemala leads nutmeg/mace/cardamom", "Guatemala",
      nmc.groupby("Area")["Production"].sum().idxmax())

# ---------------------------------------------------------------- vanilla
van = df[(df["spice"] == "Vanilla") & (df["Year"] == L)]
van_world = van["Production"].sum()
mad = van[van["Area"] == "Madagascar"]["Production"].sum()
check("World vanilla ~6,921.6 t", 6921.6, round(van_world, 1), tol=1.0)
check("Madagascar vanilla share = 45%", 45.0, round(mad / van_world * 100, 1), tol=0.15)

van2000 = df[(df["spice"] == "Vanilla") & (df["Year"] == 2000)]
mad2000 = van2000[van2000["Area"] == "Madagascar"]["Production"].sum() / van2000["Production"].sum() * 100
check("Madagascar share in 2000 was 20-25%", True, bool(20 <= mad2000 <= 25),
      note=f"actual {mad2000:.1f}%")

chilli_dry = gprod.get(("Chillies (dry)", L), 0)
check("Dried chilli is 841x vanilla", 841.0, round(chilli_dry / van_world, 0), tol=0.6)

# ---------------------------------------------------------------- green chilli scale
green_latest = gprod.get((GREEN, L), 0)
check("Green chillies = 34M tonnes", 34.4, round(green_latest / 1e6, 1), tol=0.05)
check("Green chillies > 2x all dried combined", True, bool(green_latest / wd_latest > 2),
      note=f"actual {green_latest / wd_latest:.1f}x")
check("Green chillies ~5,000x vanilla", 4970, round(green_latest / van_world), tol=60)

# ---------------------------------------------------------------- population crosswalk / per-capita
pop = pd.read_csv(POP, encoding="utf-8-sig")
ALIAS = {"China, mainland": "China", "China, Taiwan Province of": "Taiwan",
         "China, Hong Kong SAR": "Hong Kong", "China, Macao SAR": "Macau",
         "Türkiye": "Turkey", "Viet Nam": "Vietnam",
         "United States of America": "United States", "Iran (Islamic Republic of)": "Iran",
         "Russian Federation": "Russia", "Republic of Korea": "South Korea",
         "Democratic People's Republic of Korea": "North Korea",
         "Bolivia (Plurinational State of)": "Bolivia",
         "Venezuela (Bolivarian Republic of)": "Venezuela",
         "United Republic of Tanzania": "Tanzania",
         "Lao People's Democratic Republic": "Laos", "Syrian Arab Republic": "Syria",
         "Republic of Moldova": "Moldova", "Brunei Darussalam": "Brunei",
         "Democratic Republic of the Congo": "DR Congo",
         "Congo": "Republic of the Congo", "Côte d'Ivoire": "Ivory Coast",
         "Czechia": "Czech Republic", "Netherlands (Kingdom of the)": "Netherlands",
         "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
         "Republic of North Macedonia": "North Macedonia", "Cabo Verde": "Cape Verde",
         "State of Palestine": "Palestine", "Micronesia (Federated States of)": "Micronesia"}
pop_names = set(pop["Country/Territory"])
areas = sorted(df["Area"].unique())
matched = [a for a in areas if ALIAS.get(a, a) in pop_names]
unmatched = [a for a in areas if ALIAS.get(a, a) not in pop_names]
check("Crosswalk matched = 195", 195, len(matched), tol=0)
check("Crosswalk unmatched = 3", 3, len(unmatched), tol=0)
check("Unmatched are defunct entities", True,
      set(unmatched) == {"Belgium-Luxembourg", "Serbia and Montenegro", "Sudan (former)"},
      note=str(unmatched))
check("Population file has no 2023 column", True, "2023 Population" not in pop.columns)

popmap = {r["Country/Territory"]: r["2022 Population"] for _, r in pop.iterrows()}
pc = {}
for a in matched:
    if a in agg.index and agg.loc[a, "Consumption"] > 0:
        p = popmap[ALIAS.get(a, a)]
        if p > 0:
            pc[a] = agg.loc[a, "Consumption"] * 1e6 / p
check("Guyana ~64 kg/person (cited as an artifact)", 64, round(pc["Guyana"] / 1000), tol=1.5)
check("Nepal ~13 kg/person (cited as an artifact)", 13, round(pc["Nepal"] / 1000), tol=1.5)
check("Nepal is a ginger producer (as claimed)", True,
      bool(df[(df["Area"] == "Nepal") & (df["spice"] == "Ginger") &
              (df["Year"] == L)]["Production"].sum() > 0))

# the per-capita chart: big nations (>30M), artifacts dropped (<20000 g), top 12
big_pc = {a: v for a, v in pc.items()
          if popmap[ALIAS.get(a, a)] > 30_000_000 and v < 20000}
top12 = sorted(big_pc, key=big_pc.get, reverse=True)[:12]
for c in ["Nepal", "Thailand", "Bangladesh", "India", "Nigeria"]:
    check(f"{c} in top-12 per-capita among big nations", True, c in top12)

# ---------------------------------------------------------------- report
print(f"{'':3}{'CLAIM':58} {'STATED':>14} {'COMPUTED':>14}")
print("-" * 108)
fails = 0
for ok, label, claimed, actual, note in results:
    if not ok:
        fails += 1
    mark = "ok " if ok else "XX "
    extra = f"   {note}" if note else ""
    print(f"{mark}{label:58} {claimed!s:>14} {actual!s:>14}{extra}")
print("-" * 108)
if fails:
    print(f"{len(results) - fails}/{len(results)} verified  |  {fails} MISMATCH")
    sys.exit(1)
print(f"{len(results)}/{len(results)} claims verified against the raw data  |  no mismatches")
