# Baseline Statistic Inventory — portfolio-dynamic-rebuild T0

Every displayed statistic in the current root `index.html`, grouped by section.
# Format: `value | label | source-line`
Total: ~90 distinct statistics.

## Hero metrics
2,652 | Patients | index.html:574
9.3% | 90-day readmission rate | index.html:575
246 | readmission events (sub) | index.html:575
1,863 | ICD-10-CM codes mapped | index.html:576
27,884 | Diagnosis records | index.html:577
31 | DSM-5 categories | index.html:578
0.684 | Best OOF AUC | index.html:579
9.7 | Mean age | index.html:580
2017–2024 | Study period | index.html:581

## Pipeline
1,863 | pipeline step 2 ICD-10 codes | index.html:586

## Findings — cohort baseline
9.3% | cohort readmission rate (findings legend) | index.html:156

## Age bands (8)
15.9% | age 5 rate | index.html:618
82 | age 5 n | index.html:618
13 | age 5 readmit | index.html:618
14.3% | age 6 rate | index.html:619
126 | age 6 n | index.html:619
18 | age 6 readmit | index.html:619
12.5% | age 7 rate | index.html:620
208 | age 7 n | index.html:620
26 | age 7 readmit | index.html:620
9.5% | age 8 rate | index.html:621
305 | age 8 n | index.html:621
29 | age 8 readmit | index.html:621
9.0% | age 9 rate | index.html:622
368 | age 9 n | index.html:622
33 | age 9 readmit | index.html:622
9.5% | age 10 rate | index.html:623
496 | age 10 n | index.html:623
47 | age 10 readmit | index.html:623
9.1% | age 11 rate | index.html:624
538 | age 11 n | index.html:624
49 | age 11 readmit | index.html:624
5.9% | age 12 rate | index.html:625
529 | age 12 n | index.html:625
31 | age 12 readmit | index.html:625

## Gender identity (2) + group stats
9.8% | Male rate | index.html:628
1,369 | Male n | index.html:628
134 | Male readmit | index.html:628
8.7% | Female rate | index.html:628
1,283 | Female n | index.html:628
112 | Female readmit | index.html:628
1.13 | gender OR | index.html:612
0.87–1.48 | gender CI | index.html:612
.349 | gender p | index.html:612

## C-SSRS flag (2) + group stats
8.9% | C-SSRS Any flag rate | index.html:634
1,180 | C-SSRS Any flag n | index.html:634
105 | C-SSRS Any flag readmit | index.html:634
9.6% | C-SSRS No flag rate | index.html:634
1,472 | C-SSRS No flag n | index.html:634
141 | C-SSRS No flag readmit | index.html:634
0.92 | cssrs OR | index.html:613
0.71–1.20 | cssrs CI | index.html:613
.546 | cssrs p | index.html:613

## Insurance (2) + group stats
9.7% | Public insurance rate | index.html:631
1,595 | Public n | index.html:631
155 | Public readmit | index.html:631
8.7% | Private/other rate | index.html:631
1,018 | Private/other n | index.html:631
89 | Private/other readmit | index.html:631
39 | unknown insurance excluded | index.html:228
1.12 | insurance OR | index.html:614
0.85–1.48 | insurance CI | index.html:614
.402 | insurance p | index.html:614

## Restraint (2) + group stats — THESE ARE T1 RECONCILIATION TARGETS
13.1% | restraint: Restrained rate | index.html:637
312 | restraint: Restrained n | index.html:637
41 | restraint: Restrained readmit | index.html:637
8.8% | restraint: Not restrained rate | index.html:637
2,340 | restraint: Not restrained n | index.html:637
205 | restraint: Not restrained readmit | index.html:637
1.58 | restraint: group OR | index.html:615
1.10–2.26 | restraint: group CI | index.html:615
.013 | restraint: group p | index.html:615

