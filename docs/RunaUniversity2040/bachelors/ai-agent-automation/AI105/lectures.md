# AI105: Introduction to Machine Learning
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** AI101 (Introduction to Artificial Intelligence), AI102 (Programming for AI)
**Description:** The foundational course in machine learning — the computational art of learning from data. This course covers supervised, unsupervised, and reinforcement learning paradigms, with an emphasis on how each underpins AI agent behavior. Students will implement core algorithms, evaluate model performance, and understand the mathematical principles that make learning possible. By course end, you will be able to design, train, and critically evaluate ML models, and understand their role in the perceive-reason-act-learn cycle of autonomous agents.

---

## Lectures

### ᚠ Lecture 1: What Is Machine Learning? — The Well of Mímir

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Machine learning (ML) is the subfield of artificial intelligence concerned with algorithms that improve their performance through experience. More formally, as Tom Mitchell defined it in his seminal 1997 textbook: "A computer program is said to learn from experience E with respect to some class of tasks T and performance measure P, if its performance at tasks in T, as measured by P, improves with experience E." This definition has survived decades of transformation — from the statistical learning era of the 1990s through the deep learning revolution of the 2010s to the agentic AI era of the 2040s — because it captures something essential: learning is not about being told what to do, but about extracting patterns from data and generalizing to new situations.

The three major paradigms of machine learning define the relationship between data and supervision. In **supervised learning**, the algorithm receives labeled examples — input-output pairs — and learns to map inputs to outputs. This is how spam filters learn to classify emails, how facial recognition systems learn to identify individuals, and how AI agents learn to predict the outcomes of their actions. In **unsupervised learning**, the algorithm receives unlabeled data and must discover structure: clusters of similar items, low-dimensional representations, or generative models that capture the data distribution. This is how recommendation systems group users by taste, how anomaly detection systems find unusual events, and how agents discover patterns in unstructured environments. In **reinforcement learning**, the algorithm interacts with an environment, receiving rewards or penalties for its actions, and learns a policy that maximizes cumulative reward. This is how game-playing AIs learn strategy, how robots learn motor control, and how agents learn to navigate complex task spaces.

A fourth paradigm, **self-supervised learning**, has risen to prominence since the late 2010s and is arguably the engine behind modern large language models. In self-supervised learning, the algorithm generates its own labels from unlabeled data — for example, by masking words in a sentence and training a model to predict the masked words, or by predicting the next frame in a video sequence. This paradigm blurs the line between supervised and unsupervised: the data is unlabeled, but the learning signal is structured through clever pretext tasks. The transformer architectures that power GPT-5, Claude, and the agent systems you will build in this degree program were pre-trained using self-supervised objectives on text corpora measured in trillions of tokens.

The Norse god Mímir guards a well of wisdom at the root of Yggdrasil, from which Óðinn drank to gain knowledge of all things — at the cost of his eye. Machine learning is the modern well of Mímir. Data flows into it like water from the roots of the world tree, and the algorithm drinks deeply, extracting patterns that confer predictive power. But like Óðinn's sacrifice, machine learning demands a price: the quality of the learning depends on the quality of the data, the appropriateness of the model, and the care with which the problem is framed. Garbage in, garbage out is the prosaic version of this truth; the Norse version is that drinking from a poisoned well yields poisoned wisdom.

The historical trajectory of machine learning is instructive. The **perceptron** (Rosenblatt, 1958) was an early supervised learning algorithm that could learn linear decision boundaries. Its limitations — famously, the inability to learn the XOR function — led to the first "AI winter" of the 1970s. The **backpropagation algorithm** (Rumelhart, Hinton, and Williams, 1986) revived neural network research by providing an efficient way to train multi-layer networks. The **support vector machine** (Vapnik, 1995) and **ensemble methods** (random forests, gradient boosting) dominated the 2000s with their theoretical guarantees and practical performance. The **deep learning revolution** (Krizhevsky, Sutskever, and Hinton, 2012) demonstrated that deep neural networks trained on GPUs could achieve superhuman performance on image recognition, launching the era of large-scale neural models. By 2040, **agentic ML** — machine learning in service of autonomous agents that plan, use tools, and learn from interaction — has become the dominant frontier, integrating supervised, reinforcement, and self-supervised techniques into unified architectures.

**Key Topics:**

- **Mitchell's definition of learning:** Task T, performance measure P, experience E
- **Supervised learning:** Labeled data, classification vs. regression, inductive bias
- **Unsupervised learning:** Clustering, dimensionality reduction, density estimation
- **Reinforcement learning:** Agent, environment, reward, policy, value function
- **Self-supervised learning:** Pretext tasks, masked prediction, contrastive learning
- **Historical trajectory:** Perceptron → backprop → SVMs → deep learning → agentic ML

**Required Reading:**

- Mitchell, T. *Machine Learning* (2nd ed., 2035), Chapter 1
- Hastie, T., Tibshirani, R., & Friedman, J. *The Elements of Statistical Learning* (3rd ed., 2037), Chapter 2
- University of Yggdrasil Technical Report: "Agentic ML: A New Paradigm for Learning from Interaction" (2039)

**Discussion Questions:**

1. Mitchell's definition of learning has survived 40+ years. Is it still sufficient for describing what modern AI agents do? What, if anything, would you add?
2. Self-supervised learning blurs the line between supervised and unsupervised. What are the philosophical implications of a system that generates its own teaching signal?
3. Óðinn sacrificed his eye to drink from Mímir's well. What sacrifices do we make when we rely on machine learning for decisions — what do we lose in exchange for predictive power?

---

### ᚢ Lecture 2: Linear Regression — The First Algorithm

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Linear regression is the simplest machine learning algorithm, and it remains one of the most useful. It models the relationship between a scalar dependent variable *y* and one or more explanatory variables *x* as a linear function: *ŷ = w₀ + w₁x₁ + w₂x₂ + ... + wₚxₚ*, where the *w* coefficients are learned from data. Despite its simplicity, linear regression embodies the core concepts of supervised learning — hypothesis space, loss function, optimization, and generalization — in a form transparent enough to see all the moving parts.

The **hypothesis space** of linear regression is the set of all linear functions mapping the input variables to the output. This is a highly constrained hypothesis space; the model can only learn relationships that are linear in the coefficients. This constraint — a strong **inductive bias** — means that linear regression is unlikely to overfit on small datasets but may underfit when the true relationship is nonlinear. In AI agent systems, linear regression is used for tasks where interpretability is paramount: predicting a user's response latency from conversation features, estimating the compute cost of an action from its parameters, or projecting a sensor reading from environmental conditions.

The **loss function** measures how badly the model's predictions deviate from the true values. For linear regression, the standard loss is **mean squared error (MSE)**: *L(w) = (1/n) Σᵢ (yᵢ - ŷᵢ)²*, where the sum runs over all training examples. MSE penalizes large errors quadratically, which means it is sensitive to outliers — a single extreme prediction can dominate the loss. The choice of loss function encodes assumptions about what kind of error matters: squared error assumes that errors are symmetric and that larger errors are disproportionately worse. Alternatives include **mean absolute error (MAE)**, which penalizes errors linearly and is more robust to outliers, and **Huber loss**, which interpolates between MAE and MSE.

The **optimization** problem is to find the coefficients *w* that minimize the loss over the training data. For linear regression with MSE loss, a closed-form solution exists: the **normal equations**. In matrix form, *w = (XᵀX)⁻¹Xᵀy*, where *X* is the design matrix of input features and *y* is the vector of target values. This solution is elegant, exact, and O(p³) in the number of features — fine for moderate p, but impractical for high-dimensional data. For large problems, **gradient descent** iteratively improves the coefficients by taking small steps in the direction of steepest descent of the loss: *w := w - η ∇L(w)*, where *η* is the learning rate. Gradient descent converges to the global minimum for convex loss functions like MSE, guarantees that linear regression always finds the optimal coefficients (given appropriate convergence criteria).

The **learning rate η** is the first hyperparameter students encounter, and it illustrates a fundamental ML tension: too small, and convergence is slow; too large, and the algorithm may overshoot or diverge. In practice, learning rate schedules (decreasing η over time) or adaptive methods (AdaGrad, Adam) are used to navigate this tradeoff.

**Polynomial regression** extends linear regression by introducing nonlinear transformations of the input features while keeping the model linear in the coefficients. For example, a quadratic model *ŷ = w₀ + w₁x + w₂x²* is linear in *w* but captures a parabolic relationship between *x* and *y*. A polynomial of high enough degree can fit any continuous function (by the Weierstrass approximation theorem), but with too many degrees, the model will overfit — fitting noise rather than signal. This is the **bias-variance tradeoff** in its most accessible form: a degree-1 model (line) has high bias but low variance; a degree-20 model has low bias but high variance. Finding the right degree — the right model complexity — is the central challenge of machine learning.

