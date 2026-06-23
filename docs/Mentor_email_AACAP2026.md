**Subject: AACAP 2026 re-analysis — reconciling with last year's findings, and the ML approach**

Hi Dr. Ritfeld,

Thank you for meeting on short notice with me, and apologies for the delay — it took me a while to locate last year's original code. I've now re-run both the 2025 and 2026 analyses and I want to lay out what differs, why, and how I propose we handle it in the abstract, so that a reviewer comparing it to the published study finds the discrepancy already explained. The analytic errors were mine, and I've been trying to ask for help more often so that kind of issue isn't repeated.

The readmission rate (≈10% → 9.3%): A numerator error on my part: I divided the total number of readmission events (275) by patients, which double-counts the 27 children readmitted more than once within 90 days. The correct patient-level 90-day rate is 9.3% (247/2,652), which also matches the original export's summary sheet.

The "no independent predictors" result: I re-ran last year's model on last year's exact data and found that it never actually converged: I had included a "psychiatric comorbidity" flag that, at ~99.8% prevalence, is essentially a constant and caused complete separation (an astronomical, meaningless odds ratio that destabilized the whole model). Compounding that, restraint use was entered as a frequency count (only in the univariate analysis as a categorical value), and suicidality was defined as a composite of multiple factors.

Re-analyzing the original data with the original multivariate log regression model, just with the comorbidity flag removed, restraint use coded as a simple yes/no, and suicidal ideation as its own diagnosis code, R45.851, showed restraint use (OR ≈1.4–1.7 depending on adjustment) and suicidal ideation (OR ≈1.6) as significant.

The associations were present in last year's data all along; the original specification simply couldn't surface them.

I think this is reassuring rather than worrying — the conclusions that held up last year still hold: ACE category is not associated with readmission, ACE scores are significantly higher among AHCCCS-insured children, and restraint use rises roughly linearly with length of stay. The findings that changed did so for a specific, demonstrable, and fixable reason.

How I propose to handle the discordance in the submission: Because the published study is now the reference, I've added one sentence to the abstract's conclusion stating that re-analysis of the identical cohort corrected a model-specification problem, so the previously null predictors emerge. That way the discrepancy is owned and explained within the abstract itself rather than left for a reviewer to infer. The poster discussion — due later — will develop that explanation in full.

The machine-learning approach, and a distinction I should have drawn last year: Strictly speaking, saying two variables are associated is not the same as saying one predicts the other. My goal from the beginning was to predict readmission risk, and last year's abstract used the language of prediction, but a regression read for its coefficients is really an association analysis. This year I separated the two questions. For association I used a standard (unpenalized) logistic regression — the source of the odds ratios above, and the same analysis that was used last year. For prediction I used two machine-learning classifiers, random forest and CatBoost (a form of gradient boosting), which "learn" complex, non-linear combinations of features that a single regression, or even ten, cannot.

Because such models tend to perform better at evaluating the data they were trained on compared to new data, I evaluated them using a bootstrap optimism correction. Translation: The original model performance forms the "baseline". You then evaluate this model on many "alternate-universe" patient samples created via "bootstrapping", sampling from the original distribution with replacement. The realistic evaluation of performance comes from subtracting the model's ability to predict outcomes using novel data from its ability to predict outcomes using the dataset it was trained on — "optimism".

Judged that way, and even with corrections for things like minority oversampling (only 9.3% of patients were readmitted), both types of model only reach an out-of-fold AUC of about 0.66–0.68, and at any clinically useful threshold only ~15–20% of flagged children would actually be readmitted. The take-home — and I think one of the most defensible contributions of this year's poster — is that we can identify real population-level risk factors but cannot yet predict readmission for an individual child from single-site data over a relatively short timeframe. That "limits of prediction" framing is honest, and it is what the abstract now leads with.

I've attached the revised abstract for your review. Thank you again for your guidance.

Best,
[Name]
