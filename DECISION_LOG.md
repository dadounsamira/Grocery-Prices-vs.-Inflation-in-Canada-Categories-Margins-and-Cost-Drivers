# Decision Log

Every major project choice, the options considered, and why. New decisions are added at the bottom.

| # | Date | Decision | Options considered | Why | Evidence / source |
|---|---|---|---|---|---|
| 1 | 2026-09-25 | Topic: Canadian grocery prices vs. inflation | Housing affordability, labour market, commuting, credit default risk, bike share | Public, open-licence monthly data; clear decision for real users; builds on my earlier research | Dataset comparison; Statistics Canada Open Licence |
| 2 | 2026-09-25 | Treat "greedflation" as a hypothesis to test, not the conclusion | Start from greedflation as the thesis | Price tables do not contain margins; starting from a conclusion would bias the analysis | Course slide 8 ("avoid RQs unsupported by the data") |
| 3 | 2026-09-25 | Add grocer financial reports as a data source (RQ2) | Prices only | Public margins allow a timing comparison between margins and prices | Competition Bureau (2023) grocery study; SEDAR+ filings |
| 4 | 2026-09-25 | Fold wars, policy and oil into RQ3 instead of a separate RQ4 | Separate fourth research question | Course asks for three connected RQs; drivers fit naturally as model inputs | Course slide 8 |
| 5 | 2026-09-25 | Provinces as the geographic unit | National only; cities | Both core tables cover all provinces; city detail is limited | Table 18-10-0004-01 geography |
| 6 | 2026-09-25 | January 2019 as the comparison start | 2017 (retail price table start); 2020 | Pre-pandemic baseline before the 2021+ price surge | — |
| 7 | 2026-09-25 | Python only, not R | R; Python and R together | Course allows either; Python covers every step; one language keeps the pipeline simpler and reproducible | Course description |
| 8 | 2026-09-25 | SQLite for data storage | PostgreSQL | Built into Python, no server setup, one file; data volume is modest | — |
| 9 | 2026-09-25 | Power BI for the dashboard | Streamlit; Tableau | Widely used in analyst roles; I want to learn it; runs on my Windows laptop | — |
| 10 | 2026-09-25 | Interpretable models only (no black box) | Complex machine-learning models | Course requires transparent, explainable methods | Course description; slide 4 |
| 11 | 2026-09-26 | Final model choice made in M2; only the seasonal naive baseline fixed in M1 | Choose SARIMAX in M1 | Course: define the problem before the model; compare approaches in M2 | Course slides 9 and 24 |
| 12 | 2026-09-26 | Download and check the data during M1 | Download in M2 | Confirm variables and coverage exist before finalizing RQs | Course slide 17 ("inspect the dataset before finalizing your project question") |
| 13 | 2026-09-26 | One download method per source (StatCan Web Data Service, Bank of Canada Valet API, SEDAR+) | Manual CSV downloads | Scripted downloads are reproducible and record the download date | — |
| 14 | 2026-09-26 | Project title: "Grocery Prices vs. Inflation in Canada: Categories, Margins and Cost Drivers" | Four other titles | Accurate, professional, does not assume the answer | — |
| 15 | 2026-09-26 | GitHub as the single home for code, the decision log and documentation | Local folders; Azure virtual desktop only | Version history, visible to instructor, reproducible | Course slides 15 and 19 |
| 16 | 2026-09-26 | Keep the detailed GenAI log private; short AI disclosure in the public README | Public GENAI_LOG.md in the repository | Detailed declarations go in each milestone report (seen by the instructor); a short public note is standard practice on GitHub; TMU leaves the format to the instructor | TMU Academic Integrity Office AI FAQs |
| 17 | 2026-09-28 | Annual grocer gross margins, stored as sales and gross profit in data/manual/grocer_margins.csv; margin computed in Python | Quarterly margins; typing the percentages | About 15 annual reports instead of about 110 quarterly ones; copying only printed values avoids hand-calculation errors and treats all three companies the same way. Trade-off: about 9 points per company, so RQ2 trends are described, not statistically tested | Loblaw, Metro and Empire 2025 annual reports |