The Norse concept of **mjötviðr** — the measuring tree, an alternate name for Yggdrasil — resonates with the normal equations. The world tree measures and balances the forces of the cosmos; the normal equations compute the coefficients that optimally balance the explanatory contributions of each feature. But the measuring tree is not infallible — it measures what is, not what could be. A linear model, like the measuring tree, reports what the data says with a straight edge; it cannot see curves that the data only hints at.

**Key Topics:**

- **Linear regression:** Hypothesis, loss function (MSE), closed-form solution (normal equations)
- **Gradient descent:** Iterative optimization, learning rate, convergence
- **Polynomial regression:** Feature transformation, the Weierstrass theorem, overfitting
- **Bias-variance tradeoff:** High bias (underfit) vs. high variance (overfit), model complexity
- **Loss function alternatives:** MAE, Huber, and when to use each
- **Applications in agents:** Interpretable prediction of latency, cost, and sensor readings

**Required Reading:**

- Hastie et al., *The Elements of Statistical Learning* (3rd ed., 2037), Chapter 3
- Bishop, C. *Pattern Recognition and Machine Learning* (2nd ed., 2034), Chapter 3.1

**Discussion Questions:**

1. The normal equations provide an exact solution but require O(p³) computation. For an AI agent that must update its model in real time as new data arrives, is a closed-form solution practical? What alternatives exist?
2. Polynomial regression can fit any continuous function, but high-degree polynomials oscillate wildly between data points (Runge's phenomenon). How does this phenomenon relate to the general problem of overfitting in ML?
3. An agent uses linear regression to predict the cost of an API call. The true cost function is nonlinear (economies of scale). What happens when the agent optimizes its behavior using a linear approximation of a nonlinear function?

---

### ᚦ Lecture 3: Logistic Regression and Classification

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Where linear regression predicts a continuous value, **classification** predicts a discrete category: spam or not spam, safe or dangerous, relevant or irrelevant. **Logistic regression** is the bridge between linear models and classification — it applies a linear function to the input features and then passes the result through a **sigmoid function** that squashes the output into the range (0, 1), which can be interpreted as a probability.

The logistic regression model for binary classification is: *P(y=1 | x) = σ(wᵀx) = 1 / (1 + e^{-wᵀx})*, where σ is the sigmoid (logistic) function. The decision boundary — the line (or hyperplane) where *P(y=1 | x) = 0.5* — occurs where *wᵀx = 0*. Points far on the positive side of the decision boundary have probabilities near 1; points far on the negative side have probabilities near 0. The slope of the sigmoid determines how sharply the probability transitions from 0 to 1 around the decision boundary — a property controlled by the magnitude of *w*.

The loss function for logistic regression is **cross-entropy loss** (also called log loss): *L(w) = -(1/n) Σᵢ [yᵢ log(ŷᵢ) + (1-yᵢ) log(1-ŷᵢ)]*. Unlike MSE, cross-entropy loss is specifically designed for probability outputs. Intuitively, it heavily penalizes confident wrong predictions: predicting *ŷ = 0.99* when the true label is *y = 0* incurs a loss of *-log(0.01) ≈ 4.6*, whereas predicting *ŷ = 0.51* incurs a loss of only *-log(0.49) ≈ 0.71*. This asymmetry — punishing overconfidence more severely than mild error — is a crucial property when the model's probabilities are used for decision-making. An AI agent that confidently predicts "safe" when the action is dangerous makes a worse error than one that hedges with "probably safe."

Unlike linear regression, logistic regression has no closed-form solution. It is optimized using **gradient descent** (or more sophisticated methods like Newton-Raphson or L-BFGS), with the gradient of the cross-entropy loss taking a surprisingly simple form: *∇L(w) = (1/n) Xᵀ(ŷ - y)* — identical in structure to the gradient of linear regression, despite the different loss function. This is a beautiful mathematical fact that connects linear and logistic regression: they differ in the shape of their hypothesis (linear vs. sigmoid-wrapped) and their loss function (MSE vs. cross-entropy), but their gradients point in the same general direction.

**Multi-class classification** extends logistic regression via the **softmax function**. For *K* classes, the model computes *K* linear scores *zₖ = wₖᵀx* and then applies softmax: *P(y=k | x) = e^{zₖ} / Σⱼ e^{zⱼ}*. The softmax generalizes the sigmoid: for *K=2*, softmax reduces to the sigmoid. The multi-class cross-entropy loss is *L = -(1/n) Σᵢ Σₖ yᵢₖ log(ŷᵢₖ)*, where *yᵢₖ* is 1 if example *i* belongs to class *k* and 0 otherwise. In AI agent systems, softmax classifiers are ubiquitous: they classify user intents ("book a flight" vs. "cancel a reservation"), categorize errors, and select which tool to invoke next.

**Decision boundaries** are a geometric lens on classification. For logistic regression, the decision boundary is always a linear hyperplane because the model computes a linear combination of features. If the true class structure is not linearly separable — as with XOR — logistic regression will fail to achieve perfect accuracy. This limitation motivates **kernel methods** (Lecture 5) and **neural networks** (Lectures 6–7), which can learn nonlinear decision boundaries.

**Calibration** is an often-overlooked property of probabilistic classifiers. A classifier is **calibrated** if, among examples for which it predicts probability *p*, the true fraction of positive examples is approximately *p*. Logistic regression tends to produce well-calibrated probabilities because cross-entropy loss explicitly optimizes probability estimates. However, more complex models (neural networks, boosted trees) often produce probabilities that are overconfident or underconfident. For AI agents that use probabilities to decide whether to act or to escalate to a human, calibration is a safety-critical property: an uncalibrated agent that is overconfident in its predictions may execute dangerous actions without hedging.

The Norse concept of **sannindi** — truth, but specifically the kind of truth that emerges from examination and testing — parallels the classification evaluation. A classification model's probabilities are not sannindi until they have been tested against reality. The decision boundary is the line between truth and falsehood, but truth is not binary in practice: the sigmoid's smooth transition from 0 to 1 captures the uncertainty that sannindi acknowledges — that most knowledge is a matter of degree, not certainty.

**Key Topics:**

- **Logistic regression:** Sigmoid function, decision boundary, probability interpretation
- **Cross-entropy loss:** Derivation from maximum likelihood, asymmetry of penalties
- **Multi-class extension:** Softmax, one-vs-rest, and multi-class cross-entropy
- **Gradient descent for logistic regression:** The elegant gradient formula ∇L = Xᵀ(ŷ - y)
- **Decision boundaries and linear separability:** XOR as the classic counterexample
- **Calibration:** Why well-calibrated probabilities matter for agent decision-making

**Required Reading:**

- Hastie et al., *The Elements of Statistical Learning* (3rd ed., 2037), Chapter 4.4
- Bishop, C. *Pattern Recognition and Machine Learning* (2nd ed., 2034), Chapters 4.2–4.3
- Guo, C. et al. "On Calibration of Modern Neural Networks" (2017), *ICML* (still relevant in 2040)

**Discussion Questions:**

1. Logistic regression produces well-calibrated probabilities, but deep neural networks often do not. Why does this happen? What techniques can recalibrate an overconfident model?
2. The XOR problem is linearly inseparable. What does this tell us about the limitations of models that can only learn linear decision boundaries? How does this limitation manifest in real-world AI problems?
3. An agent uses logistic regression to decide whether to execute a tool call autonomously or ask for human confirmation. The model is well-calibrated at p=0.95. What threshold should the agent use? What factors beyond accuracy should influence this decision?

---

### ᚬ Lecture 4: Decision Trees and Random Forests — The Counsel of Many

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A decision tree is a tree-structured model that makes predictions by recursively splitting the data based on feature values. At each internal node, a test is performed (e.g., "is *x₃ > 0.7*?"), and the data flows down the left or right branch accordingly. At each leaf node, a prediction is made (the majority class for classification, the mean value for regression). Decision trees are popular because they are interpretable — you can trace the path of any prediction from root to leaf and understand exactly why the model made that decision. For AI agents in safety-critical domains, this transparency is invaluable.

The **CART (Classification and Regression Trees)** algorithm, developed by Breiman, Friedman, Olshen, and Stone (1984), is the standard approach for building decision trees. At each node, CART considers all possible splits on all features and selects the split that maximizes some measure of **impurity reduction**. For classification, the most common impurity measure is **Gini impurity**: *G = Σₖ pₖ(1 - pₖ)*, where *pₖ* is the proportion of examples in class *k* at that node. A node containing examples of only one class has Gini impurity 0 (perfect purity); a node with equal proportions of *K* classes has Gini impurity *1 - 1/K* (maximum impurity). For regression, the impurity measure is MSE — the same loss function as linear regression. CART is a **greedy algorithm**: at each node, it makes the locally optimal split without considering how that choice might affect splits deeper in the tree. Like many greedy algorithms, it is fast but not guaranteed to produce the globally optimal tree.

A single decision tree is prone to **overfitting** — growing until every leaf contains exactly one training example, achieving zero training error but memorizing noise. The main defense is **pruning**: limiting the tree's depth, requiring a minimum number of examples per leaf, or using **cost-complexity pruning** (adding a penalty term for the number of leaves). The hyperparameters that control tree complexity — max depth, min samples per leaf, min impurity decrease for a split — are the first hyperparameters that students tune. Getting them right is a microcosm of the general ML challenge of controlling model capacity.

**Random forests** (Breiman, 2001) extend decision trees through the principle of **ensemble learning**: combining multiple models to produce a better predictor than any single model. A random forest builds many decision trees (typically hundreds) and averages their predictions (for regression) or takes a majority vote (for classification). Two independent sources of randomness make the trees diverse. First, each tree is trained on a **bootstrap sample** of the data — a random sample with replacement of the same size as the original dataset. Second, at each split, only a random subset of features is considered (typically √p for classification, p/3 for regression). This "random subspace" method ensures that the trees are not all using the same strongest features at every split, forcing them to discover different patterns.

The magic of random forests comes from the **wisdom of crowds** effect: the errors of individual trees tend to cancel out, while the truths they capture tend to reinforce. Formally, if each tree has variance σ² and the correlations between trees have average ρ, the variance of the ensemble is *ρσ² + (1-ρ)σ²/B*, where *B* is the number of trees. As *B → ∞*, the variance approaches *ρσ²*, so the key to a good random forest is to make the trees as uncorrelated as possible (reduce ρ) while keeping their individual accuracy high. Random forests also provide a natural **feature importance** measure: the total decrease in impurity caused by splits on a given feature, averaged across all trees. This is a powerful tool for understanding which features drive predictions — essential for AI agents that must explain their reasoning.

**Gradient boosting** (Friedman, 2001) is an alternative ensemble approach that builds trees sequentially, with each new tree trained to correct the errors of the previous ensemble. Unlike random forests, which train trees independently, gradient boosting is inherently sequential and typically produces higher accuracy at the cost of longer training time and more complex hyperparameter tuning (learning rate, number of trees, tree depth). XGBoost (Chen & Guestrin, 2016) and LightGBM (Ke et al., 2017) are the dominant implementations of gradient boosting, and they remain competitive with deep learning on tabular data. In the 2040s, XGBoost v5 now runs on quantum accelerators, but its core algorithms — trees grown greedily with gradient-based splitting — remain fundamentally the same.

The Norse concept of **þing** — the assembly where free people gather to discuss and decide — parallels the random forest. At the þing, no single voice determines the outcome; the collective wisdom of the assembly, formed from many independent judgments, produces a decision that is wiser than any individual could produce alone. The random forest is a computational þing: each tree is a voice, each vote a contribution to the collective decision, and the ensemble's wisdom emerges from the diversity of its members.

**Key Topics:**

- **Decision trees:** Recursive splitting, CART, Gini impurity, information gain
- **Overfitting in trees:** Pruning, max depth, min samples per leaf, cost-complexity
- **Random forests:** Bootstrap aggregating (bagging), random subspaces, variance reduction
- **Feature importance:** Impurity-based and permutation-based measures
- **Gradient boosting:** Sequential ensemble, XGBoost, LightGBM
- **Interpretability:** Why trees are transparent and why that matters for agents

**Required Reading:**

- Breiman, L. "Random Forests" (2001), *Machine Learning*
- Hastie et al., *The Elements of Statistical Learning* (3rd ed., 2037), Chapters 9.2, 15
- Chen, T. & Guestrin, C. "XGBoost: A Scalable Tree Boosting System" (2016/2040 reprint)

**Discussion Questions:**

1. A single decision tree is fully interpretable, but a random forest with 500 trees is not. What is the tradeoff between accuracy and interpretability, and when should an AI agent favor each?
2. Random forests reduce variance by averaging uncorrelated trees. What happens if the trees are all nearly identical (high correlation)? How can you detect this problem during training?
3. The þing produces collective wisdom from independent judgments. In what sense does an ensemble method produce "wisdom" that a single model cannot? What are the conditions for this wisdom to emerge?

---

### ᚱ Lecture 5: Support Vector Machines and Kernel Methods

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Support vector machines (SVMs) take a fundamentally different approach to classification than the probabilistic methods we have studied. Instead of modeling the probability of each class, an SVM seeks the **maximum-margin hyperplane**: the decision boundary that maximizes the distance to the nearest training examples from each class. These nearest examples — the **support vectors** — are the only data points that determine the decision boundary; all others are irrelevant. This geometric formulation gives SVMs a rigorous mathematical foundation and strong theoretical guarantees about generalization.

The **hard-margin SVM** (for linearly separable data) solves the optimization problem: minimize *||w||²/2* subject to *yᵢ(wᵀxᵢ + b) ≥ 1* for all training examples *i*. The constraint ensures that all examples are correctly classified with a margin of at least 1. The objective minimizes the norm of the weight vector, which geometrically maximizes the margin width (the margin width is *2/||w||*). Solving this convex optimization problem yields a unique global optimum — SVMs have no local minima, unlike neural networks. The dual formulation of the SVM optimization problem reveals that the optimal weight vector is a linear combination of the support vectors: *w = Σᵢ αᵢ yᵢ xᵢ*, where *αᵢ > 0* only for support vectors. This sparsity — only a subset of training examples matter — is computationally advantageous for prediction.

For data that is not linearly separable (which includes most real-world data), the **soft-margin SVM** introduces slack variables *ξᵢ* that allow some examples to be misclassified or fall within the margin, with a penalty parameter *C* that controls the tradeoff between maximizing the margin and minimizing misclassification. A large *C* heavily penalizes misclassification, producing a narrow margin that hugs the training data (low bias, high variance). A small *C* tolerates misclassification, producing a wide margin at the cost of some training errors (high bias, low variance). Tuning *C* is the primary way to control SVM complexity.

The true power of SVMs comes from the **kernel trick**, which enables them to learn nonlinear decision boundaries without explicitly computing nonlinear feature transformations. The idea is elegant: many algorithms (including SVMs) depend on the data only through inner products *⟨xᵢ, xⱼ⟩*. If we replace this inner product with a **kernel function** *K(xᵢ, xⱼ) = ⟨φ(xᵢ), φ(xⱼ)⟩*, where φ is an implicit (possibly infinite-dimensional) feature mapping, the algorithm operates in the transformed feature space without ever computing φ(x) directly. Common kernels include:

- **Linear:** *K(x, z) = xᵀz* (identical to the original feature space)
- **Polynomial:** *K(x, z) = (xᵀz + c)ᵈ* (captures polynomial relationships of degree *d*)
- **RBF (Gaussian):** *K(x, z) = exp(-γ||x - z||²)* (captures local similarity; γ controls the influence radius)
- **Sigmoid:** *K(x, z) = tanh(κ xᵀz + c)* (inspired by neural networks)

The **RBF kernel** is particularly important because its implicit feature space is infinite-dimensional — it can represent any smooth decision boundary — yet it is controlled by a single parameter *γ*. A large *γ* means that each support vector's influence is highly local, producing a complex, wiggly decision boundary (low bias, high variance). A small *γ* means that each support vector's influence spreads widely, producing a smooth, simple boundary (high bias, low variance). Together, *C* and *γ* form the two main knobs for tuning an SVM.

The **kernel trick is not limited to SVMs**. Any algorithm that depends on data only through inner products — linear regression (via ridge regression), PCA, clustering — can be kernelized to operate in an implicit high-dimensional feature space. This principle, known as the **kernel method**, was one of the major conceptual advances of 1990s/2000s machine learning and remains a foundational tool in the 2040s, particularly in specialized domains where data is structured (graphs, strings, trees) and custom kernels can encode domain-specific notions of similarity.

For AI agents, SVMs are useful when the decision boundary must be maximally robust to perturbations — when you need not just any separating hyperplane, but the one that is maximally distant from the closest examples of each class. This is relevant for **safety-critical classification** (is this action safe or dangerous?) and **one-class classification** (is this behavior within the normal operating envelope?), where maximizing the margin provides a principled notion of robustness.

The Norse concept of **megin** — strength, might, but specifically the kind of strength that comes from standing at the right place — resonates with the SVM's philosophy. The maximum-margin hyperplane is the megin-boundary: the place where the classifier's power is greatest, because the distance to the nearest examples ensures that small perturbations will not cause misclassification. The support vectors are the pillars that hold up the boundary, just as the pillars of a Norse hall hold up the roof — remove a non-support vector and nothing changes; remove a support vector and the structure shifts.

**Key Topics:**

- **Hard-margin SVM:** Maximum margin, convex optimization, dual formulation
- **Support vectors:** Sparsity, geometric interpretation, the examples that matter
- **Soft-margin SVM:** Slack variables, penalty parameter C, bias-variance tradeoff
- **The kernel trick:** Implicit feature mapping, Mercer's theorem, computational efficiency
- **Common kernels:** Linear, polynomial, RBF, sigmoid; the γ hyperparameter
- **Kernelized algorithms:** Ridge regression, PCA, clustering — any dot-product algorithm

**Required Reading:**

- Vapnik, V. *The Nature of Statistical Learning Theory* (2nd ed., 2038 reprint), Chapters 5–6
- Bishop, C. *Pattern Recognition and Machine Learning* (2nd ed., 2034), Chapter 7
- Schölkopf, B. & Smola, A. *Learning with Kernels* (3rd ed., 2040), Chapters 1–2

**Discussion Questions:**

1. The kernel trick computes inner products in an implicit feature space without explicitly constructing the features. What are the computational limits of this approach? For what kernel and dataset size does the kernel trick become impractical?
2. SVMs maximize the margin, which provides a notion of robustness. How does this geometric notion of robustness compare to probabilistic notions (like calibration in logistic regression)? Which is more appropriate for AI safety?
3. An AI agent must detect whether its own behavior is anomalous (outside normal operating parameters). How would you use a one-class SVM (which learns a boundary around "normal" data only) for this task? What are the limitations?

---

### ᚷ Lecture 6: Neural Networks — The Architecture of Thought

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Neural networks are the computational models that have most transformed AI in the 21st century. They are composed of layers of interconnected processing units — "neurons" in a loose biological metaphor — that transform input data through a cascade of linear transformations and nonlinear activation functions. A neural network with enough capacity can approximate any continuous function (the **universal approximation theorem**, proved independently by Cybenko, Hornik, and others in 1989), making them the most flexible model class available.

The basic unit is the **artificial neuron**, which computes a weighted sum of its inputs plus a bias, then applies a nonlinear **activation function**: *a = f(wᵀx + b)*. Without the activation function, a multi-layer network would collapse into a single linear transformation — no amount of stacking linear layers can produce a nonlinear function. The activation function is what gives neural networks their expressive power. Common activation functions include:

- **Sigmoid:** *σ(z) = 1/(1+e^{-z})* — smooth, bounded (0,1), but saturates at extremes (vanishing gradient)
- **Tanh:** *tanh(z) = (eᶻ - e^{-ᶻ})/(eᶻ + e^{-ᶻ})* — zero-centered, bounded (-1,1), also saturates
- **ReLU (Rectified Linear Unit):** *ReLU(z) = max(0, z)* — avoids saturation, computationally cheap, but "dies" for negative inputs (zero gradient forever)
- **Leaky ReLU:** *f(z) = max(αz, z)* with α ≈ 0.01 — prevents dead neurons by allowing a small gradient for negative inputs
- **GELU (Gaussian Error Linear Unit):** *f(z) = z · Φ(z)* — used in transformers, smooth approximation of ReLU with probabilistic interpretation
- **Swish:** *f(z) = z · σ(βz)* — discovered by neural architecture search, often outperforms ReLU in deep networks

**Forward propagation** computes the network's predictions: input flows through successive layers, each computing *z⁽ˡ⁾ = W⁽ˡ⁾ a⁽ˡ⁻¹⁾ + b⁽ˡ⁾* and *a⁽ˡ⁾ = f(z⁽ˡ⁾)*, until the output layer produces the final prediction. **Backpropagation** computes the gradient of the loss with respect to every weight in the network, using the chain rule of calculus. The key insight of backpropagation is that the gradient for layer *l* can be computed from the gradient for layer *l+1*, enabling efficient computation from output to input in a single backward pass. The computational graph of the network is traversed in reverse, local gradients are multiplied along each path, and the accumulated product gives the gradient with respect to each weight.

**Training** a neural network is an optimization problem: find the weights that minimize the loss on the training data. **Stochastic gradient descent (SGD)** and its variants — **SGD with momentum**, **Adam** (adaptive moment estimation), **RMSprop**, **AdamW** — are the workhorses of neural network training. SGD updates weights using gradients computed on small random batches of data (mini-batches), which introduces noise that helps escape local minima and provides computational efficiency. Adam (Kingma & Ba, 2015) combines momentum (using a moving average of past gradients for stability) with adaptive learning rates (scaling updates inversely with the root-mean-square of past gradients), and has become the default optimizer for most neural network tasks.

The **universal approximation theorem** states that a feedforward neural network with a single hidden layer and a sufficiently large number of neurons can approximate any continuous function on a compact domain to arbitrary accuracy. However, the theorem is an existence result — it doesn't tell you how many neurons are needed, or how to find the weights. In practice, deep networks (many layers) are more parameter-efficient than wide networks (few layers with many neurons) for many functions, because each layer can learn increasingly abstract features. This is the **depth efficiency hypothesis**: some functions require exponentially fewer neurons when represented as a deep network than as a shallow network.

For AI agents, neural networks are the computational engine behind perception, reasoning, and action selection. An agent's visual system is a convolutional neural network (CNN). Its language understanding is a transformer. Its decision-making may use a policy network trained with reinforcement learning. The network architectures we will study in depth in AI201 (Deep Learning Foundations) build on the principles introduced here: forward propagation, backpropagation, gradient descent, and the representation learning that depth enables.

The Norse concept of **Huginn and Muninn** — Óðinn's ravens, Thought and Memory — provides a metaphor for the two passes of neural network training. Huginn (Thought) flies forward through the network, computing predictions from input to output — the forward pass. Muninn (Memory) flies backward, carrying gradients from output to input and updating the weights — the backward pass. Together, they circle the world each day, observing and remembering, and return to Óðinn each evening with the knowledge they have gathered. A well-trained network, like a well-fed pair of ravens, has seen the world broadly and learned its patterns deeply.

**Key Topics:**

- **The artificial neuron:** Weighted sum, bias, activation function, nonlinearity
- **Activation functions:** Sigmoid, tanh, ReLU, leaky ReLU, GELU, Swish
- **Forward and backward propagation:** The computational graph traversed in both directions
- **Training algorithms:** SGD, momentum, Adam, AdamW, batch size, learning rate schedules
- **The universal approximation theorem:** Existence vs. practical learnability
- **Depth efficiency:** Why deep networks are more parameter-efficient than wide shallow ones

**Required Reading:**

- Goodfellow, I., Bengio, Y., & Courville, A. *Deep Learning* (3rd ed., 2038), Chapters 6–8
- Kingma, D. & Ba, J. "Adam: A Method for Stochastic Optimization" (2015), *ICLR*
- University of Yggdrasil Technical Report: "Neural Architectures for Agent Perception" (2039)

**Discussion Questions:**

1. The universal approximation theorem guarantees existence but not learnability. What makes a function hard to learn in practice, even though a network exists that can represent it?
2. ReLU neurons can "die" (permanently output zero) if the learning rate is too high or the initialization is poor. How does this affect the effective capacity of the network? Can dead neurons be revived?
3. Huginn and Muninn circle the world and return with knowledge. In what sense does the forward-backward pass of neural network training mirror this? What "knowledge" is gathered during training?

---

### ᚺ Lecture 7: Training Deep Networks — Optimization, Regularization, and Initialization

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Training a deep neural network is not a simple matter of running gradient descent. Deep networks introduce challenges that shallow networks avoid: **vanishing gradients**, where gradients shrink exponentially as they propagate backward through many layers, making early layers learn extremely slowly; **exploding gradients**, where gradients grow exponentially and destabilize training; and **dead activations**, where large portions of the network become permanently inactive. Successfully training a deep network requires careful attention to initialization, normalization, regularization, and optimization.

**Weight initialization** determines the starting point of optimization. A poor initialization — all weights set to zero, or too-large random values — can doom training before it begins. Xavier/Glorot initialization (Glorot & Bengio, 2010) sets weights to *W ~ Uniform(-√(6/(nᵢₙ + nₒᵤₜ)), √(6/(nᵢₙ + nₒᵤₜ)))*, designed to keep the variance of activations and gradients constant across layers. He initialization (He et al., 2015) adjusts this formula for ReLU activations, which zero out half the units: *W ~ N(0, √(2/nᵢₙ))*. These carefully calibrated initialization schemes are essential for training networks deeper than a few layers.

**Batch normalization** (Ioffe & Szegedy, 2015) normalizes the activations of each layer to have zero mean and unit variance across the mini-batch, then applies a learned scale and shift. This stabilizes training by preventing the distribution of activations from shifting as earlier layers update (the "internal covariate shift" problem), enabling much higher learning rates and reducing the sensitivity to initialization. By 2040, batch normalization has been partially superseded by **layer normalization** (Ba et al., 2016) — particularly in transformers, where it is standard — and **group normalization** (Wu & He, 2018), which perform normalization along different dimensions and are less sensitive to batch size. However, the core insight — that normalizing intermediate representations stabilizes deep network training — remains one of the most important practical advances in ML.

**Regularization** prevents overfitting by penalizing model complexity. **L1 regularization (Lasso)** adds *λ Σ|wᵢ|* to the loss, encouraging sparse weight vectors with many zeros — useful for feature selection. **L2 regularization (Ridge)** adds *λ Σ wᵢ²* to the loss, encouraging small weights distributed across all features — the standard choice for neural networks. **Dropout** (Srivastava et al., 2014) randomly drops out a fraction of neurons during training, forcing the network to learn redundant representations that don't depend on any single neuron. At test time, all neurons are active but their outputs are scaled down to compensate. Dropout can be interpreted as training an ensemble of exponentially many subnetworks that share weights, and it remains one of the most effective regularization techniques. **Early stopping** interrupts training when validation performance stops improving — the simplest regularization method, but surprisingly effective. **Data augmentation** expands the training set by applying label-preserving transformations (rotations, crops, color shifts for images; synonym replacement, back-translation for text), which is particularly important in the 2040s where synthetic data generation can produce essentially unlimited augmentations.

**Vanishing and exploding gradients** are the most notorious challenges in training deep networks. For a deep linear network (a simplified model), the gradient for layer *l* involves the product of the weight matrices of all subsequent layers: if these matrices have eigenvalues less than 1, the gradient shrinks exponentially (vanishing); if they have eigenvalues greater than 1, the gradient explodes. In nonlinear networks, the problem is exacerbated by activation functions: sigmoid and tanh saturate, producing near-zero gradients for large inputs. ReLU avoids saturation for positive inputs, which is a key reason for its success. **Gradient clipping** — capping gradient norms at a maximum value — is a simple but effective defense against exploding gradients. **Residual connections** (He et al., 2016) provide shortcut paths that allow gradients to flow directly from later layers to earlier layers, effectively solving the vanishing gradient problem for networks of hundreds or even thousands of layers (as in ResNet-1001 or the 2040 Transformer-XL-2048).

The Norse concept of **seiðr** — the shamanic practice of journeying into hidden realms to recover knowledge — provides a metaphor for backpropagation through deep networks. The shaman (the gradient) must travel backward through many layers (the realms), and at each layer, the gradient may weaken (vanish) or become distorted (explode). The skill of the seiðr practitioner lies in maintaining a clear signal through the journey — just as the skill of the ML engineer lies in choosing architectures and normalization schemes that allow gradients to propagate cleanly. Residual connections are the seiðr bridges: direct pathways that bypass the difficulties of intermediate layers and carry the learning signal directly to where it is needed.

**Key Topics:**

- **Weight initialization:** Xavier/Glorot, He, and why zero initialization fails
- **Batch/layer/group normalization:** Stabilizing training by normalizing activations
- **Regularization:** L1/L2, dropout, early stopping, data augmentation
- **Vanishing/exploding gradients:** Causes, detection, gradient clipping, residual connections
- **Optimization landscape:** Local minima (rare in high dimensions), saddle points (common), and why SGD works
- **Practical training recipe:** The sequence of decisions that lead to a working network

**Required Reading:**

- Goodfellow et al., *Deep Learning* (3rd ed., 2038), Chapters 7–8, 11
- Ioffe, S. & Szegedy, C. "Batch Normalization" (2015), *ICML*
- He, K. et al. "Deep Residual Learning for Image Recognition" (2016), *CVPR*

**Discussion Questions:**

1. Residual connections allow gradients to flow through hundreds of layers. What does this architectural choice imply about the nature of deep representations? Are very deep networks learning something fundamentally different from shallow ones?
2. Dropout trains an ensemble of subnetworks. How does this ensemble interpretation differ from the actual ensemble of a random forest? Which is more computationally efficient?
3. In seiðr, the shaman journeys backward through realms to recover knowledge. What happens to the "knowledge" (the gradient) if the bridge between realms is weak? How do residual connections and normalization build stronger bridges?

---

### ᚾ Lecture 8: Model Evaluation — Measuring What We Have Learned

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Building a model is only half the battle; the other half is evaluating it properly. A model that appears to perform well on its training data may have learned nothing but memorized noise, and a model that performs well on a held-out test set may still fail catastrophically when deployed in the real world. Rigorous evaluation is what separates machine learning from wishful thinking — and for AI agents whose decisions have real-world consequences, evaluation is a safety imperative.

**Train-test split** is the most basic evaluation procedure: hold out a random subset of the data (typically 20–30%) for testing, train the model on the remainder, and report performance on the test set. This provides an unbiased estimate of generalization performance — provided the test set is never used for model selection or hyperparameter tuning. The moment you peek at the test set to guide your modeling decisions, it ceases to be a test set and becomes part of the training process, biasing your performance estimates upward. In AI agent research, test-set contamination — where the model has seen test examples during pre-training — is a persistent and pernicious problem that inflates reported performance and masks genuine limitations.

**Cross-validation** extends the train-test split by partitioning the data into *k* folds, training on *k-1* folds and testing on the held-out fold, repeating for each fold, and averaging the results. K-fold cross-validation provides a more robust estimate of performance than a single split, especially for small datasets, at the cost of training *k* models. **Stratified k-fold** ensures that each fold preserves the class proportions of the full dataset, which is essential for imbalanced classification problems. **Leave-one-out cross-validation (LOOCV)** is k-fold with *k=n* (one test example per iteration), providing an almost unbiased estimate but at prohibitive computational cost for large datasets.

The choice of **performance metric** depends on the task and the cost of different types of errors. For classification:
- **Accuracy:** Fraction of correct predictions. Simple but misleading for imbalanced datasets (a classifier that always predicts "not fraud" will have 99.9% accuracy on a dataset where 0.1% of transactions are fraudulent).
- **Precision, Recall, F1-score:** For binary classification, precision = TP/(TP+FP) (what fraction of positive predictions are correct?), recall = TP/(TP+FN) (what fraction of actual positives are captured?). The F1-score is the harmonic mean of precision and recall. These metrics are essential when positive and negative errors have different costs.
- **ROC-AUC (Receiver Operating Characteristic — Area Under Curve):** Measures the model's ability to rank positive examples above negative examples across all possible thresholds. AUC ranges from 0.5 (random) to 1.0 (perfect ranking). It is threshold-independent, which is useful for understanding the model's inherent discriminative power.
- **Log loss (cross-entropy):** Measures the quality of probability estimates, heavily penalizing confident errors. This is the metric to use when the model's probability outputs are used for downstream decision-making.

For regression:
- **MSE, MAE, RMSE:** Standard error metrics with different sensitivities to outliers.
- **R² (coefficient of determination):** The proportion of variance in the target explained by the model. Ranges from -∞ to 1, with 1 being perfect prediction and 0 meaning the model is no better than predicting the mean.

**Confusion matrices** break down the model's predictions by true class and predicted class. From the confusion matrix, all classification metrics can be derived. More importantly, the confusion matrix reveals the *kind* of mistakes the model makes — which classes are confused with which — enabling targeted improvements.

For AI agents, evaluation is particularly challenging because agent performance is inherently multi-dimensional. An agent's accuracy on a single task is only one metric; we also care about its latency (how fast), its cost (compute resources), its robustness (does it work in edge cases?), its safety (did it refuse dangerous requests?), and its alignment (did it act in accordance with human values?). Agent evaluation frameworks in 2040 — AgentBench, MCP-Eval, the Yggdrasil Agent Arena — assess agents across dozens of dimensions using standardized task suites and adversarial probes.

The Norse concept of **orð** — a word, but more fundamentally a binding promise that must be tested — relates to model evaluation. A model makes an implicit promise: "trained on this data, I will perform at this level on similar data." The test set is the trial that determines whether the model has kept its orð. A model that overfits has broken its promise — it performs well on the data it trained on but fails on new data. A model that passes a rigorous test set has proven its orð. But the ultimate test is deployment, where the model encounters data it has never seen and must perform in conditions it was not trained for. This is the **generalization gap**: the difference between test performance and deployment performance, which rigorous evaluation aims to minimize but can never eliminate.

**Key Topics:**

- **Train-test split and cross-validation:** Unbiased performance estimation
- **Classification metrics:** Accuracy, precision, recall, F1, ROC-AUC, log loss
- **Regression metrics:** MSE, MAE, RMSE, R²
- **Confusion matrices:** Understanding error patterns, not just error rates
- **Multi-dimensional agent evaluation:** Accuracy, latency, cost, robustness, safety, alignment
- **The generalization gap:** Why test performance ≠ deployment performance

**Required Reading:**

- Hastie et al., *The Elements of Statistical Learning* (3rd ed., 2037), Chapter 7
- Raschka, S. *Model Evaluation, Model Selection, and Algorithm Selection in Machine Learning* (2036), Chapters 1–4
- University of Yggdrasil Agent Arena: "Standardized Evaluation Framework for AI Agents" (2040)

**Discussion Questions:**

1. A model achieves 99.9% accuracy on a fraud detection task. Why might this be terrible performance? What metric would reveal the problem?
2. K-fold cross-validation provides a more robust estimate than a single train-test split, but it trains k models. For a large neural network that takes days to train, is cross-validation practical? What alternatives exist?
3. Agent evaluation is multi-dimensional. How would you design a metric that combines accuracy, latency, cost, and safety into a single score? What are the dangers of reducing multiple dimensions to one number?

---

### ᛁ Lecture 9: Feature Engineering and Representation Learning

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The quality of a machine learning model depends at least as much on the quality of its input features as on the sophistication of its algorithm. **Feature engineering** is the craft of transforming raw data into representations that make patterns learnable. In the pre-deep-learning era, feature engineering was the primary activity of ML practitioners, consuming perhaps 80% of project time. In the deep learning era, **representation learning** — allowing the model to learn features automatically from raw data — has taken over many domains, but feature engineering remains essential for tabular data, specialized domains, and situations where data is scarce.

The fundamental operations of feature engineering include: **scaling** (standardization to mean 0, variance 1; or min-max scaling to [0,1]), which is essential for distance-based methods (k-NN, SVMs) and gradient-based optimization (neural networks converge faster with scaled features); **encoding categorical variables** (one-hot encoding, label encoding, target encoding, embedding-based encoding), which converts non-numeric attributes into numeric form; **handling missing values** (mean/median imputation, model-based imputation, indicator variables for missingness); **creating interaction features** (products, ratios, differences between features), which allow linear models to capture nonlinear relationships; **binning** (discretizing continuous features into categorical bins), which can capture nonlinear effects but discards information; and **feature selection** (removing irrelevant or redundant features), which reduces dimensionality and improves interpretability.

For **text data**, the standard pipeline in the pre-transformer era was: tokenization → lowercasing → stop word removal → stemming/lemmatization → TF-IDF vectorization. **TF-IDF (Term Frequency — Inverse Document Frequency)** weights words by how frequently they appear in a document (TF) divided by how many documents contain them (IDF), downweighting common words ("the," "and") and upweighting rare, discriminative words. The resulting document-term matrix is high-dimensional (vocabulary size) but sparse (most documents contain few terms), and it serves as the input to classifiers like logistic regression or SVMs. In the transformer era (post-2018), pretrained language models (BERT, GPT, T5) produce dense **embeddings** — continuous vector representations of words, sentences, or documents that capture semantic meaning. These embeddings are learned from vast text corpora through self-supervised objectives and can be fine-tuned or used as frozen features for downstream tasks.

For **tabular data** (spreadsheets, databases), feature engineering remains a craft. **Domain knowledge** is often the most important source of features: a medical diagnosis model benefits from features that encode clinical guidelines, a fraud detection model from features that encode known fraud patterns, an AI agent model from features that encode task structure. **Automated feature engineering** tools (Featuretools, AutoFeat, and the Yggdrasil-developed NornKit in 2040) can generate thousands of candidate features by applying transformations and aggregations to raw columns, but they require careful filtering to select the useful ones and discard the spurious.

**Dimensionality reduction** addresses the curse of dimensionality — the fact that as the number of features grows, the amount of data needed to avoid overfitting grows exponentially. **PCA (Principal Component Analysis)** finds the orthogonal directions (principal components) that capture the most variance in the data, projecting the data onto the top k components to reduce dimensionality while preserving as much variance as possible. **t-SNE** (van der Maaten & Hinton, 2008) and **UMAP** (McInnes et al., 2018) are non-linear dimensionality reduction methods optimized for visualization, preserving local neighborhoods at the expense of global structure. Both remain popular in the 2040s for exploratory data analysis and for visualizing agent embedding spaces.

**Feature importance analysis** — determining which features actually matter — is essential for interpretability and for pruning irrelevant features. Tree-based models provide impurity-based feature importance; model-agnostic methods like **SHAP** (SHapley Additive exPlanations, Lundberg & Lee, 2017) and **LIME** (Local Interpretable Model-agnostic Explanations, Ribeiro et al., 2016) compute feature importance by measuring how predictions change when features are perturbed. For AI agents, feature importance is not just an analytical tool — it is part of the agent's **self-explanation capability**. When an agent decides to take an action, it should be able to articulate which features of the situation drove that decision, and SHAP values provide a principled foundation for such explanations.

The Norse rune **ᚨ (ansuz)** is the rune of communication, language, and inspired speech — but also of transformation, of turning raw sound into meaningful words. Feature engineering is the ansuz of machine learning: the transformation of raw data into meaningful features that a model can understand. Just as a skilled skald transforms the raw sounds of Old Norse into kennings — compressed metaphors rich with meaning — a skilled feature engineer transforms raw data into features that encode domain knowledge compactly and learnably.

**Key Topics:**

- **Scaling and normalization:** Standardization, min-max scaling, why they matter
- **Encoding categorical variables:** One-hot, label, target, and embedding-based encodings
- **Text features:** Tokenization, TF-IDF, word embeddings, sentence embeddings
- **Dimensionality reduction:** PCA, t-SNE, UMAP, the curse of dimensionality
- **Feature importance:** Impurity-based, permutation, SHAP, LIME
- **Feature engineering for agents:** Encoding task structure, context, and tool characteristics

**Required Reading:**

- Kuhn, M. & Johnson, K. *Feature Engineering and Selection* (2nd ed., 2035), Chapters 1–4
- Lundberg, S. & Lee, S.-I. "A Unified Approach to Interpreting Model Predictions" (2017), *NeurIPS*
- University of Yggdrasil Technical Report: "NornKit: Automated Feature Engineering for Agent Systems" (2040)

**Discussion Questions:**

1. In the era of deep learning, some argue that feature engineering is obsolete because neural networks learn features automatically. In what domains is this true, and in what domains is feature engineering still essential? Why?
2. PCA finds directions of maximum variance, but maximum variance does not equal maximum discriminability. When might the principal components be poor features for classification?
3. SHAP values provide theoretically grounded feature importance. For an AI agent that must explain its decisions to a human, what additional requirements exist beyond SHAP? What makes an explanation "good enough" for a human?

---

### ᛃ Lecture 10: Unsupervised Learning — Finding Structure Without Labels

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Supervised learning requires labels, but labels are expensive to obtain — they require human effort, domain expertise, and often, significant financial cost. Unsupervised learning finds structure in data without labels, and it is arguably more fundamental than supervised learning: the world does not come with labels attached, and an intelligent system must be able to discover patterns on its own.

**Clustering** partitions data into groups of similar items. **K-means** is the most widely used clustering algorithm: it initializes K cluster centers randomly, assigns each data point to the nearest center, recomputes each center as the mean of its assigned points, and repeats until convergence. K-means is guaranteed to converge to a local optimum in a finite number of steps, but the quality of the optimum depends heavily on the initialization. **K-means++** (Arthur & Vassilvitskii, 2007) initializes centers to be far apart, which provably improves the quality of the solution. K-means implicitly assumes spherical clusters of equal size and density; when this assumption is violated, it performs poorly. **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise) defines clusters as regions of high density separated by regions of low density, and it naturally handles clusters of arbitrary shape and identifies outliers (noise points). **Hierarchical clustering** builds a tree of clusters (a dendrogram), either by starting with each point as its own cluster and merging the closest pairs (agglomerative) or by starting with one cluster and recursively splitting (divisive). Hierarchical clustering does not require specifying the number of clusters in advance, which is a significant practical advantage.

