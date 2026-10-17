# Grocery Prices vs. Inflation in Canada: Categories, Margins and Cost Drivers

**CIND820 Big Data Analytics Capstone, Toronto Metropolitan University, Fall 2026**
Author: Samira Dadoun

## Project summary
Food prices in Canada rose sharply after 2021. This project uses public data to answer:

1. **RQ1:** Which food categories and provinces saw prices rise faster than all-items CPI since January 2019?
2. **RQ2:** Did grocery retailers' gross margins rise over the same periods that food prices outpaced overall inflation?
3. **RQ3:** How much of food inflation is associated with energy and agricultural commodity prices, the USD/CAD exchange rate and interest rates, and can a model using these factors forecast food inflation better than a seasonal naive baseline?

**Intended users:** consumer-advocacy groups and public-policy analysts who monitor food affordability.

## Data sources
| Dataset | Publisher | Access | Licence |
|---|---|---|---|
| Monthly average retail prices for selected products (18-10-0245-01) | Statistics Canada | Web Data Service API | Statistics Canada Open Licence |
| Consumer Price Index, monthly, not seasonally adjusted (18-10-0004-01) | Statistics Canada | Web Data Service API | Statistics Canada Open Licence |
| Policy rate (V39079), USD/CAD (FXUSDCAD), commodity price index (BCPI: energy, agriculture) | Bank of Canada | Valet API | Bank of Canada terms of use |
| Grocer annual reports (Loblaw, Metro, Empire), fiscal 2017-2025 | Companies (also on SEDAR+) | Manual extraction into `data/manual/grocer_margins.csv`, with report and page for every value | Public disclosure |
| Annual retail trade survey, supermarket gross margin (20-10-0066-01 for 2012-2021; 20-10-0083-01 for 2022 onward) | Statistics Canada | Web Data Service API (to be added to `get_data.py` in Milestone 3) | Statistics Canada Open Licence |

## Data access notes
- Raw data, clean data and the database are **not stored in this repository**. They are rebuilt by the scripts below.
- All Milestone 2 results use one **frozen snapshot downloaded on 2026-09-28** (the date is in every raw file name). Re-downloading later can change the data.
- The grocer annual report PDFs are kept locally in `data/manual/reports/` (not committed). Each value in `grocer_margins.csv` lists the report and page it comes from.

## How to run
```bash
pip install -r requirements.txt
python get_data.py      # 1. download raw data into data/raw/ (dated file names)
python clean_data.py    # 2. audit and clean -> data/clean/*.csv
python build_db.py      # 3. load clean tables into SQLite -> data/grocery.db
python eda.py           # 4. profiling charts and tables -> outputs/eda/
```

## Repository structure
```
├── README.md              Project overview (this file)
├── DECISION_LOG.md        Every major choice, the alternatives and why
├── LITERATURE_NOTES.md    Sources used to justify the method
├── requirements.txt       Python libraries needed
├── get_data.py            1. Downloads all public data and checks coverage
├── clean_data.py          2. Audits and cleans each source (look, audit, clean, verify, save)
├── build_db.py            3. Builds the SQLite database and joins CPI with the drivers
├── eda.py                 4. Data profiling: charts and tables
├── data/
│   ├── manual/grocer_margins.csv   Grocer sales and gross profit (committed)
│   ├── raw/  clean/  grocery.db    Created by the scripts (not committed)
└── outputs/
    ├── pipeline_diagram.png        Pipeline overview
    └── eda/                        6 charts and 2 tables from eda.py
```

## Use of generative AI
Generative AI (Claude, Anthropic) was used as a tutor to explain concepts and debug code, to draft documentation and report text, and to extract grocer figures from annual reports. All code was typed, run and verified by the author, and every extracted value was checked against its cited page. Detailed AI use declarations are included in each milestone report.

## Tools
Python (pandas, matplotlib) · SQL (SQLite) · Power BI · GitHub

## Project status
- [x] Milestone 1: Design & Strategy
- [x] Milestone 2: Architecture & Data Audit
- [ ] Milestone 3: Initial Results & Coding
- [ ] Milestone 4: Final Results & Report
- [ ] Milestone 5: Presentation & Demo
