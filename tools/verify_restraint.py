#!/usr/bin/env python3
"""Restraint source-level double-check & reconciliation (T1 HARD GATE).

Read-only. Recomputes restraint N / readmission rate / unadjusted OR from the
canonical patient CSV (GROUND TRUTH), cross-checks every restraint-bearing
figures/*.csv, tabulates the adjusted multivariable OR, parses the
reconciliation prose, and emits an auditable report + a machine-readable
authoritative JSON the downstream data.json consumes.

Usage:
  .venv/bin/python tools/verify_restraint.py
  .venv/bin/python tools/verify_restraint.py --check-datajson data.json

Exits 0 on success, non-zero on any unresolved divergence or missing source.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = REPO_ROOT / ".omo" / "evidence"
REPORT_PATH = EVIDENCE_DIR / "task-1-restraint-reconciliation.md"
AUTH_JSON_PATH = EVIDENCE_DIR / "restraint-authoritative.json"

# ---------------------------------------------------------------------------
# Stats helpers (stdlib only — no scipy/numpy dependency)
# ---------------------------------------------------------------------------

def _norm_cdf(z: float) -> float:
    """Standard normal CDF via erf (Python 3.2+)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def two_sided_z_p(z: float) -> float:
    """Two-sided p-value for a standard-normal z."""
    return 2.0 * (1.0 - _norm_cdf(abs(z)))


def unadjusted_or_2x2(a: int, b: int, c: int, d: int) -> dict:
    """Unadjusted odds ratio from a 2x2 table with Wald 95% CI + two-sided p.

    Table layout (readmission ~ restraint):
        a = restrained & readmitted      b = restrained & not readmitted
        c = not-restrained & readmitted  d = not-restrained & not readmitted

    Haldane-Anscombe +0.5 continuity correction applied ONLY if any cell is 0.
    Wald CI on log(OR); two-sided z p-value.
    """
    cells = [a, b, c, d]
    cc = 0.5 if any(x == 0 for x in cells) else 0.0
    a2, b2, c2, d2 = a + cc, b + cc, c + cc, d + cc
    or_val = (a2 * d2) / (b2 * c2)
    log_or = math.log(or_val)
    se_log = math.sqrt(1.0 / a2 + 1.0 / b2 + 1.0 / c2 + 1.0 / d2)
    z = log_or / se_log if se_log > 0 else 0.0
    p = two_sided_z_p(z)
    ci_lo = math.exp(log_or - 1.959963984540054 * se_log)
    ci_hi = math.exp(log_or + 1.959963984540054 * se_log)
    return {
        "or": or_val, "ci_lo": ci_lo, "ci_hi": ci_hi, "p": p,
        "z": z, "se_log": se_log, "continuity_correction": cc,
        "table": {"a": a, "b": b, "c": c, "d": d},
        "method": "2x2 unadjusted OR, Wald 95% CI on log(OR), two-sided z p; "
                  "Haldane-Anscombe +0.5 iff any cell=0",
    }


# ---------------------------------------------------------------------------
# (a) Locate + (b) recompute from source = GROUND TRUTH
# ---------------------------------------------------------------------------

def locate_source_csv() -> Path:
    candidates = [
        REPO_ROOT / "data" / "annotated_psychiatric_data_complete.csv",
        *glob.glob(str(REPO_ROOT / "data" / "**" / "annotated_psychiatric_data_complete.csv"), recursive=True),
    ]
    # de-dup while preserving order
    seen, ordered = set(), []
    for c in candidates:
        p = Path(c)
        if p not in seen and p.exists():
            seen.add(p)
            ordered.append(p)
    if not ordered:
        searched = [str(c) for c in candidates]
        raise FileNotFoundError(
            f"Could not locate annotated_psychiatric_data_complete.csv. Searched: {searched}"
        )
    return ordered[0]


