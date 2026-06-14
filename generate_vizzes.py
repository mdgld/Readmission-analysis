#!/usr/bin/env python3
"""
Generate interactive portfolio visualizations for the pediatric psychiatric readmission study.

Outputs to visualizations/ (4 Plotly HTML files + index.html).
Run with: uv run generate_vizzes.py
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from statsmodels.stats.proportion import proportion_confint, proportions_ztest

BASE = Path(__file__).parent
FIGURES = BASE / "figures"
OUT = BASE / "portfolio" / "visualizations"
OUT.mkdir(exist_ok=True)

COHORT_READMIT_RATE = 9.3  # 246/2652, 90-day

PALETTE = {
    "risk":       "#f0abfc",               # --accent-3 (pink)
    "protective": "#7dd3fc",               # --accent   (sky)
    "nonsig":     "rgba(255,255,255,.25)",
}

BG    = "#11182a"
GRID  = "rgba(255,255,255,.10)"
TEXT  = "#edf3ff"
MUTED = "#aebbd4"

LAYOUT_BASE = dict(
    autosize=True,
    font=dict(
        family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif",
        size=13,
        color=TEXT,
    ),
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    hoverlabel=dict(
        bgcolor="#151f35",
        bordercolor="rgba(255,255,255,.2)",
        font=dict(
            color=TEXT,
            family="Inter, ui-sans-serif, system-ui, -apple-system, sans-serif",
        ),
    ),
)


def write_html(fig: go.Figure, filename: str, title: str = "") -> None:
    chart_div = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"responsive": True},
        div_id="main-chart",
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title or filename.replace('.html', '')}</title>
  <style>
    :root {{
      --bg: #0b1020; --muted: #aebbd4; --text: #edf3ff;
      --line: rgba(255,255,255,.12);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{ height: 100%; background: var(--bg); color: var(--text); }}
    .page {{
      display: flex; flex-direction: column;
      height: 100vh; padding: .75rem 1rem;
    }}
    .back-nav {{
      flex-shrink: 0; display: flex;
      justify-content: space-between; align-items: center;
      margin-bottom: .5rem;
    }}
    .back-link {{
      color: var(--muted); text-decoration: none; font-size: .85rem;
      padding: .4rem .75rem; border: 1px solid var(--line); border-radius: 999px;
    }}
    .back-link:hover {{ color: var(--text); }}
    .chart-wrap {{
      flex: 1; min-height: 400px; position: relative;
    }}
    #main-chart {{
      width: 100% !important; height: 100% !important;
      position: absolute; inset: 0;
    }}
  </style>
</head>
<body>
  <div class="page">
    <nav class="back-nav">
      <a class="back-link" href="index.html">← All analyses</a>
    </nav>
    <div class="chart-wrap">
      {chart_div}
    </div>
  </div>
</body>
</html>"""
    path = OUT / filename
    path.write_text(html, encoding="utf-8")
    print(f"  ✓ {filename}")


# ── 1. Forest Plot ────────────────────────────────────────────────────────────

