# Download public data for CIND820 capstone project.

from datetime import date
from pathlib import Path
from zipfile import ZipFile

import zipfile
import pandas as pd
import requests




# Today s date added to the file names so we know when data was downloaded
TODAY=date.today().isoformat()

# Create folder where the raw download are saved
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

# Dataset1 : Monthly average retail prices ( table 18-10-0245-01)
table_id = "18100245"
api_url = f"https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{table_id}/en"

response = requests.get(api_url, timeout=60)
print(response.status_code)
print(response.json())

response.raise_for_status()

# Pull download link
zip_url = response.json() ["object"]
print("Download link :", zip_url)

# Download the zip file
data = requests.get(zip_url, timeout=300)
data.raise_for_status()

# Save it raw in data raw
zip_path = RAW / f"statcan_{table_id}_{TODAY}.zip"
zip_path.write_bytes(data.content)
print("Saved :", zip_path)

# Open the zip and read data inside it

with zipfile.ZipFile(zip_path, "r") as z:
    print("Files in the zip :", z.namelist())
    with z.open(f"{table_id}.csv") as f:
        prices = pd.read_csv(f, low_memory=False)

print("Rows and columns:", prices.shape)
print("Column names:", prices.columns.tolist())
print(prices.head())

# Tell pandas to read the whole file
#prices = pd.read_csv(f, low_memory=False)

# Show all columns when printing
pd.set_option("display.max_columns", None)

print("Date range:", prices["REF_DATE"].min(), "to", prices["REF_DATE"].max())
print("Geographies:", prices["GEO"].unique())
print("Number of products:", prices["Products"].nunique())