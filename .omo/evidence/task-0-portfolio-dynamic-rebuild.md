# T0 — Baseline fidelity snapshot + reusable parity comparator

## Deliverables
- `.omo/evidence/baseline-index.html` — verbatim copy of current root `index.html` (782 lines)
- `.omo/evidence/baseline-data.txt` — extracted inline data block (lines 553–780, 228 lines)
- `.omo/evidence/baseline-numbers.md` — 174 data rows across 8 section groups (hero metrics, age/gender/C-SSRS/insurance/restraint demographics, 17-row DSM-5 spectrum, forest plot, model AUC, fairness, abstract results)
- `tools/parity_diff.py` — reusable read-only comparator with `--selftest`

## Acceptance criteria (all PASS)
- `test -f .omo/evidence/baseline-index.html` ✓
- `test -f .omo/evidence/baseline-numbers.md` ✓
- `test -f tools/parity_diff.py` ✓
- `baseline-numbers.md` row count = 174 (≥70 required) ✓
- Every row matches `value | label | source` format ✓
- `python3 tools/parity_diff.py --selftest` exits 0 ✓ (correctly flags planted missing token 0.684)

## Section groups covered (8)
1. Hero metrics (9 stats)
2. Age bands (24 stats: 8 bands × rate/n/readmit)
3. Gender + C-SSRS + Insurance (each: 2 groups + OR/CI/p)
4. Restraint (2 groups + OR/CI/p — T1 RECONCILIATION TARGETS, labelled `restraint:`)
5. DSM-5 spectrum (51 stats: 17 cats × rate/n/readmit)
6. Forest plot (12 stats: 6 predictors × OR/CI)
7. Model AUC + optimism deltas (12 stats)
8. Fairness (8 stats) + abstract results (12 stats)

## Restraint values flagged for T1 reconciliation
- `13.1% | restraint: Restrained rate` (index.html:637)
- `312 | restraint: Restrained n` (index.html:637)
- `1.58 | restraint: group OR` (index.html:615)
- `1.10–2.26 | restraint: group CI` (index.html:615)
- `.013 | restraint: group p` (index.html:615)
- `1.58 | restraint: forest OR` (index.html:680)
- `1.11–2.27 | restraint: forest CI` (index.html:680)
- `1.58 | restraint: abstract OR` (index.html:753)
- `0.012 | restraint: abstract p` (index.html:753)

The `parity_diff.py` whitelist mechanism (`--restraint-whitelist`) will swap these to T1's AUTHORITATIVE values during the T10/T15 parity checks.

---

# OMO fallback debugging (side-quest requested by user)

## Symptom
User reported "token error" with fallbacks not firing despite `oh-my-openagent.jsonc` configuring `fallback_models` for every agent.

## Root cause (verified by reading plugin source)
1. **Config file precedence**: `oh-my-openagent.jsonc` is loaded (plugin `detectConfigFile`, dist/cli-node/index.js:6507 — `.jsonc` checked before `.json`). The `.json` sibling is ignored.
2. **`runtime_fallback.enabled: true` activates the runtime fallback path and DISABLES the `fallback_models` hook path** (dist/index.js:148275 `if (!runtimeFallbackEnabled) { await hooks.modelFallback... }` and :148950 `shouldHandleModelFallback = () => isModelFallbackEnabled && !isRuntimeFallbackEnabled`). The per-agent `fallback_models` arrays are still consumed, but ONLY by the runtime path (line 103561 `getFallbackModelsForSession`).
3. **`retry_on_errors` was commented out** in the user's config. The runtime path gates on `isRetryableError(error, config.retry_on_errors)` (line 103550). With `retry_on_errors` unset, it defaults to `DEFAULT_CONFIG2.retry_on_errors = [429,500,502,503,504]` (line 102357).
4. **401/403 (token/auth errors) are NOT in the default**. `isRuntimeFallbackRetryableError` (line 22189) returns true only for: `missing_api_key`/`model_not_found`/`quota_exceeded` error types, statusCodes in `retryOnErrors`, or rate-limit/overloaded message patterns. A 401 token error matches none → "Error not retryable, skipping fallback" (line 103551) → no fallback fires.

## Fix applied
Uncommented `retry_on_errors` in `oh-my-openagent.jsonc` and set to `[401, 403, 408, 425, 429, 500, 502, 503, 504, 529]`.

## Verification
- JSONC parses cleanly (node parse with comment/trailing-comma strip).
- `runtime_fallback.retry_on_errors` now includes 401 and 403.
- All 11 agents retain `fallback_models` chains (1–2 fallbacks each).
- With 401 now in `retry_on_errors`, `isRuntimeFallbackRetryableError` (line 22198: `if (statusCode && retryOnErrors.includes(statusCode)) return true`) will classify a 401 token error as retryable → the runtime path advances to the next model in the agent's `fallback_models` chain (which spans providers, so a different provider's credentials are used).

## Limitation
This fixes status-coded 401/403 errors (the common case — OpenAI/OpenRouter/Anthropic return HTTP 401 with a `statusCode` field). A pure message-based auth error with no numeric status code would still not match, because `RUNTIME_FALLBACK_RETRYABLE_ERROR_PATTERNS` (line 22136) is a compiled constant that cannot be extended via config. If such errors appear, the dist bundle would need patching (out of scope for a config fix).

## Restart required
opencode reads the config at startup. The fix takes effect on the next opencode launch — the current session was started with the old config.