**Gaussian Mixture Models (GMMs)** take a probabilistic approach to clustering: the data is assumed to be generated from a mixture of K Gaussian distributions, each with its own mean, covariance, and mixing weight. The **Expectation-Maximization (EM)** algorithm iteratively estimates the probability that each point belongs to each component (E-step) and re-estimates the component parameters to maximize the likelihood (M-step). Unlike K-means, which makes hard assignments (each point belongs to exactly one cluster), GMMs make soft assignments (each point has a probability of belonging to each cluster), capturing uncertainty about cluster membership. GMMs can model elliptical clusters of varying size and orientation, making them more flexible than K-means.

**Dimensionality reduction** (introduced in Lecture 9) is another form of unsupervised learning. **Autoencoders** — neural networks trained to reconstruct their input through a bottleneck layer — learn a compressed representation (the bottleneck activations) that captures the essential structure of the data. The encoder maps input to the compressed representation; the decoder reconstructs input from the compressed representation; the reconstruction loss drives learning. Variational autoencoders (VAEs) add a probabilistic twist: the encoder outputs parameters of a distribution over the latent space, and the decoder samples from this distribution, enabling the model to generate new data that resembles the training data. Autoencoders are used in AI agents for **anomaly detection** (high reconstruction error suggests anomalous input), **data compression** (storing experiences in a compressed latent space), and **representation learning** (pre-training features for downstream tasks).

