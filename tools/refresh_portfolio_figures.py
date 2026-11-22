"""Reproduce the gallery from local study records and the July analysis.

Published files contain aggregate plots only. Run with the analysis environment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker
from PIL import Image

INK = "#182e2c"
MUTED = "#536661"
TEAL = "#12655e"
TERRACOTTA = "#985037"
GOLD = "#a87931"
RULE = "#d5ddd6"
PAPER = "#fffefa"
NEUTRAL = "#9ba7a1"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data.json"))
    parser.add_argument(
        "--source",
        type=Path,
        required=True, help="Local July analysis checkout (or its figures directory)",
    )
    parser.add_argument("--output", type=Path, default=Path("assets/figures"))
    return parser.parse_args()


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 17,
            "axes.titleweight": "semibold",
            "axes.labelcolor": MUTED,
            "axes.edgecolor": RULE,
            "axes.facecolor": PAPER,
            "figure.facecolor": PAPER,
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": INK,
            "grid.color": RULE,
            "grid.linewidth": 0.7,
            "savefig.facecolor": PAPER,
            "savefig.bbox": "tight",
            "savefig.dpi": 180,
        }
    )


def clean_axis(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(RULE)
    ax.grid(axis="x", alpha=0.75)
    ax.set_axisbelow(True)


def build_spectrum(data: dict, output: Path) -> None:
    items = data["spectrum"]["items"]
    overall = data["summary"]["readmission_rate"]
    if any(item["readmitted"] > data["summary"]["readmitted"] for item in items):
        raise ValueError("diagnostic subgroup event count exceeds cohort event count")
    if any(item["readmitted"] > item["n"] for item in items):
        raise ValueError("diagnostic subgroup event count exceeds subgroup size")

    labels = [item["label"] for item in items][::-1]
    rates = np.array([item["rate"] for item in items][::-1])
    ns = [item["n"] for item in items][::-1]
    qs = np.array([item["q"] for item in items][::-1])
    colors = [TERRACOTTA if q < 0.05 else NEUTRAL for q in qs]

    fig, ax = plt.subplots(figsize=(11.8, 10.2))
    y = np.arange(len(labels))
    ax.barh(y, rates, color=colors, height=0.64)
    ax.axvline(overall, color=TEAL, lw=1.4, ls=(0, (4, 3)))
    for i, (rate, n) in enumerate(zip(rates, ns)):
        ax.text(rate + 0.3, i, f"{rate:.1f}%  n={n:,}", va="center", fontsize=8.2, color=MUTED)
    ax.set_yticks(y, labels)
    ax.tick_params(axis="y", labelsize=8.8, length=0, pad=7)
    ax.set_xlim(0, max(rates) + 4.7)
    ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=100, decimals=0))
    ax.set_xlabel("Observed 90-day readmission rate")
    ax.set_title("Readmission by source-mapped diagnostic category", loc="left", pad=30)
    ax.text(
        0,
        1.012,
        "One child counted once per category · categories with n ≥ 15 · terracotta indicates BH-adjusted q < .05",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=9.2,
    )
    ax.text(
        overall + 0.2,
        len(labels) - 0.2,
        f"cohort {overall:.1f}%",
        color=TEAL,
        fontsize=8.7,
        va="top",
    )
    clean_axis(ax)
    fig.text(
        0.1,
        0.015,
        "Source-mapping note: the ‘suicidal ideation / self-harm’ group includes R45.851 and two intentional self-harm codes.",
        color=MUTED,
        fontsize=8.2,
    )
    fig.subplots_adjust(left=0.35, right=0.97, top=0.91, bottom=0.08)
    fig.savefig(output / "Fig3_readmission_by_dsm5.png")
    plt.close(fig)


def build_forest(data: dict, output: Path) -> None:
    rows = data["models"]["forest"]
    labels = [row["label"] for row in rows][::-1]
    estimates = np.array([row["or"] for row in rows][::-1])
    lows = np.array([row["lo"] for row in rows][::-1])
    highs = np.array([row["hi"] for row in rows][::-1])
    kinds = [row["kind"] for row in rows][::-1]
    colors = [TERRACOTTA if kind == "risk" else TEAL if kind == "protect" else NEUTRAL for kind in kinds]
    y = np.arange(len(rows))

    fig, ax = plt.subplots(figsize=(11.8, 7.3))
    for i, (estimate, low, high, color) in enumerate(zip(estimates, lows, highs, colors)):
        ax.plot([low, high], [i, i], color=color, lw=1.5)
        ax.scatter(estimate, i, s=46, color=color, zorder=3, edgecolor=PAPER, linewidth=0.7)
        ax.text(high * 1.035, i, f"{estimate:.2f}  ({low:.2f}–{high:.2f})", va="center", fontsize=8.6, color=MUTED)
    ax.axvline(1, color=INK, lw=1, ls=(0, (3, 3)))
    ax.set_xscale("log")
    ax.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax.set_xlim(0.2, 4.8)
    ax.set_xticks([0.25, 0.5, 1, 2, 4], ["0.25", "0.5", "1", "2", "4"])
    ax.set_yticks(y, labels)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.set_xlabel("Adjusted odds ratio (95% confidence interval)")
    ax.set_title("Adjusted associations with 90-day readmission", loc="left", pad=30)
    ax.text(0, 1.015, "Full cohort · n=2,652 · multivariable logistic regression", transform=ax.transAxes, color=MUTED)
    clean_axis(ax)
    note = data["models"].get("coding_note", "")
    from textwrap import fill
    fig.text(0.05, 0.025, fill(note, 113), color=MUTED, fontsize=8.4)
    fig.subplots_adjust(left=0.34, right=0.92, top=0.86, bottom=0.18)
    fig.savefig(output / "Fig7_forest_plot.png")
    plt.close(fig)


def build_ceiling(data: dict, output: Path) -> None:
    models = data["models"]["auc"]
    names = [model["name"].replace(" Regression", "") for model in models]
    apparent = [model["apparent"] for model in models]
    corrected = [model["corrected"] for model in models]
    oof = [model["oof"] for model in models]
    x = np.arange(len(names))
    width = 0.23

    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    bars = [
        ax.bar(x - width, apparent, width, label="Apparent", color="#c7cec9"),
        ax.bar(x, corrected, width, label="Bootstrap-corrected", color=GOLD),
        ax.bar(x + width, oof, width, label="10-fold out-of-fold", color=TEAL),
    ]
    for group in bars:
        ax.bar_label(group, fmt="%.3f", padding=3, fontsize=8.5, color=INK)
    ax.axhline(0.5, color=INK, lw=0.9, ls=(0, (3, 3)))
    ax.set_ylim(0.48, 1.01)
    ax.set_xticks(x, names)
    ax.set_ylabel("Area under the ROC curve")
    ax.set_title("Training and held-out model performance", loc="left", pad=30)
    ax.text(
        0,
        1.015,
        "ACE-available validation subset · n=1,569 · 140 readmissions",
        transform=ax.transAxes,
        color=MUTED,
    )
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.grid(axis="y", alpha=0.75)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(RULE)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.85, bottom=0.22)
    fig.savefig(output / "Fig_Recon_7_predictive_ceiling.png")
    plt.close(fig)


def verify_outputs(output: Path, catalog: list) -> None:
    expected = {Path(item['file']).name for item in catalog}
    actual = {path.name for path in output.glob("*.png")}
    if actual != expected:
        raise RuntimeError(f"figure inventory mismatch: expected {sorted(expected)}, got {sorted(actual)}")
    for path in output.glob("*.png"):
        with Image.open(path) as image:
            image.verify()
        if path.stat().st_size < 20_000:
            raise RuntimeError(f"figure is unexpectedly small: {path}")


def main() -> None:
    args = parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    source = args.source.resolve()
    if source.name == 'figures' and not (source / 'data').is_dir():
        source = source.parent
    from check_descriptive_figures import checked_cohort, draw_cohort, draw_demographics
    from refresh_broad_model_figures import build_broad_figures
    from refresh_validation_figures import (
        build_fairness,
        build_optimism,
        load_and_verify,
    )

    df, los = checked_cohort(source, data)
    with TemporaryDirectory(dir=args.output.parent) as directory:
        stage = Path(directory)
        configure_matplotlib()
        draw_cohort(df, los, stage)
        draw_demographics(df, stage)
        build_spectrum(data, stage)
        build_forest(data, stage)
        subgroup, validation = load_and_verify(source / 'figures', data)
        build_fairness(subgroup, stage)
        build_optimism(validation, stage)
        build_ceiling(data, stage)
        build_broad_figures(source, stage)
        verify_outputs(stage, data['figures'])
        for item in data['figures']:
            name = Path(item['file']).name
            (stage / name).replace(args.output / name)
    print(f"Refreshed {len(data['figures'])} checked figures in {args.output}")


if __name__ == "__main__":
    main()