def make_forest_plot() -> None:
    df = pd.read_csv(FIGURES / "Recon_readmission_logit.csv")

    # The age OR is per year of chronological age; OR < 1 means older = protective
    df["label"] = df["label"].replace("Age (per yr)", "Older age (per yr)")
    df = df.sort_values("OR").reset_index(drop=True)

    def point_color(row):
        if not row["sig"]:
            return PALETTE["nonsig"]
        return PALETTE["protective"] if row["OR"] < 1 else PALETTE["risk"]

    fig = go.Figure()

    for _, row in df.iterrows():
        sig_star = " ★" if row["sig"] else ""
        fig.add_trace(
            go.Scatter(
                x=[row["OR"]],
                y=[row["label"]],
                mode="markers",
                marker=dict(color=point_color(row), size=12, symbol="square"),
                error_x=dict(
                    type="data",
                    symmetric=False,
                    array=[row["hi"] - row["OR"]],
                    arrayminus=[row["OR"] - row["lo"]],
                    color=point_color(row),
                    thickness=2,
                    width=8,
                ),
                hovertemplate=(
                    f"<b>{row['label']}{sig_star}</b><br>"
                    f"OR: {row['OR']:.2f} [{row['lo']:.2f}–{row['hi']:.2f}]<br>"
                    f"p = {row['p']:.3f}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    fig.add_vline(x=1, line_dash="dash", line_color="rgba(255,255,255,.4)", line_width=1.5)

    # Native legend via dummy traces (annotation at y=-0.24 gets clipped in 100vh layout)
    for name, color in [
        ("Significant risk factor",       PALETTE["risk"]),
        ("Significant protective factor", PALETTE["protective"]),
        ("Not significant",               PALETTE["nonsig"]),
    ]:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(color=color, size=10, symbol="square"),
            name=name,
            showlegend=True,
        ))

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=(
                "<b>Predictors of 90-Day Psychiatric Readmission</b><br>"
                "<sup>Multivariable logistic regression · n=2,652 children aged 5–12 · Arizona 2017–2024</sup>"
            ),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(
            title="Odds Ratio (95% CI)",
            type="log",
            tickvals=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
            ticktext=["0.5", "0.75", "1.0", "1.25", "1.5", "2.0"],
            gridcolor=GRID,
        ),
        yaxis=dict(title="", gridcolor=GRID),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            bgcolor="rgba(17,24,42,.8)",
            bordercolor="rgba(255,255,255,.12)",
            font=dict(size=11, color=MUTED),
        ),
        margin=dict(l=220, r=60, t=110, b=60),
    )

    write_html(fig, "forest_plot.html", "Predictors of Readmission")


# ── 2. Within-Category Heterogeneity ─────────────────────────────────────────

def make_subgroup_chart() -> None:
    df = pd.read_csv(FIGURES / "Recon_subgroup_codes.csv")
    counts = df.groupby("Category").size()
    categories = [c for c in df["Category"].unique().tolist() if counts[c] > 1]

    fig = go.Figure()

    for i, cat in enumerate(categories):
        sub = df[df["Category"] == cat].copy().reset_index(drop=True)

        colors = []
        for _, row in sub.iterrows():
            p_val = float(row["p"]) if str(row["p"]) not in ("", "nan") else 1.0
            if p_val < 0.05:
                colors.append(PALETTE["risk"] if row["OR"] > 1 else PALETTE["protective"])
            else:
                colors.append(PALETTE["nonsig"])

        fig.add_trace(
            go.Bar(
                x=sub["Subgroup"],
                y=sub["ReadmitPct"],
                name=cat,
                visible=(i == 0),
                marker_color=colors,
                customdata=np.column_stack([
                    sub["n"].values,
                    sub["OR"].values,
                    sub["CI"].values,
                    sub["p"].values,
                ]),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Readmission rate: %{y:.1f}%<br>"
                    "n = %{customdata[0]}<br>"
                    "OR: %{customdata[1]} [%{customdata[2]}]<br>"
                    "p = %{customdata[3]}"
                    "<extra></extra>"
                ),
            )
        )

    buttons = [
        dict(
            args=[{"visible": [j == i for j in range(len(categories))]}],
            label=cat,
            method="update",
        )
        for i, cat in enumerate(categories)
    ]

    fig.add_hline(
        y=COHORT_READMIT_RATE,
        line_dash="dash",
        line_color="rgba(255,255,255,.3)",
        line_width=1.5,
        annotation_text=f"Cohort average ({COHORT_READMIT_RATE}%)",
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color=MUTED,
    )

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=(
                "<b>Hidden Heterogeneity: Subgroup Risks Within DSM-5 Categories</b><br>"
                "<sup>Select a category · Red = elevated risk · Blue = protective · Gray = n.s.</sup>"
            ),
            x=0.5, xanchor="center",
        ),
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                showactive=True,
                x=0.0, xanchor="left",
                y=1.22, yanchor="top",
                bgcolor="#151f35",
                bordercolor="rgba(255,255,255,.12)",
                font=dict(color=TEXT),
            )
        ],
        yaxis=dict(
            title="90-Day Readmission Rate (%)",
            range=[0, 22],
            gridcolor=GRID,
        ),
        xaxis=dict(title=""),
        margin=dict(l=60, r=60, t=130, b=120),
        showlegend=False,
    )

    write_html(fig, "subgroup_heterogeneity.html", "Within-Category Heterogeneity")


# ── 3. Model Performance ──────────────────────────────────────────────────────