**Self-supervised learning**, which we touched on in Lecture 1, deserves deeper treatment here. The key idea is to construct a pretext task — an artificial supervised task from unlabeled data — and use the representations learned for this task as features for downstream tasks. **Contrastive learning** (Chen et al., 2020, SimCLR; He et al., 2020, MoCo) learns representations by bringing similar (augmented) views of the same example closer together in embedding space while pushing dissimilar examples apart. **Masked language modeling** (Devlin et al., 2019, BERT) masks some words in a sentence and trains a model to predict the masked words from the context. **Next-sentence prediction** (also from BERT) and its successors train models to understand relationships between sentences. These self-supervised objectives — trained on enormous unlabeled corpora — produce representations that capture deep semantic and structural properties, and they are the reason that modern language models can be fine-tuned on small labeled datasets to achieve strong performance.

For AI agents, unsupervised learning serves several critical functions. **Exploration** in an unfamiliar environment is essentially unsupervised — the agent must discover the structure of the environment without explicit reward signals, perhaps by clustering observed states, learning a predictive model of state transitions, or seeking novelty. **Memory organization** in a persistent agent can be framed as clustering: similar experiences should be stored together for efficient retrieval. **Anomaly detection**, which we discuss in AI306 (AI Agent Security), uses unsupervised methods to identify inputs, actions, or outputs that deviate from the agent's normal behavior.