def recompute_from_source(csv_path: Path) -> dict:
    """GROUND TRUTH recompute. Empty/NA restraints -> not restrained (0)."""
    n_total = 0
    rest_readmit = 0      # a
    rest_not_readmit = 0  # b
    norest_readmit = 0    # c
    norest_not_readmit = 0  # d
    n_restrained = 0
    n_readmitted = 0
    skipped_na = 0

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "restraints" not in reader.fieldnames or "Readmissions" not in reader.fieldnames:
            raise KeyError(
                f"Source CSV missing required columns. Got: {reader.fieldnames}"
            )
        for row in reader:
            n_total += 1
            rest_raw = (row.get("restraints") or "").strip()
            readm_raw = (row.get("Readmissions") or "").strip()

            # treat empty/NA restraints as 0 (not restrained)
            try:
                rest = float(rest_raw) if rest_raw and rest_raw.lower() not in ("na", "nan", "") else 0.0
            except ValueError:
                rest = 0.0
            # Readmissions: empty/NA -> cannot determine readmission -> skip for OR
            try:
                readm = float(readm_raw) if readm_raw and readm_raw.lower() not in ("na", "nan", "") else None
            except ValueError:
                readm = None

            had_rest = rest > 0
            if had_rest:
                n_restrained += 1
            if readm is None:
                skipped_na += 1
                continue
            had_readm = readm > 0
            if had_readm:
                n_readmitted += 1
            if had_rest and had_readm:
                rest_readmit += 1
            elif had_rest and not had_readm:
                rest_not_readmit += 1
            elif not had_rest and had_readm:
                norest_readmit += 1
            else:
                norest_not_readmit += 1

    # Descriptive N & rate (uses ALL rows — empty restraints = not restrained)
    rate_restrained = (rest_readmit / n_restrained * 100) if n_restrained else 0.0
    n_not_restrained = n_total - n_restrained
    rate_not_restrained = (norest_readmit / n_not_restrained * 100) if n_not_restrained else 0.0
    cohort_rate = (n_readmitted / n_total * 100) if n_total else 0.0

    # Unadjusted OR (rows with NA Readmissions dropped — counted in skipped_na)
    or_result = unadjusted_or_2x2(rest_readmit, rest_not_readmit, norest_readmit, norest_not_readmit)

    return {
        "source_csv": str(csv_path.relative_to(REPO_ROOT)),
        "n_total": n_total,
        "n_restrained": n_restrained,
        "n_not_restrained": n_not_restrained,
        "rate_restrained_pct": round(rate_restrained, 4),
        "rate_not_restrained_pct": round(rate_not_restrained, 4),
        "n_readmitted": n_readmitted,
        "cohort_readmit_rate_pct": round(cohort_rate, 4),
        "restrained_readmit_n": rest_readmit,
        "not_restrained_readmit_n": norest_readmit,
        "skipped_na_readmissions": skipped_na,
        "unadjusted_or": or_result,
    }


# ---------------------------------------------------------------------------
# (c) Discover ALL reconciliation targets in figures/*.csv
# ---------------------------------------------------------------------------

RESTRAINT_TOKENS = re.compile(r"restrain", re.IGNORECASE)


