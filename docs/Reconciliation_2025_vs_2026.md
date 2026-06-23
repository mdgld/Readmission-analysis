# Reconciling the Original (2025) and Re-Analysis (2026) Findings
### Psychiatric rehospitalization in school-aged children (single Arizona site; admissions 2017–2024)

*Prepared for Dr. Ritfeld and AACAP 2026 poster development. Every 2026 statistic below was
re-derived from the complete dataset `annotated_psychiatric_data_complete.csv` (N = 2,652 patients)
in `Readmission_2026_Extended_Analysis.ipynb`; supporting figures are named in the text. The original
2025 submission is treated as the reference point, and — because it was the submitter's own early
work on this cohort — its differences are addressed openly rather than defended.*

> **A note on what this document can now do.** The original 2025 modeling notebook *and its source
> data* have been recovered, and the source file contains the **identical 2,652-patient cohort** used
> here. The original models were therefore **re-run on their own data**, so the predictor differences
> are no longer hypothesized — they are demonstrated to be a matter of **model specification on
> identical data** (see §8 for the verified numbers). Where a difference can be explained from the data
> alone — the readmission rate (events vs patients) and the predictor specifications — it is now stated
> as fact. A companion document, `Analysis_Comparison_2025_vs_2026.md`, covers the same ground in
> tabular form.

---

## 1. Summary of what prompted this reconciliation

The 2025 submission reported three claims that do not all reproduce on careful re-analysis: a
readmission rate of approximately 10%, and a multivariable analysis that "found no independent
predictors among ACE score, restraint use, gender, insurance type, or diagnosis count," with
suicidality likewise non-predictive. The re-analysis confirms some of these statements and revises
others. Both discrepancies are now resolved as fact rather than hypothesis. The readmission-rate
discrepancy is a matter of arithmetic on a single dataset (events versus patients). The
multivariable-predictor discrepancy has likewise been settled directly: the original modeling notebook
and its source data were recovered, the source file contains the **identical 2,652-patient cohort and
outcome** used here, and the original models were **re-run on that data** (§8). The difference is
therefore demonstrably one of **model specification on identical data** — not a difference of cohort,
outcome definition, sample size, or data handling. The sections below address each claim in turn.

---

## 2. The readmission rate: 10% versus 9.3% is a numerator definition, not a data change

The outcome is rehospitalization **within 90 days of discharge** — the same window the 2025 study used.
(This was verified directly: the `Readmissions` field is 97% concordant with the independent 90-day
readmission flag in the Excel extract on the 1,206 patients common to both, and it correctly excludes
patients readmitted only after 90 days.) Of the 2,652 children, 246 were readmitted within 90 days, so
the correct **patient-level 90-day readmission rate is 9.3%** (246 / 2,652). The originally reported
figure of roughly 10% corresponds instead to the **event count**: the `Readmissions` field records 219
children readmitted once, 25 readmitted twice, and 2 readmitted three times, summing to 275 readmission
*events* (219 + 50 + 6). Dividing those 275 events by the 2,652 patients yields 10.4%, the number
recomputed independently as "10.3% total." The two figures differ only because the event count credits
the 27 children with more than one readmission multiple times. For a patient-level outcome — "what
fraction of children were rehospitalized within 90 days?" — the appropriate statistic is 9.3%, and that
is what the abstract should report. This is a numerator-definition correction within a single dataset,
not a discrepancy between cohorts or windows.

It is worth stating explicitly that the complete 2,652-patient file is the final dataset. A separate
1,920-encounter Excel extract (`2025 data/Psychiatry_readmissions_cleaned.xlsx`) carries detailed
readmission dates and is the only source permitting time-windowed analysis; it represents a
preliminary subset (1,206 of its patients link to the final cohort) and is used in this re-analysis
only for the timing and provider analyses, which are labeled as preliminary throughout.

---

## 3. The "no independent predictors" finding: a verified model-specification difference

The most consequential discrepancy concerns the multivariable model, and it has now been resolved
directly by re-running the original on its own data (§8). The 2025 submission reported that ACE score, restraint use, gender,
insurance type, and diagnosis count were not independently predictive of readmission, with
suicidality likewise non-predictive. The present, fully specified re-analysis on the complete
2,652-patient cohort instead identifies several independent predictors and one protective association
(`figures/Mv_logit_readmission.csv`; forest plot `figures/Mv_logit_forest.png`):

