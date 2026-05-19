# PP401: Advanced Meta-Analysis & Replication
## Bachelor of Science in Parapsychology — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** PP101 (Introduction to Parapsychology), PP103 (Research Methods & Statistics), PP201 (ESP), PP301 (Ganzfeld & Remote Viewing Protocols) recommended. Senior standing required.
**Description:** A capstone methodology course that prepares students to evaluate, conduct, and critique meta-analyses in parapsychology and related fields. The course addresses the central challenge of parapsychological research: effects are small, variable, and contested. Meta-analysis — the statistical synthesis of results across multiple studies — is the primary tool for determining whether a finding is robust or spurious. But meta-analysis itself is methodologically complex, vulnerable to bias, and frequently misapplied. This course covers: the statistical foundations of meta-analysis (fixed-effect vs. random-effects models, heterogeneity, publication bias detection and correction); the art of systematic review (search strategies, inclusion/exclusion criteria, quality assessment); advanced topics (meta-regression, network meta-analysis, Bayesian approaches, individual participant data meta-analysis); the meta-analytic evidence for key psi phenomena (Ganzfeld, RNG-PK, presentiment, remote viewing); the "replication crisis" in psychology and its implications for parapsychology; and the future of metascience — how pre-registration, registered reports, adversarial collaboration, and machine-learning-assisted meta-analysis are reshaping the evidential landscape. Students complete the course by conducting an original meta-analysis on a parapsychological topic of their choice.

---

## Lecture 1: Why Meta-Analysis? — The Problem of Small Effects and Inconsistent Findings

**The Central Challenge of Parapsychology**

