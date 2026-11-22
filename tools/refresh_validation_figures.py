"""Build the three validation gallery figures from verified aggregate tables.

This script intentionally reads no patient-level records. Its inputs are the aggregate
tables produced by the canonical July validation notebook and the portfolio data file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from refresh_portfolio_figures import (
    GOLD,
    INK,
    MUTED,
    RULE,
    TEAL,
    TERRACOTTA,
    build_ceiling,
    clean_axis,
    configure_matplotlib,
)

TEAL_SOFT = "#8fb9b1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data.json"))
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Directory containing the canonical aggregate validation CSV files",
    )
    parser.add_argument("--output", type=Path, default=Path("assets/figures"))
    return parser.parse_args()


def load_and_verify(source: Path, data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    subgroup = pd.read_csv(source / "AdvStats_fairness_subgroups.csv", index_col=0)
    validation = pd.read_csv(source / "AdvStats_optimism_validation.csv")

    expected_groups = {
        "Male", "Female", "Public insurance", "Private insurance",
        "Age <=9", "Age >=10", "High ACE category", "Not high ACE category",
    }
    if set(subgroup.index) != expected_groups:
        raise ValueError("fairness subgroup inventory does not match the canonical analysis")
    for first, second in [
        ("Male", "Female"),
        ("Public insurance", "Private insurance"),
        ("Age <=9", "Age >=10"),
        ("High ACE category", "Not high ACE category"),
    ]:
        if int(subgroup.loc[[first, second], "N"].sum()) != 1569:
            raise ValueError(f"{first}/{second} do not partition the 1,569-child sample")
        if int(subgroup.loc[[first, second], "Events"].sum()) != 140:
            raise ValueError(f"{first}/{second} do not partition the 140 readmissions")

    portfolio_auc = {row["name"]: row for row in data["models"]["auc"]}
    for row in validation.to_dict("records"):
        portfolio = portfolio_auc[row["Model"]]
        checks = {
            "Apparent AUC": portfolio["apparent"],
            "Bootstrap-corrected AUC": portfolio["corrected"],
            "10-fold OOF AUC": portfolio["oof"],
        }
        for column, expected in checks.items():
            if not np.isclose(row[column], expected, rtol=0, atol=1e-12):
                raise ValueError(f"{row['Model']} {column} disagrees with data.json")

    return subgroup, validation


def build_fairness(subgroup: pd.DataFrame, output: Path) -> None:
    source_order = [
        "Male", "Female", "Public insurance", "Private insurance",
        "Age <=9", "Age >=10", "High ACE category", "Not high ACE category",
    ]
    display_labels = [
        "Recorded male", "Recorded female", "AHCCCS recorded", "Other or missing insurance",
        "Age 5–9", "Age 10–12", "High ACE category", "Other ACE categories",
    ]
    rows = subgroup.loc[source_order]
    positions = np.arange(len(rows))[::-1]

    fig, axes = plt.subplots(1, 2, figsize=(13.6, 7.1), gridspec_kw={"width_ratios": [1, 1.08]})

    auc = rows["AUC"].to_numpy(float)
    error = np.vstack((auc - rows["AUC_lo"].to_numpy(float), rows["AUC_hi"].to_numpy(float) - auc))
    lower = rows["AUC_lo"].min()
    upper = rows["AUC_hi"].max()
    if lower < 0.52 or upper > 0.79:
        raise ValueError(f"fairness AUC interval [{lower:.3f}, {upper:.3f}] exceeds the plotted limits")
    axes[0].errorbar(auc, positions, xerr=error, fmt="o", capsize=3, color=TEAL,
                     ecolor=TEAL_SOFT, markersize=6, linewidth=1.7)
    axes[0].axvline(0.6600819754073778, color=INK, ls=(0, (4, 3)), lw=1, label="Overall AUC 0.660")
    axes[0].set_yticks(positions, display_labels)
    axes[0].tick_params(axis="y", length=0, pad=8)
    axes[0].set_xlim(0.52, 0.79)
    axes[0].set_xlabel("AUC with 95% bootstrap confidence interval")
    axes[0].set_title("Discrimination within subgroups", loc="left", pad=20)
    axes[0].legend(frameon=False, loc="upper left", bbox_to_anchor=(0, -0.13), borderaxespad=0)
    clean_axis(axes[0])

    metrics = [("TPR", "Sensitivity", TEAL), ("FPR", "False-positive rate", TERRACOTTA),
               ("PPV", "Positive predictive value", GOLD)]
    y = np.arange(len(rows))
    width = 0.22
    for offset, (column, label, color) in zip((-width, 0, width), metrics):
        axes[1].barh(y + offset, rows[column].to_numpy(float), width, label=label, color=color)
    axes[1].set_yticks(y, display_labels)
    axes[1].invert_yaxis()
    axes[1].tick_params(axis="y", length=0, pad=8)
    axes[1].set_xlim(0, 0.9)
    axes[1].set_xlabel("Rate at the common 0.078 alert threshold")
    axes[1].set_title("Classification at a single threshold", loc="left", pad=20)
    axes[1].legend(frameon=False, fontsize=8.7, loc="upper left", bbox_to_anchor=(0, -0.13),
                   borderaxespad=0, ncols=3, columnspacing=1)
    clean_axis(axes[1])

    fig.suptitle("Logistic regression performance across recorded patient groups", x=0.065,
                 y=0.99, ha="left", fontsize=19, fontweight="semibold")
    fig.text(0.065, 0.015,
             "Validation subset · 1,569 children · 140 readmissions · identical threshold for every group",
             color=MUTED, fontsize=9)
    fig.subplots_adjust(left=0.18, right=0.98, top=0.85, bottom=0.17, wspace=0.43)
    fig.savefig(output / "AdvStats_fairness.png")
    plt.close(fig)


def build_optimism(validation: pd.DataFrame, output: Path) -> None:
    names = validation["Model"].str.replace(" Regression", "", regex=False)
    positions = np.arange(len(names))
    fig, axis = plt.subplots(figsize=(10.5, 6.4))

    axis.vlines(positions, validation["Bootstrap-corrected AUC"], validation["Apparent AUC"],
                color=RULE, lw=7, zorder=1)
    axis.scatter(positions, validation["Apparent AUC"], color=TERRACOTTA, s=72,
                 label="Training AUC", zorder=3)
    axis.scatter(positions, validation["Bootstrap-corrected AUC"], color=GOLD, s=72,
                 label="Bootstrap-corrected", zorder=3)
    axis.scatter(positions, validation["10-fold OOF AUC"], color=TEAL, marker="D", s=58,
                 label="Held-out AUC", zorder=3)
    nested = validation["Nested-CV AUC"].to_numpy(float)
    nested_mask = np.isfinite(nested)
    axis.scatter(positions[nested_mask] + 0.08, nested[nested_mask], color=INK, marker="P", s=58,
                 label="Nested-CV AUC", zorder=3)
    for index, row in validation.iterrows():
        axis.text(index, row["Apparent AUC"] + 0.012, f"{row['Apparent AUC']:.3f}", ha="center", fontsize=8.5)
        axis.text(index, row["10-fold OOF AUC"] - 0.019, f"{row['10-fold OOF AUC']:.3f}", ha="center", fontsize=8.5)
    axis.axhline(0.5, color=INK, lw=0.9, ls=(0, (3, 3)))
    axis.set_ylim(0.49, 1.01)
    axis.set_xticks(positions, names)
    axis.set_ylabel("Area under the ROC curve")
    axis.set_title("Training performance overstates model discrimination", loc="left", pad=30)
    axis.text(0, 1.018, "Bootstrap correction and 10-fold held-out predictions",
              transform=axis.transAxes, color=MUTED)
    axis.legend(frameon=False, ncol=4, fontsize=8.8, loc="upper left")
    clean_axis(axis)
    axis.xaxis.grid(False)
    axis.yaxis.grid(True, alpha=0.75)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.83, bottom=0.13)
    fig.savefig(output / "AdvStats_optimism_validation.png")
    plt.close(fig)


def verify_outputs(output: Path) -> None:
    from PIL import Image

    for name in ["AdvStats_fairness.png", "AdvStats_optimism_validation.png",
                 "Fig_Recon_7_predictive_ceiling.png"]:
        path = output / name
        with Image.open(path) as image:
            image.verify()
        if path.stat().st_size < 20_000:
            raise RuntimeError(f"figure is unexpectedly small: {path}")


def main() -> None:
    args = parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    configure_matplotlib()
    subgroup, validation = load_and_verify(args.source, data)
    build_fairness(subgroup, args.output)
    build_optimism(validation, args.output)
    build_ceiling(data, args.output)
    verify_outputs(args.output)
    print("Refreshed and verified 3 validation figures from aggregate analysis tables")


if __name__ == "__main__":
    main()