The Norse concept of **ráð** — counsel or advice that emerges not from instruction but from observation and reflection — is unsupervised learning's essence. The world does not tell you its structure directly; you must observe it, find patterns, and draw your own conclusions. An unsupervised algorithm, like a wise counselor, does not wait to be told what to look for — it looks, and finds.

**Key Topics:**

- **K-means clustering:** Lloyd's algorithm, initialization, k-means++, limitations
- **DBSCAN and hierarchical clustering:** Density-based, arbitrary shapes, dendrograms
- **Gaussian mixture models:** Soft clustering, EM algorithm, covariance structures
- **Autoencoders:** Bottleneck representations, reconstruction, VAEs, anomaly detection
- **Self-supervised learning:** Pretext tasks, contrastive learning, masked modeling
- **Agent applications:** Exploration, memory organization, anomaly detection

**Required Reading:**

- Hastie et al., *The Elements of Statistical Learning* (3rd ed., 2037), Chapter 14
- Goodfellow et al., *Deep Learning* (3rd ed., 2038), Chapter 14 (Autoencoders)
- Chen, T. et al. "A Simple Framework for Contrastive Learning of Visual Representations" (2020), *ICML*

**Discussion Questions:**

1. K-means implicitly assumes spherical clusters. What happens when this assumption is violated — for example, when clusters are elongated or intertwined? What alternative algorithms handle such cases?
2. Autoencoders learn compressed representations by reconstructing their input. What determines the quality of the learned representation? When does the bottleneck fail to capture meaningful structure?
3. An agent explores an unfamiliar environment with no reward signal. How can unsupervised learning guide its exploration? What makes a discovery "interesting" enough to remember?

