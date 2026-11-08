# RQ3 models: seasonal naive baseline + 3 models (CIND820 Milestone 3)
from pathlib import Path
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

CLEAN = Path("data/clean")
OUT = Path("outputs/models")
OUT.mkdir(parents=True, exist_ok=True)

data = pd.read_csv(CLEAN / "model_table.csv", index_col="month")

# ===== Split: last 12 months = test set, never used for training =====
TEST_MONTHS = 12
train = data.iloc[:-TEST_MONTHS]
test = data.iloc[-TEST_MONTHS:]
print("Train:", train.shape, train.index.min(), "to", train.index.max())
print("Test: ", test.shape, test.index.min(), "to", test.index.max())

# ===== Baseline: seasonal naive, prediction for month t = y(t-12) =====
naive_pred = data["y"].shift(12).iloc[-TEST_MONTHS:]

results = []
mae = mean_absolute_error(test["y"], naive_pred)
rmse = mean_squared_error(test["y"], naive_pred) ** 0.5
results.append({"model": "Seasonal naive", "MAE": round(mae, 3), "RMSE": round(rmse, 3)})

print(pd.DataFrame(results))
print(pd.DataFrame({"actual": test["y"], "naive": naive_pred}).round(2))

# ===== Block 2: choose lags on training data, fit the linear regression =====
import statsmodels.api as sm

DRIVERS = ["agri_index", "energy_index", "usdcad", "policy_rate"]
chosen = []
for driver in DRIVERS:
    lag_cols = [c for c in data.columns if c.startswith(driver + "_lag")]
    corrs = train[lag_cols].corrwith(train["y"])
    best = corrs.abs().idxmax()
    chosen.append(best)
    print(driver, "->", best, "| r =", round(corrs[best], 2))

month_cols = [c for c in data.columns if c.startswith("m_")]
FEATURES = chosen + month_cols + ["covid", "ukraine"]

X_train = sm.add_constant(train[FEATURES])
X_test = sm.add_constant(test[FEATURES], has_constant="add")
linear = sm.OLS(train["y"], X_train).fit()
print(linear.summary())

linear_pred = linear.predict(X_test)
mae = mean_absolute_error(test["y"], linear_pred)
rmse = mean_squared_error(test["y"], linear_pred) ** 0.5
results.append({"model": "Linear regression", "MAE": round(mae, 3), "RMSE": round(rmse, 3)})
print(pd.DataFrame(results))

# ===== Block 3: check the regression assumptions =====
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

residuals = linear.resid
fitted = linear.fittedvalues

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
axes[0].scatter(fitted, residuals)
axes[0].axhline(0, color="grey", linestyle="--")
axes[0].set_title("Residuals vs fitted (linearity, constant variance)")
axes[0].set_xlabel("Fitted value")
axes[0].set_ylabel("Residual")
plot_acf(residuals, lags=12, ax=axes[1])
axes[1].set_title("Autocorrelation of residuals (independence)")
sm.qqplot(residuals, line="s", ax=axes[2])
axes[2].set_title("Q-Q plot (normality)")
fig.tight_layout()
fig.savefig(OUT / "linear_assumption_checks.png", dpi=150)
plt.show()

print("Durbin-Watson (about 2 = no autocorrelation):", round(durbin_watson(residuals), 2))
print("Breusch-Pagan p-value (above 0.05 = constant variance OK):", round(het_breuschpagan(residuals, X_train)[1], 3))
print("Shapiro-Wilk p-value (above 0.05 = normal residuals OK):", round(stats.shapiro(residuals).pvalue, 3))

X_drivers = sm.add_constant(train[chosen])
for i, name in enumerate(X_drivers.columns):
    if name != "const":
        print("VIF", name, round(variance_inflation_factor(X_drivers.values, i), 2))

# ===== Block 4: regression tree and random forest =====
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV

cv = TimeSeriesSplit(n_splits=5)

tree_search = GridSearchCV(DecisionTreeRegressor(random_state=42),
                           {"max_depth": [2, 3, 4], "min_samples_leaf": [3, 5, 8]},
                           cv=cv, scoring="neg_mean_absolute_error")
tree_search.fit(train[FEATURES], train["y"])
tree = tree_search.best_estimator_
print("Tree settings:", tree_search.best_params_)

tree_pred = tree.predict(test[FEATURES])
mae = mean_absolute_error(test["y"], tree_pred)
rmse = mean_squared_error(test["y"], tree_pred) ** 0.5
results.append({"model": "Regression tree", "MAE": round(mae, 3), "RMSE": round(rmse, 3)})

forest_search = GridSearchCV(RandomForestRegressor(n_estimators=300, random_state=42),
                             {"max_depth": [3, 5, None], "min_samples_leaf": [2, 5]},
                             cv=cv, scoring="neg_mean_absolute_error")
forest_search.fit(train[FEATURES], train["y"])
forest = forest_search.best_estimator_
print("Forest settings:", forest_search.best_params_)

forest_pred = forest.predict(test[FEATURES])
mae = mean_absolute_error(test["y"], forest_pred)
rmse = mean_squared_error(test["y"], forest_pred) ** 0.5
results.append({"model": "Random forest", "MAE": round(mae, 3), "RMSE": round(rmse, 3)})

comparison = pd.DataFrame(results)
comparison["better_than_baseline_%"] = ((1 - comparison["MAE"] / comparison["MAE"][0]) * 100).round(1)
print(comparison)

# ===== Block 5: save results and charts =====
from sklearn.tree import plot_tree

comparison.to_csv(OUT / "model_comparison.csv", index=False)
forecasts = pd.DataFrame({"actual": test["y"], "seasonal_naive": naive_pred,
                          "linear": linear_pred, "tree": tree_pred, "forest": forest_pred})
forecasts.round(3).to_csv(OUT / "test_forecasts.csv")
print(forecasts.round(2))

# Chart 1: actual vs the 4 forecasts
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(forecasts.index, forecasts["actual"], color="black", linewidth=2.5, marker="o", label="Actual")
for column in ["seasonal_naive", "linear", "tree", "forest"]:
    ax.plot(forecasts.index, forecasts[column], marker=".", linestyle="--", label=column)
ax.axhline(0, color="grey", linewidth=0.8)
ax.set_title("Monthly change in store-food prices: actual vs forecasts (test months)")
ax.set_ylabel("Monthly % change")
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "forecasts_vs_actual.png", dpi=150)
plt.show()

# Chart 2: which features the forest relied on
importance = pd.Series(forest.feature_importances_, index=FEATURES).sort_values().tail(8)
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(importance.index, importance.values)
ax.set_title("Random forest: feature importance (top 8)")
ax.set_xlabel("Importance (share of the forest's improvement)")
fig.tight_layout()
fig.savefig(OUT / "forest_feature_importance.png", dpi=150)
plt.show()

# Chart 3: the regression tree drawn as a diagram
fig, ax = plt.subplots(figsize=(14, 6))
plot_tree(tree, feature_names=FEATURES, filled=True, rounded=True, precision=2, ax=ax)
ax.set_title("Regression tree (depth 2)")
fig.tight_layout()
fig.savefig(OUT / "regression_tree.png", dpi=150)
plt.show()