def make_model_performance() -> None:
    opt = pd.read_csv(FIGURES / "AdvStats_optimism_validation.csv")
    boots = pd.read_csv(FIGURES / "AdvStats_bootstrap_CIs.csv").set_index("Model")

    models = opt["Model"].tolist()
    apparent = opt["Apparent AUC"].tolist()
    corrected = opt["Bootstrap-corrected AUC"].tolist()
    oof = opt["10-fold OOF AUC"].fillna(np.nan).tolist()

    ci_lo = [boots.loc[m, "ROC 2.5%"] for m in models]
    ci_hi = [boots.loc[m, "ROC 97.5%"] for m in models]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Apparent AUC (training)",
            x=models,
            y=apparent,
            marker_color="rgba(125,211,252,.3)",
            hovertemplate="<b>%{x}</b><br>Apparent AUC: %{y:.3f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Bootstrap-corrected AUC",
            x=models,
            y=corrected,
            marker_color="#7dd3fc",
            error_y=dict(
                type="data",
                symmetric=False,
                array=[ci_hi[i] - corrected[i] for i in range(len(models))],
                arrayminus=[corrected[i] - ci_lo[i] for i in range(len(models))],
                thickness=2,
                width=8,
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Bootstrap-corrected AUC: %{y:.3f}<br>"
                "(95% CI from %{customdata[0]:.3f}–%{customdata[1]:.3f})"
                "<extra></extra>"
            ),
            customdata=list(zip(ci_lo, ci_hi)),
        )
    )

    # OOF only where available (LogReg has no OOF in this dataset)
    oof_values = [v if not (isinstance(v, float) and np.isnan(v)) else None for v in oof]
    fig.add_trace(
        go.Bar(
            name="10-fold OOF AUC (most conservative)",
            x=models,
            y=oof_values,
            marker_color="#c4b5fd",
            hovertemplate="<b>%{x}</b><br>OOF AUC: %{y:.3f}<extra></extra>",
        )
    )

    fig.add_hline(y=0.5, line_dash="dot", line_color="rgba(255,255,255,.3)", line_width=1,
                  annotation_text="Chance (0.50)", annotation_font_size=10,
                  annotation_font_color=MUTED)

    fig.add_annotation(
        text="Even with 2,652 patients, PPV ≈ 20% at the optimal threshold — insufficient for individual triage",
        xref="paper", yref="paper", x=0.5, y=-0.18,
        showarrow=False, font=dict(size=11, color=MUTED), align="center",
    )

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=(
                "<b>The Limits of Prediction: Apparent vs. Corrected Model Performance</b><br>"
                "<sup>Optimism correction reveals tree-model overfit · Logistic regression remains competitive</sup>"
            ),
            x=0.5, xanchor="center",
        ),
        barmode="group",
        yaxis=dict(
            title="AUC-ROC",
            range=[0, 1.0],
            gridcolor=GRID,
        ),
        xaxis=dict(title=""),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(17,24,42,.8)", bordercolor="rgba(255,255,255,.12)",
        ),
        margin=dict(l=70, r=40, t=120, b=100),
    )

    write_html(fig, "model_performance.html", "Model Performance")


# ── 4. DSM-5 Readmission Rates ────────────────────────────────────────────────