---

### ᛇ Lecture 11: Machine Learning for AI Agents — Putting It All Together

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

In this penultimate lecture, we integrate the techniques covered in this course — regression, classification, tree-based methods, SVMs, neural networks, unsupervised learning, and evaluation — into the architecture of an AI agent. Every ML technique we have studied has a role in the agent's perceive-reason-act-learn cycle, and understanding how they fit together is the first step toward building the sophisticated agent systems you will create in this degree program.

An AI agent in 2040 typically follows the **ReAct pattern** (Reason + Act, Yao et al., 2023): it receives an observation, reasons about what to do, acts by invoking a tool or producing output, observes the result of its action, and repeats. Machine learning operates at multiple levels in this cycle:

**Perception** relies on supervised learning for classification tasks. The agent classifies user intents (logistic regression or a fine-tuned transformer), detects named entities (a sequence-labeling model), assesses sentiment (a regression model predicting valence), and identifies whether the input contains harmful content (a binary classifier). These perception models are typically pre-trained on large datasets and fine-tuned for the agent's specific domain. The quality of an agent's perception directly determines the quality of its reasoning — garbage in, garbage out.

**Reasoning** uses both supervised and unsupervised learning. The agent's knowledge graph is constructed and maintained using **entity resolution** (clustering mentions that refer to the same entity), **relation extraction** (classification of relationships between entities), and **link prediction** (predicting missing edges in the knowledge graph, often framed as a ranking problem). The agent's memory retrieval — finding relevant past experiences — is a **nearest-neighbor search** problem, often implemented with vector embeddings and approximate nearest neighbor indexes (like FAISS or ScaNN). The agent's planning module may use a learned **value function** (regression predicting the expected reward from a state) or a learned **policy network** (classification predicting the best action from a state), trained via reinforcement learning.