| Predictor | Adjusted OR | 95% CI | p |
|---|---|---|---|
| Suicidal ideation (ICD R45.851) | 2.59 | 1.82–3.66 | <0.001 |
| Depressive-disorder burden | 1.73 | 1.21–2.46 | 0.003 |
| Diagnostic complexity (per added DSM-5 category) | 1.34 | 1.19–1.51 | <0.001 |
| Physical restraint use | 1.52 | 1.06–2.17 | 0.023 |
| Younger age (per additional year of age) | 0.91 | 0.84–0.99 | 0.023 |
| Non-suicidal self-injury (NSSI) | 0.40 | 0.27–0.59 | <0.001 (protective) |
| ACE score, C-SSRS flags, gender (identity at admission), insurance, length of stay | not significant | — | >0.05 |

Both the comparison and its cause are now established, because the original models were re-run on the
identical cohort (§8). The divergence is demonstrably one of **model specification**, and the specific
choices responsible are known: in the 2025 model, restraint was entered as a **frequency count** (and
additionally absorbed into a composite "externalizing" term), and suicidality was folded into a broad
composite, inside a model that **failed to converge** because one covariate was present in 99.8% of
children. Re-fitting the same data with restraint as a binary flag and suicidal ideation as its own
diagnosis code recovers the associations (§8). Two alternative explanations can therefore be positively
**excluded**: a different outcome definition and a different sample — both the cohort (2,652 children)
and the outcome (`Readmissions > 0`) are identical across the two analyses. An earlier draft of this
document attributed the divergence to the *unit of diagnostic analysis* (individual ICD codes versus
aggregated DSM-5 categories); that explanation is also insufficient, since it cannot move the
non-diagnostic predictors (restraint, the diagnostic-complexity count, and age) and does not fit the
suicidality result, which is predictive under the original's own ICD-code measure. The accurate,
defensible characterization is not that restraint was *omitted* in 2025 — the submission listed it among
the variables tested — but that it was coded in a way (a count, double-entered, inside an unstable
model) that prevented it from reaching significance; coded as a simple yes/no on the same data, it
reaches significance.

Two operational clarifications support these results. *Diagnostic complexity* here is the count of
distinct **DSM-5 categories** (median 3), which is coarser than the count of distinct **ICD-10
diagnoses** (median 6, only moderately correlated, ρ≈0.58); the readmission association holds under
both (adjusted OR ≈1.36 per category and ≈1.05 per distinct diagnosis, both p < 0.001), so it is not an
artifact of how complexity is defined (`figures/Biv_14_complexity_measures.*`). *ACE* remains
non-predictive even under the broader ACEs Aware pediatric definition of "high ACE" (score ≥4, or 1–3
with a physical ACE-Associated Health Condition such as asthma or severe obesity); that tiering reveals
a modest *unadjusted* gradient (low 5.5%, intermediate 8.9%, high 9.4%) that does not survive
adjustment (§3A; `figures/Biv_13_ace_expanded.*`).

---

## 4. ACE replicates as null; suicidality depends entirely on how it is measured

ACE score is the one variable that replicates cleanly: after adjustment it is not associated with
readmission (OR 1.04 per point, p = 0.38 in the complete-case model that includes it; bivariate view
`figures/Biv_04_ace_readmit.png`), concordant with 2025. A clinically meaningful but separate
observation is that ACE scores are substantially higher among publicly insured children (median 4
versus 2; Mann-Whitney p < 0.001; `figures/Biv_07_ace_insurance.png`), an equity signal that bears on
interpretation even though ACE does not itself predict readmission.