def make_dsm5_rates() -> None:
    df = pd.read_csv(BASE / "annotated_psychiatric_data_complete.csv")
    df["readmitted"] = (df["Readmissions"] > 0).astype(int)

    cat_cols = [
        "VisitDiags_DSM5Categories",
        "NonSuicidialDiags_DSM5Categories",
        "ChronicDiags_DSM5Categories",
    ]

    def parse_cats(val: object) -> set:
        if pd.isna(val) or str(val).strip() == "":
            return set()
        return {
            c.strip()
            for c in str(val).split(";")
            if c.strip() and "(Non-DSM5)" not in c and c.strip() != "nan"
        }

    rows = []
    for _, row in df.iterrows():
        cats: set = set()
        for col in cat_cols:
            cats |= parse_cats(row.get(col))
        for cat in cats:
            rows.append({"dsm5": cat, "readmitted": int(row["readmitted"])})

    # Deduplicate per patient per category handled by collecting unique cats above
    long = pd.DataFrame(rows)

    results = []
    for cat, grp in long.groupby("dsm5"):
        n = len(grp)
        if n < 20:
            continue
        k = int(grp["readmitted"].sum())
        rate = 100.0 * k / n
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        _, p_val = proportions_ztest(k, n, value=COHORT_READMIT_RATE / 100)
        if p_val < 0.001:
            star = " ***"
        elif p_val < 0.01:
            star = " **"
        elif p_val < 0.05:
            star = " *"
        else:
            star = ""
        results.append(
            {"Category": cat + star, "N": n, "Readmitted": k,
             "Rate": rate, "CI_lo": 100 * lo, "CI_hi": 100 * hi}
        )

    res = pd.DataFrame(results).sort_values("Rate", ascending=True)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=res["Rate"],
            y=res["Category"],
            orientation="h",
            marker=dict(
                color=res["Rate"],
                colorscale=[[0, "rgba(125,211,252,.35)"], [0.5, "#7dd3fc"], [1, "#c4b5fd"]],
                showscale=False,
            ),
            error_x=dict(
                type="data",
                symmetric=False,
                array=(res["CI_hi"] - res["Rate"]).tolist(),
                arrayminus=(res["Rate"] - res["CI_lo"]).tolist(),
                thickness=1.5,
                width=6,
            ),
            customdata=np.column_stack([res["N"].values, res["Readmitted"].values]),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Readmission rate: %{x:.1f}%<br>"
                "Patients with this dx: %{customdata[0]}<br>"
                "Readmitted: %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=COHORT_READMIT_RATE,
        line_dash="dash",
        line_color="rgba(255,255,255,.3)",
        line_width=1.5,
        annotation_text="Cohort avg (9.3%)",
        annotation_position="top right",
        annotation_font_size=10,
        annotation_font_color=MUTED,
    )

    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=(
                "<b>90-Day Readmission Risk by DSM-5 Diagnostic Category</b><br>"
                "<sup>Patients may appear in multiple categories · 95% Wilson CI · n ≥ 20 · * p&lt;.05, ** p&lt;.01, *** p&lt;.001 vs. cohort average</sup>"
            ),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(title="90-Day Readmission Rate (%)", gridcolor=GRID),
        yaxis=dict(title="", automargin=True),
        margin=dict(l=230, r=60, t=110, b=60),
    )

    write_html(fig, "dsm5_readmission_rates.html", "DSM-5 Readmission Rates")


# ── Index Page ────────────────────────────────────────────────────────────────

INDEX_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Interactive Analyses — Pediatric Psychiatric Readmission</title>
  <style>
    :root {
      --bg: #0b1020;
      --panel: #11182a;
      --text: #edf3ff;
      --muted: #aebbd4;
      --line: rgba(255,255,255,.12);
      --accent: #7dd3fc;
      --accent-2: #c4b5fd;
      --accent-3: #f0abfc;
      --shadow: 0 20px 60px rgba(0,0,0,.35);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      background:
        radial-gradient(circle at 12% 8%, rgba(125,211,252,.16), transparent 28rem),
        radial-gradient(circle at 88% 2%, rgba(196,181,253,.18), transparent 30rem),
        var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: clamp(3rem, 8vw, 8rem) clamp(1rem, 6vw, 6rem);
      max-width: 900px;
      margin: 0 auto;
    }
    a { color: inherit; }
    .back-link {
      display: inline-block;
      margin-bottom: 1.5rem;
      color: var(--muted);
      text-decoration: none;
      font-size: .9rem;
    }
    .back-link:hover { color: var(--text); }
    .eyebrow {
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-weight: 800;
      font-size: .78rem;
      margin-bottom: .75rem;
    }
    h1 {
      font-size: clamp(2rem, 5vw, 3.5rem);
      letter-spacing: -.05em;
      line-height: 1.05;
      margin-bottom: 1rem;
    }
    .lede { color: var(--muted); font-size: 1.05rem; line-height: 1.7; max-width: 60ch; margin-bottom: 3rem; }
    .cards { display: grid; gap: 1rem; }
    .card {
      display: block;
      text-decoration: none;
      color: inherit;
      padding: 1.4rem;
      border: 1px solid var(--line);
      border-radius: 1.4rem;
      background: rgba(17,24,42,.78);
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
      transition: border-color .2s;
    }
    .card:hover { border-color: var(--accent); }
    .card-num {
      font-size: .78rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .14em;
      color: var(--accent);
      margin-bottom: .5rem;
    }
    .card h2 { font-size: 1.15rem; letter-spacing: -.03em; margin-bottom: .5rem; }
    .card p { color: var(--muted); font-size: .92rem; line-height: 1.65; }
    .finding {
      margin-top: .85rem;
      padding: .7rem 1rem;
      background: rgba(125,211,252,.08);
      border: 1px solid rgba(125,211,252,.25);
      border-radius: .75rem;
      font-size: .85rem;
      color: var(--text);
    }
    .open-label {
      display: inline-block;
      margin-top: .9rem;
      color: var(--accent);
      font-weight: 700;
      font-size: .85rem;
    }
    footer {
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--line);
      font-size: .85rem;
      color: var(--muted);
    }
  </style>