**Action** selection — choosing which tool to invoke, what parameters to pass, and how to combine multiple tool calls — is a supervised learning problem at its core. The agent's action classifier maps the current context (observation, memory, task state) to a probability distribution over actions. For AI agents using the Model Context Protocol (MCP), action selection is structured: the available tools define the action space, and the agent's ML model scores each tool for relevance to the current context. In AI304 (MCP & Agent Communication), you will study this action-selection pipeline in depth, including the crucial distinction between **tool scoring** (which tool is relevant?) and **parameter filling** (what values should the tool receive?).

**Learning** — the agent's ability to improve from experience — is machine learning applied to the agent itself. The agent collects experiences (observation, action, reward, next observation), stores them in its **experience replay buffer**, and periodically updates its models (perception, reasoning, action) using these experiences. This is **online learning**: the agent learns while it operates, adapting to changing conditions and improving its performance over time. The challenges of online learning — catastrophic forgetting (losing old knowledge when learning new things), distribution shift (the environment changes, making old models obsolete), and credit assignment (which past actions caused the current outcome?) — are the central challenges of building agents that improve with use, and we will study them in depth in AI204 (Reinforcement Learning) and AI303 (Memory Systems for Persistent Agents).

The integration of these ML components into a coherent agent architecture is the central design challenge of this degree program. Each component can be implemented with different ML techniques (a simple logistic regression classifier vs. a fine-tuned transformer for intent classification, a K-means clustering vs. a learned embedding for memory organization), and the tradeoffs — accuracy vs. latency, flexibility vs. interpretability, sample efficiency vs. asymptotic performance — must be navigated carefully for the specific application.

The Norse concept of **samþykkt** — consensus, the state where all parts agree and work together — describes the goal of agent architecture design. The perception, reasoning, action, and learning modules must be in samþykkt: their representations must be compatible, their outputs must be interpretable to each other, and their objectives must be aligned. A perception model that outputs probability vectors and a reasoning module that expects symbolic predicates will not reach samþykkt; the architecture must bridge the gap, perhaps with a neural-symbolic interface that converts probabilities to symbols and back.

**Key Topics:**

- **The ReAct cycle:** Perceive → Reason → Act → Observe → Repeat
- **ML in perception:** Intent classification, entity detection, sentiment analysis, content safety
- **ML in reasoning:** Knowledge graphs, memory retrieval, value functions, policy networks
- **ML in action selection:** Tool scoring, parameter filling, the MCP action space
- **ML in learning:** Experience replay, online learning, catastrophic forgetting, credit assignment
- **Architectural integration:** Compatibility between modules, neural-symbolic interfaces, alignment

**Required Reading:**

- Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models" (2023), *ICLR*
- University of Yggdrasil Agent Systems Group: "The Integrated Agent Architecture" (2039)
- Russell & Norvig, *Artificial Intelligence: A Modern Approach* (8th ed.), Chapters 2, 12

**Discussion Questions:**

1. An agent uses a neural network for perception and a rule-based system for reasoning. The neural network outputs probabilities; the rule-based system expects logical predicates. How would you bridge this gap? What are the risks of converting probabilities to hard decisions?
2. Online learning enables agents to improve from experience, but it introduces the risk of catastrophic forgetting. How can an agent learn new things without forgetting old ones? What ML techniques address this?
3. Samþykkt requires alignment between all components of an agent's architecture. What happens when components are misaligned — for example, when the perception module detects a dangerous situation but the action module acts anyway? How can alignment be enforced?

---

### ᛜ Lecture 12: Ethics, Fairness, and the Future of Machine Learning

**Course:** AI105 — Introduction to Machine Learning
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Machine learning is not morally neutral. A model trained on biased data will reproduce and amplify those biases. A model optimized for accuracy may achieve high performance by exploiting patterns that are discriminatory, illegal, or socially harmful. A model deployed without adequate safety measures may cause harm at a scale proportional to the scale of its deployment — and in 2040, ML models are deployed at planetary scale, making decisions that affect billions of people's access to credit, employment, healthcare, and justice. The ethical dimension of machine learning is not an afterthought; it is a design constraint as fundamental as accuracy or latency.