Suicidality is more delicate, and it is essential to specify the measure. The original analysis
operationalized suicidality through an **ICD diagnosis code** (suicidal ideation, R45.851), not
through the C-SSRS flag columns; the two capture different constructs and, in this cohort, point in
opposite directions (`figures/Biv_04b_suicidality_measures.png`). Measured the original's way, the
suicidal-ideation code is present in 50.8% of children and is **strongly and independently predictive**
of readmission (adjusted OR 2.59, 95% CI 1.82–3.66, p < 0.001; readmission 11.4% with the code versus
7.1% without). The C-SSRS flags, by contrast, are non-predictive (univariate OR 1.03, p = 0.86;
adjusted OR ≈ 1.00). The implication is important and should not be soft-pedaled: under the same
ICD-code definition the original used, suicidality does **not** replicate as null — the re-analysis
finds it among the strongest predictors. This is therefore a genuine divergence rather than a
concordance, and the apparent agreement disappears once the correct measure is compared. A further
clinically coherent contrast accompanies it: non-suicidal self-injury (NSSI), a distinct DSM-5
category, is *protective* (adjusted OR 0.40, p < 0.001), so the two self-harm constructs separate
sharply — suicidal ideation marking higher readmission risk and NSSI marking lower — which is itself a
substantive new finding rather than an artifact.

---

## 5. Restraint use and length of stay: a robust, separable finding

Although restraint use is only a modest predictor of readmission, it is the dominant correlate of
index length of stay. In the multivariable linear model (`figures/Mv_ols_los.csv`) restraint use is
associated with roughly six additional inpatient days, and the bivariate contrast is of similar
magnitude (median 12 versus 8 days; Mann-Whitney p < 0.001; `figures/Biv_06_restraint_los.png`). The
effect behaves as a binary signal rather than a dose: the restraint *count* correlates with length of
stay largely because any restraint marks a more acute admission. This finding is stable across
specifications and is independent of the readmission question.

---

## 6. The methodological headline: categories average over opposite subgroups

The subgroup analysis (`figures/Sub_forest_panels.png`, `figures/Sub_subgroup_outcomes.csv`) supplies
the poster's principal methodological message. Broad DSM-5 categories conceal clinically opposite
subgroups, so that a category can appear neutral on average while containing both elevated- and
reduced-risk constituents — the suicidal-ideation-versus-NSSI split in §4 is a concrete example. This
is a finding in its own right and a caution about interpretation: it argues against reducing
readmission risk to any single coarse diagnostic label. It is *not*, however, offered as the
explanation for the §3 predictor divergence, which extends to non-diagnostic variables and is better
understood as a power/specification difference (§3, §8).

---

## 7. Prediction remains limited, honestly reported

The predictive models reinforce caution. Across logistic regression, random forest, and CatBoost, the
out-of-fold area under the ROC curve sits between 0.64 and 0.68 (`figures/MLx_roc.png`,
`figures/MLx_oof_performance.csv`), and augmenting the feature set with additional diagnostic flags
does not improve discrimination — a bootstrap comparison finds the augmented model marginally *worse*
out-of-fold (ΔAUC −0.010), the expected behavior of a model already at its information ceiling. High
apparent AUCs from unvalidated tree models are optimism artifacts and are not reported as performance.
The practical implication is that these variables characterize *population-level* risk factors but
cannot triage individual children, and the abstract should claim no more than that.

---

## 8. The original 2025 analysis, reproduced: the divergence is specification, not data

The original 2025 notebooks have been located (`2025 data/e3b1900e-….ipynb`, the modeling notebook)
together with their source data (`2025 data/1854 …(Patient Info).csv`). That file contains the
**identical 2,652-patient cohort** used here (same readmission distribution: 2,406/219/25/2), and the
original outcome is the same — `Readmissions > 0` (9.3%). The notebooks were saved without outputs, so
the original models were **re-run on their own source data** to obtain verified numbers. The result
settles the predictor question: the difference between the 2025 conclusion and the present one is due
**entirely to model specification, not to the data or the cohort.**

The original *primary* multivariable model — the basis for "no independent predictors" — is
demonstrably degenerate. Re-fitting it reproduces a model that **fails to converge**, because one of
its terms, a psychiatric-comorbidity flag, is present in **99.8%** of children (essentially a
constant) and induces **complete separation** (its odds ratio explodes to ~10⁸ with p≈1.0 — a
mathematical artifact, not a finding). Within that unstable model, restraint use was entered as a
**count** (OR 1.00, p=0.90) *and* simultaneously **double-counted** inside a composite "externalizing"
term, so it could not surface independently; and suicidality was entered as a broad composite
(C-SSRS flags **or** ACE ≥4 **or** PTSD codes **or** self-harm codes), which diluted it to OR 1.33
(p=0.10).