## DSM-5 diagnostic spectrum (17)
21.6% | Tic Disorders rate | index.html:642
51 | Tic Disorders n | index.html:642
11 | Tic Disorders readmit | index.html:642
18.8% | Other Neurodevelopmental rate | index.html:643
101 | Other Neurodevelopmental n | index.html:643
19 | Other Neurodevelopmental readmit | index.html:643
18.8% | Dissociative Disorders rate | index.html:644
32 | Dissociative Disorders n | index.html:644
6 | Dissociative Disorders readmit | index.html:644
18.2% | Psychotic Disorders rate | index.html:645
55 | Psychotic Disorders n | index.html:645
10 | Psychotic Disorders readmit | index.html:645
17.7% | Other Mental Disorder rate | index.html:646
232 | Other Mental Disorder n | index.html:646
41 | Other Mental Disorder readmit | index.html:646
15.6% | Bipolar & Related rate | index.html:647
147 | Bipolar & Related n | index.html:647
23 | Bipolar & Related readmit | index.html:647
15.1% | Specific Learning Disorder rate | index.html:648
93 | Specific Learning Disorder n | index.html:648
14 | Specific Learning Disorder readmit | index.html:648
14.5% | Personality Disorder rate | index.html:649
138 | Personality Disorder n | index.html:649
20 | Personality Disorder readmit | index.html:649
14.0% | Obsessive-Compulsive rate | index.html:650
114 | Obsessive-Compulsive n | index.html:650
16 | Obsessive-Compulsive readmit | index.html:650
14.0% | Intellectual Disability rate | index.html:651
57 | Intellectual Disability n | index.html:651
8 | Intellectual Disability readmit | index.html:651
13.6% | Autism Spectrum rate | index.html:652
513 | Autism Spectrum n | index.html:652
70 | Autism Spectrum readmit | index.html:652
13.6% | Conduct Disorder rate | index.html:653
484 | Conduct Disorder n | index.html:653
66 | Conduct Disorder readmit | index.html:653
11.4% | ADHD rate | index.html:654
1,399 | ADHD n | index.html:654
159 | ADHD readmit | index.html:654
11.4% | Non-Suicidal Self-Injury rate | index.html:655
1,348 | NSSI n | index.html:655
154 | NSSI readmit | index.html:655
10.8% | Anxiety Disorders rate | index.html:656
1,154 | Anxiety Disorders n | index.html:656
125 | Anxiety Disorders readmit | index.html:656
10.7% | Depressive Disorders rate | index.html:657
1,779 | Depressive Disorders n | index.html:657
191 | Depressive Disorders readmit | index.html:657
10.3% | Trauma & Stressor-Related rate | index.html:658
1,424 | Trauma n | index.html:658
146 | Trauma readmit | index.html:658

## DSM-5 prose
14.2% | DMDD rate (prose) | index.html:283
1.82 | DMDD OR (prose) | index.html:283
9.0% | MDD single-episode rate (prose) | index.html:283

## Forest plot (6 predictors)
1.78 | forest: Depressive disorders OR | index.html:679
1.23–2.58 | forest: Depressive disorders CI | index.html:679
1.58 | restraint: forest OR | index.html:680
1.11–2.27 | restraint: forest CI | index.html:680
1.31 | forest: Diagnostic complexity OR | index.html:681
1.11–1.53 | forest: Diagnostic complexity CI | index.html:681
0.90 | forest: Older age OR | index.html:682
0.83–0.97 | forest: Older age CI | index.html:682
0.91 | forest: C-SSRS flag OR | index.html:683
0.68–1.23 | forest: C-SSRS flag CI | index.html:683
0.98 | forest: Male sex OR | index.html:684
0.72–1.33 | forest: Male sex CI | index.html:684

## Model AUC (3 models × 3 metrics)
0.712 | Logistic apparent AUC | index.html:700
0.685 | Logistic corrected AUC | index.html:700
0.665 | Logistic oof AUC | index.html:700
0.853 | RF apparent AUC | index.html:701
0.752 | RF corrected AUC | index.html:701
0.684 | RF oof AUC | index.html:701
0.904 | CatBoost apparent AUC | index.html:702
0.789 | CatBoost corrected AUC | index.html:702
0.641 | CatBoost oof AUC | index.html:702

## Optimism deltas
0.047 | Logistic Δ optimism | index.html:411
0.169 | RF Δ optimism | index.html:412
0.263 | CatBoost Δ optimism | index.html:413

## Clinical read callout
0.90 | CatBoost reached (clinical read) | index.html:422
0.64–0.68 | out-of-fold AUC range (clinical read) | index.html:422

## Fairness (4 pairings)
25.7% | fairness: Age gap | index.html:717
4.8 | fairness: Age AUC gap | index.html:717
21.6% | fairness: ACE gap | index.html:718
1.9 | fairness: ACE AUC gap | index.html:718
20.7% | fairness: Insurance gap | index.html:719
5.8 | fairness: Insurance AUC gap | index.html:719
10.0% | fairness: Sex gap | index.html:720
4.4 | fairness: Sex AUC gap | index.html:720

## Abstract — Results chips
1.31 | abstract: complexity OR | index.html:752
1.58 | restraint: abstract OR | index.html:753
0.012 | restraint: abstract p | index.html:753
1.78 | abstract: depressive OR | index.html:754
0.002 | abstract: depressive p | index.html:754
1.10 | abstract: younger age OR | index.html:754
0.853 | abstract: RF apparent AUC | index.html:756
0.752 | abstract: RF corrected AUC | index.html:756
20% | abstract: PPV | index.html:756
0.257 | abstract: age gap | index.html:757
0.207 | abstract: insurance gap | index.html:757
0.216 | abstract: ACE gap | index.html:757

## Footer
2026 | footer year | index.html:546
