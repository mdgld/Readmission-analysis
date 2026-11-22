"""Rebuild the five full-cohort predictive-model gallery figures.

This module mirrors the July 2026 `Readmission_ML_A_Models.ipynb` estimand:
2,652 children, ACE imputed with iterative random-forest imputation, and 10-fold
out-of-fold predictions. It writes aggregate plots only.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import statsmodels.api as sm
from catboost import CatBoostClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from matplotlib.ticker import PercentFormatter
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

SEED = 42
INK, MUTED, RULE, PAPER = "#182e2c", "#536661", "#d5ddd6", "#fffefa"
TEAL, GREEN, GREEN_SOFT, TERRACOTTA, ROSE = (
    "#12655e",
    "#4d7c68",
    "#91ad9e",
    "#985037",
    "#c98f79",
)

FEATURE_LABELS = {
    "age": "Age at admission",
    "gender_male": "Male gender identity",
    "insurance_public": "AHCCCS recorded",
    "ace_score": "ACE score",
    "had_restraints": "Physical restraint use",
    "csrss_any": "Any C-SSRS flag",
    "los_days": "Length of stay",
    "n_dsm5_categories": "Distinct diagnostic categories",
    "has_medical_comorbidity": "Medical comorbidity",
    "has_nssi": "Self-injury code group",
    "has_trauma": "Trauma/stressor disorders",
    "has_adhd": "ADHD",
    "has_asd": "Autism spectrum disorder",
    "has_conduct": "Conduct disorder",
    "has_depression": "Depressive disorders",
    "has_anxiety": "Anxiety disorders",
    "has_bipolar": "Bipolar disorders",
    "has_psychotic": "Psychotic disorders",
    "has_suicidal_ideation": "Suicidal ideation (R45.851)",
    "has_neurocognitive": "Neurocognitive/organic code",
    "complexity_x_age": "Age × diagnostic complexity",
    "ace_x_csrss": "ACE score × C-SSRS flag",
    "medical_x_los": "Medical comorbidity × length of stay",
}
BASE_FEATURES = list(FEATURE_LABELS)[:20]
INTERACTIONS = ["complexity_x_age", "ace_x_csrss", "medical_x_los"]
MODEL_FEATURES = BASE_FEATURES + INTERACTIONS

MODEL_COLORS = {
    "Logistic regression": TEAL,
    "Random forest": GREEN,
    "Random forest with SMOTE": GREEN_SOFT,
    "CatBoost numerical": TERRACOTTA,
    "CatBoost native categorical": ROSE,
}


def _configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 16,
            "axes.titleweight": "semibold",
            "axes.labelcolor": MUTED,
            "axes.edgecolor": RULE,
            "axes.facecolor": PAPER,
            "figure.facecolor": PAPER,
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": INK,
            "grid.color": RULE,
            "savefig.facecolor": PAPER,
            "savefig.bbox": "tight",
            "savefig.dpi": 180,
        }
    )


def _category_count(row: pd.Series) -> int:
    categories: set[str] = set()
    for column in ["VisitDiags_DSM5Categories", "ChronicDiags_DSM5Categories"]:
        value = row.get(column, "")
        if pd.notna(value) and str(value).strip():
            categories.update(part.strip() for part in str(value).split(";") if part.strip())
    return len(categories)


def _prepare(analysis_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    source = analysis_dir / "data" / "annotated_psychiatric_data_complete.csv"
    data = pd.read_csv(source, low_memory=False)
    if data["MRN"].isna().any() or not data["MRN"].is_unique:
        raise ValueError("The model requires exactly one row per child.")

    data["readmitted"] = (data["Readmissions"].fillna(0) > 0).astype(int)
    data["age"] = pd.to_numeric(data["Pt_Age_Visit"], errors="coerce")
    data["gender_male"] = (
        data["GenderCode"].astype(str).str.strip().str.lower() == "male"
    ).astype(int)
    data["insurance_public"] = data["Insurance"].astype(str).str.contains(
        "AHCCCS", case=False, na=False
    ).astype(int)
    data["ace_score"] = pd.to_numeric(data["ACEscore"], errors="coerce")
    data["had_restraints"] = (
        pd.to_numeric(data["restraints"], errors="coerce").fillna(0) > 0
    ).astype(int)
    data["csrss_yellow"] = data["Yellow flags (C-SRSS)"].notna().astype(int)
    data["csrss_orange"] = data["Orange flags (C-SSRS)"].notna().astype(int)
    data["csrss_red"] = data["Red flags (C-SSRS)"].notna().astype(int)
    data["csrss_any"] = (
        data[["csrss_yellow", "csrss_orange", "csrss_red"]].sum(axis=1) > 0
    ).astype(int)

    visit = pd.to_datetime(data["VisitDate"], errors="coerce", format="mixed")
    discharge = pd.to_datetime(data["DischDate"], errors="coerce", format="mixed")
    data["los_days"] = (discharge - visit).dt.days
    invalid = visit.isna() | discharge.isna() | data["los_days"].lt(0)
    data = data.loc[~invalid].copy().reset_index(drop=True)
    data["n_dsm5_categories"] = data.apply(_category_count, axis=1)

    category_text = (
        data["VisitDiags_DSM5Categories"].fillna("")
        + ";"
        + data["ChronicDiags_DSM5Categories"].fillna("")
    ).str.lower()
    flags = {
        "has_nssi": "non-suicidal self-injury",
        "has_trauma": "trauma and stressor",
        "has_adhd": "adhd",
        "has_asd": "autism spectrum",
        "has_conduct": "conduct disorder",
        "has_depression": "depressive disorders",
        "has_anxiety": "anxiety disorders",
        "has_bipolar": "bipolar",
        "has_psychotic": "psychotic",
    }
    for column, phrase in flags.items():
        data[column] = category_text.str.contains(phrase, na=False, regex=False).astype(int)

    allowed_medical_chapters = frozenset("CDEGHIJKLMNQ")
    data["has_medical_comorbidity"] = data["ChronicDiags"].fillna("").apply(
        lambda value: int(
            any(
                token.strip().upper()[0] in allowed_medical_chapters
                for token in str(value).split(",")
                if token.strip()
            )
        )
    )
    all_codes = (
        data["VisitDiags"].fillna("")
        + ","
        + data["NonSuicidialDiags"].fillna("")
        + ","
        + data["ChronicDiags"].fillna("")
    ).str.upper()
    data["has_suicidal_ideation"] = all_codes.str.contains(
        "R45.851", regex=False
    ).astype(int)
    neuro_codes = ["F02.80", "F0280", "F03.91", "F0391", "F05", "F07.81", "F0781", "F09"]
    data["has_neurocognitive"] = (
        category_text.str.contains("neurocognitive", na=False, regex=False)
        | all_codes.apply(lambda value: any(code in value for code in neuro_codes))
    ).astype(int)

    model = data[BASE_FEATURES + ["readmitted"]].copy()
    imputer = IterativeImputer(
        estimator=RandomForestRegressor(n_estimators=50, random_state=SEED),
        max_iter=10,
        random_state=SEED,
    )
    model[["age", "ace_score", "los_days"]] = imputer.fit_transform(
        model[["age", "ace_score", "los_days"]]
    )
    model = model.dropna().reset_index(drop=True)
    raw = model.copy()

    scale_columns = ["age", "los_days", "ace_score", "n_dsm5_categories"]
    model[scale_columns] = StandardScaler().fit_transform(model[scale_columns])
    model["complexity_x_age"] = model["n_dsm5_categories"] * model["age"]
    model["ace_x_csrss"] = model["ace_score"] * model["csrss_any"]
    model["medical_x_los"] = model["has_medical_comorbidity"] * model["los_days"]
    raw["complexity_x_age"] = raw["n_dsm5_categories"] * raw["age"]
    raw["ace_x_csrss"] = raw["ace_score"] * raw["csrss_any"]
    raw["medical_x_los"] = raw["has_medical_comorbidity"] * raw["los_days"]
    model[INTERACTIONS] = StandardScaler().fit_transform(model[INTERACTIONS])

    native_columns = raw[BASE_FEATURES].copy()
    native_categorical = [
        "gender_male",
        "insurance_public",
        "had_restraints",
        "csrss_any",
        "has_medical_comorbidity",
        *[column for column in BASE_FEATURES if column.startswith("has_") and column != "has_medical_comorbidity"],
    ]
    for column in native_categorical:
        native_columns[column] = native_columns[column].astype(str)
    return raw, native_columns, model[MODEL_FEATURES].to_numpy(), model["readmitted"].to_numpy()


def _catboost(*, categorical: list[int] | None = None) -> CatBoostClassifier:
    return CatBoostClassifier(
        iterations=500,
        depth=4,
        learning_rate=0.05,
        auto_class_weights="Balanced",
        eval_metric="AUC",
        random_seed=SEED,
        verbose=0,
        cat_features=categorical,
        allow_writing_files=False,
        thread_count=-1,
    )


def _fit_predictions(
    x: np.ndarray, native: pd.DataFrame, y: np.ndarray
) -> tuple[dict[str, np.ndarray], dict[str, object], list[int]]:
    probabilities = {name: np.zeros(len(y)) for name in MODEL_COLORS}
    categorical_names = [
        "gender_male",
        "insurance_public",
        "had_restraints",
        "csrss_any",
        "has_medical_comorbidity",
        *[column for column in BASE_FEATURES if column.startswith("has_") and column != "has_medical_comorbidity"],
    ]
    categorical_indices = [native.columns.get_loc(column) for column in categorical_names]
    native_values = native.to_numpy()
    cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=SEED)
    for train, test in cv.split(x, y):
        logistic = sm.Logit(
            y[train], sm.add_constant(x[train], has_constant="add")
        ).fit(disp=0, maxiter=200)
        probabilities["Logistic regression"][test] = logistic.predict(
            sm.add_constant(x[test], has_constant="add")
        )

        forest = RandomForestClassifier(
            n_estimators=500,
            max_depth=6,
            min_samples_leaf=10,
            class_weight="balanced",
            random_state=SEED,
            n_jobs=-1,
        )
        forest.fit(x[train], y[train])
        probabilities["Random forest"][test] = forest.predict_proba(x[test])[:, 1]

        smote_forest = ImbPipeline(
            [
                ("smote", SMOTE(random_state=SEED)),
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=500,
                        max_depth=6,
                        min_samples_leaf=10,
                        random_state=SEED,
                        n_jobs=-1,
                    ),
                ),
            ]
        )
        smote_forest.fit(x[train], y[train])
        probabilities["Random forest with SMOTE"][test] = smote_forest.predict_proba(x[test])[:, 1]

        numerical_catboost = _catboost()
        numerical_catboost.fit(x[train], y[train])
        probabilities["CatBoost numerical"][test] = numerical_catboost.predict_proba(x[test])[:, 1]

        native_catboost = _catboost(categorical=categorical_indices)
        native_catboost.fit(native_values[train], y[train])
        probabilities["CatBoost native categorical"][test] = native_catboost.predict_proba(native_values[test])[:, 1]

    forest_full = RandomForestClassifier(
        n_estimators=500,
        max_depth=6,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
    ).fit(x, y)
    native_full = _catboost(categorical=categorical_indices)
    native_full.fit(native_values, y)
    return probabilities, {"Random forest": forest_full, "CatBoost": native_full}, categorical_indices


def _clean(axis: plt.Axes) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(alpha=0.7)
    axis.set_axisbelow(True)


def _plot_roc(y: np.ndarray, probabilities: dict[str, np.ndarray], output: Path) -> None:
    figure, axis = plt.subplots(figsize=(8.4, 7.2))
    for name, values in probabilities.items():
        false_positive, true_positive, _ = roc_curve(y, values)
        axis.plot(
            false_positive,
            true_positive,
            lw=2.2,
            color=MODEL_COLORS[name],
            label=f"{name} · AUC {roc_auc_score(y, values):.3f}",
        )
    axis.plot([0, 1], [0, 1], color=MUTED, ls=(0, (4, 3)), lw=1.2, label="Chance")
    axis.set(xlabel="False-positive rate", ylabel="True-positive rate", xlim=(0, 1), ylim=(0, 1))
    axis.set_title("ROC curves for held-out predictions", loc="left", pad=25)
    axis.text(0, 1.02, f"10-fold cross-validation · full cohort · n={len(y):,}", transform=axis.transAxes, color=MUTED)
    axis.legend(frameon=False, loc="lower right", fontsize=8.8)
    _clean(axis)
    figure.savefig(output / "Fig8_ROC_curves.png")
    plt.close(figure)


def _plot_calibration(y: np.ndarray, probabilities: dict[str, np.ndarray], output: Path) -> None:
    selected = ["CatBoost numerical", "Random forest", "Logistic regression"]
    figure, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    axes[0].plot([0, 1], [0, 1], color=MUTED, ls=(0, (4, 3)), lw=1.2, label="Perfect calibration")
    for name in selected:
        values = probabilities[name]
        observed, predicted = calibration_curve(y, values, n_bins=10, strategy="quantile")
        axes[0].plot(predicted, observed, "o-", lw=2, ms=5, color=MODEL_COLORS[name], label=f"{name} · Brier {brier_score_loss(y, values):.3f}")
        axes[1].hist(values, bins=40, alpha=0.42, density=True, color=MODEL_COLORS[name], label=name)
    axes[0].axhline(y.mean(), color=INK, ls=(0, (2, 3)), lw=1, label=f"Observed rate · {y.mean():.1%}")
    axes[0].set(xlabel="Mean predicted probability", ylabel="Observed readmission rate", title="Reliability diagram")
    axes[1].axvline(y.mean(), color=INK, ls=(0, (4, 3)), lw=1.2, label=f"Observed rate · {y.mean():.1%}")
    axes[1].set(xlabel="Predicted probability", ylabel="Density", title="Prediction distributions")
    for axis in axes:
        axis.legend(frameon=False, fontsize=8.2)
        _clean(axis)
    figure.suptitle("Calibration of held-out predictions", x=0.07, ha="left", fontsize=16, fontweight="semibold")
    figure.text(0.07, 0.91, f"10-fold cross-validation · full cohort · n={len(y):,}", color=MUTED)
    figure.subplots_adjust(top=0.8, wspace=0.3)
    figure.savefig(output / "Fig_Calibration.png")
    plt.close(figure)


def _crossover(y: np.ndarray, values: np.ndarray, maximum: float) -> dict:
    thresholds = np.linspace(0.01, maximum, 400)
    rows = []
    for threshold in thresholds:
        prediction = values >= threshold
        _, false_positive, false_negative, _ = confusion_matrix(y, prediction).ravel()
        rows.append((threshold, false_positive, false_negative))
    threshold, false_positive, false_negative = min(rows, key=lambda row: abs(row[1] - row[2]))
    return {"threshold": float(threshold), "false_positive": int(false_positive), "false_negative": int(false_negative)}


def _plot_thresholds(y: np.ndarray, probabilities: dict[str, np.ndarray], output: Path) -> dict:
    configs = [
        ("CatBoost numerical", 0.65),
        ("Random forest", 0.60),
        ("Logistic regression", 0.50),
    ]
    major_thresholds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60]
    figure, axes = plt.subplots(2, 3, figsize=(15, 8.5), sharex=True)
    crossovers = {}
    maximum_workload = 0.0
    for column, (name, maximum) in enumerate(configs):
        values = probabilities[name]
        closest = _crossover(y, values, maximum)
        crossovers[name] = closest
        thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
        thresholds += [value for value in [0.55, 0.60, 0.65] if value <= maximum]
        metrics = []
        for threshold in thresholds:
            prediction = values >= threshold
            _, false_positive, false_negative, true_positive = confusion_matrix(y, prediction).ravel()
            metrics.append(
                (
                    100 * prediction.mean(),
                    100 * true_positive / (true_positive + false_negative),
                    100 * true_positive / (true_positive + false_positive) if prediction.any() else np.nan,
                )
            )
        workload, sensitivity, precision = np.asarray(metrics).T
        workload_axis, performance_axis = axes[:, column]
        bars = workload_axis.bar(thresholds, workload, width=0.031, color=MODEL_COLORS[name], alpha=0.82)
        maximum_workload = max(maximum_workload, float(workload.max()))
        # Label the main ticks to keep the narrow bars legible at nearby thresholds.
        workload_labels = [
            ("<1%" if 0 < rate < 1 else f"{rate:.0f}%") if threshold in major_thresholds
            else ""
            for threshold, rate in zip(thresholds, workload)
        ]
        workload_axis.bar_label(bars, labels=workload_labels, padding=3, fontsize=8)
        workload_axis.axhline(
            100 * y.mean(), color=INK, ls=(0, (4, 3)), lw=1, zorder=1,
            label=f"Observed cohort readmission rate ({y.mean():.1%})",
        )
        for axis in axes[:, column]:
            axis.axvline(
                closest["threshold"],
                color="#704c75",
                ls=(0, (2, 2)),
                lw=1.5,
                label="Closest false-positive and false-negative counts",
            )
            _clean(axis)
        workload_axis.set_title(name, loc="left", pad=23)
        workload_axis.text(
            0, 1.03,
            f"{closest['threshold']:.1%} · {closest['false_positive']} false alarms, "
            f"{closest['false_negative']} missed readmissions",
            transform=workload_axis.transAxes, fontsize=9, color=MUTED,
        )
        if column == 0:
            workload_axis.set_ylabel("Children flagged (%)")
            performance_axis.set_ylabel("Percent")
        performance_axis.plot(thresholds, sensitivity, "o-", color=TEAL, label="Sensitivity")
        performance_axis.plot(thresholds, precision, "s--", color=TERRACOTTA, label="Positive predictive value")
        performance_axis.set(
            xlabel="Risk-score threshold", xlim=(0.025, 0.68), ylim=(0, 100),
            xticks=major_thresholds,
        )
        performance_axis.xaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    for axis in axes[0]:
        axis.set_ylim(0, min(110, maximum_workload + 10))
    handles, labels = axes[0, 0].get_legend_handles_labels()
    for handle, label in zip(*axes[1, 0].get_legend_handles_labels()):
        if label not in labels:
            handles.append(handle)
            labels.append(label)
    figure.suptitle("Flagging workload and detection across thresholds", x=0.07, ha="left", fontsize=16, fontweight="semibold")
    figure.text(0.07, 0.932, f"Held-out predictions · full cohort · n={len(y):,}", color=MUTED)
    figure.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.065, 0.916),
                  ncols=4, frameon=False, fontsize=9)
    figure.subplots_adjust(left=0.07, right=0.98, top=0.8, hspace=0.19, wspace=0.19)
    figure.savefig(output / "Fig14_flagging_thresholds.png")
    plt.close(figure)
    return crossovers


def _plot_importance(models: dict[str, object], output: Path) -> dict[str, list[str]]:
    forest_values = np.asarray(models["Random forest"].feature_importances_)
    cat_values = np.asarray(models["CatBoost"].get_feature_importance(type="PredictionValuesChange"))
    settings = [
        ("Random forest", forest_values, MODEL_FEATURES, "Mean decrease in impurity"),
        ("CatBoost", cat_values, BASE_FEATURES, "PredictionValuesChange"),
    ]
    figure, axes = plt.subplots(1, 2, figsize=(13.5, 6.7))
    top = {}
    for axis, (name, values, columns, measure) in zip(axes, settings):
        order = np.argsort(values)[-15:]
        labels = [FEATURE_LABELS[columns[index]] for index in order]
        axis.barh(labels, values[order], color=GREEN if name == "Random forest" else ROSE)
        axis.set(xlabel=measure, title=name)
        _clean(axis)
        top[name] = [FEATURE_LABELS[columns[index]] for index in order[::-1]]
    figure.suptitle("How the fitted tree models used recorded features", x=0.07, ha="left", fontsize=16, fontweight="semibold")
    figure.text(0.07, 0.91, "Full-cohort fits · importance scales differ between models", color=MUTED)
    figure.subplots_adjust(left=0.24, right=0.98, top=0.82, wspace=0.55)
    figure.savefig(output / "Fig9_Feature_Importance_SideBySide.png")
    plt.close(figure)
    return top


def _plot_shap(
    raw: pd.DataFrame,
    native: pd.DataFrame,
    model: CatBoostClassifier,
    output: Path,
) -> list[str]:
    shap_values = np.asarray(shap.TreeExplainer(model).shap_values(native.to_numpy()))
    mean_absolute = np.abs(shap_values).mean(axis=0)
    order = np.argsort(mean_absolute)[-12:]
    display = raw[BASE_FEATURES].rename(columns=FEATURE_LABELS)
    shap.summary_plot(
        shap_values,
        display,
        feature_names=[FEATURE_LABELS[column] for column in BASE_FEATURES],
        max_display=12,
        show=False,
        alpha=0.5,
        plot_size=(9.4, 7.2),
        rng=SEED,
    )
    figure = plt.gcf()
    axis = plt.gca()
    axis.set_xlabel("Signed SHAP contribution to the CatBoost score")
    axis.set_title("Direction and spread of CatBoost contributions", loc="left", pad=24)
    figure.savefig(output / "Fig10_SHAP_summary.png")
    plt.close(figure)
    return [FEATURE_LABELS[BASE_FEATURES[index]] for index in order[::-1]]


def build_broad_figures(analysis_dir: Path, output: Path) -> dict:
    """Rebuild the five figures and return aggregate verification evidence."""
    analysis_dir, output = Path(analysis_dir), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    _configure_style()
    raw, native, x, y = _prepare(analysis_dir)
    if len(y) != 2_652 or int(y.sum()) != 246:
        raise RuntimeError(
            f"Full-cohort check failed before fitting: n={len(y):,}, events={int(y.sum()):,}"
        )
    probabilities, models, _ = _fit_predictions(x, native, y)

    aucs = {name: roc_auc_score(y, values) for name, values in probabilities.items()}
    expected = {
        "Logistic regression": 0.683,
        "Random forest": 0.691,
        "Random forest with SMOTE": 0.684,
        "CatBoost numerical": 0.648,
        "CatBoost native categorical": 0.669,
    }
    for name, expected_auc in expected.items():
        if round(aucs[name], 3) != expected_auc:
            raise RuntimeError(f"{name} AUC changed: {aucs[name]:.6f}")

    _plot_roc(y, probabilities, output)
    _plot_calibration(y, probabilities, output)
    crossovers = _plot_thresholds(y, probabilities, output)
    importance = _plot_importance(models, output)
    shap_order = _plot_shap(raw, native, models["CatBoost"], output)

    files = [
        "Fig8_ROC_curves.png",
        "Fig9_Feature_Importance_SideBySide.png",
        "Fig10_SHAP_summary.png",
        "Fig14_flagging_thresholds.png",
        "Fig_Calibration.png",
    ]
    for name in files:
        path = output / name
        if not path.exists() or path.stat().st_size < 20_000:
            raise RuntimeError(f"Missing or unexpectedly small figure: {path}")
    return {
        "sample_n": len(y),
        "readmitted_n": int(y.sum()),
        "readmission_rate": float(y.mean()),
        "auc": aucs,
        "average_precision": {name: average_precision_score(y, values) for name, values in probabilities.items()},
        "brier": {
            name: brier_score_loss(y, probabilities[name])
            for name in ["Logistic regression", "Random forest", "CatBoost numerical"]
        },
        "fp_fn_crossovers": crossovers,
        "top_features": importance,
        "catboost_mean_absolute_shap_order": shap_order,
        "files": files,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_broad_figures(args.analysis, args.output), indent=2))


if __name__ == "__main__":
    main()
