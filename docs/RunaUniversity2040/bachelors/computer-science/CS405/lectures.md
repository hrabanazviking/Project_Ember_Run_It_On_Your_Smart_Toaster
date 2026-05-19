# CS405: Research Methods in Computer Science
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS301 (Algorithms), CS303 (Software Engineering), CS304 (Distributed Systems), or instructor consent
**Description:** A rigorous introduction to the philosophy, design, execution, and communication of research in computer science. Covers literature review methodology, quantitative and qualitative methods, experimental design, statistical analysis, academic writing, peer review, open science practices, and the ethics of human subjects research. Prepares students for the CS407 Capstone and graduate-level research.

**Instructor:** Dr. Eiríkr Hafsteinn, D.Phil. (Oxon.), Professor of Computational Epistemology
**Office:** Yggdrasil Hall, Room 407-A
**Seminar:** Wednesdays 14:00–16:00, Freyja Auditorium

---

## Lectures

---

ᚠ **Lecture 1: The Philosophy of Scientific Inquiry — What Does It Mean to Know?**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Research begins not with methodology but with epistemology — the theory of knowledge itself. Before a student can design an experiment, they must confront a deceptively simple question: what counts as *knowing* something in computer science? This lecture traces the philosophical foundations of scientific inquiry from the logical positivists of the Vienna Circle through Popperian falsificationism, Kuhnian paradigm shifts, and Lakatosian research programmes, landing firmly in the computational epistemology of the 2040s. We examine how each philosophical stance implies a different standard of evidence, a different relationship between theory and experiment, and ultimately a different vision of what computer science as a discipline *is*.

### Key Topics