</head>
<body>
  <a class="back-link" href="../">← Back to portfolio</a>
  <p class="eyebrow">Interactive analyses</p>
  <h1>Subgroup &amp; model deep-dives</h1>
  <p class="lede">
    Four interactive analyses that go beyond the portfolio summary — hover for exact
    statistics, use dropdowns to explore within-category risk, and compare model
    performance before and after optimism correction.
  </p>

  <div class="cards">
    <a class="card" href="forest_plot.html">
      <p class="card-num">01</p>
      <h2>What predicts 90-day readmission?</h2>
      <p>
        Multivariable logistic regression forest plot with 95% CIs. Hover over any
        point for exact odds ratios, confidence intervals, and p-values.
      </p>
      <div class="finding">
        Depressive disorders (OR 1.78), diagnostic complexity (OR 1.31/category), and
        physical restraint use (OR 1.58) emerged as significant — while ACE score,
        C-SSRS flags, and length of stay did not.
      </div>
      <span class="open-label">Open interactive chart ↗</span>
    </a>

    <a class="card" href="subgroup_heterogeneity.html">
      <p class="card-num">02</p>
      <h2>Hidden heterogeneity within DSM-5 categories</h2>
      <p>
        Select a DSM-5 category from the dropdown to see how aggregate risk conceals
        opposite signals in subgroups. Colors show direction of effect vs. the cohort
        average (9.3%).
      </p>
      <div class="finding">
        Within Depressive Disorders: DMDD carries 14.2% readmission (OR 1.82)
        while single-episode MDD is flat at 9.0% (OR 0.96, n.s.).
      </div>
      <span class="open-label">Open interactive chart ↗</span>
    </a>

    <a class="card" href="model_performance.html">
      <p class="card-num">03</p>
      <h2>The limits of prediction</h2>
      <p>
        Apparent vs. bootstrap-corrected vs. out-of-fold AUC for logistic regression,
        random forest, and CatBoost. Visualizes the optimism inflation common in small
        clinical datasets.
      </p>
      <div class="finding">
        CatBoost apparent AUC 0.90 collapsed to 0.64 OOF — worse than logistic
        regression. PPV &asymp; 20% at the optimal threshold rules out individual triage.
      </div>
      <span class="open-label">Open interactive chart ↗</span>
    </a>

    <a class="card" href="dsm5_readmission_rates.html">
      <p class="card-num">04</p>
      <h2>Readmission risk across the diagnostic spectrum</h2>
      <p>
        Ranked bar chart of 90-day readmission rates for every DSM-5 category in the
        cohort (n &ge; 20). Wilson 95% CIs shown. Hover for patient counts and raw numbers.
      </p>
      <div class="finding">
        Highest rates in tic disorders (21.6%) and other neurodevelopmental conditions;
        lowest in adjustment and somatic categories (&lt;7%).
      </div>
      <span class="open-label">Open interactive chart ↗</span>
    </a>
  </div>

  <footer>
    Interactive charts generated with Plotly &middot; All data are aggregated —
    no individual patient records are displayed.
  </footer>
</body>
</html>
"""


def write_index() -> None:
    path = OUT / "index.html"
    path.write_text(INDEX_HTML, encoding="utf-8")
    print(f"  ✓ index.html")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating visualizations...")
    make_forest_plot()
    make_subgroup_chart()
    make_model_performance()
    make_dsm5_rates()
    write_index()
    print(f"\nDone. Open {OUT / 'index.html'} in a browser.")
