# Load the clean tables into one SQLite database (CIND820 Milestone 2)
import sqlite3
from pathlib import Path
import pandas as pd

CLEAN = Path("data/clean")
DB = Path("data/grocery.db")

conn = sqlite3.connect(DB)
for name in ["retail_prices_clean", "cpi_clean", "drivers_monthly"]:
    table = pd.read_csv(CLEAN / f"{name}.csv")
    table.to_sql(name, conn, if_exists="replace", index=False)
    print("Loaded:", name, table.shape)

# VERIFY: ask the database itself how many rows each table has
for name in ["retail_prices_clean", "cpi_clean", "drivers_monthly"]:
    count = pd.read_sql(f"SELECT COUNT(*) AS n FROM {name}", conn)
    print(name, "rows in database:", count["n"][0])
conn.close()

# STEP 2: join the CPI with the drivers on the month, in SQL
conn = sqlite3.connect(DB)
query = """
SELECT c.REF_DATE AS month, c.GEO, c."Group", c.VALUE AS cpi,
       d.energy_index, d.agri_index, d.usdcad, d.policy_rate
FROM cpi_clean AS c
JOIN drivers_monthly AS d
  ON c.REF_DATE = d.month
"""
joined = pd.read_sql(query, conn)
print("Joined:", joined.shape)
print("Missing:", joined.isna().sum().sum())
joined.to_sql("cpi_with_drivers", conn, if_exists="replace", index=False)
conn.close()