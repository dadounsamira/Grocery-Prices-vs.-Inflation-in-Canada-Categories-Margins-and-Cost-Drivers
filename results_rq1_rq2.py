# RQ1 and RQ2 first results (CIND820 Milestone 3)
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

CLEAN = Path("data/clean")
OUT = Path("outputs/results")
OUT.mkdir(parents=True, exist_ok=True)

# ===== RQ1: category gap vs all-items, every province =====
cpi = pd.read_csv(CLEAN / "cpi_clean.csv")
start = cpi[cpi["REF_DATE"] == "2019-01"].pivot(index="GEO", columns="Group", values="VALUE")
end = cpi[cpi["REF_DATE"] == "2026-08"].pivot(index="GEO", columns="Group", values="VALUE")
pct = end / start * 100 - 100

CATEGORIES = ["Meat", "Fish, seafood and other marine products", "Dairy products and eggs",
              "Bakery and cereal products (excluding baby food)", "Fruit, fruit preparations and nuts",
              "Vegetables and vegetable preparations", "Other food products and non-alcoholic beverages"]
gap = pct[CATEGORIES].sub(pct["All-items"], axis=0).round(1)
gap.columns = ["Meat", "Fish", "Dairy & eggs", "Bakery & cereal", "Fruit & nuts", "Vegetables", "Other food"]
gap = gap.sort_values("Meat", ascending=False)
print(gap)
print("Cells above +5 points:", (gap > 5).sum().sum(), "of", gap.size)
gap.to_csv(OUT / "rq1_gap_category_by_province.csv")

fig, ax = plt.subplots(figsize=(10, 6))
image = ax.imshow(gap.values, cmap="RdBu_r", vmin=-25, vmax=25, aspect="auto")
ax.set_xticks(range(len(gap.columns)))
ax.set_xticklabels(gap.columns, rotation=30, ha="right")
ax.set_yticks(range(len(gap.index)))
ax.set_yticklabels(gap.index)
for i in range(gap.shape[0]):
    for j in range(gap.shape[1]):
        ax.text(j, i, gap.iloc[i, j], ha="center", va="center", fontsize=8)
fig.colorbar(image, label="Category inflation minus all-items inflation (points)")
ax.set_title("RQ1: food category gap vs overall inflation, Jan 2019 to Aug 2026")
fig.tight_layout()
fig.savefig(OUT / "rq1_gap_heatmap.png", dpi=150)
plt.show()

# ===== RQ2: grocer margins vs the yearly food-price gap =====
margins = pd.read_csv("data/manual/grocer_margins.csv")
margins["gross_margin"] = margins["gross_profit_millions"] / margins["sales_millions"] * 100
margin_table = margins.pivot(index="fiscal_year", columns="company", values="gross_margin").round(1)

canada = cpi[cpi["GEO"] == "Canada"].pivot(index="REF_DATE", columns="Group", values="VALUE")
canada["year"] = canada.index.str[:4].astype(int)
yearly = canada.groupby("year")[["Food purchased from stores", "All-items"]].mean()
yearly_change = (yearly.pct_change() * 100).round(1)
yearly_change["food_gap"] = (yearly_change["Food purchased from stores"] - yearly_change["All-items"]).round(1)

rq2 = margin_table.join(yearly_change["food_gap"])
print(rq2)
rq2.to_csv(OUT / "rq2_margins_vs_food_gap.csv")

fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.bar(rq2.index, rq2["food_gap"], color="lightgrey", label="Food inflation minus all-items (points)")
ax1.axhline(0, color="grey", linewidth=0.8)
ax1.set_ylabel("Food gap (percentage points)")
ax2 = ax1.twinx()
for company in ["Loblaw", "Metro", "Empire"]:
    ax2.plot(rq2.index, rq2[company], marker="o", label=company)
ax2.set_ylabel("Gross margin (%)")
ax1.set_title("RQ2: grocer gross margins and the food-price gap, 2017-2025")
fig.subplots_adjust(bottom=0.2)
fig.legend(loc="lower center", ncol=4)
fig.savefig(OUT / "rq2_margins_vs_gap.png", dpi=150)
plt.show()

print(rq2[["Loblaw", "Metro", "Empire"]].corrwith(rq2["food_gap"]).round(2))