# Coding Assistance Declaration (Milestone 3)

This declaration covers AI coding assistance only. The use of generative AI for writing is declared separately in the GenAI statement of each milestone report.

## Tool used
Claude (Anthropic), used through the Claude app as a chat-based coding tutor. No code-completion extension (such as GitHub Copilot) was installed in PyCharm.

## How it was used
- **Learning:** I asked it to explain each new concept before coding it (monthly target, lags, train/test split in time, regression assumptions, VIF, regression trees, random forests, `TimeSeriesSplit` and `GridSearchCV`).
- **Code proposals:** it proposed the code for each step in small blocks (Blocks A–D in `model_data.py`, Blocks 1–5 in `models.py`, the RQ1/RQ2 blocks in `results_rq1_rq2.py`), each with a line-by-line explanation.
- **Manual coding:** I typed every block myself in PyCharm, ran it, and committed each task separately. Typing the code instead of pasting it kept my Python skills active and made me read every line.
- **Debugging:** when something failed (for example `ModuleNotFoundError: sklearn`, a script pausing at `plt.show()`, an overlapping chart legend), I shared the error or screenshot and fixed it after the explanation.
- **Notebook:** `M3_initial_results.ipynb` assembles the same code from the three scripts in order, with explanations, plus one descriptive-statistics cell (histogram, boxplot, variance, mode) proposed by the assistant. It was executed end to end and exported to `M3_initial_results.html`.

## How prompts were refined
I asked for one idea at a time and for plain-language explanations; when an answer was unclear I asked follow-up questions (for example "what do you mean by lags?", "why is farm 9 months and energy 12?", "what does this block really do?") until I could explain the step myself.

## How outputs were verified
- Every block printed checks that I compared with expected values: table shapes (86 months x 42 columns), date ranges, 0 missing values, event month counts (4 and 11), train/test sizes (74 and 12).
- Leakage was checked by design: lags and model settings chosen on training months only; the 12 test months used once.
- Results were checked against charts and tables; I corrected an AI description of the RQ1 fish results that did not match the heatmap.
- The full pipeline was re-run from the clean data in a separate environment and reproduced exactly the same `model_comparison.csv`, `test_forecasts.csv` and RQ1/RQ2 tables.

## Accountability
I can explain, run and debug every step of this milestone's code without assistance.