Re-fitting cleaner specifications **on the very same 2,652-patient file** tells the opposite story:

| Specification (original data, N=2,652) | OR | p |
|---|---|---|
| Restraint as a **count** (as the abstract's model used it) | 1.00 | 0.90 |
| Restraint as a **binary** flag (any vs none), univariate | **1.74** | <0.001 |
| Restraint (binary), adjusted for externalizing diagnoses | **1.39** | 0.04 |
| Suicidal ideation, **ICD code R45.851** alone (vs the broad composite) | **1.65** | <0.001 |

So restraint use and suicidal ideation are both associated with readmission in the original data; the
2025 abstract missed them because of three specification choices — coding restraint as a frequency
rather than a yes/no, double-entering it, and burying suicidal ideation inside a heterogeneous
composite — compounded by a non-converging model. The present re-analysis, with restraint as a binary
flag and suicidal ideation as its own code, reproduces these signals (adjusted OR 1.52 and 2.59) and
adds appropriate covariates. The honest, collegial framing for Dr. Ritfeld is therefore not that a
variable was "overlooked," but that **the prior abstract rested on one unstable model specification,
and re-analysis on the same data shows the associations were present all along.** This re-analysis,
fully documented with saved outputs in `Readmission_2026_Extended_Analysis.ipynb`, is the
authoritative, reproducible record for the cohort.

---

## 9. What changed, and the standing of each explanation

| Original 2025 statement | Re-analysis (2026) | Explanation and its standing |
|---|---|---|
| Readmission rate ≈ 10% | 9.3% per patient (246/2,652); 10.4% is the event count (275 events) | **Demonstrated** from current data: events double-count the 27 children readmitted more than once |
| No independent predictors among ACE, restraint, gender, insurance, diagnosis count | Suicidal ideation–ICD (OR 2.59), depressive burden (1.73), diagnostic complexity (1.34), restraint (1.52), younger age (0.91) independent; NSSI protective (0.40) | **Demonstrated** by re-running the original on the identical cohort (§8): a **model-specification** difference — restraint coded as a count + double-counted, suicidality a broad composite, inside a non-converging model. Same cohort/outcome rule out sample-size and outcome-definition explanations |
| Restraint use non-predictive | Independently predictive; dominant driver of length of stay | Comparison **demonstrated**; restraint was **tested, not omitted**, in 2025 — firm from the submission text |
| Suicidality non-predictive | **Predictive** when measured as the original did, by ICD code (R45.851, OR 2.59); C-SSRS flags (different construct) non-predictive (OR 1.03) | Comparison **demonstrated**; this is a genuine **divergence**, not a replication — agreement was an artifact of comparing the wrong measure |
| ACE non-predictive | Non-predictive (OR 1.04, n.s.); but higher in publicly insured children | **Replicates** for readmission (the one clean concordance); equity signal is a separate, new observation |

---

## 10. Recommended framing for the abstract and the note to collaborators

Three practical recommendations follow from the sections above (the underlying detail is in §3 and §8
and is not repeated here). First, **report the rate as the patient-level 9.3%**, mentioning the
event-based 10.4% only to explain the earlier figure, and present any time-windowed or readmission-stay
results explicitly as the **preliminary 1,920-encounter subset**, not the full cohort. Second, **own the
predictor discordance in the submission itself**: because the published 2025 study is the reference, the
abstract and poster should state plainly that re-analysis of the identical cohort corrected a
model-specification problem (a non-converging model), so the previously null predictors emerge — framed
as a fixable specification issue on the same data, not a disagreement between datasets. Third, **avoid
two specific overstatements**: that any variable was *omitted* in 2025 (restraint was tested, merely
coded as a count), and that suicidality *replicates* as null (under its ICD-code measure it does not).
The defensible poster claims are that roughly one in eleven children was rehospitalized within 90 days;
that suicidal ideation, depressive burden, diagnostic complexity, restraint use, and younger age are
independent correlates of readmission while non-suicidal self-injury is protective; that restraint use
is the principal driver of length of stay; and that individual-level prediction remains beyond reach
with these single-site data.

---

## Appendix A — How each variable was measured (so the methods are unambiguous)

Precise operationalization matters here, because two of the central disagreements with 2025 turned on
*how* a construct was defined rather than on the data. The readmission outcome is patient-level: a child
counts as readmitted if the `Readmissions` field is greater than zero — that is, if they were
rehospitalized **within 90 days of discharge** (verified against the Excel extract's 90-day flag) —
which yields 246 of 2,652 (9.3%). Length of stay is the discharge date minus the
admission date in days. Restraint use is treated as a binary indicator of whether any physical restraint
episode was recorded, because the signal is carried by the fact of restraint rather than by its
frequency; the raw count is not dose-dependent. Gender is the gender identity recorded at admission (the
`GenderCode` field), not natal sex, and public insurance denotes AHCCCS, Arizona's Medicaid program.

Suicidality is deliberately measured two ways, because the two measures diverge and the original analysis
used the diagnosis-code version. The first is the ICD-10 code R45.851 ("suicidal ideation"), present in
roughly half the cohort and strongly associated with readmission; the second is the set of C-SSRS
screening flags (the yellow, orange, and red columns, coded by presence), which are not associated with
readmission. Reporting both, and labeling which is which, prevents the apparent contradiction that arises
when "suicidality" is left undefined. Adverse childhood experiences are captured by the recorded ACE
score (0–10); for a clinically grounded "high ACE" category we follow the ACEs Aware pediatric algorithm,
under which a child is high-risk if the ACE score is four or more, or one to three accompanied by a
physical ACE-Associated Health Condition (asthma, severe obesity, atopy or eczema, recurrent headaches,
unexplained somatic symptoms, sleep disturbance, enuresis or encopresis, or failure to thrive). ACE is
non-predictive of readmission under either the simple threshold or this expanded definition.

Diagnostic complexity is reported in two complementary ways — the number of distinct DSM-5 *categories* a
child's diagnoses span (median three) and the number of distinct ICD-10 *codes* they carry (median six) —
and the readmission association holds under both, so it is not an artifact of the coarser measure. The
individual diagnosis indicators (depressive disorders, trauma- and stressor-related disorders, ADHD,
non-suicidal self-injury, and so on) are presence flags built by matching each child's diagnoses to DSM-5
*category* labels, so they operate at the category level rather than at the level of individual codes.

## Appendix B — The machine learning, in plain language

A statistical distinction underlies this whole section and is worth stating plainly: showing that two
variables are *associated* is not the same as showing that one *predicts* the other. The 2025 abstract
used the language of prediction, but a regression read for its coefficients is an association analysis;
this re-analysis separates the two questions and answers them with two different kinds of model. To
describe *associations* — which factors are linked to readmission once the others are accounted for — we
used logistic regression, the standard method that yields the odds ratios quoted above. To test
*prediction* — whether, knowing everything recorded at discharge, we could flag in advance which
individual child would return — we used machine-learning classifiers, specifically a random forest and
gradient boosting (CatBoost). These learn complex, non-linear combinations of features that a single regression
line cannot, which makes them powerful but also prone to over-fitting: looking impressive on the children
they were trained on while failing on new ones.

To keep the predictive claims honest, the models were judged only on children they had never seen, using
ten-fold cross-validation — training on ninety percent of the cohort, testing on the held-out ten percent,
and rotating through — together with a bootstrap optimism correction that estimates and subtracts the
remaining over-optimism. Judged this way, the models reach an out-of-fold area under the ROC curve of
about 0.66 to 0.68, where 0.5 is a coin flip and 1.0 is perfect; the higher "apparent" values near 0.85
are mirages that disappear under proper validation. At any clinically useful operating point the positive
predictive value is only about fifteen to twenty percent, meaning roughly four of every five flagged
children would not actually be readmitted. We also examined fairness — whether error rates differ by age,
gender, insurance, or ACE category — and found appreciable gaps by age and gender. The honest conclusion,
and the one the poster makes, is that these models surface real population-level risk factors but cannot
responsibly triage an individual child; identifying risk factors proved far easier than building a
deployable predictive tool from a single, modestly sized site.