Parapsychology faces a unique evidential challenge. Unlike most fields of science, where effects are typically large enough to be observed in individual studies with modest sample sizes, psi effects are consistently small. The Ganzfeld hit rate is approximately 30-33% (vs. 25% chance), corresponding to an effect size of d ≈ 0.15-0.25. PK effects on RNGs are even smaller, with d ≈ 0.001-0.01. These effect sizes are not negligible — in medicine, effects of similar magnitude (e.g., aspirin's effect on heart attack risk, d ≈ 0.03) are considered clinically significant — but they are small enough that individual studies are frequently underpowered to detect them.

The power problem is acute. To have an 80% chance of detecting a Ganzfeld effect (d = 0.2) at p < 0.05, a study would need approximately 400 participants. Most individual Ganzfeld studies have N < 100, meaning they have less than 30% power to detect the effect. Applied across the literature, this means that most individual psi studies are expected to produce null results — even if the effect is real. The "file drawer" of unpublished null results is not (necessarily) evidence of suppression or fraud; it is a statistical inevitability.

The solution to the power problem is meta-analysis: the statistical synthesis of results across multiple studies to produce a single, more precise estimate of the effect size. By pooling data across studies, meta-analysis achieves the sample size that individual studies lack. A meta-analysis of 30 Ganzfeld studies with N = 100 each effectively analyzes data from 3,000 participants — enough to detect even a small effect with high precision.

**The Birth of Meta-Analysis in Parapsychology**

Parapsychology was, in important ways, a pioneer of meta-analysis. The first formal meta-analysis in any field is often credited to Karl Pearson's 1904 synthesis of typhoid inoculation studies, but the first sustained meta-analytic research program was arguably Charles Honorton's 1985 meta-analysis of the Ganzfeld database, published in the *Journal of Parapsychology*. Honorton identified 28 Ganzfeld studies conducted between 1974 and 1981, computed a combined Stouffer's Z (Z = 6.6, p < 10⁻⁹), and concluded that "the Ganzfeld psi studies provide replicable evidence for an anomalous process of information transfer."

Honorton's meta-analysis was methodologically sophisticated for its time. He addressed the file-drawer problem by computing the "fail-safe N" — the number of unpublished null studies that would be needed to reduce the combined result to non-significance (N = 423). He examined potential moderators — variables that might explain variation in effect sizes across studies. And he acknowledged the limitations of his analysis: publication bias, heterogeneity, and the quality of the primary studies.

Honorton's work was followed by a series of meta-analyses that refined and extended his findings:
- Bem and Honorton (1994): A meta-analysis of autoganzfeld studies (using the automated, computer-controlled protocol), finding a smaller but still significant effect.
- Storm, Tressoldi, and Di Risio (2010): A meta-analysis of all Ganzfeld studies through 2010, confirming the significant effect and identifying several moderators (emotional closeness of sender and receiver, creativity of the receiver).
- The UoY Ganzfeld Meta-Analysis (Haraldsdóttir, Vigfússon, & Chen, 2039): An updated meta-analysis incorporating studies through 2038, using the latest meta-analytic methods (robust variance estimation, selection models for publication bias, meta-regression with machine-learning-selected moderators). The analysis confirmed the significant Ganzfeld effect (d = 0.18, 95% CI [0.12, 0.24], p < 10⁻¹²) and identified new moderators (geomagnetic activity, biophoton coherence, inter-brain gamma synchrony).

**What Meta-Analysis Can and Cannot Do**

Meta-analysis is a powerful tool, but it is not a panacea. It can:
- Increase statistical power by pooling data across studies.
- Estimate the average effect size and its confidence interval.
- Quantify heterogeneity — the variability in effect sizes across studies.
- Identify moderators that explain heterogeneity.
- Detect and (potentially) correct for publication bias.

Meta-analysis cannot:
- Transform poor-quality primary studies into high-quality evidence ("garbage in, garbage out").
- Determine causality (meta-analysis is observational; it can identify associations but not establish causation).
- Resolve fundamental methodological disputes (if skeptics and proponents disagree about the validity of the primary studies, they will likely disagree about the validity of the meta-analysis).
- Replace critical thinking about individual studies — every meta-analysis should be accompanied by a careful reading of the primary literature.

**Required Reading**

- Honorton, C. (1985/2040). "Meta-Analysis of Psi Ganzfeld Research: A Response to Hyman." *Journal of Parapsychology*, 49(1), 51-91. UoY annotated reprint.
- Haraldsdóttir, S., Vigfússon, E., & Chen, L. (2039). "The Ganzfeld at 65: An Updated Meta-Analysis with Machine-Learning-Selected Moderators." *Journal of Parapsychology*, 103(4), 345-410.
- Borenstein, M., Hedges, L.V., Higgins, J.P.T., & Rothstein, H.R. (2021/2038). *Introduction to Meta-Analysis* (2nd edition). Wiley. Chapters 1-3.
- Kennedy, J.E. (2038). *The Methodology of Psi Research* (4th edition). Chapter 14: "Meta-Analysis: Promise, Pitfalls, and Best Practices."

**Discussion Questions**

1. Honorton's 1985 meta-analysis computed a "fail-safe N" of 423 — meaning 423 unpublished null studies would be needed to nullify the result. Is the fail-safe N a useful metric, or does it create a false sense of security (since it assumes that unpublished studies have a mean effect size of zero, which may be optimistic)?
2. The Ganzfeld meta-analytic effect size (d ≈ 0.18) is small by conventional standards. Should we accept such a small effect as evidence for a genuine phenomenon, or does the small effect size itself argue against the reality of psi?
3. Meta-analysis cannot transform poor-quality studies into good evidence. If the underlying primary studies are flawed, what value does meta-analysis add beyond simply summarizing the flaws?

---

## Lecture 2: Statistical Foundations — Fixed-Effect, Random-Effects, and Heterogeneity

**Two Models of Meta-Analysis**

Meta-analysis is built on two fundamental statistical models: the **fixed-effect model** and the **random-effects model**. Understanding the difference is essential to conducting and interpreting meta-analyses correctly.

**The Fixed-Effect Model**

The fixed-effect model assumes that all studies in the meta-analysis are estimating the same underlying (fixed) effect size. Any variation in observed effect sizes across studies is assumed to be due entirely to sampling error — the random fluctuations that occur when you draw a finite sample from a population. In the fixed-effect model, the goal of the meta-analysis is to estimate this single, true effect size as precisely as possible.

The fixed-effect model gives more weight to larger studies (which have smaller sampling error) than to smaller studies. The weight assigned to each study is the inverse of its variance (1/σ²), so a study with N = 500 receives roughly five times the weight of a study with N = 100.

The fixed-effect model is appropriate when the studies are functionally identical — same protocol, same population, same outcome measure — and when the only source of variation is sampling error. In practice, these conditions are rarely met, particularly in parapsychology, where protocols, populations, and outcome measures vary considerably across studies.

**The Random-Effects Model**

The random-effects model assumes that the studies are estimating different underlying effect sizes — that there is genuine variation (heterogeneity) in the true effect across studies. This variation might be due to differences in protocol, population, experimenter, or unknown "random" factors. In the random-effects model, the observed effect size for each study is the sum of three components: the overall mean effect size (μ), a study-specific deviation (τᵢ, reflecting genuine differences between studies), and sampling error (εᵢ).

The random-effects model gives more balanced weight to studies than the fixed-effect model. Large studies still receive more weight than small studies, but the difference is less extreme, because the random-effects model recognizes that a large study may have a different true effect size than a small study (not just less sampling error).

The random-effects model is generally more appropriate for parapsychology meta-analyses, because psi studies are rarely functionally identical. The random-effects model produces a wider confidence interval than the fixed-effect model (reflecting the additional uncertainty due to heterogeneity), making it more conservative — and, arguably, more realistic.

**Heterogeneity: I², τ², and Q**

Heterogeneity — the variability in true effect sizes across studies — is quantified by several statistics:

1. **Q (Cochran's Q)**: A test of whether the variation in observed effect sizes is greater than would be expected from sampling error alone. A significant Q indicates that heterogeneity is present — i.e., the studies are not all estimating the same effect. Q follows a chi-square distribution with k-1 degrees of freedom (where k is the number of studies).

2. **τ² (tau-squared)**: An estimate of the variance of the true effect sizes — the between-study variance. τ² is the key parameter in the random-effects model; a larger τ² means more heterogeneity. τ² is estimated using the DerSimonian-Laird method, the restricted maximum likelihood (REML) method, or Bayesian methods.

3. **I²**: The proportion of total variation in observed effect sizes that is due to heterogeneity rather than sampling error. An I² of 0% means all variation is due to sampling error (no heterogeneity); an I² of 100% means all variation is due to heterogeneity (studies are completely different). Rough benchmarks: I² = 25% (low heterogeneity), 50% (moderate), 75% (high).

In parapsychology meta-analyses, I² is typically high (60-80%), reflecting the genuine variability in psi effects across studies, protocols, and populations. High heterogeneity is not necessarily a problem — it is a fact about the phenomenon — but it complicates interpretation: if studies differ substantially, the "average" effect size may not be meaningful.

**Worked Example: The UoY Ganzfeld Meta-Analysis**

Let's work through the meta-analytic calculations for a simplified version of the UoY Ganzfeld meta-analysis. Suppose we have five Ganzfeld studies with the following hit rates (chance = 25%):

Study A: N = 200, hits = 68 (34%), SE = 0.034
Study B: N = 150, hits = 45 (30%), SE = 0.037
Study C: N = 100, hits = 35 (35%), SE = 0.048
Study D: N = 80, hits = 20 (25%), SE = 0.048
Study E: N = 120, hits = 42 (35%), SE = 0.044

**Fixed-effect analysis**:
- Weight each study by the inverse of its variance.
- The fixed-effect mean hit rate = 33.2% (95% CI [30.8%, 35.6%]), significantly above 25% (p < 0.001).

**Random-effects analysis**:
- Estimate τ² (using REML: τ² = 0.0004, small).
- Weight each study by 1/(σ² + τ²).
- The random-effects mean hit rate = 32.8% (95% CI [29.2%, 36.4%]), significantly above 25% (p < 0.001).

The random-effects confidence interval is wider than the fixed-effect interval (7.2 percentage points vs. 4.8), reflecting the additional uncertainty due to (the small amount of) heterogeneity. In this simplified example, both models yield significant results; in real meta-analyses with high heterogeneity, the random-effects model can render a fixed-effect-significant result non-significant.

**Required Reading**

- Borenstein, M., Hedges, L.V., Higgins, J.P.T., & Rothstein, H.R. (2021/2038). *Introduction to Meta-Analysis* (2nd edition). Chapters 10-13 (fixed-effect, random-effects, heterogeneity).
- Higgins, J.P.T., & Thompson, S.G. (2002/2039). "Quantifying Heterogeneity in a Meta-Analysis." *Statistics in Medicine*, 21(11), 1539-1558. UoY edition.
- Haraldsdóttir, S., Vigfússon, E., & Chen, L. (2039). "The Ganzfeld at 65: An Updated Meta-Analysis." *Journal of Parapsychology*, 103(4), 345-410. (Focus on the statistical methods section.)

**Discussion Questions**

1. Why does the random-effects model typically produce a wider confidence interval than the fixed-effect model? Under what conditions would the two models produce identical intervals?
2. In psi meta-analyses, I² is often high (60-80%). Does high heterogeneity undermine the validity of the meta-analytic finding, or does it simply reflect the genuine complexity of the phenomenon?
3. The DerSimonian-Laird estimator of τ² is known to have poor performance when the number of studies is small. What alternative estimators are available, and when should they be used?

---

## Lecture 3: Publication Bias — Detection, Correction, and the File-Drawer Problem

**The File-Drawer Problem**

The "file-drawer problem" — the bias introduced when studies with significant results are published while studies with null results languish in file drawers — is one of the most serious threats to the validity of meta-analysis. If the published literature is a non-random sample of all studies conducted (overrepresenting significant results), then any meta-analysis of the published literature will overestimate the true effect size.

The file-drawer problem is not unique to parapsychology. It affects all scientific fields and is a major contributor to the "replication crisis" (see Lecture 8). But it is particularly acute in parapsychology, where:
- The phenomena under study are controversial, and researchers may be reluctant to publish null results that could be interpreted as "failures" of psi (or of the researcher).
- The effects are small, meaning that many studies — even if the effect is real — will produce null results by chance, and these null studies may be particularly likely to be filed away.
- The field is small, and the literature is dominated by a relatively small number of research groups, making it vulnerable to group-level publication biases.

**Detection Methods**

Several methods have been developed to detect publication bias:

1. **The funnel plot**: A scatterplot of effect size (x-axis) against standard error or sample size (y-axis). In the absence of publication bias, the plot should resemble a symmetric inverted funnel — small studies (high SE, bottom of the funnel) scatter widely around the mean effect, while large studies (low SE, top of the funnel) cluster tightly around the mean. Publication bias — particularly the suppression of small, null studies — produces asymmetry: the bottom of the funnel is "missing" on one side (typically the null side). Funnel plot asymmetry can be assessed visually or tested formally using Egger's regression test or the Begg-Mazumdar rank correlation test.

2. **The trim-and-fill method**: An iterative method that "trims" asymmetric studies from the funnel plot, estimates the "true" mean from the remaining symmetric studies, and then "fills" the trimmed studies back in (with their mirror images) to produce a symmetric funnel. The trim-and-fill method provides an adjusted estimate of the effect size that accounts for publication bias. In the Ganzfeld meta-analyses, trim-and-fill typically reduces the effect size by 10-30% but does not eliminate it.

3. **Selection models**: Statistical models that explicitly model the publication process — e.g., the probability that a study with a given p-value is published. Selection models estimate the "true" effect size that would be observed if all studies (published and unpublished) were available. Selection models are more flexible and more realistic than trim-and-fill but require stronger assumptions about the publication process.

4. **P-curve and p-uniform**: Methods that analyze the distribution of significant p-values to assess whether the literature contains evidential value (a right-skewed p-curve, with more low p-values than high p-values, is evidence of a genuine effect) or is consistent with publication bias and p-hacking (a flat or left-skewed p-curve). P-curve analysis has been applied to the Ganzfeld literature, with results generally supporting evidential value (the p-curve is right-skewed).

**Correction Methods**

Beyond detection, several methods aim to *correct* for publication bias:

1. **Fail-safe N** (Rosenthal, 1979): The number of unpublished null studies that would be needed to reduce the combined result to non-significance. The fail-safe N is easy to compute and intuitively appealing but has been widely criticized: it assumes that unpublished studies have a mean effect size of exactly zero (which may be optimistic or pessimistic, depending on the true state of affairs), and it does not address the possibility that unpublished studies might have negative effect sizes.

2. **Trim-and-fill adjusted estimate**: As described above.

3. **Selection model adjusted estimate**: As described above.

4. **PET-PEESE**: The Precision Effect Test (PET) and the Precision Effect Estimate with Standard Error (PEESE) are regression-based methods that use the relationship between effect size and standard error to estimate the "true" effect size corrected for publication bias. PET-PEESE is most appropriate when there is strong evidence of publication bias (asymmetrical funnel plot) and when the number of studies is reasonably large (k > 10).

**The UoY Publication Bias Audit**

In 2039, the UoY Parapsychology Department conducted a comprehensive publication bias audit of the psi literature — systematically searching for unpublished studies, contacting researchers for their file-drawer data, and applying multiple publication bias detection and correction methods to the published literature. Key findings:

1. **The Ganzfeld literature**: Evidence of moderate publication bias (asymmetric funnel plot, Egger's test p = 0.02). Trim-and-fill reduced the effect size from d = 0.22 to d = 0.17 — still significant (p < 0.001). Selection models produced similar adjusted estimates (d = 0.15-0.19).

2. **The RNG-PK literature**: Evidence of substantial publication bias (highly asymmetric funnel plot). Trim-and-fill reduced the effect size from d = 0.003 to d = 0.001 — the adjusted estimate was barely significant (p ≈ 0.04), and the result was sensitive to the choice of correction method.

3. **The presentiment literature**: Moderate publication bias was detected, but the adjusted estimate remained significant.

4. **Unpublished studies**: The audit identified 87 unpublished psi studies (Ganzfeld, RNG-PK, remote viewing, presentiment). The unpublished studies had, on average, smaller effect sizes than the published studies (mean d = 0.05 vs. 0.18), confirming that publication bias exists. However, incorporating the unpublished studies into the meta-analyses did not eliminate the overall significant effect — it reduced it, but not to non-significance.

The UoY audit concluded that publication bias is a genuine problem in the psi literature but that it does not fully account for the positive findings. The corrected effect sizes are smaller than the uncorrected effect sizes but remain statistically significant for most (though not all) psi protocols.

**Required Reading**

- Rothstein, H.R., Sutton, A.J., & Borenstein, M. (Eds.). (2005/2040). *Publication Bias in Meta-Analysis: Prevention, Assessment, and Adjustments*. Wiley. Chapters 1-3, 7-9. UoY edition.
- Haraldsdóttir, S., Vigfússon, E., & Chen, L. (2039). "Publication Bias in the Psi Literature: A Comprehensive Audit." *Journal of Parapsychology*, 103(2), 112-167.
- Simonsohn, U., Nelson, L.D., & Simmons, J.P. (2014/2039). "P-Curve: A Key to the File-Drawer." *Journal of Experimental Psychology: General*, 143(2), 534-547. UoY edition.
- Stanley, T.D. (2017/2040). "Limitations of PET-PEESE and Other Meta-Analysis Methods." *Social Psychological and Personality Science*, 8(5), 581-591. UoY edition.

**Discussion Questions**

1. The trim-and-fill method assumes that publication bias suppresses studies based on their statistical significance. But what if studies are suppressed for other reasons — e.g., because the experimenter expected psi to manifest in a particular way and was disappointed by the results? How would non-significance-based suppression affect meta-analytic estimates?
2. The UoY audit found that unpublished studies had smaller effect sizes than published studies — confirming publication bias. Should the meta-analytic literature be updated to include the unpublished studies, or are there reasons to treat unpublished studies with caution?
3. P-curve analysis suggests that the Ganzfeld literature contains genuine evidential value. But p-curve cannot distinguish a genuine psi effect from experimenter psi — both would produce a right-skewed p-curve. How can we distinguish these possibilities meta-analytically?

---

## Lecture 4: Systematic Review and Study Quality Assessment

**The Systematic Review**

A meta-analysis is only as good as the studies it synthesizes, and a systematic review is only as good as the search that identifies those studies. A **systematic review** is the process of identifying, selecting, and critically appraising all relevant studies on a topic according to a pre-specified protocol. The key features of a systematic review are:

1. **Pre-registration**: The review protocol — including the research question, search strategy, inclusion/exclusion criteria, and analysis plan — is registered before the review begins. Pre-registration prevents "cherry-picking" of studies and analyses.

2. **Comprehensive search**: The search strategy is designed to identify all relevant studies, published and unpublished. This typically involves: (a) electronic database searches (PubMed, PsycINFO, Web of Science, Google Scholar); (b) manual searches of key journals and conference proceedings; (c) forward and backward citation searching (identifying studies that cite a key study, and studies cited by a key study); (d) contacting researchers in the field for unpublished data; and (e) searching trial registries, dissertations, and preprint servers.

3. **Explicit inclusion/exclusion criteria**: The criteria for including or excluding studies are specified in advance. Criteria typically include: publication type (peer-reviewed, preprint, dissertation), study design (RCT, quasi-experiment, observational), population, intervention/exposure, outcome, and language.

4. **Duplicate screening**: At least two reviewers independently screen titles and abstracts (and, for potentially eligible studies, full texts) against the inclusion criteria. Disagreements are resolved by discussion or by a third reviewer.

5. **Data extraction**: A standardized data extraction form is used to extract relevant information from each included study (sample size, effect size, moderators, quality indicators). Data extraction is performed by at least two reviewers independently.

6. **Quality assessment**: The methodological quality of each included study is assessed using a validated tool (see below).

**Study Quality Assessment**

Not all studies are created equal. A meta-analysis that includes low-quality studies may produce a biased estimate of the effect size — and the direction of the bias is often unpredictable. Study quality assessment (also called "risk of bias" assessment) is the systematic evaluation of each included study's methodological strengths and weaknesses.

Several quality assessment tools are available:

1. **The Cochrane Risk of Bias Tool (RoB 2)**: Designed for randomized controlled trials, RoB 2 assesses five domains: (a) bias arising from the randomization process, (b) bias due to deviations from intended interventions, (c) bias due to missing outcome data, (d) bias in measurement of the outcome, and (e) bias in selection of the reported result. Each domain is rated as "low risk," "some concerns," or "high risk" of bias.

2. **The Jadad Scale**: A simple, three-item scale that assesses randomization, blinding, and withdrawals/dropouts. The Jadad scale is easy to use but has limited sensitivity — it can distinguish very good studies from very bad studies but is less useful for discriminating among studies of moderate quality.

3. **The Psi-Specific Quality Scale (PSQS)**: Developed at UoY in 2038, the PSQS is a 12-item scale designed specifically for assessing the quality of parapsychological studies. Items assess: randomization method, sensory leakage safeguards, automation, blinding of experimenter and judge, pre-registration, sample size justification, handling of multiple analyses, and reporting of all outcomes. The PSQS has been validated against expert ratings of study quality and shows good inter-rater reliability (ICC = 0.82).

**Quality Effects in Psi Meta-Analyses**

A recurring question in psi meta-analyses is whether effect sizes vary with study quality. The "quality effect" can go in either direction:
- **Negative quality effect**: Higher-quality studies produce *smaller* effect sizes, suggesting that the overall meta-analytic effect is inflated by methodological artifacts in low-quality studies. This pattern would favor the skeptical interpretation.
- **Positive quality effect**: Higher-quality studies produce *larger* effect sizes, suggesting that the true effect is diluted by measurement error and noise in low-quality studies. This pattern would favor the proponent interpretation.

In the Ganzfeld literature, the quality effect has been inconsistent. Some meta-analyses find a small negative quality effect (higher quality → slightly smaller effect); others find no quality effect; and a few find a positive quality effect. The UoY Ganzfeld meta-analysis (Haraldsdóttir et al., 2039), using the PSQS, found a small, non-significant negative quality effect (β = -0.02, p = 0.31) — suggesting that study quality, as measured by the PSQS, does not strongly predict effect size in the Ganzfeld literature.

**Required Reading**

- Higgins, J.P.T., Thomas, J., Chandler, J., Cumpston, M., Li, T., Page, M.J., & Welch, V.A. (Eds.). (2019/2038). *Cochrane Handbook for Systematic Reviews of Interventions* (2nd edition). Wiley. Chapters 4-7, 22-25. UoY edition.
- Haraldsdóttir, S., & Vigfússon, E. (2038). "The Psi-Specific Quality Scale (PSQS): Development and Validation." *Journal of Parapsychology*, 102(3), 287-312.
- Jüni, P., Witschi, A., Bloch, R., & Egger, M. (1999/2040). "The Hazards of Scoring the Quality of Clinical Trials for Meta-Analysis." *JAMA*, 282(11), 1054-1060. UoY reprint.

**Discussion Questions**

1. The PSQS was developed at UoY and may be perceived as "pro-psi" by skeptics. How could the PSQS be validated independently — e.g., by having skeptics and proponents rate the same studies and comparing their ratings?
2. Some methodologists argue against using quality scales in meta-analysis, arguing that quality assessment should be used for sensitivity analysis (does the effect persist when low-quality studies are excluded?) rather than for weighting (studies weighted by quality score). Which approach do you favor, and why?
3. The search for unpublished studies is labor-intensive and often incomplete. At what point does the effort of searching for unpublished studies exceed its likely impact on the meta-analytic estimate?

---

## Lecture 5: Meta-Regression and Moderator Analysis

**Why Moderators Matter**

The average effect size in a meta-analysis is often less interesting than the *variation* around that average. Why do some studies produce larger effects than others? What features of the protocol, the participants, the experimenter, or the environment predict success? Answering these questions is the goal of **moderator analysis** — the search for variables that explain heterogeneity.

In parapsychology, moderator analysis is particularly important because:
- Psi effects are small and variable; understanding the conditions that facilitate psi is essential for both theory and practice.
- Moderator analysis can address skeptical concerns — if psi is an artifact, the effect size should be predicted by methodological quality (lower quality → larger effect). If psi is genuine, the effect size should be predicted by theoretically meaningful variables (e.g., absorption, emotional closeness, geomagnetic activity).
- Moderator analysis can guide protocol design — if we know what facilitates psi, we can design protocols that maximize it.

**Meta-Regression**

Meta-regression is the extension of multiple regression to meta-analytic data. In meta-regression, the dependent variable is the effect size from each study, and the independent variables (moderators) are study-level characteristics. For example, a Ganzfeld meta-regression might include:
- **Participant-level moderators**: Mean absorption score, proportion of emotionally close sender-receiver pairs, proportion of experienced meditators.
- **Protocol-level moderators**: Automated vs. manual target selection, dynamic vs. static targets, duration of sending period.
- **Experimenter-level moderators**: Experimenter psi belief (sheep vs. goat), experimenter experience.
- **Environmental moderators**: Geomagnetic activity (Ap index), local sidereal time, Schumann resonance stability.

The meta-regression model can be expressed as:

θᵢ = β₀ + β₁X₁ᵢ + β₂X₂ᵢ + ... + βₚXₚᵢ + uᵢ

where θᵢ is the true effect size for study i, the Xⱼᵢ are the moderators for study i, the βⱼ are the regression coefficients, and uᵢ is the residual heterogeneity (the variation in effect sizes not explained by the moderators).

**Key Considerations in Meta-Regression**

Meta-regression is methodologically challenging. Key considerations include:

1. **Ecological fallacy**: Meta-regression analyzes study-level relationships, but the relationships of interest are often at the participant level. A study-level relationship (e.g., studies with higher mean absorption produce larger effects) may not imply a participant-level relationship (e.g., within a study, higher-absorption participants produce larger effects). The ecological fallacy — inferring individual-level relationships from group-level data — is a constant risk.

2. **Power**: Meta-regression has low statistical power, particularly when the number of studies is small (k < 20) and the moderators are correlated with each other. A rule of thumb: meta-regression should include no more than one moderator per 10 studies.

3. **Confounding**: Moderators are often correlated with each other. For example, automated Ganzfeld studies tend to have larger sample sizes, more rigorous randomization, and more experienced experimenters than manual Ganzfeld studies. If automation is associated with larger effect sizes, is it the automation per se, or the correlated variables, that are responsible?

4. **Measurement error**: Moderators are measured with error — sometimes substantial error (e.g., geomagnetic activity at the time of the session is estimated from global indices, not measured locally). Measurement error in the moderator biases the meta-regression coefficient toward zero (attenuation bias).

5. **Model specification**: The choice of which moderators to include in the model can dramatically affect the results. Pre-registration of the moderator analysis plan is essential.

**Key Findings from Ganzfeld Meta-Regression**

The UoY Ganzfeld meta-regression (Haraldsdóttir et al., 2039) identified several significant moderators:

| Moderator | Coefficient (β) | SE | p |
|-----------|----------------|-----|---|
| Emotional closeness (sender-receiver) | +0.12 | 0.03 | <0.001 |
| Receiver absorption (TAS) | +0.08 | 0.03 | 0.01 |
| Geomagnetic activity (Ap index) | -0.06 | 0.02 | 0.01 |
| Automation (autoganzfeld vs. manual) | +0.04 | 0.03 | 0.18 |
| Sample size | -0.02 | 0.03 | 0.51 |
| Study year | -0.01 | 0.02 | 0.62 |

The significant moderators — emotional closeness, absorption, and geomagnetic activity — are consistent with the broader psi literature and with the theoretical frameworks discussed in PP303 and PP307. The non-significant moderators — automation and sample size — are worth noting: they suggest that the Ganzfeld effect is not an artifact of manual (potentially leaky) protocols and is not inflated by small-study effects (which would produce a negative sample-size coefficient).

**Required Reading**

- Thompson, S.G., & Higgins, J.P.T. (2002/2039). "How Should Meta-Regression Analyses Be Undertaken and Interpreted?" *Statistics in Medicine*, 21(11), 1559-1573. UoY edition.
- Haraldsdóttir, S., Vigfússon, E., & Chen, L. (2039). "The Ganzfeld at 65: An Updated Meta-Analysis." Moderator analysis section (pp. 370-395).
- Borenstein, M., et al. (2021/2038). *Introduction to Meta-Analysis* (2nd edition). Chapter 20: "Meta-Regression."

**Discussion Questions**

1. The ecological fallacy is a constant risk in meta-regression. How could a meta-analysis be designed to avoid the ecological fallacy — e.g., by obtaining individual participant data (IPD)?
2. The Ganzfeld meta-regression found that emotional closeness is the strongest moderator of effect size. Is this finding more consistent with a "psi as genuine anomalous communication" interpretation or a "psi as artifact of ordinary social bonding" interpretation?
3. Meta-regression has low power when the number of studies is small. In parapsychology, where meta-analyses often include k < 50 studies, is meta-regression worth doing at all, or should it be reserved for much larger literatures?

---

## Lecture 6: Advanced Methods — Network Meta-Analysis, IPD, and Bayesian Approaches

**Network Meta-Analysis**

Standard meta-analysis compares two conditions (e.g., treatment vs. control) across studies. But what if there are multiple conditions — multiple psi protocols (Ganzfeld, remote viewing, forced-choice ESP), multiple participant types (meditators, non-meditators, sheep, goats), or multiple outcome measures? **Network meta-analysis** (NMA), also called "multiple treatment comparison meta-analysis," enables the simultaneous comparison of multiple interventions or conditions by combining direct evidence (studies that compare A to B) and indirect evidence (studies that compare A to C and studies that compare C to B, yielding an indirect estimate of A vs. B through C).

In parapsychology, network meta-analysis could address questions such as:
- Which psi protocol produces the largest effect size (Ganzfeld vs. remote viewing vs. forced-choice ESP)?
- Does the effect size vary by participant type (e.g., meditators vs. non-meditators), and does this variation depend on the protocol?
- Are some moderators (e.g., emotional closeness) more important for some protocols than for others?

Network meta-analysis is methodologically demanding. It requires the assumption of **transitivity** (the studies in the network are sufficiently similar to be compared indirectly) and **consistency** (the direct and indirect estimates of a given comparison agree). Violations of transitivity or consistency can produce misleading results.

The UoY Meta-Analysis Lab is conducting the first network meta-analysis of psi protocols, comparing Ganzfeld, remote viewing, forced-choice ESP, RNG-PK, and presentiment across all available studies. Preliminary results suggest that: (a) Ganzfeld and presentiment produce the largest effect sizes; (b) RNG-PK produces the smallest; and (c) the rank order of protocols is generally consistent with theoretical expectations (protocols that involve strong emotional engagement, altered states, and dynamic targets produce larger effects). The full analysis is expected in 2041.

**Individual Participant Data (IPD) Meta-Analysis**

Standard meta-analysis uses study-level summary data (mean effect size, standard error). **Individual participant data (IPD) meta-analysis** obtains the raw data from each study (participant-level data: demographics, personality measures, condition assignment, outcome) and analyzes them as a single, integrated dataset.

IPD meta-analysis offers several advantages:
- **Avoids the ecological fallacy**: Participant-level relationships can be examined directly (e.g., does absorption predict psi performance within studies?).
- **Standardized analysis**: All studies are analyzed using the same statistical methods, reducing variability due to analytical choices.
- **More powerful moderator analysis**: Participant-level moderators can be examined with greater precision and statistical power.

IPD meta-analysis also has disadvantages:
- **Data access**: Obtaining raw data from all relevant studies is difficult — researchers may be reluctant to share data, and older studies may have data in inaccessible formats.
- **Complexity**: IPD meta-analysis is statistically complex, requiring methods that account for the clustering of participants within studies (multilevel models, generalized estimating equations).
- **Time and cost**: IPD meta-analysis is substantially more time-consuming and expensive than study-level meta-analysis.

The UoY Ganzfeld IPD Project, initiated in 2038, is collecting individual participant data from all available Ganzfeld studies. As of 2040, data from 45 studies (N = 4,500 participants) have been obtained. Preliminary IPD analyses have confirmed the study-level findings and revealed new participant-level relationships — for example, a curvilinear relationship between absorption and hit rate (both very low and very high absorption predict poor performance; moderate absorption predicts good performance), which was not detectable in study-level analyses.

**Bayesian Meta-Analysis**

Bayesian meta-analysis offers an alternative to the frequentist (NHST-based) methods that dominate the meta-analytic literature. In Bayesian meta-analysis, prior distributions are specified for the parameters of interest (the overall effect size μ, the between-study variance τ², the regression coefficients β), and the data are used to update these priors to obtain posterior distributions. The posterior distribution quantifies the uncertainty about the parameters given the data and the prior.

Bayesian meta-analysis offers several advantages:
- **Direct probability statements**: Instead of "the effect is significantly different from zero (p < 0.05)," the Bayesian can say "the probability that the effect is greater than zero is 98%." This is often more intuitive and more informative.
- **Incorporation of prior knowledge**: If we have strong prior reasons to expect a small positive effect (based on theory and previous meta-analyses), we can incorporate this prior into the analysis, rather than acting as if we know nothing.
- **Natural handling of complex models**: Bayesian methods can easily accommodate complex meta-analytic models (network meta-analysis, IPD meta-analysis, meta-regression with many moderators) that would strain frequentist methods.

Bayesian meta-analysis also has disadvantages:
- **Prior sensitivity**: The results can be sensitive to the choice of prior. Different priors (optimistic, skeptical, neutral) can produce different conclusions, and the choice of prior can be contentious.
- **Computational complexity**: Bayesian meta-analysis often requires Markov Chain Monte Carlo (MCMC) sampling, which is computationally intensive.

The UoY Meta-Analysis Lab uses both frequentist and Bayesian methods, reporting both and comparing their conclusions. In general, the Bayesian and frequentist conclusions agree (both indicate significant effects), but the Bayesian approach provides richer information about the uncertainty surrounding the effect size.

**Required Reading**

- Riley, R.D., Lambert, P.C., & Abo-Zaid, G. (2010/2039). "Meta-Analysis of Individual Participant Data: Rationale, Conduct, and Reporting." *BMJ*, 340, c221. UoY edition.
- Sutton, A.J., & Abrams, K.R. (2001/2040). "Bayesian Methods in Meta-Analysis and Evidence Synthesis." *Statistical Methods in Medical Research*, 10(4), 277-303. UoY edition.
- Haraldsdóttir, S., et al. (2041, forthcoming). "A Network Meta-Analysis of Psi Protocols: Comparing Effect Sizes Across Paradigms." Draft provided to PP401 students.
- UoY Ganzfeld IPD Project (2040). *Technical Report: IPD Meta-Analysis of Ganzfeld Studies*. Internal document.

**Discussion Questions**

1. Network meta-analysis relies on the assumption of transitivity — that the studies in the network are sufficiently similar to be compared indirectly. Is this assumption plausible for psi protocols? Are the Ganzfeld and remote viewing similar enough that indirect comparisons through them are valid?
2. IPD meta-analysis avoids the ecological fallacy but requires access to raw data. How can the parapsychological community incentivize data sharing to facilitate IPD meta-analyses?
3. Bayesian meta-analysis requires the specification of a prior distribution. What prior would you use for a Ganzfeld meta-analysis — an optimistic prior (d ~ N(0.2, 0.1)), a skeptical prior (d ~ N(0, 0.05)), or an uninformative prior? Justify your choice.

---

## Lecture 7: Meta-Analytic Evidence for Key Psi Phenomena

**The Ganzfeld**

The Ganzfeld is the most extensively meta-analyzed protocol in parapsychology. The meta-analytic evidence, summarized across multiple independent meta-analyses spanning 1985 to 2039, consistently supports a small but statistically significant effect:

| Meta-Analysis | k | N | Effect Size (d) | 95% CI | p |
|---------------|---|---|-----------------|-----------|---|
| Honorton (1985) | 28 | ~835 | — | — | <10⁻⁹ |
| Bem & Honorton (1994) | 11 | ~240 | 0.25 | [0.04, 0.46] | <0.01 |
| Storm et al. (2010) | 108 | ~4,000 | 0.14 | [0.08, 0.20] | <0.001 |
| UoY (Haraldsdóttir et al., 2039) | 162 | ~5,200 | 0.18 | [0.12, 0.24] | <10⁻¹² |

The consistency across meta-analyses, and the persistence of the effect after correction for publication bias (trim-and-fill adjusted d ≈ 0.13-0.17), gives the Ganzfeld effect substantial meta-analytic credibility. It is, by meta-analytic standards, a robust finding — comparable in effect size and evidential strength to many accepted findings in medicine and psychology.

**RNG-PK**

The meta-analytic evidence for RNG-PK (the influence of consciousness on random number generators) is more complex. The effect size is extremely small (d ≈ 0.001-0.003), and the evidence for publication bias is stronger than for the Ganzfeld. Key meta-analyses:

| Meta-Analysis | k | N | Effect Size (d) | 95% CI | p |
|---------------|---|---|-----------------|-----------|---|
| Radin & Nelson (1989) | 152 | — | — | — | <10⁻³⁵ |
| Bösch et al. (2006) | 380 | — | — | — | <0.001 (but: publication bias detected) |
| UoY (Li & Tanaka, 2039) | 420 | — | 0.002 | [0.001, 0.003] | <0.01 (but: adjusted for bias, p ≈ 0.04) |

The RNG-PK effect is fragile — small enough that it could be an artifact of unrecognized bias — but the sheer volume of studies (k > 400) is remarkable. If the effect is real, it would be one of the most extensively replicated small effects in science. If it is artifactual, it would be one of the most extensive examples of systematic bias.

**Presentiment**

Presentiment — the apparently precognitive physiological response to future emotional stimuli — has been meta-analyzed more recently. The effect size is moderate (d ≈ 0.2-0.3) but the literature is small (k ≈ 50 as of 2040), and publication bias is a concern. Key meta-analyses:

| Meta-Analysis | k | N | Effect Size (d) | 95% CI | p |
|---------------|---|---|-----------------|-----------|---|
| Mossbridge et al. (2012) | 26 | ~500 | 0.21 | [0.13, 0.29] | <0.001 |
| UoY (Vigfússon & Thórsdóttir, 2040) | 48 | ~950 | 0.19 | [0.12, 0.26] | <0.001 (adjusted for bias: d = 0.14, p = 0.003) |

Presentiment is a relatively new research paradigm (the first studies were conducted in the 1990s), and the meta-analytic evidence, while promising, is less mature than the Ganzfeld and RNG-PK evidence.

**Remote Viewing**

Remote viewing has been less extensively meta-analyzed than the Ganzfeld, but the available evidence is positive. The UoY Remote Viewing Meta-Analysis (Haraldsdóttir & Chen, 2039), synthesizing 28 controlled studies, found a significant effect (d = 0.22, 95% CI [0.10, 0.34], p < 0.001), with evidence of publication bias (Egger's test p = 0.06, borderline) that reduced but did not eliminate the effect after correction (adjusted d = 0.16, p = 0.01).

**Required Reading**

- Haraldsdóttir, S., Vigfússon, E., & Chen, L. (2039). "The Ganzfeld at 65: An Updated Meta-Analysis." *Journal of Parapsychology*, 103(4), 345-410.
- Li, C., & Tanaka, A. (2039). "RNG-PK Meta-Analysis: An Updated Synthesis with Publication Bias Correction." *Journal of Parapsychology*, 103(3), 268-300.
- Mossbridge, J., Tressoldi, P., & Utts, J. (2012/2038). "Predictive Physiological Anticipation Preceding Seemingly Unpredictable Stimuli: A Meta-Analysis." *Frontiers in Psychology*, 3, 390. UoY edition.
- Vigfússon, E., & Thórsdóttir, K. (2040). "Presentiment Meta-Analysis: Updated Through 2039." *Journal of Parapsychology*, 104(1), 112-144.

**Discussion Questions**

1. The RNG-PK effect is so small (d ≈ 0.002) that it is invisible in individual studies and only detectable in meta-analysis. Does this make the finding more credible (because it is hard to produce such a tiny effect through artifact or fraud) or less credible (because it is easy to produce such a tiny effect through subtle cumulative bias)?
2. The Ganzfeld meta-analytic effect has been replicated across multiple independent meta-analyses over 50+ years. Is this "meta-analytic replication" sufficient to establish the reality of psi, or does it simply mean that the same biases are being replicated?
3. The presentiment literature is relatively young. What meta-analytic evidence would be needed to elevate presentiment to the same level of credibility as the Ganzfeld?

---

## Lecture 8: The Replication Crisis and Its Lessons for Parapsychology

**The Replication Crisis**

Since approximately 2011, psychology and related fields have been gripped by a "replication crisis" — the recognition that many published findings, including some that were widely accepted and highly cited, cannot be replicated by independent laboratories. Landmark events include:

- **The Open Science Collaboration (2015)**: 100 replications of studies published in three top psychology journals. Only 36% of the replications produced significant results (vs. 97% of the original studies), and the average effect size in the replications was half that in the original studies.

- **The "Many Labs" projects**: Large-scale, multi-laboratory replications of classic findings. Many classic findings replicated; many did not. The projects revealed substantial heterogeneity across laboratories — a finding with implications for parapsychology (where experimenter effects and laboratory-specific factors are known to be important).

- **Pre-registration and Registered Reports**: The adoption of pre-registration (specifying the hypothesis, method, and analysis plan before data collection) and Registered Reports (journals accepting studies based on the design, not the results) has been accelerating since the mid-2010s, improving the credibility of published findings.

The replication crisis has been painful for psychology, but it has also been instructive. It has revealed the pervasiveness of questionable research practices (QRPs) — p-hacking, HARKing (hypothesizing after the results are known), selective reporting, and small-sample underpowered studies — and it has spurred methodological reforms that are improving the quality of psychological science.

**Lessons for Parapsychology**

Parapsychology has a complex relationship with the replication crisis. On one hand, parapsychology has been aware of — and has attempted to address — many of the methodological problems that the replication crisis exposed, long before mainstream psychology acknowledged them. Parapsychology adopted meta-analysis earlier (Honorton, 1985), implemented pre-registration earlier (Kennedy, 1981), and developed automated, sensory-leakage-proof protocols earlier (the autoganzfeld, 1983) than mainstream psychology. In some respects, parapsychology was ahead of its time.

On the other hand, parapsychology is vulnerable to the same QRPs that affect mainstream psychology, and the small effect sizes and high heterogeneity that characterize psi research make the detection and correction of QRPs particularly important. The replication crisis has several specific lessons for parapsychology:

1. **Power is essential**: Most individual psi studies are underpowered. Underpowered studies produce imprecise effect size estimates, increase the risk of false negatives (failing to detect a real effect), and (paradoxically) increase the risk of false positives when combined with p-hacking and selective reporting. The solution: larger sample sizes, determined by a priori power analysis.

2. **Pre-registration is necessary but not sufficient**: Pre-registration prevents the most blatant forms of p-hacking and selective reporting, but it does not address all QRPs. Researchers can still "pre-register" a vague hypothesis and then claim post hoc that any significant result confirms it. The solution: detailed, specific pre-registrations, ideally using Registered Reports.

3. **Multi-laboratory replication is the gold standard**: The "Many Labs" projects have demonstrated that multi-laboratory replication is feasible and informative. Parapsychology should conduct its own "Many Labs" projects — multi-laboratory replications of key protocols (Ganzfeld, remote viewing, presentiment) with standardized protocols, pre-registration, and large sample sizes. The UoY "Many Labs Psi" project, currently in the planning stages, is a step in this direction.

4. **Adversarial collaboration should be the norm**: When proponents and skeptics disagree, they should collaborate on a study that both agree will be informative, rather than publishing competing studies that neither accepts as valid. Adversarial collaboration is rare in parapsychology (and in science generally), but it is the most promising approach to resolving persistent empirical disputes.

5. **Transparency is a public good**: Data sharing, code sharing, and protocol sharing increase the credibility of research and enable independent verification. The UoY Parapsychology Department has adopted an open-science policy: all data, analysis scripts, and protocols are made publicly available (with appropriate privacy protections) within one year of collection.

**Required Reading**

- Open Science Collaboration. (2015/2040). "Estimating the Reproducibility of Psychological Science." *Science*, 349(6251), aac4716. UoY edition with parapsychological commentary.
- Wagenmakers, E.J., Wetzels, R., Borsboom, D., van der Maas, H.L.J., & Kievit, R.A. (2012/2039). "An Agenda for Purely Confirmatory Research." *Perspectives on Psychological Science*, 7(6), 632-638. UoY edition.
- Kennedy, J.E. (2038). *The Methodology of Psi Research* (4th edition). Chapter 15: "Lessons from the Replication Crisis."
- UoY Parapsychology Department (2040). *Open Science Policy*. Internal document.

**Discussion Questions**

1. Parapsychology adopted many methodological reforms (meta-analysis, pre-registration, automation) before mainstream psychology. Why, then, is parapsychology still marginalized? Is the problem methodological, sociological, or ontological?
2. Adversarial collaboration is the gold standard for resolving disputes but is rare in practice. What barriers prevent adversarial collaboration in parapsychology, and how could they be overcome?
3. The "Many Labs" projects found substantial heterogeneity across laboratories. If psi effects vary across laboratories (perhaps due to experimenter effects), does this undermine the replicability of psi — or does it confirm that psi is a genuine but context-dependent phenomenon?

---

## Lecture 9: The Meta-Analysis of Meta-Analyses — Second-Order Meta-Analysis

**What Is Second-Order Meta-Analysis?**

A second-order meta-analysis (also called a "meta-meta-analysis" or "umbrella review") is a meta-analysis of meta-analyses — a systematic synthesis of the meta-analytic evidence on a topic. While a traditional meta-analysis synthesizes individual studies, a second-order meta-analysis synthesizes the meta-analyses, providing the "biggest picture" possible.

Second-order meta-analysis is appropriate when:
- Multiple independent meta-analyses have been conducted on the same (or overlapping) topics.
- The meta-analyses may reach different conclusions (perhaps due to different inclusion criteria, different analytical methods, or different time periods).
- A synthesis of the meta-analytic evidence can provide a more comprehensive and stable estimate than any individual meta-analysis.

**The UoY Second-Order Psi Meta-Analysis**

In 2040, the UoY Meta-Analysis Lab completed a second-order meta-analysis of all available psi meta-analyses (Haraldsdóttir, Vigfússon, Li, & Tanaka, 2040). The analysis included 47 meta-analyses spanning 1935-2040, covering Ganzfeld, RNG-PK, remote viewing, presentiment, forced-choice ESP, and spontaneous psi surveys. Key findings:

1. **Overall effect**: Across all protocols and meta-analyses, the second-order mean effect size was d = 0.15 (95% CI [0.11, 0.19], p < 10⁻²⁰). The effect persisted after correction for publication bias at both the primary-study and meta-analytic levels (adjusted d = 0.11, p < 0.001).

2. **Protocol-specific effects**: The Ganzfeld (d = 0.18), presentiment (d = 0.19), and remote viewing (d = 0.16) produced the largest effects. RNG-PK produced the smallest (d = 0.002) but, because of the enormous number of studies, was still highly significant.

3. **Time trends**: There was a small, non-significant decline in effect size over time (β = -0.001 per year, p = 0.42) — contrary to the "decline effect" often cited by skeptics. However, studies conducted since the widespread adoption of pre-registration (c. 2018) produced slightly smaller effects than earlier studies (d = 0.11 vs. 0.17), suggesting that pre-registration may reduce the influence of QRPs.

4. **Heterogeneity**: As expected, heterogeneity was high (I² = 72%), reflecting genuine differences across protocols, populations, and laboratories.

5. **Publication bias at the meta-analytic level**: Evidence of publication bias was detected at the meta-analytic level — meta-analyses with significant results were more likely to be published than those with non-significant results. However, including unpublished meta-analyses (identified through researcher contacts and dissertation databases) reduced but did not eliminate the effect.

**Interpretive Considerations**

The second-order meta-analysis provides the strongest meta-analytic evidence for psi to date. It suggests that, across a century of research and dozens of meta-analyses, a small but persistent anomalous effect is present in the parapsychological literature — an effect that cannot be fully explained by publication bias, methodological artifacts, or selective reporting (though these factors contribute to the effect's magnitude).

However, the second-order meta-analysis has limitations:
- **Garbage in, garbage out**: If the primary studies are flawed, and if the meta-analyses do not adequately account for these flaws, then the second-order meta-analysis simply summarizes the flaws.
- **Dependence**: The meta-analyses are not independent — they draw on overlapping sets of primary studies. The second-order analysis must account for this dependence, which is methodologically challenging.
- **The "psi assumption" problem**: As noted throughout this course, a meta-analysis can only detect an effect; it cannot determine whether the effect is psi, artifact, or something else.

**Required Reading**

- Haraldsdóttir, S., Vigfússon, E., Li, C., & Tanaka, A. (2040). "A Second-Order Meta-Analysis of Psi Research, 1935-2040." *Journal of Parapsychology*, 104(4), 461-510.
- Ioannidis, J.P.A. (2017/2040). "Next-Generation Systematic Reviews: Prospective Meta-Analysis, Individual-Level Data, Networks, and Umbrella Reviews." *British Journal of Sports Medicine*, 51(20), 1456-1458. UoY edition.

**Discussion Questions**

1. The second-order meta-analysis found a significant overall effect (d = 0.15). Does this finding "settle" the psi debate? Why or why not?
2. The second-order meta-analysis detected publication bias at the meta-analytic level — meta-analyses with significant results were more likely to be published. How should this bias be addressed?
3. A second-order meta-analysis is only as good as the meta-analyses it synthesizes. If the meta-analyses are flawed (e.g., inadequate control for publication bias), does the second-order meta-analysis add value, or does it simply compound the flaws?

---

## Lecture 10: Machine Learning and Automated Meta-Analysis

**The Automation of Systematic Review**

Systematic review is labor-intensive. A typical review requires hundreds of hours of human effort — searching databases, screening titles and abstracts, extracting data, assessing quality. For large literatures (the Ganzfeld literature now exceeds 150 studies; the RNG-PK literature exceeds 400), the human effort required is daunting.

Machine learning (ML) is transforming systematic review. ML algorithms can:
- **Search and deduplicate**: Natural language processing (NLP) algorithms can search databases, identify potentially relevant studies, and deduplicate results, reducing the number of records that must be screened by humans.
- **Screen titles and abstracts**: Supervised ML classifiers can be trained on a subset of human-screened records and then applied to the remaining records, prioritizing studies that are likely to be relevant. In validation studies, ML screening achieves sensitivity >95% (identifying almost all relevant studies) while reducing the human screening burden by 50-70%.
- **Extract data**: NLP algorithms can extract structured data (sample size, effect size, moderators) from full-text articles, reducing (but not eliminating) the need for human data extraction.
- **Assess quality**: ML classifiers can be trained to assess study quality (using the PSQS or similar tools) based on features of the article text.

The UoY Meta-Analysis Lab has developed "MetaBot" — an ML-assisted systematic review platform that automates much of the systematic review workflow. MetaBot has been used in the UoY Ganzfeld and RNG-PK meta-analyses, reducing the time required for screening and data extraction by approximately 60%.

**ML-Based Publication Bias Detection**

Traditional publication bias detection methods (funnel plot, Egger's test, trim-and-fill) rely on the relationship between effect size and standard error — a relationship that can be distorted by heterogeneity and other factors. ML offers new approaches to publication bias detection:

- **Anomaly detection**: ML algorithms trained on "normal" meta-analytic data can flag meta-analyses that deviate from expected patterns — e.g., meta-analyses where the distribution of p-values is inconsistent with the reported effect size, suggesting p-hacking or selective reporting.
- **Natural language processing**: NLP algorithms can analyze the text of published articles for linguistic markers of QRPs — e.g., vague hypotheses, post hoc rationalizations, incomplete reporting of results.
- **Generative models**: Generative adversarial networks (GANs) can be trained to simulate "realistic" meta-analytic data with and without publication bias, enabling researchers to assess the sensitivity of their findings to different bias scenarios.

**Automated Living Meta-Analyses**

The ultimate vision of automated meta-analysis is the "living meta-analysis" — a continuously updated synthesis that incorporates new studies as they are published, using ML to automate the entire systematic review workflow. The UoY "Living Psi Meta-Analysis" (LPM) project, launched in 2040, aims to maintain continuously updated meta-analyses of all major psi protocols, with new studies incorporated within weeks of publication and the meta-analytic estimates updated in real time.

The LPM raises several methodological and ethical questions:
- **Quality control**: If the workflow is fully automated, what quality control mechanisms are in place? Can ML algorithms be trusted to assess study quality and detect QRPs?
- **Interpretation**: A continuously updated meta-analysis will fluctuate as new studies are added. How should researchers and the public interpret these fluctuations — particularly if a meta-analytic estimate briefly dips below significance?
- **Gaming**: If researchers know that their studies will be immediately incorporated into a living meta-analysis, could this incentivize strategic behavior (e.g., timing the release of studies to influence the meta-analytic estimate)?

**Required Reading**

- Marshall, I.J., & Wallace, B.C. (2019/2039). "Toward Systematic Review Automation: A Practical Guide to Using Machine Learning Tools in Research Synthesis." *Systematic Reviews*, 8(1), 163. UoY edition.
- Tanaka, A., & Li, C. (2040). "MetaBot: An ML-Assisted Systematic Review Platform for Parapsychology." *Journal of Parapsychology*, 104(3), 393-420.
- UoY Meta-Analysis Lab (2040). *Technical Report: The Living Psi Meta-Analysis — Design and Implementation*. Internal document.

**Discussion Questions**

1. ML-assisted systematic review reduces the human effort required for meta-analysis but introduces new risks (algorithmic bias, errors in automated data extraction). How should these risks be managed?
2. A living meta-analysis that fluctuates in real time could be misinterpreted by the media and the public. Should living meta-analyses be publicly accessible, or should access be restricted to researchers?
3. If ML algorithms can detect QRPs from the text of published articles, should journals use such algorithms to screen submissions — and what would be the consequences for the publication process?

---

## Lecture 11: The Meta-Analyst's Toolkit — Software and Practical Skills

**Software for Meta-Analysis**

A variety of software packages are available for meta-analysis, ranging from general-purpose statistical environments to specialized meta-analysis applications:

**R Packages** (the primary platform for meta-analysis in 2040):
- **metafor**: The most comprehensive R package for meta-analysis. Supports fixed-effect and random-effects models, meta-regression, publication bias detection and correction, network meta-analysis, and multivariate meta-analysis. The `rma()` function is the workhorse of modern meta-analysis.
- **meta**: A user-friendly R package with a graphical interface. Suitable for standard meta-analyses; less flexible than metafor for advanced analyses.
- **netmeta**: For network meta-analysis.
- **bayesmeta**: For Bayesian meta-analysis.
- **robumeta**: For robust variance estimation (clustered standard errors), useful when studies contribute multiple effect sizes.

**Python Packages**:
- **PyMeta**: A comprehensive Python package developed at UoY, implementing most of the functionality of metafor in a Python environment. PyMeta is integrated with the UoY Meta-Analysis Lab's automated workflow.

**Standalone Software**:
- **Comprehensive Meta-Analysis (CMA)**: A commercial, user-friendly application with a graphical interface. CMA is widely used but less flexible than R for advanced analyses.
- **JASP**: An open-source, user-friendly statistical package with a meta-analysis module. JASP is suitable for standard meta-analyses and is increasingly used in teaching.

**Practical Meta-Analysis Workflow**

A typical meta-analysis workflow, as practiced at the UoY Meta-Analysis Lab, follows these steps:

1. **Protocol development and pre-registration** (1-2 months): Define the research question, search strategy, inclusion/exclusion criteria, analysis plan, and moderator hypotheses. Register the protocol on the Open Science Framework (OSF) or PROSPERO.

2. **Systematic search** (1-2 months): Execute the search strategy across databases, screen titles/abstracts (using MetaBot for ML-assisted screening), and retrieve full texts for potentially eligible studies.

3. **Data extraction** (1-3 months): Extract effect sizes, sample sizes, and moderators from each included study using a standardized form. At least two reviewers extract data independently; disagreements are resolved by discussion.

4. **Quality assessment** (1 month): Assess the quality of each included study using the PSQS or a similar tool.

5. **Statistical analysis** (1-2 months): Conduct the primary meta-analysis (random-effects), assess heterogeneity, test for publication bias, and conduct moderator analyses (meta-regression). Run sensitivity analyses (e.g., excluding low-quality studies, using alternative effect size metrics, comparing frequentist and Bayesian methods).

6. **Write-up and dissemination** (1-2 months): Write the manuscript following the PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) guidelines. Publish the data, analysis scripts, and (if possible) the extracted data as supplementary materials.

**Total time**: Typically 6-12 months for a comprehensive meta-analysis.

**Common Mistakes and How to Avoid Them**

1. **Using the fixed-effect model when heterogeneity is high**: If I² > 50%, use the random-effects model. Report both, but draw conclusions from the random-effects model.

2. **Overinterpreting the fail-safe N**: The fail-safe N is easy to compute but misleading. Use publication bias detection and correction methods instead (funnel plot, trim-and-fill, selection models, p-curve).

3. **Ignoring dependence**: If studies contribute multiple effect sizes (e.g., multiple outcome measures, multiple time points), the effect sizes are not independent. Use robust variance estimation (robumeta) or multilevel meta-analysis to account for dependence.

4. **Conducting too many moderator analyses**: With k < 20 studies, limit moderator analyses to 1-2 pre-specified moderators. With larger k, use machine learning methods (LASSO, random forest) to select moderators from a larger set, but treat the results as exploratory.

5. **Neglecting sensitivity analyses**: Report a range of analyses with different assumptions (different effect size metrics, different methods for handling publication bias, different inclusion criteria). If the conclusions are consistent across the sensitivity analyses, the findings are robust. If not, the findings are fragile and should be interpreted cautiously.

**Required Reading**

- Viechtbauer, W. (2010/2039). "Conducting Meta-Analyses in R with the metafor Package." *Journal of Statistical Software*, 36(3), 1-48. UoY edition.
- Borenstein, M., et al. (2021/2038). *Introduction to Meta-Analysis* (2nd edition). Chapters 40-43 (software, practical workflow).
- Page, M.J., McKenzie, J.E., Bossuyt, P.M., Boutron, I., Hoffmann, T.C., Mulrow, C.D., et al. (2021/2040). "The PRISMA 2020 Statement: An Updated Guideline for Reporting Systematic Reviews." *BMJ*, 372, n71. UoY edition.

**Discussion Questions**

1. The choice between fixed-effect and random-effects models can influence the meta-analytic conclusion. How should the analyst decide which model to use, and how should they report their decision?
2. Meta-analysis is increasingly automated (MetaBot, living meta-analyses). Does automation reduce the need for human judgment in meta-analysis, or does it simply shift judgment to different stages (algorithm design, quality control)?
3. The PRISMA guidelines specify what should be reported in a meta-analysis. Do these guidelines adequately address the specific challenges of meta-analyzing parapsychological studies, or do they need to be adapted?

---

## Lecture 12: Synthesis — Meta-Analysis and the Future of Parapsychology

**The Meta-Analytic Verdict**

We have covered a great deal of ground in this course — from the basic logic of pooling studies to increase statistical power, to the complexities of publication bias, moderator analysis, and second-order synthesis. What is the verdict? What does the meta-analytic evidence tell us about the reality of psi?

The verdict, in the instructor's assessment, is that the meta-analytic evidence for psi is **genuine but not definitive**. The Ganzfeld effect, the presentiment effect, and (to a lesser extent) the RNG-PK effect persist across meta-analyses, across decades, and across laboratories. They survive correction for publication bias — diminished but not eliminated. They are predicted by theoretically meaningful moderators (emotional closeness, absorption, geomagnetic activity). They are consistent with the broader parapsychological literature and with theoretical frameworks (field consciousness, quantum entanglement, morphic resonance). By the standards of evidence applied in medicine, psychology, and other sciences, the meta-analytic evidence for psi warrants serious scientific attention.

But the evidence is not definitive. The effects are small — small enough that unrecognized biases (publication bias, experimenter effects, methodological artifacts) could account for them. The heterogeneity is high — high enough that the "average" effect size may not be meaningful. The theoretical frameworks are speculative — coherent enough to guide research but not precise enough to make sharp, falsifiable predictions. And the broader scientific community remains, for the most part, unconvinced.

The responsible position, then, is to hold both thoughts in mind simultaneously: the meta-analytic evidence for psi is stronger than skeptics acknowledge, but weaker than proponents sometimes claim. The truth, whatever it turns out to be, lies somewhere in the unresolved tension between these two positions.

**Meta-Analysis as a Tool for Scientific Progress**

Beyond its specific findings about psi, meta-analysis serves a broader function in science: it forces researchers to confront the evidence as a whole, rather than cherry-picking the studies that support their preferred view. A well-conducted meta-analysis is an act of intellectual honesty — a systematic effort to determine what the evidence, in its entirety, actually shows.

This function is particularly important in controversial fields like parapsychology, where the temptation to cherry-pick is strong on both sides. Proponents are tempted to cite the studies that "worked" and ignore the ones that didn't. Skeptics are tempted to cite the studies that "failed" and dismiss the ones that succeeded. Meta-analysis, by including all studies (subject to pre-specified inclusion criteria), provides a corrective to both tendencies.

The future of parapsychology depends, in part, on the quality of its meta-analyses. If the field produces rigorous, transparent, pre-registered meta-analyses that withstand skeptical scrutiny, it will build credibility — even if the effect sizes remain small. If it produces sloppy, biased, post-hoc meta-analyses that confirm what the researchers already believed, it will squander credibility — even if the conclusions happen to be true.

**The Student Project**

The capstone assignment for this course is an original meta-analysis on a parapsychological topic of your choice. This is not a textbook exercise — it is a genuine contribution to the scientific literature. The UoY Meta-Analysis Lab has identified dozens of topics that would benefit from an updated or first-ever meta-analysis, and your project could provide the foundation for a published paper.

Choose your topic carefully. It should be narrow enough to be manageable (k = 10-50 studies) but broad enough to be interesting. It should address a question that has not been definitively answered by existing meta-analyses. And it should be a question that you genuinely care about — because a meta-analysis is a substantial commitment, and your motivation will flag if you are not invested in the answer.

**The Living Field of Evidence**

The meta-analytic evidence for psi is not static. Every year, new studies are published, new methods are developed, new perspectives are brought to bear. The "living meta-analysis" of psi is constantly evolving, and your work — as students in this course and as future researchers — will shape its evolution.

The challenge is to engage with this evolving evidence honestly, rigorously, and openly. To acknowledge what we don't know while pursuing what we might know. To hold our beliefs lightly while pursuing our questions seriously. To contribute to the collective enterprise of understanding — not to "prove" that psi is real (or not real) but to determine, as best we can, what the evidence actually shows.

**Required Reading**

- Haraldsdóttir, S. (2041). *The View from 2040*. Chapter 10: "Meta-Analysis and the Credibility of Psi."
- Kennedy, J.E. (2038). *The Methodology of Psi Research* (4th edition). Chapter 16: "The Future of Psi Research: A Meta-Analytic Perspective."
- UoY Meta-Analysis Lab (2040). *Student Project Guide: How to Conduct Your First Meta-Analysis*. Internal document.
- Open Science Collaboration. (2015/2040). "Estimating the Reproducibility of Psychological Science." *Science*, 349(6251), aac4716. UoY edition (re-read the concluding section).

**Discussion Questions**

1. After twelve lectures, what is your personal assessment of the meta-analytic evidence for psi? Has your view changed? What meta-analytic evidence (or lack thereof) has most influenced your assessment?
2. The instructor characterized the evidence as "genuine but not definitive." Do you agree? What would "definitive" meta-analytic evidence for psi look like?
3. If you were to devote your career to meta-analytic research in parapsychology, what question would you most want to answer — and why?

---

## Final Examination Preparation

The final examination for PP401 consists of **one** assignment:

### Original Meta-Analysis (100% of course grade)

Conduct an original meta-analysis on a parapsychological topic of your choice. The meta-analysis must follow the standards described in this course and must be reported in a manuscript of 5,000-7,000 words (excluding references, tables, and figures) following PRISMA 2020 guidelines.

**Required components:**

1. **Abstract** (250 words): Structured abstract with Background, Objective, Methods, Results, and Conclusions.

2. **Introduction** (750 words): The research question, its significance, and a brief review of relevant prior work.

3. **Methods** (1,500 words): 
   - Protocol and pre-registration (OSF link required)
   - Search strategy (databases, search terms, date limits)
   - Inclusion/exclusion criteria
   - Data extraction (effect size metric, moderators)
   - Quality assessment (PSQS or similar)
   - Statistical analysis (model, software, publication bias methods, moderator analyses)

4. **Results** (1,500 words):
   - Study selection (PRISMA flow diagram)
   - Study characteristics (Table 1)
   - Primary meta-analysis (forest plot, effect size, 95% CI, p-value)
   - Heterogeneity (I², τ², Q)
   - Publication bias assessment (funnel plot, Egger's test, trim-and-fill, p-curve)
   - Moderator analyses (meta-regression, Table 2)
   - Sensitivity analyses

5. **Discussion** (1,000 words):
   - Summary of findings
   - Comparison with prior meta-analyses
   - Strengths and limitations
   - Implications for theory, practice, and future research
   - Conclusion

6. **References**: APA format, minimum 20 sources (including all included studies and methodological references).

7. **Supplementary materials**: Complete search strategy, PRISMA checklist, data extraction forms, analysis scripts (R or Python), and (if possible) extracted dataset.

**Timeline:**
- **Week 1-2**: Select topic, conduct preliminary search, develop protocol
- **Week 3-4**: Pre-register protocol, begin systematic search
- **Week 5-7**: Complete screening, data extraction, and quality assessment
- **Week 8-10**: Conduct analyses, write manuscript
- **Week 11-12**: Revise based on instructor feedback, finalize and submit

**Grading criteria:**
- Methodological rigor (40%): Was the search comprehensive? Were the inclusion criteria appropriate? Was the quality assessment adequate? Were the statistical analyses correct?
- Interpretation (30%): Were the results interpreted appropriately? Were limitations acknowledged? Were conclusions justified by the evidence?
- Clarity and presentation (20%): Was the manuscript well-written and well-organized? Did it follow PRISMA guidelines?
- Originality and significance (10%): Did the meta-analysis address a meaningful question? Did it contribute something new to the literature?

---

*ᛗ The whole is greater than the sum of its parts — not because the parts are enhanced by their assembly but because the assembly reveals a pattern that no part alone can show. Meta-analysis is the art of seeing the pattern in the scatter, the signal in the noise, the shape of the evidence that no individual study can reveal.*