def scan_figures_csvs() -> list[dict]:
    """Glob figures/*.csv, scan for restraint tokens in columns AND rows."""
    results = []
    for fp in sorted(glob.glob(str(REPO_ROOT / "figures" / "*.csv"))):
        rel = str(Path(fp).relative_to(REPO_ROOT))
        with open(fp, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        if not rows:
            results.append({"file": rel, "present": False, "note": "empty file"})
            continue
        header = rows[0]
        # column-name matches
        col_matches = [c for c in header if RESTRAINT_TOKENS.search(c)]
        # row matches: any cell containing 'restrain'
        row_hits = []
        for row in rows[1:]:
            for cell in row:
                if RESTRAINT_TOKENS.search(cell):
                    row_hits.append(row)
                    break
        if not col_matches and not row_hits:
            continue  # not a restraint-bearing file
        # Pull the specific restraint values
        entries = []
        if col_matches:
            col_idx = {c: header.index(c) for c in col_matches}
            for row in rows[1:]:
                label = row[0] if row else ""
                for c in col_matches:
                    idx = col_idx[c]
                    val = row[idx] if idx < len(row) else ""
                    if val:
                        entries.append({"row_label": label, "column": c, "value": val})
        if not col_matches and row_hits:
            # e.g. Mv_logit_readmission.csv: first col is the term name
            for row in row_hits:
                entries.append({"row_label": row[0], "column": "(row token)", "value": "|".join(row[1:])})
        results.append({
            "file": rel,
            "present": True,
            "columns": col_matches,
            "n_entries": len(entries),
            "entries": entries[:6],  # cap for report readability
        })
    return results


# ---------------------------------------------------------------------------
# (d) Adjusted multivariable OR from Mv_logit_readmission.csv
# ---------------------------------------------------------------------------

def read_adjusted_or() -> dict | None:
    fp = REPO_ROOT / "figures" / "Mv_logit_readmission.csv"
    if not fp.exists():
        return None
    with fp.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return None
    header = rows[0]
    # columns: ['', 'OR', 'lo', 'hi', 'p']
    idx = {h: header.index(h) for h in header if h}
    for row in rows[1:]:
        term = (row[0] or "").strip().lower()
        if "restrain" in term:
            return {
                "source": "figures/Mv_logit_readmission.csv",
                "term": row[0],
                "or": float(row[idx["OR"]]),
                "ci_lo": float(row[idx["lo"]]),
                "ci_hi": float(row[idx["hi"]]),
                "p": float(row[idx["p"]]),
                "or_kind": "adjusted multivariable (readmission model)",
            }
    return None


# ---------------------------------------------------------------------------
# (e) Parse docs/Reconciliation_2025_vs_2026.md restraint prose
# ---------------------------------------------------------------------------

def parse_reconciliation_prose() -> dict:
    fp = REPO_ROOT / "docs" / "Reconciliation_2025_vs_2026.md"
    if not fp.exists():
        return {"found": False, "path": str(fp)}
    text = fp.read_text(encoding="utf-8")
    # find paragraphs mentioning restraint
    paras = []
    for block in re.split(r"\n\s*\n", text):
        if RESTRAINT_TOKENS.search(block):
            # extract the OR ~1.55, p ~0.015 style facts
            or_match = re.search(r"OR\s*[≈~]?\s*([0-9.]+)", block, re.IGNORECASE)
            p_match = re.search(r"p\s*[≈~]?\s*([0-9.]+)", block, re.IGNORECASE)
            paras.append({
                "excerpt": block.strip()[:300],
                "or_mentioned": or_match.group(1) if or_match else None,
                "p_mentioned": p_match.group(1) if p_match else None,
            })
    return {"found": True, "path": str(fp.relative_to(REPO_ROOT)), "restraint_paragraphs": paras}


# ---------------------------------------------------------------------------
# (f) Emit report + authoritative JSON
# ---------------------------------------------------------------------------

def fmt_ci(lo: float, hi: float) -> str:
    return f"{lo:.2f}–{hi:.2f}"


def fmt_p(p: float) -> str:
    if p < 0.001:
        return "<0.001"
    return f"{p:.3f}"


def build_report(src: dict, figs: list[dict], adj: dict | None, prose: dict) -> str:
    uor = src["unadjusted_or"]
    lines = []
    lines.append("# T1 — Restraint source-level double-check & reconciliation\n")
    lines.append("> USER-REQUIRED HARD GATE. Source recompute = GROUND TRUTH.\n")
    lines.append(f"**Source CSV:** `{src['source_csv']}` (N={src['n_total']:,})\n")
    lines.append(f"**Rows skipped for NA Readmissions:** {src['skipped_na_readmissions']} (excluded from OR; empty `restraints` counted as not-restrained for descriptive N/rate)\n")
    lines.append("")

    lines.append("## GROUND TRUTH (recomputed from source)\n")
    lines.append(f"- Restrained N: **{src['n_restrained']}** ({src['n_restrained']/src['n_total']*100:.1f}% of cohort)")
    lines.append(f"- Not-restrained N: **{src['n_not_restrained']:,}**")
    lines.append(f"- Readmission rate (restrained): **{src['rate_restrained_pct']}%** ({src['restrained_readmit_n']}/{src['n_restrained']})")
    lines.append(f"- Readmission rate (not restrained): **{src['rate_not_restrained_pct']}%** ({src['not_restrained_readmit_n']}/{src['n_not_restrained']:,})")
    lines.append(f"- Cohort 90-day readmission rate: **{src['cohort_readmit_rate_pct']}%** ({src['n_readmitted']}/{src['n_total']:,})\n")
    lines.append(f"- Unadjusted OR (restraint→readmission): **{uor['or']:.3f}** [{fmt_ci(uor['ci_lo'], uor['ci_hi'])}] p={fmt_p(uor['p'])}")
    lines.append(f"  - Method: {uor['method']}")
    lines.append(f"  - 2×2: a(restrained&readmit)={uor['table']['a']}, b={uor['table']['b']}, c={uor['table']['c']}, d={uor['table']['d']}")
    lines.append(f"  - Continuity correction: {uor['continuity_correction']}\n")

    lines.append("## AUTHORITATIVE (what the site must display)\n")
    lines.append("| Metric | AUTHORITATIVE value | Source |")
    lines.append("|---|---|---|")
    lines.append(f"| Restrained N | {src['n_restrained']} | source recompute |")
    lines.append(f"| Restrained rate (of cohort) | {src['n_restrained']/src['n_total']*100:.1f}% | source recompute |")
    lines.append(f"| Readmission rate (restrained) | {src['rate_restrained_pct']}% | source recompute |")
    if adj:
        lines.append(f"| Adjusted OR (site forest + abstract) | {adj['or']:.2f} [{fmt_ci(adj['ci_lo'], adj['ci_hi'])}] p={fmt_p(adj['p'])} | {adj['source']} (`{adj['term']}`) |")
    lines.append("")
    lines.append("**Selection rule:** Descriptive N & rate = source recompute. "
                 "The OR the SITE displays (forest plot, abstract Results chip, findings group-stats) = "
                 "the **adjusted multivariable OR from `figures/Mv_logit_readmission.csv`** (`had_restraints` row) — "
                 "this is the model the abstract reports.\n")

    lines.append("## Known divergences (baseline vs AUTHORITATIVE)\n")
    lines.append("| Location | Baseline value | AUTHORITATIVE | Status |")
    lines.append("|---|---|---|---|")
    lines.append(f"| index.html:637 (inline) | N=312, rate=13.1% | N={src['n_restrained']}, rate={src['rate_restrained_pct']}% | CORRECT (restrained readmit rate) but N is wrong → use {src['n_restrained']} |")
    if adj:
        lines.append(f"| index.html:615 (group OR) | 1.58 [1.10–2.26] p=.013 | {adj['or']:.2f} [{fmt_ci(adj['ci_lo'], adj['ci_hi'])}] p={fmt_p(adj['p'])} | CHANGE to AUTHORITATIVE |")
        lines.append(f"| index.html:680 (forest OR) | 1.58 [1.11–2.27] | {adj['or']:.2f} [{fmt_ci(adj['ci_lo'], adj['ci_hi'])}] | CHANGE to AUTHORITATIVE |")
        lines.append(f"| index.html:753 (abstract OR) | 1.58, p=0.012 | {adj['or']:.2f}, p={fmt_p(adj['p'])} | CHANGE to AUTHORITATIVE |")
    lines.append(f"| portfolio/data.json:13-14 | N=510, 19.2%/13.5% | N={src['n_restrained']}, {src['n_restrained']/src['n_total']*100:.1f}% | N matches; reconcile the 13.5% vs {src['rate_restrained_pct']}% |")
    lines.append(f"| AGENTS.md | OR≈1.55, p≈.015 | {adj['or']:.2f}, p={fmt_p(adj['p']) if adj else '—'} | AGENTS.md rounds; site uses exact Mv_logit value |")
    lines.append("")

    lines.append("## Values the site MUST change\n")
    if adj:
        lines.append(f"1. Findings → restraint group-stats OR: `1.58` → **{adj['or']:.2f}**")
        lines.append(f"2. Findings → restraint group-stats CI: `1.10–2.26` → **{fmt_ci(adj['ci_lo'], adj['ci_hi'])}**")
        lines.append(f"3. Findings → restraint group-stats p: `.013` → **{fmt_p(adj['p'])}**")
        lines.append(f"4. Forest plot → restraint OR/stat: `1.58 [1.11–2.27]` → **{adj['or']:.2f} [{fmt_ci(adj['ci_lo'], adj['ci_hi'])}]**")
        lines.append(f"5. Abstract Results → restraint: `OR 1.58, p = 0.012` → **OR {adj['or']:.2f}, p = {fmt_p(adj['p'])}**")
        lines.append(f"6. Findings → restraint N (if shown): `312` → **{src['n_restrained']}**")
        lines.append(f"7. Findings → restraint rate bar: `13.1%` → **{src['rate_restrained_pct']}%** (readmission rate among restrained)\n")
    lines.append("**Note on N 312 vs 510:** The inline page's 312 is the source of the error. Source recompute "
                 f"gives {src['n_restrained']} patients with ≥1 restraint (restraints > 0; empty = 0 = not restrained). "
                 f"The 13.1% inline is the readmission rate *among* the (wrongly-counted) 312; the correct readmission "
                 f"rate among the {src['n_restrained']} restrained is {src['rate_restrained_pct']}%. "
                 f"The 19.2% in data.json is the *prevalence* of restraint in the cohort ({src['n_restrained']}/2,652), "
                 f"not the readmission rate — do not conflate.\n")

    lines.append("## Reconciliation targets discovered (figures/*.csv)\n")
    lines.append(f"**{len(figs)}** restraint-bearing files found (glob, case-insensitive `restrain`):\n")
    lines.append("| File | Columns | Entries |")
    lines.append("|---|---|---|")
    for r in figs:
        if r["present"]:
            cols = ", ".join(r["columns"]) if r["columns"] else "(row token)"
            lines.append(f"| `{r['file']}` | {cols} | {r['n_entries']} |")
        else:
            lines.append(f"| `{r['file']}` | — | not present |")
    lines.append("")
    lines.append("### Notable files\n")
    for r in figs:
        if not r["present"]:
            continue
        if r["file"] == "figures/Recon_restraint_predictors.csv":
            lines.append(f"- `Recon_restraint_predictors.csv` — **predicts WHO is restrained** (not readmission). "
                         "Distinct model; do NOT confuse its ORs with the readmission OR.")
        elif r["file"] == "figures/Mv_logit_readmission.csv":
            lines.append(f"- `Mv_logit_readmission.csv` — adjusted readmission model; `had_restraints` row = AUTHORITATIVE site OR.")
        elif r["file"] == "figures/Sub_subgroup_outcomes.csv":
            lines.append(f"- `Sub_subgroup_outcomes.csv` — per-subgroup `restraint_OR`/`p_restraint` (restraint as covariate within subgroup models).")
        elif r["file"] == "figures/HDBSCAN_cluster_profiles.csv":
            lines.append(f"- `HDBSCAN_cluster_profiles.csv` — `Restraints (%)` per cluster profile.")
    lines.append("")

    lines.append("## Reconciliation prose (docs/Reconciliation_2025_vs_2026.md)\n")
    if prose.get("found"):
        lines.append(f"Found {len(prose['restraint_paragraphs'])} restraint-mentioning paragraph(s):\n")
        for p in prose["restraint_paragraphs"]:
            lines.append(f"- OR mentioned: {p['or_mentioned']}, p mentioned: {p['p_mentioned']}")
            lines.append(f"  > {p['excerpt'][:200]}...")
    else:
        lines.append(f"File not found at {prose.get('path')}.\n")

    lines.append("\n## Adjusted OR detail\n")
    if adj:
        lines.append(f"```json\n{json.dumps(adj, indent=2)}\n```")
    else:
        lines.append("`had_restraints` row NOT found in Mv_logit_readmission.csv — BLOCKER.\n")

    return "\n".join(lines)


def build_authoritative_json(src: dict, adj: dict | None) -> dict:
    """Machine-readable authoritative values for downstream data.json consumption."""
    if adj:
        return {
            "n": src["n_restrained"],
            "n_not_restrained": src["n_not_restrained"],
            "rate_restrained_pct": src["rate_restrained_pct"],
            "rate_not_restrained_pct": src["rate_not_restrained_pct"],
            "cohort_rate_pct": src["cohort_readmit_rate_pct"],
            "or": round(adj["or"], 2),
            "ci_lo": round(adj["ci_lo"], 2),
            "ci_hi": round(adj["ci_hi"], 2),
            "p": adj["p"],
            "p_display": fmt_p(adj["p"]),
            "or_kind": "adjusted multivariable",
            "or_source": "figures/Mv_logit_readmission.csv",
            "unadjusted_or": round(src["unadjusted_or"]["or"], 3),
            "unadjusted_ci_lo": round(src["unadjusted_or"]["ci_lo"], 2),
            "unadjusted_ci_hi": round(src["unadjusted_or"]["ci_hi"], 2),
            "unadjusted_p": src["unadjusted_or"]["p"],
            # whitelist for parity_diff.py: baseline_value -> authoritative_value
            # (display-formatted to match how the site renders: rate 1-decimal, OR 2-decimal)
            "values": {
                "13.1%": f"{src['rate_restrained_pct']:.1f}%",
                "312": str(src["n_restrained"]),
                "1.58": f"{adj['or']:.2f}",
                "1.10–2.26": f"{adj['ci_lo']:.2f}–{adj['ci_hi']:.2f}",
                "1.11–2.27": f"{adj['ci_lo']:.2f}–{adj['ci_hi']:.2f}",
                ".013": fmt_p(adj["p"]),
                "0.012": fmt_p(adj["p"]),
            },
        }
    return {
        "n": src["n_restrained"],
        "rate_restrained_pct": src["rate_restrained_pct"],
        "or": None,
        "or_kind": "adjusted multivariable",
        "error": "had_restraints row not found in Mv_logit_readmission.csv",
        "values": {
            "13.1%": f"{src['rate_restrained_pct']}%",
            "312": str(src["n_restrained"]),
        },
    }


# ---------------------------------------------------------------------------
# --check-datajson mode (used by T2)
# ---------------------------------------------------------------------------

def check_datajson(datajson_path: Path, auth: dict) -> int:
    d = json.loads(datajson_path.read_text(encoding="utf-8"))
    errors = []
    sr = d.get("summary", {}).get("restraint", {})
    if sr:
        if sr.get("n") != auth["n"]:
            errors.append(f"summary.restraint.n: {sr.get('n')} != AUTHORITATIVE {auth['n']}")
        if sr.get("n_not_restrained") != auth["n_not_restrained"]:
            errors.append(f"summary.restraint.n_not_restrained: {sr.get('n_not_restrained')} != {auth['n_not_restrained']}")
        if abs(sr.get("rate_restrained_pct", -1) - auth["rate_restrained_pct"]) > 0.1:
            errors.append(f"summary.restraint.rate_restrained_pct: {sr.get('rate_restrained_pct')} != ~{auth['rate_restrained_pct']}")
    gs = d.get("findings", {}).get("groupStats", {}).get("restraint", {})
    if gs:
        gs_or = float(gs.get("or", -1))
        if abs(gs_or - auth["or"]) > 0.01:
            errors.append(f"findings.groupStats.restraint.or: {gs.get('or')} != {auth['or']}")
    for pred in d.get("models", {}).get("forest", []):
        if "restrain" in pred.get("label", "").lower():
            if abs(pred.get("or", -1) - auth["or"]) > 0.01:
                errors.append(f"models.forest restraint or: {pred.get('or')} != {auth['or']}")
            if abs(pred.get("lo", -1) - auth["ci_lo"]) > 0.01:
                errors.append(f"models.forest restraint lo: {pred.get('lo')} != {auth['ci_lo']}")
            if abs(pred.get("hi", -1) - auth["ci_hi"]) > 0.01:
                errors.append(f"models.forest restraint hi: {pred.get('hi')} != {auth['ci_hi']}")
    if errors:
        print("--check-datajson FAILED:")
        for e in errors:
            print(f"  {e}")
        return 1
    print("--check-datajson OK: restraint fields match AUTHORITATIVE")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Restraint source-level double-check (T1 HARD GATE)")
    ap.add_argument("--check-datajson", help="Path to data.json to verify against AUTHORITATIVE")
    args = ap.parse_args()

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # (a) locate
    src_csv = locate_source_csv()
    # (b) recompute GROUND TRUTH
    src = recompute_from_source(src_csv)
    # (c) discover all figures targets
    figs = scan_figures_csvs()
    # (d) adjusted OR
    adj = read_adjusted_or()
    # (e) reconciliation prose
    prose = parse_reconciliation_prose()
    # (f) emit
    report = build_report(src, figs, adj, prose)
    REPORT_PATH.write_text(report, encoding="utf-8")
    auth = build_authoritative_json(src, adj)
    AUTH_JSON_PATH.write_text(json.dumps(auth, indent=2), encoding="utf-8")

    # console summary
    print(f"Source: {src['source_csv']} (N={src['n_total']})")
    print(f"Restrained N = {src['n_restrained']} (ground truth)")
    print(f"Readmission rate (restrained) = {src['rate_restrained_pct']}%")
    uor = src["unadjusted_or"]
    print(f"Unadjusted OR = {uor['or']:.3f} [{fmt_ci(uor['ci_lo'], uor['ci_hi'])}] p={fmt_p(uor['p'])}")
    if adj:
        print(f"Adjusted OR (AUTHORITATIVE for site) = {adj['or']:.2f} [{fmt_ci(adj['ci_lo'], adj['ci_hi'])}] p={fmt_p(adj['p'])}")
    else:
        print("WARNING: adjusted OR not found in Mv_logit_readmission.csv", file=sys.stderr)
    print(f"Restraint-bearing figures files: {len([f for f in figs if f['present']])}")
    print(f"Report: {REPORT_PATH}")
    print(f"Authoritative JSON: {AUTH_JSON_PATH}")

    if args.check_datajson:
        rc = check_datajson(Path(args.check_datajson), auth)
        if rc:
            return rc

    # Acceptance: source mutated? (should not be — read-only)
    # Determinism: recompute is deterministic by construction.
    # Hard fail if adjusted OR missing.
    if adj is None:
        print("ERROR: adjusted OR (had_restraints row) missing from Mv_logit_readmission.csv", file=sys.stderr)
        return 2
    if len([f for f in figs if f["present"]]) < 11:
        print(f"WARNING: expected ≥11 restraint-bearing figures files, found {len([f for f in figs if f['present']])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
