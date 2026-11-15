# M4: rolling-origin evaluation, timing and model comparison (CIND820 Milestone 4)
from pathlib import Path
import time  ## M4: rolling-origin evaluation, timing and model comparison (CIND820 Milestone 4)
from pathlib import Path
import time

import pandas as pd
import statsmodels.api as sm
from scipy import stats  #statistical tests, to check if one model is really better than another
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.tree import DecisionTreeRegressor

CLEAN = Path("data/clean")
OUT = Path("outputs/evaluation")
OUT.mkdir(parents=True, exist_ok=True)

DRIVERS = ["agri_index", "energy_index", "usdcad", "policy_rate"]
TEST_MONTHS = 12
N_WINDOWS = 4

data = pd.read_csv(CLEAN / "model_table.csv", index_col="month")
MONTH_COLS = [c for c in data.columns if c.startswith("m_")]


def choose_lags(train):
    """For each driver, keep the lag most correlated with y, using the training months only."""
    chosen = []
    for driver in DRIVERS:
        lag_cols = [c for c in train.columns if c.startswith(driver + "_lag")]
        corrs = train[lag_cols].corrwith(train["y"])
        chosen.append(corrs.abs().idxmax())
    return chosen

import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.tree import DecisionTreeRegressor

CLEAN = Path("data/clean")
OUT = Path("outputs/evaluation")
OUT.mkdir(parents=True, exist_ok=True)

DRIVERS = ["agri_index", "energy_index", "usdcad", "policy_rate"]
TEST_MONTHS = 12
N_WINDOWS = 4

data = pd.read_csv(CLEAN / "model_table.csv", index_col="month")
MONTH_COLS = [c for c in data.columns if c.startswith("m_")]


def choose_lags(train):
    """For each driver, keep the lag most correlated with y, using the training months only."""
    chosen = []
    for driver in DRIVERS:
        lag_cols = [c for c in train.columns if c.startswith(driver + "_lag")]
        corrs = train[lag_cols].corrwith(train["y"])
        chosen.append(corrs.abs().idxmax())
    return chosen


def seasonal_naive(train, test, features):
    """Forecast each test month with the actual change in the same month one year earlier."""
    return data["y"].shift(12).loc[test.index]


def linear_regression(train, test, features):
    """Fit OLS on the training months and forecast the test months."""
    model = sm.OLS(train["y"], sm.add_constant(train[features])).fit()
    return model.predict(sm.add_constant(test[features], has_constant="add"))


def tuned_tree(train, test, features):
    """Tune a regression tree with time-series cross-validation, then forecast."""
    search = GridSearchCV(DecisionTreeRegressor(random_state=42),
                          {"max_depth": [2, 3, 4], "min_samples_leaf": [3, 5, 8]},
                          cv=TimeSeriesSplit(n_splits=5), scoring="neg_mean_absolute_error")
    search.fit(train[features], train["y"])
    return search.best_estimator_.predict(test[features])


def tuned_forest(train, test, features):
    """Tune a random forest with time-series cross-validation, then forecast."""
    search = GridSearchCV(RandomForestRegressor(n_estimators=300, random_state=42),
                          {"max_depth": [3, 5, None], "min_samples_leaf": [2, 5]},
                          cv=TimeSeriesSplit(n_splits=5), scoring="neg_mean_absolute_error")
    search.fit(train[features], train["y"])
    return search.best_estimator_.predict(test[features])


MODELS = {"Seasonal naive": seasonal_naive, "Linear regression": linear_regression,
          "Regression tree": tuned_tree, "Random forest": tuned_forest}


scores = []
forecasts = []
for w in range(N_WINDOWS):
    test_end = len(data) - (N_WINDOWS - 1 - w) * TEST_MONTHS
    test_start = test_end - TEST_MONTHS
    train = data.iloc[:test_start]
    test = data.iloc[test_start:test_end]
    lags = choose_lags(train)
    features = lags + MONTH_COLS + ["covid", "ukraine"]
    print(f"Window {w + 1}: train {train.index[0]} to {train.index[-1]} ({len(train)} months),",
          f"test {test.index[0]} to {test.index[-1]} | lags: {lags}")
    for name, model in MODELS.items():
        start = time.perf_counter()
        pred = model(train, test, features)
        seconds = time.perf_counter() - start
        scores.append({"window": w + 1, "model": name,
                       "MAE": mean_absolute_error(test["y"], pred),
                       "RMSE": mean_squared_error(test["y"], pred) ** 0.5,
                       "seconds": seconds})
        forecasts.append(pd.DataFrame({"window": w + 1, "model": name,
                                       "actual": test["y"], "forecast": list(pred)}))

scores = pd.DataFrame(scores)
forecasts = pd.concat(forecasts)
print(scores.round(3))


# ===== Block 4: summarize stability, efficiency and test the differences =====
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)

mae_table = scores.pivot(index="window", columns="model", values="MAE")
summary = scores.groupby("model").agg(MAE_mean=("MAE", "mean"), MAE_std=("MAE", "std"),
                                      RMSE_mean=("RMSE", "mean"), seconds_mean=("seconds", "mean"))
baseline_mae = mae_table["Seasonal naive"]
summary["windows_beating_baseline"] = [(mae_table[m] < baseline_mae).sum() for m in summary.index]
summary["better_than_baseline_%"] = (1 - summary["MAE_mean"] / summary.loc["Seasonal naive", "MAE_mean"]) * 100
print(mae_table.round(3))
print(summary.round(3))

errors = forecasts.assign(abs_error=(forecasts["actual"] - forecasts["forecast"]).abs())
abs_errors = errors.reset_index().pivot_table(index=["window", "month"], columns="model", values="abs_error")
tests = []
for name in ["Linear regression", "Regression tree", "Random forest"]:
    t_stat, p_value = stats.ttest_rel(abs_errors["Seasonal naive"], abs_errors[name])
    tests.append({"model": name, "mean_error_reduction": (abs_errors["Seasonal naive"] - abs_errors[name]).mean(),
                  "t": t_stat, "p_value": p_value, "months": len(abs_errors)})
tests = pd.DataFrame(tests)
print(tests.round(3))

scores.round(4).to_csv(OUT / "rolling_scores.csv", index=False)
summary.round(4).to_csv(OUT / "rolling_summary.csv")
tests.round(4).to_csv(OUT / "model_tests.csv", index=False)
forecasts.round(4).to_csv(OUT / "rolling_forecasts.csv")