- **The Positivist Legacy:** Carnap, Neurath, and the verification principle — the dream of a unified science built on observation statements alone. Why the verification principle collapsed under its own weight (Hempel's paradox, the problem of theoretical terms) and what computer science inherited from its failure: an allergy to unverifiable claims but also a deep unease about the theoretical status of algorithms that exist only in mathematical abstraction.
- **Popper and Falsification:** The demarcation problem — separating science from non-science not by *verifiability* but by *falsifiability*. A theory is scientific only if it sticks its neck out, making predictions that could, in principle, be shown wrong. In CS terms: does your neural network architecture make a falsifiable claim, or is it merely engineering? The uncomfortable truth that most CS "research" is actually engineering under Popper's criterion — and why that matters for how we evaluate claims.
- **Kuhn's Structure of Scientific Revolutions:** The concept of the paradigm — a shared set of exemplars, methods, and metaphysical commitments that define "normal science." Kuhn's argument that science progresses not by accumulation but by crisis and revolution. In CS: are we in a period of normal science (incremental improvements to deep learning) or paradigm crisis (the growing evidence that scaling alone won't yield AGI)? The uncomfortable fit between Kuhn's historically-grounded model and the ahistorical self-image of computer science.
- **Lakatos and Research Programmes:** A synthesis of Popper and Kuhn — research programmes with a "hard core" of unfalsifiable assumptions protected by a "protective belt" of auxiliary hypotheses. Progress is measured not by individual falsifications but by whether the programme is "progressive" (predicting novel facts) or "degenerating" (merely accommodating anomalies post hoc). This maps remarkably well onto how CS subfields actually evolve — the deep learning programme, formal verification programme, quantum computing programme.
- **Computational Epistemology in 2040:** The rise of AI-generated hypotheses, automated experiment design, and large-scale computational replication has forced a re-examination of what it means to "know" something. If an AI system discovers a theorem that no human can understand (as with recent automated proofs in the Liquid Tensor Experiment), does the computer science community "know" it? The emerging field of *machine-aided epistemology* and the University of Yggdrasil's own VERÐANDI framework for tracking the provenance and epistemic status of computationally-derived claims.

### Required Reading

- Popper, K. (1959). *The Logic of Scientific Discovery*. Hutchinson. (Chapters 1–4)
- Kuhn, T.S. (1962/2012). *The Structure of Scientific Revolutions*. University of Chicago Press. (Chapters II–V, IX–X)
- Lakatos, I. (1978). *The Methodology of Scientific Research Programmes*. Cambridge University Press. (Chapter 1)
- Hafsteinn, E. & Ljósálfar, S. (2038). "Computational Epistemology: Knowledge Provenance in the Age of AI Discovery." *Journal of Machine-Aided Reasoning*, 14(3), 201–248.
- Verndal, A. (2040). "VERÐANDI: A Framework for Epistemic Status Tracking in Automated Research Pipelines." *UoY Technical Report* TR-2040-07.

### Discussion Questions

1. Is computer science a "science" in Popper's sense, or is it better understood as a branch of mathematics, engineering, or something else entirely? What hangs on the answer?
2. Kuhn's model predicts that paradigm shifts are resisted by the established generation. Can you identify potential paradigm shifts currently being resisted in CS, and by whom?
3. If an AI system proves a theorem that no human can verify step-by-step, should the CS community accept it as knowledge? What epistemic standard should apply?

### Practice Problems

- Classify five recent CS papers (from the 2039–2040 proceedings of NeurIPS, PLDI, or POPL) according to whether they operate within normal science or challenge a paradigm, and defend your classification.
- Draft a one-page "epistemic status statement" for your own research interests, following the VERÐANDI framework: what do you claim to know, how do you know it, what could falsify it, and what is your confidence level?

---

ᚢ **Lecture 2: Literature Review Methodology — Mapping the Scholarly Landscape**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Every research project begins with a question: what do we already know? The literature review is not a bureaucratic formality — it is the intellectual foundation upon which all subsequent work rests. A poor literature review produces redundant research, missed insights, and wasted effort. This lecture provides a systematic framework for conducting literature reviews in computer science, from formulating search queries to synthesising findings into a coherent narrative that identifies genuine gaps in knowledge.

### Key Topics

- **The Purpose of Review:** Beyond "has this been done before" — the literature review as gap analysis, as theoretical grounding, as methodological benchmark, and as intellectual positioning. The difference between a *descriptive* review (what exists), a *critical* review (what's wrong with what exists), and an *integrative* review (how disparate findings fit together). Why computer science PhD theses consistently underperform on critical and integrative dimensions compared to natural sciences.
- **Systematic Review Protocols:** The PRISMA 2040 framework adapted for computer science. Defining inclusion/exclusion criteria *before* searching (not retrofitting them to get the results you want). Search strategy design: database selection (ACM DL, IEEE Xplore, arXiv, DBLP, Semantic Scholar), keyword construction (Boolean operators, synonym mapping, controlled vocabularies), grey literature inclusion. Documentation standards that enable reproducibility — the review itself should be a research artefact.
- **Scoping Reviews and Meta-Analysis:** When a systematic review is impossible (too broad, too heterogeneous, too nascent a field), the scoping review maps the territory without synthesising results. Meta-analysis, conversely, statistically combines quantitative results across studies — increasingly important in ML/AI research where thousands of papers report performance metrics. The Cohen's d, Hedges' g, and the file-drawer problem (publication bias toward positive results). Forest plots and funnel plots as diagnostic tools.
- **AI-Assisted Literature Review:** By 2040, AI tools have transformed literature review from a manual slog into a human-AI collaboration. Semantic Scholar's TLDR generation, Elicit's automated evidence synthesis, and the University of Yggdrasil's own Huginn Research Raven (a fine-tuned model for CS literature synthesis). However: *uncritical reliance on AI assistants produces plausible-looking but factually wrong summaries.* The student's responsibility is verification — every AI-generated claim must be traced back to a primary source. Case study: the 2038 incident where an AI-generated literature review fabricated citations that were subsequently cited by 47 real papers before being detected.
- **Synthesis and Gap Identification:** The hardest skill — reading 200 papers and emerging with something to say that none of them said individually. Techniques: concept matrix construction (mapping papers × themes), chronological tracing (how has the problem evolved?), methodological clustering (who uses which methods and why?), and contradiction mapping (where do papers disagree, and what does the disagreement reveal?). The "so what?" test: if your literature review doesn't end with a clear, specific, defensible statement of what remains unknown and why it matters, it isn't finished.

### Required Reading

- Kitchenham, B. & Charters, S. (2007). "Guidelines for Performing Systematic Literature Reviews in Software Engineering." Keele University Technical Report EBSE-2007-01. (Updated 2039 edition)
- Grant, M.J. & Booth, A. (2009). "A Typology of Reviews: An Analysis of 14 Review Types and Associated Methodologies." *Health Information & Libraries Journal*, 26(2), 91–108.
- Page, M.J. et al. (2021). "The PRISMA 2020 Statement: An Updated Guideline for Reporting Systematic Reviews." *BMJ*, 372, n71. (Adapted for CS as PRISMA-CS 2040)
- Birgirsdóttir, K. (2039). "Hallucinated Citations in AI-Generated Literature Reviews: A Case Study and Detection Framework." *Proceedings of the ACM Conference on Research Integrity*, 12–24.
- University of Yggdrasil Library. (2040). "CS Literature Search Guide: Databases, Queries, and Tools." [Online resource, updated termly]

### Discussion Questions

1. What distinguishes a good literature review from a mere annotated bibliography? Can you find examples of both in recent CS conference proceedings?
2. How should the research community handle the growing problem of AI-generated literature reviews with fabricated citations? Is retraction sufficient, or do we need new verification infrastructure?
3. Is meta-analysis in ML research fundamentally flawed because different papers use different datasets, hardware, and hyperparameters? Or does statistical synthesis still provide value?

### Practice Problems

- Design a systematic review protocol for the question: "What is the effect of code generation AI assistants on junior developer productivity?" Include search terms, databases, inclusion/exclusion criteria, and a quality assessment framework.
- Using a concept matrix, analyse 10 papers on a CS topic of your choice and identify one specific, defensible research gap.

---

ᚦ **Lecture 3: Research Design — From Questions to Testable Hypotheses**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

A research question is the seed; a research design is the trellis that shapes its growth. This lecture bridges the gap between "I wonder whether..." and "Here is exactly how I will find out." We cover the architecture of research: how to transform vague curiosity into falsifiable hypotheses, how to select methods that can actually answer your question (rather than methods you happen to know), and how to anticipate and mitigate threats to validity before you collect a single data point.

### Key Topics

- **From Question to Hypothesis:** The "PICOC" framework adapted for CS: Population (what systems/users/algorithms?), Intervention (what are you changing/introducing?), Comparison (what's the baseline?), Outcome (what are you measuring?), Context (under what conditions?). A well-formed hypothesis is not "neural networks are good at image recognition" but "Vision Transformer architectures with patch size 16×16 achieve higher top-1 accuracy than ResNet-152 on ImageNet-2040 at p < 0.01 when both are trained from scratch for 300 epochs." Specificity is the soul of testability.
- **Types of Research Design:** The taxonomy of CS research designs — *formal* (proofs, models, axiomatic systems), *experimental* (controlled experiments, A/B tests, randomised controlled trials), *observational* (case studies, surveys, ethnographic studies of developer behaviour), *simulation-based* (agent-based modelling, Monte Carlo methods, synthetic data generation), and *design science* (building an artefact and evaluating it). Each design type has its own validity criteria, its own notion of rigour, and its own characteristic failure modes. The most common mistake in CS research: using an experimental design for a question that requires formal proof, or vice versa.
- **Construct Validity:** Are you measuring what you think you're measuring? In CS, this is pernicious. "Developer productivity" measured in lines of code rewards verbosity. "Algorithm efficiency" measured in wall-clock time depends on hardware, compiler, and background load. "User satisfaction" measured by a single Likert item captures noise, not signal. The solution: multiple operationalisations, validated instruments where they exist (NASA-TLX for cognitive load, SUS for system usability), and explicit argumentation linking constructs to measures.
- **Internal Validity:** Can you actually attribute the observed effect to your intervention? The classic threats: history (something else happened during the experiment), maturation (subjects changed over time), selection bias (groups weren't equivalent to begin with), instrumentation (your measurement tool changed or was inconsistently applied), and attrition (subjects dropped out non-randomly). In CS specifically: hardware variation, library versioning, random seed sensitivity, and compiler optimisations that silently change program semantics.
- **External Validity:** Does your finding generalise beyond the specific conditions of your study? The crisis of external validity in ML research — models tested on curated benchmarks that don't represent real-world data distributions (ImageNet→medical imaging, MNIST→handwriting in the wild). The concept of "ecological validity" — does your experimental setting resemble the actual context of use? Studying programmer behaviour in a 30-minute lab study vs. observing real developers over six months: entirely different knowledge claims.
- **Preregistration and Registered Reports:** The 2030s reform. Preregistering your hypothesis, methods, and analysis plan *before* collecting data prevents HARKing (Hypothesising After Results are Known) and p-hacking. Registered Reports go further — the journal reviews your introduction and methods *before* you run the experiment, guaranteeing publication regardless of outcome. This eliminates publication bias against null results. In 2040, the University of Yggdrasil requires preregistration for all empirical CS theses. The Yggdrasil Preregistration Portal (YPP) is integrated with the VERÐANDI framework.

### Required Reading

- Wohlin, C. et al. (2012). *Experimentation in Software Engineering*. Springer. (Chapters 4–7: Variables, Design, Analysis)
- Easterbrook, S. et al. (2008). "Selecting Empirical Methods for Software Engineering Research." In *Guide to Advanced Empirical Software Engineering*, Springer, 285–311.
- Nosek, B.A. et al. (2018). "The Preregistration Revolution." *PNAS*, 115(11), 2600–2606.
- Sculley, D. et al. (2038). "The Validity Crisis in ML Benchmarking: A Meta-Analysis of 5,000 Papers." *Journal of Machine Learning Research*, 39, 1–47.
- Thorsdóttir, G. (2040). "YPP: The Yggdrasil Preregistration Portal — Design and First-Year Outcomes." *UoY Computing Education Research*, 3(1), 12–34.

### Discussion Questions

1. Consider a recent CS paper you've read. Identify at least two threats to internal validity and two to external validity. How could the authors have mitigated them?
2. Is mandatory preregistration appropriate for all CS research, or are there subfields (e.g., theoretical computer science) where it makes no sense? Defend your position.
3. How would you design a study to measure whether pair programming with an AI assistant improves code quality, ensuring strong construct validity?

### Practice Problems

- Take a vague research interest ("I want to study whether Rust prevents bugs") and transform it into a specific, falsifiable hypothesis with operationalised constructs, a defined population, intervention, comparison, outcome, and context.
- Design a preregistration for a simple experiment (e.g., comparing two sorting algorithm animations for teaching effectiveness) using the YPP template.

---

ᚨ **Lecture 4: Quantitative Methods — Measurement, Inference, and Reproducibility**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Quantitative methods are the lingua franca of empirical computer science, yet they are systematically misunderstood and misapplied. This lecture is not a statistics course — it is a course in *thinking quantitatively*: what numbers can and cannot tell us, how to design measurements that survive scrutiny, and why the replication crisis in psychology has profound lessons for CS. We focus on the logic of statistical inference rather than its mechanics, though key techniques are demonstrated.

### Key Topics

- **Measurement Theory:** Every quantitative study begins with measurement, and every measurement embeds assumptions. The four levels of measurement (Stevens, 1946): nominal (labels, no ordering), ordinal (ranked, no fixed intervals), interval (equal intervals, arbitrary zero), and ratio (equal intervals, true zero). Why treating Likert-scale data as interval data is widespread but questionable. In CS: benchmarking scores — are they ratio data? (A system scoring 90% is not necessarily "twice as good" as one scoring 45%, depending on the metric's properties.)
- **Descriptive Statistics and Visualisation:** The often-neglected first step. Before running any test, *look at your data*. Histograms, box plots, violin plots, Q-Q plots for distribution checking. Measures of central tendency (mean, median, mode — and when each is appropriate) and dispersion (standard deviation, IQR, MAD). The Anscombe quartet as a permanent warning: four datasets with identical means, variances, correlations, and regression lines — and radically different structures. In CS: always plot your benchmark results before reporting summary statistics.
- **Inferential Statistics — The Logic:** The Neyman-Pearson framework: null hypothesis (H₀), alternative hypothesis (H₁), Type I error (α, false positive), Type II error (β, false negative), statistical power (1−β). The p-value: *not* the probability that H₀ is true, but the probability of observing data at least as extreme as yours *if* H₀ were true. The widespread misinterpretation: p = 0.03 does NOT mean "there's a 3% chance my finding is a fluke" — it means "if there were no effect, I'd see results this extreme 3% of the time." The difference is everything.
- **Effect Sizes and Confidence Intervals:** The 2030s shift away from null hypothesis significance testing (NHST) toward estimation. A p-value tells you whether an effect exists; an effect size tells you whether it *matters*. Cohen's d (small=0.2, medium=0.5, large=0.8), η² for ANOVA, and the increasingly popular "probability of superiority" (the probability that a randomly chosen observation from group A exceeds one from group B). Confidence intervals communicate precision — a 95% CI of [0.02, 0.04] says something very different from [−0.50, 0.54], even if both are "statistically significant."
- **Power Analysis:** The most underused tool in CS research. Statistical power is the probability of detecting an effect if it exists. Underpowered studies waste resources, produce unreliable results, and contribute to the replication crisis. Power depends on sample size, effect size, α level, and the specific test. Before running your experiment, conduct a power analysis: "If the true effect size is d = 0.5, how many participants/systems/benchmarks do I need to have an 80% chance of detecting it?" G*Power, the `pwr` package in R, and the `statsmodels` library in Python are your tools.
- **The Replication Crisis in CS:** Psychology's replication crisis (only ~40% of findings replicate) has a CS analogue that is only now being documented. The specific CS pathologies: reliance on a small set of benchmark datasets (overfitting to CIFAR-10, ImageNet, etc.), unreported hyperparameter tuning (which is data-dependent p-hacking), cherry-picked random seeds, and the file-drawer problem where negative results are simply never submitted. The solution: preregistration, benchmark diversity, sensitivity analysis across random seeds, and venues like the *Journal of Negative Results in Computer Science*.

### Required Reading

- Cumming, G. (2014). "The New Statistics: Why and How." *Psychological Science*, 25(1), 7–29.
- Cohen, J. (1992). "A Power Primer." *Psychological Bulletin*, 112(1), 155–159.
- Wasserstein, R.L. & Lazar, N.A. (2016). "The ASA Statement on p-Values: Context, Process, and Purpose." *The American Statistician*, 70(2), 129–133.
- Henderson, P. et al. (2038). "Deep Reinforcement Learning That Matters: A Reproducibility Audit." *Proceedings of AAAI*, 3201–3208. [Updated 2040 edition]
- Gunnarsdóttir, H. (2040). "Benchmark Overfitting: A Quantitative Analysis of 15 Years of ImageNet Results." *Pattern Recognition*, 142, 109–128.

### Discussion Questions

1. Why do you think p-values remain dominant in CS research despite decades of criticism? What would it take to shift the field toward estimation and effect sizes?
2. Choose a CS subfield you know well. What would a replication crisis audit look like — which practices are most vulnerable?
3. If you were reviewing a paper that reported p = 0.049 with n = 12, what questions would you ask the authors?

### Practice Problems

- Given a benchmark dataset with two algorithm variants, compute descriptive statistics, visualise the distributions, run an appropriate statistical test, report the effect size with confidence intervals, and write a one-paragraph interpretation suitable for a paper.
- Conduct a power analysis: you want to detect a medium effect (d = 0.5) with 80% power at α = 0.05 (two-tailed) using an independent-samples t-test. What minimum sample size do you need?

---

ᚱ **Lecture 5: Qualitative Methods — Understanding the Human Side of Computing**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Not everything that matters can be counted. Computer science is ultimately a human endeavour — tools are built by people, for people, within social and organisational contexts that quantitative methods alone cannot capture. This lecture introduces qualitative research methods adapted for computing: interviews, thematic analysis, grounded theory, and ethnography. We dispel the myth that qualitative research is "soft" or "subjective" — it is *different*, with its own rigorous standards of validity, reliability, and generalisability.

### Key Topics

- **Why Qualitative Methods in CS?** The questions that resist quantification: How do developers actually use version control in practice (not how they say they do)? What makes a code review feel helpful vs. hostile? Why do organisations adopt (or resist) AI tools? How do open-source communities govern themselves? These are questions about meaning, experience, and social process — the domain of qualitative inquiry. The growing recognition in CS that human factors are not confounding variables to be controlled away but the central objects of study.
- **Interviews — Structured, Semi-Structured, and Unstructured:** The interview as a research instrument. Structured interviews (fixed questions, fixed order) for comparability; semi-structured (topic guide, flexible probing) for depth; unstructured (conversational, emergent) for exploration. Crafting interview questions: open-ended, non-leading, singular (one question at a time). The art of the follow-up: "Can you tell me more about that?", "What did that feel like?", "Can you give me an example?" Transcription, coding, and the iterative nature of interview-based research — you learn as you go, and later interviews should be informed by earlier ones.
- **Thematic Analysis:** The workhorse of qualitative CS research. Braun and Clarke's (2006, 2021) six-phase approach: (1) familiarisation with data, (2) generating initial codes, (3) searching for themes, (4) reviewing themes, (5) defining and naming themes, (6) producing the report. The distinction between inductive (data-driven, bottom-up) and deductive (theory-driven, top-down) coding. Reflexive thematic analysis emphasises that themes don't "emerge" from data — the researcher *constructs* them through active interpretive labour. Quality criteria: coherence, rigour, and the "so what?" test applied to each theme.
- **Grounded Theory:** More than a coding technique — a full methodology for building theory from data. Strauss and Corbin's systematic approach (open coding, axial coding, selective coding) vs. Charmaz's constructivist grounded theory. Constant comparison: every new piece of data is compared with existing codes and categories, refining the emerging theory iteratively. Theoretical saturation: the point at which new data no longer prompts new insights. In CS: grounded theory has been used to build models of debugging behaviour, API usability, and the adoption of programming paradigms.
- **Ethnography and Participant Observation:** The deepest qualitative method — embedding yourself in a community or organisation for an extended period to understand its practices, values, and tacit knowledge. In CS: ethnographies of software teams (Sharp & Robinson, 2008), open-source communities (Ducheneaut, 2005), and AI research labs. The ethnographer's dilemma: participation vs. observation, insider vs. outsider status, and the ethical obligation to protect participants while producing honest accounts. Field notes, reflexivity journals, and the long durée of ethnographic analysis — months of observation yielding insights no survey could capture.
- **Mixed Methods:** The false dichotomy. Most significant CS research questions benefit from both quantitative and qualitative approaches. Explanatory sequential design (quant → qual: survey identifies patterns, interviews explain them). Exploratory sequential design (qual → quant: interviews generate hypotheses, experiment tests them). Convergent design (both simultaneously, results integrated at interpretation). The key: each method must be executed to its own standards of rigour — a weak qualitative component doesn't become stronger by being paired with strong quantitative work.

### Required Reading

- Braun, V. & Clarke, V. (2006). "Using Thematic Analysis in Psychology." *Qualitative Research in Psychology*, 3(2), 77–101.
- Charmaz, K. (2014). *Constructing Grounded Theory* (2nd ed.). SAGE. (Chapters 1–4)
- Sharp, H., Dittrich, Y., & de Souza, C.R.B. (2016). "The Role of Ethnographic Studies in Empirical Software Engineering." *IEEE Transactions on Software Engineering*, 42(8), 786–804.
- Hoda, R. (2039). "Socio-Technical Grounded Theory for Software Engineering: A 2040 Update." *Empirical Software Engineering*, 45(2), 201–234.
- Einarsdóttir, T. (2040). "Developer Experiences with AI Pair Programming: A Longitudinal Qualitative Study at Three Organisations." *Proceedings of CHI 2040*, 1–18.

### Discussion Questions

1. Is qualitative research "generalisable" in the same way quantitative research is? If not, what kind of knowledge does it produce, and why is it valuable?
2. How would you design a mixed-methods study to understand why some open-source projects thrive while structurally similar ones die?
3. Discuss the ethical challenges of conducting ethnographic research within your own professional community (e.g., studying fellow CS students or developers).

### Practice Problems

- Conduct a mini thematic analysis: recruit two peers for 15-minute interviews on "what makes a good code review," transcribe key excerpts, generate initial codes, and identify 2-3 candidate themes.
- Write a reflexivity statement: what are your own biases, experiences, and assumptions about software development, and how might they influence your interpretation of qualitative data?

---

ᚲ **Lecture 6: Experimental Design — Control, Randomisation, and Causal Inference**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The randomised controlled experiment is the gold standard for causal inference — the only research design that can, in principle, establish that X *causes* Y rather than merely being associated with it. This lecture covers the logic, mechanics, and pitfalls of experimental design in computing research: how to construct treatment and control groups, why randomisation matters (and when it's impossible), and how to handle the practical constraints that make "ideal" experiments unattainable.

### Key Topics

- **The Logic of Causal Inference:** The fundamental problem: we can never observe the same unit under both treatment and control conditions. The counterfactual framework (Rubin, 1974; Pearl, 2009): the causal effect is the difference between what happened and what *would have* happened. Randomisation solves this by ensuring that, on average, treatment and control groups are equivalent on all confounding variables — observed and unobserved. In CS: if we want to know whether a new IDE feature improves debugging speed, we can't compare the same programmer's debugging with and without the feature simultaneously. We randomise programmers to conditions and compare group means.
- **Between-Subjects vs. Within-Subjects Designs:** Between-subjects: each participant is in one condition (treatment or control). Requires larger samples, but avoids carryover effects. Within-subjects: each participant experiences all conditions (in counterbalanced order). More statistical power (each participant is their own control), but vulnerable to order effects, learning effects, and fatigue. In CS usability studies, within-subjects is common but demands careful counterbalancing (Latin square designs). The crossover design: A→B for half, B→A for half.
- **Factorial Designs:** Studying multiple factors simultaneously. A 2×2 factorial design tests two independent variables, each with two levels, yielding four conditions. Main effects (does factor A matter?), interaction effects (does the effect of A depend on B?). In CS: testing algorithm (A vs. B) × dataset size (small vs. large) to see not just which algorithm is better but whether the advantage depends on data scale. The power of factorial designs: more information per participant than separate single-factor experiments.
- **Quasi-Experiments:** When randomisation is impossible or unethical. Natural experiments (an external event creates treatment-like variation — e.g., a company suddenly adopting a new tool, providing a before/after comparison). Difference-in-differences (comparing change over time in treatment vs. control groups). Regression discontinuity (assignment based on a cutoff score — e.g., comparing projects just above and below a funding threshold). Instrumental variables. Each quasi-experimental design trades the clean interpretability of randomisation for practical feasibility — and each brings its own assumptions that must be defended.
- **Threats to Experimental Validity, Revisited:** The specific threats that experimental design addresses: selection bias (solved by randomisation), history (solved by concurrent control group), maturation (solved by control group), testing effects (solved by control group or Solomon four-group design), instrumentation (solved by standardised measurement protocols), regression to the mean (solved by control group and baseline measurement), and experimenter bias (solved by double-blinding — participants and experimenters don't know who's in which condition). In CS: what does "blinding" mean when the participant is a computer program? (Answer: it doesn't apply — but the *researcher analysing results* should be blinded to condition.)

### Required Reading

- Campbell, D.T. & Stanley, J.C. (1963). *Experimental and Quasi-Experimental Designs for Research*. Rand McNally. (Chapters 1–3, 5)
- Pearl, J. & Mackenzie, D. (2018). *The Book of Why: The New Science of Cause and Effect*. Basic Books. (Chapters 1–4)
- Kohavi, R., Tang, D., & Xu, Y. (2020). *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing*. Cambridge University Press. (Chapters 1–5)
- Siegmund, J. et al. (2038). "Quasi-Experimental Methods in Software Engineering Research: A Systematic Mapping Study." *Empirical Software Engineering*, 43, 78–115.
- Hafsteinn, E. (2040). "A/B Testing at Scale in the Age of Continuous Deployment: Lessons from 10,000 Experiments." *Communications of the ACM*, 63(4), 56–65.

### Discussion Questions

1. When is it ethical to randomise human participants to conditions that might affect their work performance? Where do you draw the line?
2. A/B testing has become ubiquitous in web companies. What are the limitations of A/B testing as a research paradigm — what kinds of questions can't it answer?
3. Design a hypothetical experiment: you believe that requiring students to write tests before code improves code quality. What's your design? What are the threats to validity?

### Practice Problems

- Given a scenario (comparing two code review tools on bug detection rate), design a between-subjects experiment, a within-subjects experiment, and a quasi-experiment. For each, identify the key validity threats and how you would mitigate them.
- Analyse a published CS experiment of your choice: identify the design type, evaluate the randomisation procedure, and critique the handling of potential confounds.

---

ᚷ **Lecture 7: Survey Methodology — Sampling, Measurement, and the Perils of Self-Report**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Surveys are simultaneously the most widely used and most widely abused research method in computer science. A well-designed survey can illuminate developer attitudes, technology adoption patterns, and community norms at scale. A poorly designed survey produces garbage — and worse, garbage that looks like data. This lecture covers the entire survey lifecycle: sampling strategy, questionnaire design, pilot testing, administration, and analysis, with emphasis on the specific challenges of surveying technical populations.

### Key Topics

- **Sampling — Who Are You Actually Studying?** The sampling frame is the list from which you draw respondents; the sample is who actually responds. The gap between them is nonresponse bias — and it's almost always the biggest threat to survey validity. Convenience sampling (posting on Twitter, Reddit, or Hacker News) reaches whoever happens to see your post — not a representative sample of any defined population. Probability sampling (simple random, stratified, cluster) is ideal but rare in CS research. Snowball sampling (respondents recruit more respondents) amplifies existing network biases. In 2040, the best practice is to clearly define your target population, acknowledge your actual sample's limitations, and conduct sensitivity analyses: how might your conclusions change if non-respondents differ systematically from respondents?
- **Questionnaire Design:** The art and science of asking good questions. Principles: use simple, concrete language; avoid double-barrelled questions ("Is the tool fast and easy to use?" — two questions, one answer); avoid leading questions ("Most developers find this tool helpful — do you?"); provide balanced response scales (equal numbers of positive and negative options, not "Excellent / Very Good / Good / Fair" which skews positive); include "Not Applicable" and "Prefer Not to Say" options. The Likert scale: 5-point vs. 7-point, labelled endpoints vs. all points labelled, the acquiescence bias (tendency to agree) and how reverse-coded items detect it.
- **Validated Instruments:** Don't reinvent the wheel. For measuring established constructs, use instruments that have been psychometrically validated: the System Usability Scale (SUS, Brooke, 1996) for usability, the NASA Task Load Index (NASA-TLX) for cognitive workload, the Technology Acceptance Model (TAM, Davis, 1989) for adoption intentions, the Unified Theory of Acceptance and Use of Technology (UTAUT2, Venkatesh et al., 2012) for technology adoption. Adapting an existing instrument for CS: validate the adaptation with a pilot study, check internal consistency (Cronbach's α ≥ 0.70), and report the reliability in your paper.
- **Pilot Testing:** Essential and routinely skipped. Before launching your survey to 500 developers, test it with 5–10. Watch them complete it (think-aloud protocol: "tell me what you're thinking as you read each question"). The questions you think are clear will confuse people. The response options you think are exhaustive will miss common cases. The survey you think takes 5 minutes will take 15. Iterate: test → revise → test again. In 2040, AI-assisted pilot testing (simulated respondents with diverse profiles) can catch obvious problems, but nothing replaces testing with real humans from your target population.
- **Ethics and Data Protection:** Surveys involving human subjects require ethical approval (IRB in the US, Research Ethics Committee in the UK, equivalent at UoY). Key principles: informed consent (participants must understand what they're agreeing to, including data storage, anonymisation, and the right to withdraw), minimisation of harm (avoid questions that could cause distress, provide support resources if needed), confidentiality (anonymise data, store securely, limit access), and honest reporting (don't data-dredge for "significant" findings post hoc). GDPR compliance for EU/UK respondents: lawful basis for processing, data minimisation, right to erasure.

### Required Reading

- Fowler, F.J. (2014). *Survey Research Methods* (5th ed.). SAGE. (Chapters 1–6)
- Groves, R.M. et al. (2009). *Survey Methodology* (2nd ed.). Wiley. (Chapters 1, 4, 6)
- Kitchenham, B.A. & Pfleeger, S.L. (2008). "Personal Opinion Surveys." In *Guide to Advanced Empirical Software Engineering*, Springer, 63–92.
- Smith, E. et al. (2039). "The Developer Survey Quality Checklist: A Systematic Assessment Tool." *IEEE Transactions on Software Engineering*, 65(8), 1234–1256.
- University of Yggdrasil Research Ethics Committee. (2040). "Guidelines for Online Survey Research with Technical Populations." UoY-REC-2040-03.

### Discussion Questions

1. How would you sample "all professional software developers in the United Kingdom"? What's your sampling frame, and what biases does it introduce?
2. The System Usability Scale produces a single number (0–100). What does this number actually mean? What does it hide?
3. Discuss: Is it ethical to analyse public GitHub data (commits, comments, pull requests) without explicit consent from the developers who created it?

### Practice Problems

- Design a 15-item questionnaire to measure "developer trust in AI code generation tools." Include demographic items, construct items (with at least one reverse-coded item), and a validated usability/trust instrument. Pilot it with three peers and revise.
- Given a dataset of survey responses, check internal consistency (Cronbach's α) for a multi-item scale, identify items that reduce reliability, and recommend improvements.

---

ᚹ **Lecture 8: Data Management and Reproducible Research — FAIR Principles in Practice**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Research data has a lifecycle — from collection through cleaning, analysis, and archiving — and poor management at any stage can render an otherwise excellent study irreproducible. This lecture introduces the FAIR principles (Findable, Accessible, Interoperable, Reusable) and the practical tools and workflows that make computational research reproducible: version control for data (not just code), literate programming, containerisation, and open data repositories. By 2040, the expectation is that any empirical CS paper should come with everything needed to reproduce its results.

### Key Topics

- **The FAIR Principles:** Published in 2016, codified as community standard by 2030, legally mandated by many funding bodies by 2040. *Findable:* data has a persistent identifier (DOI), rich metadata, and is registered in a searchable resource. *Accessible:* data is retrievable by its identifier using a standard protocol, with clear authentication and authorisation procedures. *Interoperable:* data uses formal, accessible, shared, and broadly applicable languages for knowledge representation. *Reusable:* data has clear usage licenses, detailed provenance, and meets domain-relevant community standards. In CS: this means publishing datasets on Zenodo, Figshare, or institutional repositories with DOIs, documenting schemas, and using standard formats (JSON, CSV, Parquet) rather than proprietary ones (.mat, .sav).
- **Version Control for Research:** Git for code is standard; Git (or Git LFS) for data is becoming standard. The research project should be a single repository containing code, data (or links to data), documentation, and the manuscript itself. Tools: DVC (Data Version Control) for large datasets, Git LFS for binary assets, Quilt for data package management. The `renv` package (R) and `pip freeze` / `poetry.lock` (Python) for capturing exact dependency versions. The goal: another researcher clones your repository and runs a single command to reproduce your entire analysis pipeline.
- **Literate Programming and Computational Notebooks:** The idea, dating back to Knuth (1984), that code and narrative should be interwoven. Jupyter Notebooks, R Markdown, Quarto, and Observable are modern instantiations. Strengths: transparency, educational value, natural integration of text, code, and visualisations. Weaknesses: hidden execution state (cells run out of order), poor diffing in version control, temptation to produce "notebook spaghetti." Best practices for 2040: clear cell ordering, `Restart & Run All` before committing, Jupyter Notebook diffs via `nbdime`, and considering `.qmd` (Quarto) files as an alternative with better version control properties.
- **Containerisation for Reproducibility:** "It works on my machine" is the death of reproducible research. Docker (and its HPC-friendly cousin, Singularity/Apptainer) solves this by packaging the entire computational environment — OS, libraries, dependencies, code — into a portable image. For CS research: a Dockerfile that specifies the exact Ubuntu version, Python version, package versions (pinned), and any system dependencies. The container can be built and run on any machine with Docker. In 2040, the University of Yggdrasil's Research Computing Service maintains a repository of base containers for common CS research stacks.
- **Data Management Plans (DMPs):** Required by UoY and most funders before research begins. What data will you collect or generate? How will it be documented? How will you handle ethics, consent, and confidentiality? Where will it be stored during the project (with backups)? How and where will it be archived and shared afterwards? Who is responsible? Writing a DMP forces you to think through data management *before* you have data — which is exactly when you should be thinking about it.

### Required Reading

- Wilkinson, M.D. et al. (2016). "The FAIR Guiding Principles for Scientific Data Management and Stewardship." *Scientific Data*, 3, 160018.
- Sandve, G.K. et al. (2013). "Ten Simple Rules for Reproducible Computational Research." *PLoS Computational Biology*, 9(10), e1003285.
- Rule, A. et al. (2019). "Ten Simple Rules for Writing and Sharing Computational Analyses in Jupyter Notebooks." *PLoS Computational Biology*, 15(7), e1007007.
- Grüning, B. et al. (2038). "Practical Reproducibility in Computational Science: A 2040 Update." *Nature Methods*, 35(4), 301–320.
- UoY Research Data Service. (2040). "Data Management Planning for Computer Science: A Practical Guide." [Online, updated annually]

### Discussion Questions

1. Is full reproducibility a realistic goal for all CS research, or are there kinds of studies (e.g., large-scale A/B tests at proprietary companies) where it's fundamentally impossible?
2. What are the privacy implications of the FAIR principles — how do we make data accessible while protecting participant confidentiality?
3. How should the CS community handle papers whose results cannot be reproduced because the original computational environment no longer exists?

### Practice Problems

- Take one of your own programming projects and make it reproducible: add a `requirements.txt` or `environment.yml` with pinned versions, write a `README.md` with setup instructions, and create a Dockerfile that builds and runs the project.
- Write a Data Management Plan for a hypothetical study involving surveys of 200 developers and analysis of their public GitHub repositories. Address FAIR principles, ethics, storage, and archiving.

---

ᚺ **Lecture 9: Statistical Methods for Computer Science — Beyond t-tests**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The independent-samples t-test is the hammer of CS empiricism, and not every problem is a nail. This lecture surveys the statistical toolkit beyond introductory methods: non-parametric tests for when normality assumptions fail, ANOVA for multi-group comparisons, regression for modelling relationships, and Bayesian approaches that offer an alternative philosophical framework. Each method is presented with its assumptions, its appropriate use cases in CS research, and its common misapplications.

### Key Topics

- **Non-Parametric Tests:** When your data violates the assumptions of parametric tests (normality, homogeneity of variance, interval/ratio measurement). The Mann-Whitney U test (alternative to independent t-test), Wilcoxon signed-rank test (alternative to paired t-test), Kruskal-Wallis test (alternative to one-way ANOVA). Advantages: fewer assumptions, robust to outliers. Disadvantages: lower statistical power when assumptions *are* met, tests medians not means, harder to compute effect sizes. In CS benchmarking: if your runtime measurements are heavily skewed (common with systems research), non-parametric tests are often more appropriate.
- **ANOVA and Multiple Comparisons:** Analysis of Variance tests whether three or more group means differ. One-way ANOVA (one factor), two-way ANOVA (two factors with interaction). The F-test tells you *whether* there's a difference somewhere, but not *where*. Post-hoc tests (Tukey's HSD, Bonferroni correction, Holm-Bonferroni) identify which specific pairs differ while controlling the familywise error rate. The multiple comparisons problem: if you run 20 t-tests at α = 0.05, you expect one false positive by chance alone. Corrections adjust α downward but reduce power — the eternal trade-off.
- **Regression Analysis:** Modelling the relationship between a dependent variable and one or more independent variables. Linear regression (continuous outcome), logistic regression (binary outcome), Poisson regression (count outcome). The regression equation: Y = β₀ + β₁X₁ + β₂X₂ + ... + ε. Interpreting coefficients: β₁ is the expected change in Y for a one-unit change in X₁, holding all other variables constant. Key diagnostics: R² (proportion of variance explained), residual plots (checking linearity, homoscedasticity, normality), multicollinearity (VIF > 10 is trouble), and influential points (Cook's distance). In CS: predicting code review latency from reviewer experience, patch size, and time of day.
- **The Generalised Linear Model (GLM) and Beyond:** Linear regression assumes normally distributed errors. GLMs relax this: link functions connect the linear predictor to the response distribution. Logistic regression (binary outcome, logit link), Poisson regression (count outcome, log link), Gamma regression (positive continuous, inverse link). Mixed-effects models (aka multilevel models, hierarchical models) handle clustered/nested data: students within classes, commits within repositories, measurements within subjects. Random intercepts and random slopes model group-level variation without the degrees-of-freedom penalty of fixed effects.
- **Bayesian Statistics — An Introduction:** The Bayesian framework: probability as degree of belief, not long-run frequency. Bayes' theorem: P(H|D) = P(D|H) × P(H) / P(D). Prior distribution (what you believed before seeing data) × likelihood (what the data say) → posterior distribution (what you should believe now). Advantages: natural incorporation of prior knowledge, intuitive interpretation of credible intervals ("there's a 95% probability the true effect lies in this range" — which is what people mistakenly think confidence intervals mean), no p-values, sequential updating as new data arrives. Disadvantages: prior sensitivity (different priors → different posteriors), computational intensity (MCMC sampling), and the fact that most CS reviewers still don't understand Bayesian results. In 2040, Bayesian methods are increasingly standard, driven by probabilistic programming languages (Stan, PyMC, Turing.jl).
- **Machine Learning for Research — Caution:** ML methods (random forests, neural networks, gradient boosting) are powerful predictive tools, but they are *not* substitutes for statistical inference. ML models optimise for prediction, not for understanding causal relationships. A random forest might predict bug-prone files with high accuracy but tell you nothing about *why* those files are bug-prone. When your research question is "does X cause Y?", use statistical methods. When it's "can we predict Y from X?", ML may be appropriate — but report interpretable metrics, avoid data leakage, and don't overclaim.

### Required Reading

- Field, A. (2018). *Discovering Statistics Using IBM SPSS Statistics* (5th ed.). SAGE. (Chapters on ANOVA, regression, GLM)
- McElreath, R. (2020). *Statistical Rethinking: A Bayesian Course with Examples in R and Stan* (2nd ed.). CRC Press. (Chapters 1–4)
- Kruschke, J.K. (2015). *Doing Bayesian Data Analysis* (2nd ed.). Academic Press. (Chapters 1–6)
- Arcuri, A. & Briand, L. (2038). "A Practical Guide for Using Statistical Tests to Assess Randomized Algorithms in Software Engineering." *IEEE Transactions on Software Engineering*, 64(3), 456–478.
- Gelman, A. et al. (2039). "Bayesian Workflow: A 2040 Perspective." *Statistical Science*, 44(1), 1–28.

### Discussion Questions

1. When should a CS researcher choose non-parametric over parametric tests? Can you think of common CS scenarios where parametric assumptions are routinely violated?
2. "Bayesian methods are philosophically superior but practically harder — the extra effort isn't worth it." Argue for or against this position.
3. How should the CS community handle the growing use of ML methods in empirical research papers, given that most CS researchers are not trained statisticians?

### Practice Problems

- Given a dataset comparing four sorting algorithms on three types of input, run a two-way ANOVA, check assumptions, conduct post-hoc tests, and write up the results.
- Re-analyse a published CS experiment using Bayesian methods: specify appropriate priors, compute posterior distributions, and compare your conclusions with the original frequentist analysis.

---

ᚾ **Lecture 10: Academic Writing — Structure, Argument, and the Craft of Persuasion**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Research that isn't communicated effectively might as well not have been done. Academic writing is not merely "typing up results" — it is the craft of constructing a persuasive argument that leads the reader from "I don't know this" to "I believe this, and I understand why." This lecture covers the structure of CS papers, the anatomy of effective arguments, and the writing process itself: how to draft, revise, and emerge with prose that is clear, precise, and compelling.

### Key Topics

- **The IMRaD Structure and Its Variations:** Introduction, Methods, Results, and Discussion — the dominant structure of empirical CS papers, inherited from the natural sciences. The Introduction is a funnel: broad context → specific problem → gap → your contribution → roadmap. The Methods section is a recipe: another researcher should be able to replicate your study from this section alone. The Results section is evidence: what did you find, presented neutrally, without interpretation. The Discussion section is meaning: what do the results mean, how do they relate to prior work, what are the limitations, what are the implications? Alternative structures: the "anatomy of a system" paper (architecture → implementation → evaluation), the theory paper (definitions → lemmas → theorems → proofs), the position paper (claim → arguments → counterarguments → rebuttal).
- **The Argument as Architecture:** Every paper makes a claim and defends it. The claim should be specific, falsifiable, and significant. The defence should be logical, evidence-based, and honest about limitations. The "They Say / I Say" model (Graff & Birkenstein): academic writing is a conversation — situate your argument in relation to what others have said ("While X argues that ___, I contend that ___ because ___"). Signposting: tell the reader what's coming ("In this section, we first ___, then ___, and finally ___"). Topic sentences: each paragraph should open with a sentence that states its main point — a reader should be able to follow your argument by reading only the first sentence of each paragraph.
- **Clarity, Precision, and the War on Jargon:** The best CS writing is clear, not clever. Avoid passive voice unless the agent is genuinely unknown or irrelevant ("We measured latency" not "Latency was measured"). Avoid nominalisations that hide the action ("We implemented" not "The implementation of"). Define terms before using them. Use consistent terminology throughout. Jargon is necessary for precision within a subfield but alienating outside it — a paper submitted to a general CS venue should define specialised terms on first use. The "grandmother test": could an intelligent non-specialist understand the abstract?
- **Figures and Tables:** "A picture is worth a thousand words" — but a bad figure is worth negative a thousand words. Principles: every figure should have a clear message; label axes with units; use colour intentionally (not decoratively); avoid chartjunk (3D effects, gratuitous gradients, pie charts with more than 5 slices); choose the right visualisation for the data (bar charts for categories, line charts for trends, scatter plots for relationships, box plots for distributions). Tables should present precise numbers; figures should reveal patterns. Never use a figure when a sentence would do — and never use a sentence when a figure would do better.
- **The Writing Process:** Writing is rewriting. First draft: get words on the page, don't edit as you go (the "shitty first draft" principle from Lamott). Second draft: fix structure — does the argument flow? Are sections in the right order? Third draft: fix paragraphs — does each paragraph have one main idea? Do paragraphs connect? Fourth draft: fix sentences — cut unnecessary words, vary sentence length, check grammar. Final pass: read aloud — your ear catches awkwardness your eye skips over. The toolchain: LaTeX (still standard in CS for its typesetting quality, though alternatives like Typst are gaining ground), Markdown with Pandoc for conversion, reference managers (Zotero, Paperpile), collaborative writing (Overleaf, which by 2040 has real-time AI-assisted editing and reference checking).
- **Peer Review — Giving and Receiving:** Peer review is the quality control mechanism of science, and it's adversarial by design but should be constructive in practice. As a reviewer: be specific ("the sampling strategy doesn't support the claimed generalisation because..." not "the methodology is weak"), be fair (evaluate the work the authors did, not the work you wish they'd done), be professional (no personal attacks, no sarcasm), and be timely. As an author receiving reviews: read them, walk away for 24 hours, read them again. Separate the signal from the emotional reaction. Address every point in your response letter, even if you disagree (and explain why you disagree). The rebuttal is an opportunity, not an ordeal.

### Required Reading

- Zobel, J. (2014). *Writing for Computer Science* (3rd ed.). Springer. (Chapters 1–8)
- Graff, G. & Birkenstein, C. (2021). *They Say / I Say: The Moves That Matter in Academic Writing* (5th ed.). W.W. Norton.
- Lamott, A. (1994). *Bird by Bird: Some Instructions on Writing and Life*. Anchor Books. (The "Shitty First Drafts" chapter)
- Tufte, E.R. (2001). *The Visual Display of Quantitative Information* (2nd ed.). Graphics Press.
- Knuth, D.E., Larrabee, T., & Roberts, P.M. (2038). *Mathematical Writing* (2040 Digital Edition). Mathematical Association of America.

### Discussion Questions

1. How does writing for a CS conference differ from writing for a journal? What changes in structure, depth, and audience?
2. Is the peer review system fundamentally broken, or are its flaws tolerable given the absence of a better alternative? What would a better system look like in 2040?
3. Analyse the abstract of a recent CS paper: does it clearly state the problem, the approach, the results, and the significance? Rewrite it if necessary.

### Practice Problems

- Take a section of your own writing (or a published paper's methods section) and revise it for clarity: cut 20% of the words without losing meaning, convert passive to active voice, and ensure every paragraph has a clear topic sentence.
- Write a peer review of a short paper (provided in class). Then exchange reviews with a partner and critique each other's reviews: were they constructive? Specific? Fair?

---

ᚨ (Ansuz) **Lecture 11: Open Science and Research Integrity — The Moral Foundations of Scholarship**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

Science is a social enterprise built on trust — trust that data are real, that methods are honestly reported, that conclusions follow from evidence. When that trust is violated, the entire edifice is compromised. This lecture examines research integrity not as a set of rules to avoid punishment but as a positive ethical commitment: what does it mean to be an honest researcher? We cover fabrication, falsification, and plagiarism (FFP), the greyer territory of questionable research practices (QRPs), and the open science movement that makes integrity visible through transparency.

### Key Topics

- **FFP — The Cardinal Sins:** Fabrication (making up data), falsification (manipulating or selectively deleting data to get desired results), and plagiarism (presenting others' work as your own). These are the "red lines" — in 2040 as in 1920, they end careers. But the line between falsification and "data cleaning" can blur: when does removing outliers become cherry-picking? When does image enhancement become image manipulation? The standard: document every data exclusion decision with a clear rationale *before* analysing results. If you're tempted to bend this rule, you already know you're on the wrong side of it.
- **Questionable Research Practices (QRPs):** The grey zone that does more cumulative damage than outright fraud. P-hacking: running multiple analyses and reporting only the significant ones. HARKing: presenting a post-hoc finding as if it were an a priori hypothesis. Selective reporting: publishing only the studies that "worked." Data peeking: checking results partway through data collection and stopping when significance is reached. In CS specifically: cherry-picking the random seed that gives the best result, reporting only the best hyperparameter configuration, comparing your method against weak baselines, and the pervasive "benchmark hack" — designing your method to perform well on a specific benchmark rather than solving the underlying problem.
- **The Open Science Movement:** The response to the replication crisis. Open access: research should be freely available, not locked behind paywalls. (By 2040, Plan S and similar mandates have made most CS research open access.) Open data: the data behind published claims should be available for scrutiny. Open code: the analysis scripts, and ideally the experimental software itself, should be published. Open materials: surveys, stimuli, protocols. Preregistration: the hypothesis and analysis plan are registered before data collection. Registered Reports: journals accept papers based on the question and methods, before results are known. Preprints: posting papers to arXiv *before* peer review accelerates dissemination and invites community feedback.
- **Authorship and Credit:** Who qualifies as an author? The ICMJE criteria: (1) substantial contributions to conception, design, data acquisition, or analysis; (2) drafting or critically revising the work; (3) final approval of the published version; (4) agreement to be accountable for all aspects. All four must be met. "Gift authorship" (adding someone who didn't contribute) and "ghost authorship" (omitting someone who did) are both unethical. Author order: in CS, the first author typically did the most work; the last author is often the senior/PI. Some subfields use alphabetical ordering (theoretical CS, mathematics). Discuss author order *before* starting the project, not after the paper is written.
- **Conflicts of Interest:** Financial (company funding research that might benefit the company), personal (reviewing a friend's or rival's paper), and intellectual (attachment to a theory that the data might disprove). Conflicts don't disqualify you from research, but they must be *declared* so readers can evaluate your work with full context. In 2040, the growing entanglement of academia and industry in CS/AI research makes conflict-of-interest disclosure more critical than ever. When a tech company funds academic AI safety research, the conflict is inherent — but transparency preserves the possibility of trust.
- **Whistleblowing and Institutional Responses:** What should you do if you suspect research misconduct? The University of Yggdrasil's Research Integrity Officer (RIO) is the first point of contact. Document your concerns. Do not make public accusations without going through proper channels — both for legal protection and to ensure fair process. The painful reality: whistleblowers often suffer retaliation, and institutions often protect their own. The 2040 reforms: independent oversight bodies, protected whistleblower status, and mandatory integrity training for all research students — but the hardest problems remain social, not procedural.

### Required Reading

- National Academies of Sciences, Engineering, and Medicine. (2017). *Fostering Integrity in Research*. National Academies Press. (Chapters 1–3)
- Munafò, M.R. et al. (2017). "A Manifesto for Reproducible Science." *Nature Human Behaviour*, 1, 0021.
- Nosek, B.A., Spies, J.R., & Motyl, M. (2012). "Scientific Utopia: II. Restructuring Incentives and Practices to Promote Truth Over Publishability." *Perspectives on Psychological Science*, 7(6), 615–631.
- Björnsdóttir, Á. (2039). "Questionable Research Practices in AI: A Survey of 2,000 NeurIPS Authors." *Proceedings of the AAAI/ACM Conference on AI Ethics*, 45–58.
- UoY Research Integrity Office. (2040). "Code of Practice for Research Integrity." [University policy document, updated annually]

### Discussion Questions

1. Where is the line between "data cleaning" and "data falsification"? Can you construct a scenario that genuinely tests this boundary?
2. Should open science practices (preregistration, open data, open code) be mandatory for all published CS research, or should there be exceptions? What would those exceptions be?
3. You discover that a colleague's published paper contains results that you strongly suspect are fabricated, but you have no proof. What do you do?

### Practice Problems

- Audit a published CS paper for QRPs: does it report all dependent variables measured? Are the analyses clearly specified as confirmatory or exploratory? Are all data exclusions justified?
- Write a preregistration for a simple experiment, then imagine the results come out the opposite of what you predicted. Write the discussion section honestly, without HARKing or spinning the findings.

---

ᛞ **Lecture 12: The Future of CS Research — AI, Automation, and the Changing Nature of Discovery**

**Course:** CS405 — Research Methods in CS
**Degree:** Bachelor of Science in Computer Science, 2040

---

### Overview

The tools of research are themselves being transformed by the technologies they study. In 2040, AI systems can search literature, generate hypotheses, design experiments, write code, analyse data, and draft manuscripts. This lecture confronts the profound question: as AI becomes an increasingly capable research collaborator, what remains distinctively human about the research enterprise? And how must our standards of rigour, credit, and integrity evolve when our co-author is a machine?

### Key Topics

- **AI-Assisted Literature Discovery:** By 2040, tools like Semantic Scholar's Research Feed, Elicit, and the UoY Huginn system can process thousands of papers and surface relevant findings. But AI-driven literature discovery introduces new biases: algorithmic recommendations create filter bubbles, over-representation of well-cited (not necessarily best) work, and language bias toward English-language publications. The researcher's responsibility: use AI tools as discovery aids, not as epistemic authorities. Verify AI-summarised claims against primary sources, and actively seek out perspectives the algorithm might miss.
- **Automated Experimentation:** Platforms like AutoML, Bayesian optimisation, and automated A/B testing frameworks can run thousands of experiments and identify optimal configurations. This raises the bar for what counts as a "contribution": merely reporting that configuration X outperforms configuration Y on benchmark Z is increasingly automatable and decreasingly interesting. The distinctive human contribution is *asking good questions* — formulating hypotheses that matter, designing experiments that genuinely test those hypotheses, and interpreting results in a broader theoretical context. Automation handles the "how"; the researcher provides the "why."
- **AI as Co-Author?** The 2038 ACM policy: AI systems cannot be listed as authors because authorship requires accountability, and AI cannot be held accountable. However, the use of AI in research must be transparently disclosed. By 2040, this policy is under strain: AI systems now contribute substantially to some papers' intellectual content (generating novel hypotheses, discovering unexpected patterns, even suggesting experimental designs the humans hadn't considered). Should the policy change? The opposing arguments: (pro) if a system contributed intellectually, acknowledging it as co-author is honest; (con) authorship is a social contract of responsibility that machines cannot enter into. The UoY position (2040): AI contributions should be described in a dedicated "AI Assistance Statement" section, specifying which AI tools were used, for what purposes, and how outputs were verified.
- **The Reproducibility of AI-Augmented Research:** If your research pipeline includes an AI component (LLM for hypothesis generation, AutoML for model selection), reproducing your results requires access to the *exact same AI system with the same parameters*. But commercial AI systems are black boxes, updated silently by their providers, with no guarantee of behavioural consistency over time. This creates a new kind of reproducibility crisis: even with open code and open data, AI-augmented results may be irreproducible because the AI component has changed. Solutions: use open-weight models where possible, record exact model versions and inference parameters, and for commercial APIs, document the API version, date of access, and prompt templates. The VERÐANDI framework's AI provenance module addresses this.
- **Research Ethics in the AI Era:** New ethical challenges: (1) AI systems trained on copyrighted material — does using them for research constitute copyright infringement? (2) The environmental cost of large-scale AI research — how should we weigh computational carbon footprint against scientific benefit? (3) AI-generated research that is intentionally or unintentionally deceptive — the 2038 "paper mill" scandal where AI generated plausible-looking but entirely fabricated CS papers that passed peer review at low-tier venues. (4) The global equity problem — researchers at well-resourced institutions have access to AI tools that researchers in the Global South do not, potentially widening the research inequality gap. These are not hypotheticals — they are the ethical landscape you will navigate as a CS researcher in the 2040s.
- **What Remains Human:** As AI automates the mechanical aspects of research, the core human competencies become more, not less, valuable: curiosity (the drive to ask questions no algorithm would think to ask), critical thinking (the ability to recognise when an AI-generated answer is plausibly wrong), creativity (synthesising ideas across domains in ways current AI cannot), ethical judgment (deciding what should be researched, not just what can be), and communication (writing prose that doesn't just inform but persuades, inspires, and connects). The CS405 course exists precisely to cultivate these competencies — because the researcher who only knows methods will be replaced by the machine that executes them faster. The researcher who knows *why* we do research, and can communicate that vision with clarity and integrity, will remain irreplaceable.

### Required Reading

- ACM Ethics & Plagiarism Committee. (2038). "Policy on AI-Generated Content in Scholarly Publications." *Communications of the ACM*, 61(12), 8–9.
- Birhane, A. et al. (2039). "The Values Encoded in Machine Learning Research: A Critical Analysis." *Proceedings of FAccT 2040*, 1–15.
- Hutson, M. (2038). "Artificial Intelligence and the Future of Peer Review." *Science*, 380(6640), 12–14.
- Thorsdóttir, G. & Hafsteinn, E. (2040). "VERÐANDI AI Provenance Module: Tracking Computational Epistemic Dependencies." *UoY Technical Report* TR-2040-12.
- UoY Centre for AI Ethics. (2040). "Guidelines for the Ethical Use of AI in Academic Research." [Institutional policy, revised annually]

### Discussion Questions

1. Should an AI system that makes a genuine intellectual contribution to a paper be acknowledged as a co-author? Why or why not?
2. How should the CS community address the environmental costs of AI research? Is "carbon impact statements" on papers a meaningful response or empty signalling?
3. What aspects of the research process do you believe will remain uniquely human in 2060? What aspects do you expect to be fully automated?

### Practice Problems

- Draft an "AI Assistance Statement" for your CS407 capstone project, specifying which AI tools you used, how you used them, and how you verified their outputs.
- Write a one-page reflection: what kind of researcher do you want to be in the 2040s, and what skills from this course will matter most for that vision?

---

---

## Final Examination Preparation

The final examination for CS405 consists of two components:

### Part A: Research Proposal (60%)
Design a complete research proposal for a computer science research question of your choice. The proposal must include:
1. **Introduction and Literature Review** (2–3 pages): What is the research question, why does it matter, and what does prior work say?
2. **Research Design** (2–3 pages): Hypothesis/hypotheses, methodology (quantitative, qualitative, or mixed), sampling strategy, data collection instruments, analysis plan. Include a power analysis if quantitative.
3. **Validity and Ethics** (1 page): Threats to validity and how you will mitigate them. Ethical considerations (human subjects? data protection? conflicts of interest?).
4. **Data Management Plan** (1 page): Following FAIR principles.
5. **Preregistration** (using the YPP template): Submit alongside the proposal.

Your proposal should demonstrate mastery of the entire research lifecycle covered in this course.

### Part B: Critical Analysis Essay (40%)
Choose ONE of the following:

- **Option 1:** Select a published empirical CS paper and write a 3-page methodological critique. Evaluate its research design, statistical analysis, handling of validity threats, and reproducibility. Identify at least three specific strengths and three specific weaknesses. Propose concrete improvements.

- **Option 2:** Write a 3-page essay on the following prompt: *"Computer science research in 2040 is increasingly conducted with AI assistance — from literature review through data analysis to drafting. What are the implications for research integrity, and what institutional and individual practices should the CS community adopt to ensure that AI-augmented research remains trustworthy?"*

- **Option 3:** Design and pilot a small-scale research study (e.g., a survey with n ≥ 20, a controlled experiment comparing two tools, or a qualitative interview study with n ≥ 5). Write a 3-page report including methodology, results, and a reflexive discussion of what you learned about the research process. Include your instruments and data (anonymised) as appendices.

### Exam Rubric
| Criterion | Weight | Excellent (A) | Good (B) | Adequate (C) | Insufficient (D/F) |
|-----------|--------|---------------|----------|--------------|---------------------|
| Research question clarity & significance | 15% | Specific, falsifiable, well-motivated | Clear but somewhat vague | Present but underdeveloped | Missing or trivial |
| Literature grounding | 15% | Systematic, identifies genuine gap | Adequate coverage, gap identified | Superficial, gap unclear | Missing or anecdotal |
| Methodological rigour | 25% | Appropriate design, justified choices, addresses validity | Appropriate but not fully justified | Questionable fit for question | Clearly inappropriate |
| Statistical/analytical plan | 15% | Correct, well-powered, assumptions checked | Mostly correct, minor issues | Errors or omissions | Fundamentally flawed |
| Communication quality | 15% | Clear, well-structured, persuasive | Readable but uneven | Difficult to follow | Incoherent |
| Ethics and integrity | 15% | Comprehensive, thoughtful treatment | Adequate coverage | Superficial | Missing or negligent |

---

*This course was woven by the faculty of the University of Yggdrasil, 2040. The runes of inquiry are carved not in stone but in the living practice of honest scholarship. May your research honour the truth-seeking tradition that stretches from the þulr at the thingstead to the scientist at the bench.*