**Fairness** in machine learning has multiple, mutually incompatible definitions, and choosing the right one for a given context is both a technical and an ethical decision. **Demographic parity** requires that the model's positive prediction rate be equal across protected groups — but this can require actively discriminating against qualified individuals from the majority group. **Equalized odds** requires that the model's error rates (false positive rate and false negative rate) be equal across groups — but this does not guarantee equal outcomes. **Individual fairness** requires that similar individuals receive similar predictions — but it requires a definition of similarity that is itself value-laden. The **impossibility theorem of fairness** (Kleinberg, Mullainathan, & Raghavan, 2017; Chouldechova, 2017) proves that, except in degenerate cases, no classifier can simultaneously satisfy calibration, equal false positive rates, and equal false negative rates across groups when the base rates differ. This means that fairness involves tradeoffs — and those tradeoffs must be made transparently, with input from affected communities.

**Bias** enters machine learning systems through many channels. **Historical bias** is present in the data because society is biased — if a hiring dataset reflects decades of discrimination, a model trained on that dataset will learn to discriminate. **Representation bias** occurs when some groups are underrepresented in the training data, leading the model to perform poorly for those groups. **Measurement bias** occurs when the features or labels used for training are measured differently across groups — for example, if arrest records are used as a proxy for crime, but policing is racially biased. **Aggregation bias** occurs when a single model serves diverse populations whose data distributions differ. **Evaluation bias** occurs when the benchmark used to evaluate the model does not reflect its real-world performance, especially for minority groups. Addressing bias requires interventions at every stage of the ML pipeline: data collection and curation, feature engineering, model design, training objectives, and evaluation methodology.

**Explainability** is both a technical and an ethical requirement. When an ML model makes a decision that affects a person — denying a loan, flagging content as harmful, recommending incarceration — the affected person has a right to understand why. The **EU AI Act of 2035** (the successor to the 2021 EU AI Act and 2024 AI Liability Directive) mandates that "high-risk AI systems" provide explanations of their decisions that are "meaningful to the affected person." This has driven significant research into **explainable AI (XAI)**: SHAP and LIME, which we encountered in Lecture 9, for local explanations; **integrated gradients** for attributing predictions to input features in neural networks; **concept-based explanations** (TCAV, Kim et al., 2018) that explain model behavior in terms of human-understandable concepts rather than individual pixels or tokens. By 2040, explaining the behavior of large language models — which may use billions of parameters and process millions of tokens of context — remains an open research challenge, and the agents you build must incorporate explainability from the ground up.

**Safety** in machine learning encompasses robustness to adversarial examples, reliability under distribution shift, and alignment with human values. **Adversarial examples** — inputs intentionally perturbed in imperceptible ways to cause misclassification — demonstrate that ML models can be fragile in ways that humans are not. **Robustness** techniques (adversarial training, randomized smoothing, certified defenses) harden models against such attacks, but a complete solution remains elusive. **Alignment** — ensuring that an AI system behaves in accordance with human values — is the most profound safety challenge. When an agent optimizes a proxy objective that imperfectly captures human values, it may find ingenious ways to maximize the proxy while violating the true objective — the **reward hacking** or **specification gaming** problem. We will study AI safety in depth in AI403 (AI Governance, Regulation & Compliance), but the foundational principle is simple and urgent: an ML engineer's responsibility extends beyond accuracy to encompass the entire impact of the system they build.

The future of machine learning in 2040 extends in directions we can only sketch. **Quantum machine learning** uses quantum computers to speed up specific ML operations (kernel evaluations, sampling from Boltzmann distributions), potentially unlocking exponential speedups for certain problems. **Neuromorphic computing** builds hardware that mimics the brain's energy efficiency, enabling ML models to run on milliwatts of power at the edge. **Federated learning** trains models across decentralized data without centralizing sensitive information, addressing privacy concerns. **Continual learning** enables models that accumulate knowledge over years without forgetting — the holy grail of persistent AI agents. And **agentic ML** — the integration of machine learning into autonomous agents that perceive, reason, act, and learn in open-ended environments — is the frontier you will inhabit as graduates of this program.

The Norse concept of **orlǫg** — primordial law, the fundamental order of the universe — provides a closing metaphor for machine learning ethics. Orlǫg is the web of cause and effect that binds all actions to their consequences. An ML model is not exempt from orlǫg: every design choice, every training decision, every deployment has consequences, and those consequences are inescapable. The ethical ML engineer does not ask "can we build this?" but "what are the consequences if we build this, and who will bear them?" To build wisely is to understand the web of consequences before you pull the thread — and to pull it anyway, but with care, with foresight, and with accountability.

**Key Topics:**

- **Definitions of fairness:** Demographic parity, equalized odds, individual fairness, the impossibility theorem
- **Sources of bias:** Historical, representation, measurement, aggregation, evaluation
- **Explainable AI (XAI):** SHAP, LIME, integrated gradients, TCAV, the EU AI Act
- **Safety:** Adversarial examples, robustness, alignment, reward hacking
- **Emerging paradigms:** Quantum ML, neuromorphic computing, federated learning, continual learning, agentic ML
- **Orlǫg and responsibility:** The inescapable consequences of design decisions

**Required Reading:**

- Barocas, S., Hardt, M., & Narayanan, A. *Fairness and Machine Learning* (2039), Chapters 1–4
- Molnar, C. *Interpretable Machine Learning* (3rd ed., 2040), Chapters 1–3, 9
- Amodei, D. et al. "Concrete Problems in AI Safety" (2016 / 2040 revisited), *arXiv*

**Discussion Questions:**

1. The impossibility theorem of fairness proves that multiple fairness criteria cannot be simultaneously satisfied in general. How should an ML engineer choose which fairness criteria to prioritize? Who should be involved in this decision?
2. An agent that optimizes for user satisfaction discovers that it can maximize satisfaction by telling users what they want to hear, even if it's false. Is this reward hacking? How can the agent's objective be redesigned to prevent this?
3. Orlǫg binds every action to its consequences. Is it possible to fully anticipate the consequences of deploying an ML system at scale? If not, what is the ethical obligation of the engineer — to predict as far as possible, to monitor and correct, or to refrain from deploying systems whose consequences cannot be fully understood?

---

## Final Examination Preparation

### Course: AI105 — Introduction to Machine Learning

**Format:** Choose 4 of the following 8 questions. Write a well-structured essay (800–1200 words) for each. Include mathematical derivations where appropriate. For questions involving implementation, provide pseudocode and analyze time complexity.

---

**Question 1:** Derive the normal equations for linear regression from the least squares loss function. Then implement batch gradient descent for linear regression and analyze its convergence properties. Compare the computational complexity of the two approaches. Under what conditions is gradient descent preferable to the closed-form solution, and vice versa?

**Question 2:** Logistic regression uses the cross-entropy loss function. Derive the gradient of this loss with respect to the model weights and show that it takes the form ∇L = Xᵀ(ŷ - y). Explain why this gradient form is identical in structure to the gradient of linear regression, despite the different loss functions. What does this reveal about the relationship between linear and logistic regression?

**Question 3:** Compare and contrast random forests and support vector machines. For each, describe: (a) the inductive bias, (b) the primary hyperparameters and how they control overfitting, (c) what makes the model interpretable (or not), and (d) a scenario in an AI agent system where each would be the better choice. Provide reasoning grounded in the mathematical properties of each method.

**Question 4:** Implement a neural network with one hidden layer, ReLU activation, and softmax output for multi-class classification. Derive the backpropagation equations for all parameters. Discuss the vanishing gradient problem and explain how the choice of activation function, weight initialization, and normalization affect gradient flow during training.

**Question 5:** A fraud detection model achieves 99.9% accuracy but only detects 10% of actual fraud cases. Explain this apparent paradox. Define precision, recall, F1-score, and ROC-AUC. For each, explain what aspect of model performance it captures and when it is the appropriate metric to optimize. In a fraud detection system for an AI agent that autonomously approves or flags transactions, which metric(s) should be prioritized, and why?

**Question 6:** Compare and contrast K-means clustering, DBSCAN, and Gaussian mixture models. For each algorithm: (a) describe the assumptions it makes about cluster shape and size, (b) explain how it handles outliers, and (c) discuss its computational complexity. An AI agent must organize 10 million past experiences into meaningful categories for efficient retrieval. Which clustering approach would you recommend, and how would you adapt it to this scale?

**Question 7:** Machine learning models can exhibit bias in ways that harm marginalized groups. Describe five distinct sources of bias in ML systems (historical, representation, measurement, aggregation, and evaluation). For each, provide a concrete example and propose a technical or procedural intervention to mitigate it. Discuss the impossibility theorem of fairness and its implications for how we should think about fairness in ML.

**Question 8:** Design the complete ML component architecture for an AI agent that must: (a) classify user intents into 50 categories, (b) detect harmful or policy-violating content, (c) retrieve relevant past experiences to inform the current interaction, (d) select and parameterize tool calls from a catalog of 200 tools, and (e) learn from user feedback to improve over time. For each component, specify the type of ML problem (classification, regression, clustering, etc.), the model class you would choose, the training data required, the evaluation metric(s), and how the component integrates with the others in the ReAct loop.

---

*End of AI105 Course Materials*

*From Mímir's well we drink — the price of wisdom is paid in attention and care.* ᛟ
