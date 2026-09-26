# Grocery Prices vs. Inflation in Canada: Categories, Margins and Cost Drivers

**CIND820 Big Data Analytics Capstone, Toronto Metropolitan University, Fall 2026**
Author: Samira Dadoun

## Project summary
Food prices in Canada rose sharply after 2021. This project uses public data to answer:

1. **RQ1:** Which food categories and provinces saw prices rise faster than all-items CPI since January 2019?
2. **RQ2:** Did grocery retailers' gross margins rise over the same periods that food prices outpaced overall inflation?
3. **RQ3:** How much of food inflation is associated with energy prices, the USD/CAD exchange rate and interest rates, and can a model using these factors forecast food inflation better than a simple baseline?

**Intended users:** consumer-advocacy groups and public-policy analysts who monitor food affordability.

## Data sources
| Dataset | Publisher | Access | Licence |
|---|---|---|---|
| Monthly average retail prices for selected products (18-10-0245-01) | Statistics Canada | Web Data Service API | Statistics Canada Open Licence |
| Consumer Price Index, monthly, not seasonally adjusted (18-10-0004-01) | Statistics Canada | Web Data Service API | Statistics Canada Open Licence |
| Policy rate, USD/CAD exchange rate, commodity price index | Bank of Canada | Valet API | Bank of Canada terms of use |
| Grocer financial reports (Loblaw, Metro, Empire) | Companies, via SEDAR+ | Manual extraction | Public disclosure |

Raw data is **not stored in this repository**. Run `get_data.py` to download it.

## How to run
```bash
pip install -r requirements.txt
python get_data.py
```
This downloads the raw files into `data/raw/` (with the download date in each file name) and writes a coverage report to `data/coverage_report.txt`.

## Repository structure
```
├── README.md            Project overview (this file)
├── DECISION_LOG.md      Every major choice and why it was made
├── requirements.txt     Python libraries needed
├── get_data.py          Downloads all public data and checks coverage
└── data/                Created by get_data.py (raw files are not committed)
```

## Use of generative AI
Generative AI (Claude, Anthropic) was used to support planning, explain code and review drafts. All code in this repository was written, tested and verified by the author. Detailed AI use declarations are included in each milestone report.

## Tools
Python · SQL (SQLite) · Power BI · GitHub

## Project status
- [ ] Milestone 1: Design & Strategy
- [ ] Milestone 2: Architecture & Data Audit
- [ ] Milestone 3: Initial Results & Coding
- [ ] Milestone 4: Final Results & Report
- [ ] Milestone 5: Presentation & Demo
