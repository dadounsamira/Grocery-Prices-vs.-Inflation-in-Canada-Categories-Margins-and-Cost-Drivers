# Download public data for CIND820 capstone project.

from datetime import date
from pathlib import Path


import zipfile
import pandas as pd
import requests

# Show all columns when printing #moved the set up from bottom to top to see all columns bc pandas hides some columns when the table is too wide for the screen.
pd.set_option("display.max_columns", None)


# Today s date added to the file names so we know when data was downloaded
TODAY=date.today().isoformat()

# Create folder where the raw download are saved
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

# Reusable function: works for any Statistics Canada table, given its ID
def load_statcan(table_id):
    """Download a Statistics Canada table (if not already done today) and return it as a DataFrame."""
    # Download only if today's file isn't already saved
    zip_path = RAW / f"statcan_{table_id}_{TODAY}.zip"
    if zip_path.exists():
        print("Already downloaded today:", zip_path)
    else:
        api_url = f"https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{table_id}/en"
        response = requests.get(api_url, timeout=60)
        response.raise_for_status()
        zip_url = response.json()["object"]
        print("Download link:", zip_url)
        data = requests.get(zip_url, timeout=300)
        data.raise_for_status()
        zip_path.write_bytes(data.content)
        print("Saved:", zip_path)

    # Open the zip and read data inside it
    with zipfile.ZipFile(zip_path, "r") as z:
        print("Files in the zip :", z.namelist())
        with z.open(f"{table_id}.csv") as f:
            df = pd.read_csv(f, low_memory=False)
    return df


# Dataset1 : Monthly average retail prices ( table 18-10-0245-01)
prices = load_statcan("18100245")
print("Rows and columns:", prices.shape)
print("Column names:", prices.columns.tolist())
print(prices.head())


print("Date range:", prices["REF_DATE"].min(), "to", prices["REF_DATE"].max())
print("Geographies:", prices["GEO"].unique())
print("Number of products:", prices["Products"].nunique())


# Dataset 2: Consumer Price Index, monthly, not seasonally adjusted (table 18-10-0004-01)
cpi = load_statcan("18100004")
print("CPI rows and columns:", cpi.shape)
print("CPI column names:", cpi.columns.tolist())
print("CPI date range:", cpi["REF_DATE"].min(), "to", cpi["REF_DATE"].max())
print("CPI geographies:", cpi["GEO"].unique())