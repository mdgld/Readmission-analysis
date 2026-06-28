#!/usr/bin/env python3
"""Parity comparator — verifies rendered DOM preserves baseline statistics.

Usage:
  python3 tools/parity_diff.py --dom <dump> --baseline <baseline-numbers.md> [--restraint-whitelist <json>]
  python3 tools/parity_diff.py --selftest

Exits 0 if all baseline statistics are found in the DOM (or match the
authoritative whitelist for restraint items).  Exits 1 on any unexplained
MISSING or CHANGED token.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_baseline(path: str) -> list[tuple[str, str, str]]:
    """Parse baseline-numbers.md -> list of (value, label, source) tuples.

    Each data row has the format:  value | label | source
    Lines starting with '#' or table separators are skipped.
    """
    rows: list[tuple[str, str, str]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("|") and "---" in stripped:
            continue
        parts = [p.strip() for p in stripped.split("|")]
        if len(parts) >= 3 and all(parts[:3]):
            rows.append((parts[0], parts[1], parts[2]))
    return rows


# ---------------------------------------------------------------------------
# Normalisation & search
# ---------------------------------------------------------------------------

_DASH_MAP = str.maketrans({
    "\u2013": "-",  # en-dash
    "\u2014": "-",  # em-dash
    "\u2212": "-",  # minus sign
})


def normalize(text: str) -> str:
    """Normalise unicode dashes and whitespace for robust comparison."""
    return text.translate(_DASH_MAP).replace("\xa0", " ").strip()


def value_in_dom(value: str, dom_text: str) -> bool:
    """Return True if *value* appears as a substring in the DOM text.

    Both haystack and needle are normalised (en-dash -> hyphen, nbsp -> space)
    so that ``1.23–2.58`` in the baseline matches ``1.23-2.58`` in the DOM.
    """
    return normalize(value) in normalize(dom_text)


# ---------------------------------------------------------------------------
# Restraint whitelist
# ---------------------------------------------------------------------------

def load_whitelist(path: str) -> dict[str, str]:
    """Load a restraint-whitelist JSON mapping baseline_value -> authoritative_value.

    Expected schema::

        {
          "values": {
            "13.1%": "13.5%",
            "312":   "510",
            "1.58":  "1.52",
            ...
          }
        }

    A flat ``{old: new}`` dict at the top level is also accepted.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "values" in raw and isinstance(raw["values"], dict):
        return {str(k): str(v) for k, v in raw["values"].items()}
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    raise ValueError("restraint-whitelist JSON must be an object or have a 'values' object")


def is_restraint_label(label: str) -> bool:
    """Heuristic: labels prefixed with 'restraint:' are reconciliation targets."""
    return label.lower().startswith("restraint:")


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------

def check_parity(
    baseline_rows: list[tuple[str, str, str]],
    dom_text: str,
    whitelist: dict[str, str] | None = None,
) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str, str]], list[tuple[str, str, str]]]:
    """Return (ok, changed, missing) lists.

    - *ok*: (value, label, source) — value found in DOM.
    - *changed*: (baseline_value, authoritative_value, label, source) — restraint
      item where the baseline value is gone and the authoritative value is present.
    - *missing*: (value, label, source) — neither baseline nor authoritative found.
    """
    ok: list[tuple[str, str, str]] = []
    changed: list[tuple[str, str, str, str]] = []
    missing: list[tuple[str, str, str]] = []

    for value, label, source in baseline_rows:
        is_restraint = is_restraint_label(label)
        auth_value: str | None = None

        if is_restraint and whitelist:
            auth_value = whitelist.get(value)
            if auth_value is not None and value_in_dom(auth_value, dom_text):
                changed.append((value, auth_value, label, source))
                continue
            if auth_value is not None and value_in_dom(value, dom_text):
                # Old value still present — should have been replaced.
                missing.append((f"{value} (expected {auth_value})", label, source))
                continue

        if value_in_dom(value, dom_text):
            ok.append((value, label, source))
        else:
            missing.append((value, label, source))

    return ok, changed, missing


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def report(ok, changed, missing) -> None:
    print(f"Parity check: {len(ok)} OK, {len(changed)} CHANGED (restraint-corrected), {len(missing)} MISSING")
    if changed:
        print("\nCHANGED (restraint reconciliation — expected):")
        for old, new, label, src in changed:
            print(f"  {old} -> {new}  |  {label}  |  {src}")
    if missing:
        print("\nMISSING / UNEXPECTED:")
        for value, label, src in missing:
            print(f"  {value}  |  {label}  |  {src}")


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_selftest() -> int:
    """Plant a missing token in a fixture and assert the comparator flags it."""
    fixture_baseline = (
        "9.3% | cohort readmission rate | test:1\n"
        "2,652 | patients | test:2\n"
        "0.684 | best OOF AUC | test:3\n"
    )
    # DOM contains 9.3% and 2,652 but NOT 0.684
    fixture_dom = "The cohort had 2,652 patients with a 9.3% readmission rate."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as bf:
        bf.write(fixture_baseline)
        bpath = bf.name
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as df:
        df.write(fixture_dom)
        dpath = df.name

    try:
        rows = parse_baseline(bpath)
        assert len(rows) == 3, f"Selftest: expected 3 baseline rows, got {len(rows)}"

        ok, changed, missing = check_parity(rows, fixture_dom)
        assert len(ok) == 2, f"Selftest: expected 2 OK, got {len(ok)}"
        assert len(missing) == 1, f"Selftest: expected 1 MISSING, got {len(missing)}"
        assert missing[0][0] == "0.684", f"Selftest: expected 0.684 missing, got {missing[0][0]}"

        # Also test the restraint whitelist path
        wl = {"9.3%": "10.0%"}
        ok2, changed2, missing2 = check_parity(rows, fixture_dom, whitelist=wl)
        # 9.3% is not a restraint: label, so whitelist is ignored — still OK
        assert len(ok2) == 2, f"Selftest: non-restraint whitelist mismatch: ok={len(ok2)}"

        print("Selftest PASSED: comparator correctly flags missing token 0.684")
        return 0
    except AssertionError as exc:
        print(f"Selftest FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        os.unlink(bpath)
        os.unlink(dpath)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Parity comparator for portfolio rebuild")
    ap.add_argument("--dom", help="Path to rendered DOM text dump")
    ap.add_argument("--baseline", help="Path to baseline-numbers.md")
    ap.add_argument("--restraint-whitelist", help="JSON with authoritative restraint values")
    ap.add_argument("--selftest", action="store_true", help="Run internal self-test and exit")
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    if not args.dom or not args.baseline:
        ap.error("--dom and --baseline are required (unless --selftest)")

    dom_text = Path(args.dom).read_text(encoding="utf-8")
    baseline_rows = parse_baseline(args.baseline)

    whitelist: dict[str, str] | None = None
    if args.restraint_whitelist:
        whitelist = load_whitelist(args.restraint_whitelist)

    ok, changed, missing = check_parity(baseline_rows, dom_text, whitelist)
    report(ok, changed, missing)

    # Changed (restraint-corrected) is EXPECTED, not a failure.
    # Only unexplained MISSING is a failure.
    if missing:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    sys.exit(main())
