# CS207: Introduction to Machine Learning
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4  
**Prerequisites:** CS102 — Discrete Mathematics for CS; CS104 — Object-Oriented Programming; CS201 — Data Structures & Algorithms II  
**Description:** Supervised and unsupervised learning, neural networks, backpropagation, SVMs, ensemble methods, deep learning foundations. Practical exercises in PyTorch and JAX on the Yggdrasil Mimir Research Cluster.

---

## Lecture 1: The Learning Problem — From Oracles to Algorithms That Generalise

Machine learning is the study of algorithms that improve their performance on a task as they are given more data. Tom Mitchell's 1997 formulation provides the canonical definition: a computer program is said to learn from experience E with respect to some class of tasks T and performance measure P, if its performance at tasks in T, as measured by P, improves with experience E. This definition is deliberately broad — it encompasses everything from linear regression (which improves its prediction of housing prices as it sees more houses) to modern foundation models (which improve their text generation as they process more tokens from the internet). The unifying insight is that learning *is generalisation from experience* — the capacity to perform well on data that the learner has not seen before, by extracting patterns from data that it has.

The formal setup frames every machine learning problem as a search through a hypothesis space. We have an input domain **X** (the set of possible inputs), a label space **Y** (the set of possible outputs), and an unknown target function *f*: X → Y that we wish to approximate. We receive a training set *D* = {(x₁, y₁), ..., (xₙ, yₙ)} drawn from an unknown distribution *P* over X × Y, and we seek a hypothesis *h*: X → Y (drawn from hypothesis class H) that minimises the expected loss R(*h*) = E_{(x,y)~P}[L(h,(x,y))]. Since *P* is unknown, we can only compute the empirical risk *R̂*(*h*) = (1/n)Σᵢ L(h,(xᵢ,yᵢ)). The empirical risk minimisation principle selects *h* minimising *R̂*(*h*), but this permits overfitting: a hypothesis achieving zero training error may generalise poorly because it memorises noise rather than learning structure. Regularisation — adding penalties for complexity or restricting H — is the countermeasure.

**Bias-variance decomposition** illuminates the fundamental tradeoff. For regression with squared loss, expected prediction error decomposes into bias² (systematic error from the algorithm's inductive preferences), variance (sensitivity to the particular training sample), and irreducible error (noise no algorithm can eliminate). High bias means underfitting; high variance means overfitting. The sweet spot balances expressiveness against stability — this tension is invariant to the algorithm, a property of the learning problem itself. In 2040, the "double descent" phenomenon (Belkin et al., 2019) has reshaped our understanding: past the interpolation threshold, test error decreases *again* as model capacity increases, subverting the classical U-shaped bias-variance curve. This discovery reconciled the empirical success of over-parameterised deep networks with classical statistical theory, though the precise interplay between double descent and the bias-variance tradeoff remains an active area of inquiry at Yggdrasil's Mimir Lab.

**PAC learning** (Probably Approximately Correct) provides the theoretical scaffolding. A concept class C is PAC-learnable if there exists an algorithm that, for any ε > 0 and δ > 0 and for any distribution *P* over X, outputs a hypothesis *h* with error at most ε with probability at least 1−δ, given poly(1/ε,1/δ,n) examples. The **VC dimension** measures hypothesis class expressiveness: the largest number of points H can shatter. Sample complexity scales as O((d_VC/ε)log(1/ε) + log(1/δ)). **No free lunch theorems** (Wolpert, 1996) establish that no algorithm dominates on average over all distributions — every hypothesis class encodes an inductive bias, a bet on the world's structure. The practical implication is profound: the success of any ML system depends not on universal superiority but on the alignment between its inductive biases and the structure of the problem domain. Modern deep learning's success can be understood as exploiting the compositional, hierarchical structure natural to physical phenomena and human-designed data.

The **supervised/unsupervised/reinforcement** taxonomy partitions learning by feedback type. Supervised learning receives explicit labels, unsupervised learning discovers hidden structure, and reinforcement learning optimises cumulative reward through interaction. Each paradigm has distinct assumptions, algorithms, and guarantees — covered in subsequent lectures. Self-supervised learning, which generates supervisory signals from the data itself (as in masked language modelling), has emerged by 2040 as a fourth major paradigm, powering foundation models that learn rich representations from unlabelled corpora and then adapt to downstream tasks with minimal fine-tuning.

**Required Reading:**
- Tom Mitchell, *Machine Learning* (McGraw-Hill, 1997/2040), chs. 1–2
- Shai Shalev-Shwartz & Shai Ben-David, *Understanding Machine Learning* (Cambridge UP, 2014/2040), chs. 1–3
- Belkin et al., "Reconciling Modern Machine-Learning Practice and the Classical Bias–Variance Trade-Off," *PNAS* 116:32 (2019): 15849–15854
- Yggdrasil ML Lab: Bias-Variance Decomposition, VC Dimension Explorer (2040)

**Discussion Questions:**
1. Does deep learning violate the bias-variance tradeoff, or does it shift the sweet spot when datasets become very large? How does the double descent phenomenon change your answer?
2. The no free lunch theorems render no algorithm universally superior. Does this make algorithm selection meaningless, or does it elevate it to a meta-learning problem?
3. PAC learnability guarantees have sample complexity bounds that far exceed practical needs. What explains the gap between theory and practice?

---

## Lecture 2: Linear Models — Regression, Classification, and the Geometry of Decision Boundaries

Linear regression finds weights **w** ∈ ℝᵈ and bias *b* minimising MSE: L(w,b) = (1/n)Σᵢ(wᵀxᵢ+b−yᵢ)². The OLS solution w* = (XᵀX)⁻¹Xᵀy is BLUE (Best Linear Unbiased Estimator) under Gauss-Markov assumptions: zero-mean errors, homoscedasticity, no autocorrelation, and no perfect multicollinearity. When these assumptions fail — nonlinearity, heteroscedasticity, correlated errors — remedies include transformations, weighted least squares, and generalised least squares. Ridge regression (L₂) adds λ||w||² to the loss, which ensures invertibility of XᵀX+λI and shrinks coefficients toward zero — a computational convenience that doubles as a statistical safeguard. Lasso (L₁) adds λΣ|wⱼ|, producing sparse solutions for automatic feature selection. Elastic Net blends both: α·L₁ + (1−α)·L₂. The sparsity of Lasso comes at a cost: it can select at most *n* features (when n < d, the "high-dimensional" regime common in genomics and NLP), and correlated features create instability. Elastic Net addresses both by allowing grouped selection.

**Logistic regression** models P(y=1|x) = σ(wᵀx+b) with binary cross-entropy loss ℓ = −Σ[yᵢlog(ŷᵢ) + (1−yᵢ)log(1−ŷᵢ)]. The decision boundary is the hyperplane wᵀx+b=0, producing a linear separator. **Multiclass logistic regression** (softmax regression) extends to K classes: P(y=k|x) = exp(wₖᵀx+bₖ) / Σⱼexp(wⱼᵀx+bⱼ), with categorical cross-entropy loss. The softmax function, named for its "soft" approximation of the argmax, provides not just a classification decision but a calibrated probability distribution — if the model is well-specified. In practice, logistic regression's probability estimates are often poorly calibrated, motivating techniques like Platt scaling (fitting a sigmoid to the scores) and isotonic regression (monotonic recalibration).

**Gradient descent** updates w ← w − η∇L(w). **Stochastic gradient descent** (SGD) approximates gradients using mini-batches, introducing noise that helps escape shallow local minima — a feature, not a bug. **Adam** (Kingma & Ba, 2015) combines adaptive learning rates (per-parameter scaling based on past gradient magnitudes) with momentum (exponential moving average of past gradients), serving as the default optimiser for deep learning. Adam's theoretical convergence guarantees require decreasing learning rates, but in practice a constant learning rate with warmup is standard. **Learning rate scheduling** — cosine annealing, step decay, one-cycle policies — has evolved from engineering folklore to principled theory (Smith, 2018) connecting learning rate dynamics to loss landscape geometry.

The geometric interpretation of linear models is essential. Logistic regression finds the maximum-margin hyperplane in feature space (related to SVMs, as Lecture 4 will show). Regularisation constrains this hyperplane: L₂ produces small weights in all directions (a "round" constraint), L₁ drives weights exactly to zero (a "diamond" constraint aligned with axes). The shape of the constraint region determines which solutions are favoured — a deep connection between optimisation geometry and inductive bias that recurs throughout machine learning. On the Mimir Cluster, students implement all variants from scratch in NumPy before using PyTorch, ensuring that the abstractions rest on firm mathematical foundations.

**Required Reading:**
- Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning* (2nd ed., 2009/2040), chs. 3–4
- Bishop, *Pattern Recognition and Machine Learning* (2006/2040), chs. 3–4
- Smith, "A Bayesian Perspective on Generalisation and Stochastic Gradient Descent," *ICLR '18* (2018)

**Discussion Questions:**
1. What are the most common violations of linear regression assumptions, and how can you detect and address them? When does addressing violations matter versus when is OLS robust?
2. Under what conditions does Lasso fail to select the correct features? How does Elastic Net address these failures?
3. Adam's default learning rates work remarkably well across problems. Does this indicate that the loss landscape of neural networks has universal geometric properties, or is it mere coincidence?

---

## Lecture 3: Decision Trees and Ensemble Methods — The Wisdom and the strategies of Crowds

Decision trees partition input space with axis-aligned splits, producing a piecewise-constant decision surface. At each internal node, the algorithm selects the feature and threshold that maximally reduces impurity: Gini impurity G(S) = 1 − Σₖpₖ² for classification, variance Var(S) = (1/|S|)Σᵢ(yᵢ−ȳ)² for regression. Splitting greedily continues until a stopping criterion — minimum samples per leaf, maximum depth, or impurity reduction threshold — is met. Overfitting is addressed by pre-pruning (stopping early) and post-pruning (cost-complexity pruning with parameter α that trades tree size against training error). CART (Classification and Regression Trees, Breiman et al., 1984) remains the canonical framework, though its greedy optimisation guarantees only local optima. Decision trees are interpretable, handle mixed data types, and require no feature scaling — but they are high-variance estimators: small changes in training data can produce substantially different trees.

**Random forests** (Breiman, 2001) address this variance through ensemble averaging. Each tree is trained on a bootstrap sample (sampling with replacement), and at each split, only a random subset of √d features is considered. This decorrelates the trees: if every tree split on the strongest feature, they would all look similar; random feature subsetting forces diversity. Out-of-bag (OOB) error provides efficient cross-validation without a held-out set — each training point is predicted only by the trees that did not see it in their bootstrap sample. The forest's prediction is the majority vote (classification) or average (regression) across all trees. Breiman showed that as the number of trees grows, the forest does not overfit; it converges to a limit. However, individual trees still overfit — the ensemble merely averages out this overfitting.

**Gradient boosting** (Friedman, 2001) takes the opposite approach: instead of averaging independent models, it builds trees sequentially, each fitting the negative gradient of the loss with respect to the current prediction. The learning rate (shrinkage) controls each tree's contribution: small learning rates require more trees but generalise better. **XGBoost** (Chen & Guestrin, 2016) adds L₁ and L₂ regularisation on leaf weights, sparse-aware splitting for missing values, cache-aware access patterns, and approximate quantile sketch for large datasets. **LightGBM** (Ke et al., 2017) uses histogram-based splitting and leaf-wise growth (rather than level-wise) for speed, competitive accuracy, and lower memory. **CatBoost** (Prokhorenkova et al., 2018) handles categorical features via ordered target statistics, preventing target leakage, and uses ordered boosting to reduce prediction shift. Gradient boosting typically wins on tabular data competitions; random forests are faster to train, more robust to hyperparameter choices, and more interpretable.

**SHAP values** (Lundberg & Lee, 2017) provide local explanations by fairly allocating predictions among features using Shapley values from cooperative game theory. For any prediction f(x), each feature's SHAP value φᵢ is its marginal contribution averaged over all possible feature orderings: φᵢ = Σ_{S⊆N\{i}} (|S|!(|N|−|S|−1)!)/|N|! · [f(S∪{i}) − f(S)]. This guarantee of local accuracy (Σᵢφᵢ = f(x) − E[f]) and consistency makes SHAP the most theoretically grounded explanation method. TreeSHAP exploits the tree structure for exact polynomial-time computation, making it practical for ensembles of thousands of trees. However, SHAP values describe the model's behaviour, not the causal mechanism generating the data — a critical distinction that students must absorb early.

**Required Reading:**
- Breiman, "Random Forests," *Machine Learning* 45:1 (2001): 5–32
- Friedman, "Greedy Function Approximation: A Gradient Boosting Machine," *Annals of Statistics* 29:5 (2001): 1189–1232
- Chen & Guestrin, "XGBoost: A Scalable Tree Boosting System," *KDD '16* (2016): 785–794
- Lundberg & Lee, "A Unified Approach to Interpreting Model Predictions," *NeurIPS '17* (2017): 4765–4774
- Prokhorenkova et al., "CatBoost: Unbiased Boosting with Categorical Features," *NeurIPS '18* (2018)

**Discussion Questions:**
1. Is there a fundamental interpretability-accuracy tradeoff, or can we have both? What does the existence of SHAP values tell us about this question?
2. XGBoost dominates tabular data while neural networks dominate unstructured data. Why does this divide persist in 2040?
3. Are SHAP values genuine explanations of the underlying phenomenon, or merely decompositions of the model's decision process? What is the difference?

---

## Lecture 4: Support Vector Machines and Kernel Methods — Maximum Margins and Implicit Feature Spaces

Support vector machines find the maximum-margin hyperplane separating two classes. The primal problem minimises ||w||²/2 subject to yᵢ(wᵀxᵢ+b) ≥ 1 for all training points. Geometrically, the margin is the distance between the hyperplanes wᵀx+b=1 and wᵀx+b=−1, equal to 2/||w||. Maximising the margin minimises ||w||², a convex optimisation with a unique global optimum — unlike neural networks, SVMs have no local minima. The solution depends only on **support vectors** — training points on or within the margin boundary. This sparsity (typically 5–20% of training points are support vectors) gives SVMs computational advantages and theoretical generalisation guarantees via margin bounds: with probability 1−δ, the error is bounded by O((R²||w||² + log(1/δ))/n), where R bounds the data radius.

The soft-margin SVM introduces slack variables ξᵢ ≥ 0 and regularisation parameter C: minimise ||w||²/2 + C·Σξᵢ subject to yᵢ(wᵀxᵢ+b) ≥ 1−ξᵢ. This allows misclassifications, trading margin width against training errors. As C → ∞, the hard-margin SVM is recovered; as C → 0, the model tolerates more errors. The choice of C is typically made via cross-validation or theoretical bounds.

The dual formulation transforms the problem todepend on data only through inner products: maximise Σᵢαᵢ − ½ΣᵢΣⱼαᵢαⱼyᵢyⱼ⟨xᵢ,xⱼ⟩ subject to 0 ≤ αᵢ ≤ C and Σᵢαᵢyᵢ = 0. This enables the **kernel trick**: replacing ⟨xᵢ,xⱼ⟩ with K(xᵢ,xⱼ) = ⟨φ(xᵢ),φ(xⱼ)⟩ implicitly maps to high-dimensional (even infinite-dimensional) feature spaces without computing φ(x). **Mercer's theorem** guarantees that any symmetric, positive semi-definite kernel corresponds to an inner product in some feature space. Standard kernels include: Linear K(u,v) = uᵀv, Polynomial K(u,v) = (γuᵀv+r)ᵈ, RBF K(u,v) = exp(−γ||u−v||²), and Sigmoid K(u,v) = tanh(γuᵀv+r). The RBF kernel is universal: given appropriate γ, it can approximate any continuous function on a compact set, mapping to an infinite-dimensional feature space.

Computational limitations arise from the O(n²) storage and O(n³) time for the Gram matrix. **Random Fourier Features** (Rahimi & Recht, 2007) approximate the RBF kernel by randomly sampling from the kernel's Fourier transform, reducing the kernel computation to a linear inner product in a lower-dimensional explicit feature space. **Nyström approximation** subsamples m landmark points and approximates the full kernel matrix via low-rank decomposition. Both methods reduce computation from O(n³) to O(nm²) while preserving most accuracy. In 2040, kernel methods remain competitive on small to medium datasets and in domains where margin guarantees matter (medical diagnosis, adversarial robustness), though deep learning dominates large-scale vision and language tasks.

The kernel trick extends beyond SVMs to kernel PCA (projecting data into the kernel feature space and performing PCA there), kernel k-means, and kernel ridge regression. Kernel methods exploit the same insight as neural networks — that linear methods in a rich feature space are powerful — but they do so explicitly (via the kernel) rather than implicitly (via learned representations). The relationship between kernels and neural networks is deeper than it appears: an infinitely wide single-hidden-layer network with random weights is equivalent to a particular kernel (the neural tangent kernel, Jacot et al., 2018), a connection that has driven significant theoretical progress in understanding deep learning.

**Required Reading:**
- Bishop, *Pattern Recognition and Machine Learning* (2006/2040), chs. 6–7
- Schölkopf & Smola, *Learning with Kernels* (MIT Press, 2002/2040)
- Cortes & Vapnik, "Support-Vector Networks," *Machine Learning* 20:3 (1995): 273–297
- Rahimi & Recht, "Random Features for Large-Scale Kernel Machines," *NeurIPS '07* (2007): 1177–1184

**Discussion Questions:**
1. What is the relationship between the soft-margin SVM and logistic regression in the limit of small C? How does this connect SVMs to probabilistic models?
2. The RBF kernel maps to infinite dimensions. Why doesn't this overfit, and what role does the margin play?
3. When are approximate kernel methods (Random Fourier Features, Nyström) justified, and when is exact computation preferable despite the cost?

---

## Lecture 5: Neural Networks and Backpropagation — The Chain Rule Unleashed

Artificial neurons compute a = σ(wᵀx+b). Activations include sigmoid σ(z) = 1/(1+e⁻ᶻ) (saturating, historically popular, now largely abandoned for hidden layers), tanh(z) = (eᶻ−e⁻ᶻ)/(eᶻ+e⁻ᶻ) (zero-centred, improved gradients), ReLU(z) = max(0,z) (non-saturating for positive inputs, modern default), Leaky ReLU(z) = max(αz,z) for small α (addresses "dying ReLU" where neurons permanently output zero), ELU(z) = {z if z>0; α(eᶻ−1) otherwise} (smooth, zero-centred), GELU(z) = z·Φ(z) (Gaussian Error Linear Unit, smooth approximation of ReLU, used in Transformers), and Swish(z) = z·σ(z) (self-gated, non-monotonic, competitive with ReLU in deep networks).

Feedforward networks compose layers: ŷ = σ_L(W_L ...σ₁(W₁x+b₁)...+b_L). The **universal approximation theorem** (Cybenko 1989; Hornik 1991) guarantees that a single hidden layer with sufficient width can approximate any continuous function on a compact set to arbitrary precision. However, width grows exponentially for complex functions, while depth provides **efficiency**: deep networks represent certain functions with exponentially fewer neurons than shallow ones. The depth-width tradeoff is analogous to the circuit complexity hierarchy in computational theory — some functions require exponential size in shallow circuits but polynomial size in deep circuits. This theoretical insight explains why depth, not just width, is crucial for practical architectures.

**Backpropagation** (Rumelhart, Hinton & Williams, 1986) computes gradients via the chain rule in reverse topological order. For a network with L layers, the forward pass computes activations aₗ = σₗ(Wₗaₗ₋₁+bₗ) and the backward pass computes δₗ = (Wₗ₊₁ᵀδₗ₊₁) ⊙ σₗ'(zₗ), yielding gradients ∂L/∂Wₗ = δₗaₗ₋₁ᵀ and ∂L/∂bₗ = δₗ. Cost is 2–3× the forward pass. The **vanishing gradient problem** (Hochreiter 1991) plagues early layers: if |σ'(z)| < 1 in each layer, gradients shrink exponentially through depth. Solutions include ReLU (|ReLU'(z)| = 1 for z > 0), batch normalisation (reducing internal covariate shift by normalising activations to zero mean and unit variance), and residual connections (allowing gradients to flow directly via addition rather than multiplication). The **exploding gradient problem** is the dual: unbounded gradients cause instability, addressed by gradient clipping and careful initialisation.

**Weight initialisation** critically affects training dynamics. Xavier/Glorot initialisation sets Var(w) = 2/(nₗ+nₗ₊₁) for sigmoid/tanh, preserving activation variance across layers. He initialisation sets Var(w) = 2/nₗ for ReLU, compensating for the dead half. Kaiming initialisation extends He to Leaky ReLU. In 2040, sophisticated initialisation schemes (e.g., LayerScale, FixUp) and training dynamics analysis (neural tangent kernel, mean-field theory) have largely demystified why these schemes work, connecting random initialisation to the training landscape.

The computational graph abstraction underpins modern frameworks. PyTorch builds the graph dynamically (define-by-run), enabling flexible debugging and dynamic architectures; JAX builds it lazily with tracing (just-in-time compilation), enabling fusion, vectorisation, and automatic batching. Both compute the same gradients — backpropagation is just the chain rule applied to a directed acyclic graph — but differ in when and how the graph is constructed. On the Mimir Cluster, students implement backpropagation by hand on small networks (to build intuition) before using Autograd (NumPy-based) and then PyTorch/JAX (production tools).

**Required Reading:**
- Goodfellow, Bengio & Courville, *Deep Learning* (2016/2040), chs. 6–8
- Rumelhart, Hinton & Williams, "Learning Representations by Back-Propagating Errors," *Nature* 323 (1986): 533–536
- Glorot & Bengio, "Understanding the Difficulty of Training Deep Feedforward Neural Networks," *AISTATS '10* (2010): 249–256
- He et al., "Delving Deep into Rectifiers," *ICCV '15* (2015): 1026–1034

**Discussion Questions:**
1. Why are deep networks more effective than wide shallow ones? What does circuit complexity theory tell us about the representational advantage of depth?
2. Compare how ReLU, batch normalisation, and residual connections address vanishing gradients. Do they solve the same problem or different problems?
3. What are the hardware implications of backpropagation for billion-parameter networks? How do GPU memory hierarchies affect gradient computation strategies?

---

## Lecture 6: Convolutional Neural Networks — Vision and the Architecture of Spatial Perception

Convolutional neural networks exploit three structural priors for grid-like data: **local connectivity** (each neuron connects to a small receptive field rather than all inputs), **weight sharing** (the same filter is applied across spatial positions, encoding translation equivariance), and **hierarchical composition** (low-level features combine into mid-level patterns which combine into high-level concepts). These priors dramatically reduce parameters: a fully connected layer from a 224×224×3 input to 4096 outputs requires 224×224×3×4096 ≈ 611M parameters, while a 3×3 convolution with 64 filters requires only 3×3×3×64 + 64 ≈ 1.8K. This thousand-fold reduction is not merely efficient — it encodes the inductive bias that spatially local patterns are translation-invariant, which is why CNNs generalise from remarkably few examples.

Architectural evolution tells a story of escalating ambition. **LeNet-5** (LeCun et al., 1998, ~60K params) digitised mail sorting with 7 layers. **AlexNet** (Krizhevsky et al., 2012, 60M params) won ImageNet 2012 by 10 percentage points, introducing ReLU activations, dropout regularisation, and GPU training — a watershed moment that catalysed the deep learning revolution. **VGGNet** (Simonyan & Zisserman, 2014, 16–19 layers) demonstrated that depth with small (3×3) filters consistently outperforms fewer large filters. **GoogLeNet/Inception** (Szegedy et al., 2015) introduced multi-scale processing via parallel convolution paths with different receptive field sizes. **ResNet** (He et al., 2016) solved the degradation problem (deeper networks performing worse) with residual connections: y = F(x) + x, allowing gradients to bypass layers. ResNet-152 achieved 3.57% top-5 error on ImageNet, better than human performance on the same benchmark. **EfficientNet** (Tan & Le, 2019) showed that systematically scaling depth, width, and resolution using compound coefficients yields Pareto-optimal architectures. **Vision Transformers** (Dosovitskiy et al., 2020) challenged the convolution monopoly by splitting images into patches and processing them with self-attention, achieving state-of-the-art when data is abundant. By 2040, hierarchical vision transformers (Swin, ViT-Kids) and convolution-attention hybrids (CoAtNet, EfficientNetV3) coexist, each dominating different data regimes.

Transfer learning leverages pre-trained models (ImageNet, or Yggdrasil's NordicHeritage-2040 dataset of 50M images from archaeological and cultural heritage domains) as starting points. Fine-tuning achieves strong performance with few labels by reusing low-level features (edges, textures) while adapting high-level representations. **Data augmentation** expands training distributions: geometric transforms (flipping, rotation, cropping), photometric transforms (colour jitter, brightness, contrast), and advanced methods like MixUp (linearly interpolating pairs of images and labels), CutMix (replacing image patches with other images), and RandAugment (automated augmentation policy search). In 2040, diffusion-based augmentation generates realistic synthetic training data conditioned on class labels, and self-supervised pre-training (DINO v3, BYOL-2) provides representations that rival supervised pre-training without labels.

**Required Reading:**
- Goodfellow, Bengio & Courville, *Deep Learning* (2016/2040), ch. 9
- He et al., "Deep Residual Learning for Image Recognition," *CVPR '16* (2016): 770–778
- LeCun, Bengio & Hinton, "Deep Learning," *Nature* 521 (2015): 436–444
- Dosovitskiy et al., "An Image Is Worth 16×16 Words," *ICLR '21* (2021)

**Discussion Questions:**
1. What assumptions does CNN weight sharing encode about the visual world, and when do they fail? How do vision transformers challenge these assumptions?
2. Do residual connections change representable functions, or just make optimisation easier? What does the linear approximation of ResNet (y ≈ x + εF(x)) suggest?
3. What are the ethical implications of ImageNet pre-training for non-Western contexts? How does the cultural composition of training data affect downstream fairness?

---

## Lecture 7: Recurrent Neural Networks, Sequence Modelling, and the Attention Revolution

Recurrent neural networks process sequential data via hidden state hₜ = f(Wₕₕh_{t−1}+Wₓₕxₜ+bₕ), maintaining a compressed summary of past inputs. Vanilla RNNs suffer from the vanishing gradient problem: in long sequences, gradients either vanish (making early inputs invisible to updates) or explode (causing instability). Gradient clipping (thresholding at a maximum norm) prevents explosion; LSTM and GRU architectures address vanishing. The **LSTM** (Hochreiter & Schmidhuber, 1997) introduces three gates and a cell state: the forget gate fₜ = σ(Wf·[h_{t−1},xₜ]+bf) decides what to discard, the input gate iₜ = σ(Wi·[h_{t−1},xₜ]+bi) decides what to store, and the output gate oₜ = σ(Wo·[h_{t−1},xₜ]+bo) decides what to emit. The cell state cₜ = fₜ⊙c_{t−1}+iₜ⊙tanh(Wc·[h_{t−1},xₜ]+bc) provides an unobstructed gradient pathway (the additive identity preserves gradients), enabling memory over hundreds of time steps. The **GRU** (Cho et al., 2014) simplifies with ~25% fewer parameters by merging the forget and input gates into an update gate and dispensing with the separate cell state.

Bidirectional RNNs process both directions: hₜ = [→hₜ;←hₜ], enabling context from both past and future. Sequence-to-sequence models (Sutskever et al., 2014) encode an input sequence into a fixed-length vector and decode it into an output sequence. The bottleneck of compressing variable-length input into a single vector motivated **attention** (Bahdanau et al., 2015): instead of using the final hidden state, let the decoder query all encoder hidden states, weighting each by relevance to the current decoding step. Attention scores are computed as eₜᵢ = a(sₜ₋₁, hᵢ) and normalised as αₜᵢ = softmax(eₜᵢ), producing a context vector cₜ = Σᵢαₜᵢhᵢ that dynamically focuses on the most relevant encoder states.

**Transformers** (Vaswani et al., 2017) eliminate recurrence entirely, replacing it with self-attention: Attention(Q,K,V) = softmax(QKᵀ/√dₖ)V, where Q=XW_Q, K=XW_K, V=XW_V are learned projections of the input. Multi-head attention runs h parallel attention heads with different projection matrices, concatenating and projecting the results: MultiHead(Q,K,V) = Concat(head₁,...,headₕ)W_O where headᵢ = Attention(QWᵢ_Q, KWᵢ_K, VWᵢ_V). Position-wise feed-forward networks (FFN(x) = max(0, xW₁+b₁)W₂+b₂ with inner dimension 4×d), layer normalisation, and sinusoidal (or learned) positional encodings complete the architecture. The encoder applies self-attention over the full input; the decoder uses masked self-attention (preventing future leakage) and cross-attention to the encoder output.

The computational cost of self-attention is O(n²d) for sequence length n and model dimension d, creating a fundamental bottleneck for long sequences. Efficient attention variants in 2040 include: **Sparse attention** (allowing each position to attend to only a subset), **Linear attention** (approximating softmax with kernel methods to achieve O(nd²)), **Flash Attention** (Dao et al., 2022, tiling the attention computation for optimal GPU memory access, reducing memory from O(n²) to O(n)), and **State-space models** (Gu et al., 2022, maintaining a learned continuous state that provides O(n) inference with competitive quality). The Mimir Research Cluster runs Transformer and state-space model experiments on the Huginn-8B language model, giving students hands-on experience with billion-parameter architectures.

**Required Reading:**
- Hochreiter & Schmidhuber, "Long Short-Term Memory," *Neural Computation* 9:8 (1997): 1735–1780
- Bahdanau, Cho & Bengio, "Neural Machine Translation by Jointly Learning to Align and Translate," *ICLR '15* (2015)
- Vaswani et al., "Attention Is All You Need," *NeurIPS '17* (2017): 5998–6008
- Dao et al., "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness," *NeurIPS '22* (2022)

**Discussion Questions:**
1. LSTMs still struggle with sequences exceeding 1,000 time steps. Why does the additive architecture not fully solve the vanishing gradient problem?
2. Self-attention is O(n²) while RNNs are O(n). Why have Transformers replaced RNNs despite this disadvantage? What does this tell us about the role of parallelisation in modern hardware?
3. How does neural attention relate to human cognitive attention? Is the analogy productive or misleading?

---

## Lecture 8: Unsupervised Learning — Clustering, Dimensionality Reduction, and the Geometry of Latent Spaces

Unsupervised learning discovers structure in unlabelled data, operating without explicit supervisory signals. **K-means** partitions n points into k clusters minimising within-cluster sum of squares: argmin_C Σⱼ=1ᵏ Σ_{xᵢ∈Cⱼ} ||xᵢ − μⱼ||², alternating between assignment (each point to its nearest centroid) and update (centroids to cluster means). It converges to local minima (not global, because the problem is NP-hard in general), is sensitive to initialisation (addressed by K-means++ which spreads initial centroids), and requires k a priori. The algorithm assumes spherical, equally sized clusters — violations degrade performance. **Hierarchical clustering** builds dendrograms via agglomerative (bottom-up, merging closest clusters) or divisive (top-down, splitting clusters) strategies with various linkage criteria (single, complete, average, Ward's). Agglomerative clustering costs O(n²) time and space, producing a full dendrogram that reveals cluster structure at every granularity. **DBSCAN** (Ester et al., 1996) defines clusters as connected regions of high density, discovering arbitrarily shaped clusters and identifying noise points, but struggles with varying densities.

**Principal Component Analysis** finds orthogonal directions of maximum variance via eigendecomposition of the covariance matrix XXᵀ or SVD of centred X. The first k principal components minimise reconstruction error ||X − Xₖ||², providing the optimal linear dimensionality reduction. PCA is equivalent to finding the best k-dimensional affine subspace for the data — a spectral method with closed-form solutions. **t-SNE** (van der Maaten & Hinton, 2008) minimises KL divergence between probability distributions in high and low dimensions, excelling at visualising local cluster structure but distorting global geometry. **UMAP** (McInnes et al., 2020) preserves both local and global structure via fuzzy simplicial set approximation, is faster than t-SNE, and supports mapping new points to the embedding. Both are tools for exploration, not for downstream modelling — the non-linear embeddings they produce lack an inverse mapping (unlike PCA).

**Autoencoders** learn compressed representations through an encoder-decoder architecture trained to reconstruct input. The bottleneck dimension forces the model to capture the most essential features. **Variational autoencoders** (Kingma & Welling, 2014) add probabilistic interpretation: the encoder outputs Gaussian parameters μ(x) and σ(x), the latent z ~ N(μ(x), σ²(x)I) is sampled via the reparameterisation trick z = μ + σ⊙ε where ε ~ N(0,I), and training maximises the ELBO = E[log p(x|z)] − KL(q(z|x)||p(z)), balancing reconstruction quality against regularisation toward the prior. The prior enables generation: sampling z ~ N(0,I) and decoding produces novel samples. **β-VAE** (Higgins et al., 2017) weights the KL term by β > 1 to encourage disentangled representations where each latent dimension controls a single generative factor.

**GANs** (Goodfellow et al., 2014) pit a generator G against a discriminator D in a minimax game: min_G max_D V(D,G) = E_{x~p_data}[log D(x)] + E_{z~p_z}[log(1−D(G(z)))]. At equilibrium, G generates from p_data and D outputs ½ everywhere. Failure modes include mode collapse (G produces limited diversity), training instability (oscillating losses), and vanishing gradients (when D is too strong, G receives no gradient). **Wasserstein GANs** (Arjovsky et al., 2017) replace the JS divergence with the Wasserstein distance, providing meaningful gradients even when distributions don't overlap — at the cost of requiring Lipschitz continuity (enforced via weight clipping or gradient penalty). **Diffusion models** (Ho et al., 2020; Song et al., 2021) define a forward process that adds Gaussian noise over T steps and a reverse process that learns to denoise. A neural network predicts the noise (or equivalently the score function), and generation proceeds by starting from pure noise and iteratively denoising. Diffusion models are more stable than GANs (no adversarial dynamics), produce higher-quality and more diverse samples than VAEs, and are the foundation of state-of-the-art image/video generation in 2040. The mathematical framework unifies with score matching (Vincent, 2011), Langevin dynamics, and stochastic differential equations.

**Required Reading:**
- Goodfellow et al., "Generative Adversarial Nets," *NeurIPS '14* (2014): 2672–2680
- Kingma & Welling, "Auto-Encoding Variational Bayes," *ICLR '14* (2014)
- Ho, Jain & Abbeel, "Denoising Diffusion Probabilistic Models," *NeurIPS '20* (2020): 6840–6851
- Song et al., "Score-Based Generative Modeling through Stochastic Differential Equations," *ICLR '21* (2021)

**Discussion Questions:**
1. What are the limitations of k-means++ for choosing k, and what alternatives exist (silhouette score, gap statistic, BIC)? When is clustering fundamentally ill-posed?
2. GAN training is famously unstable. What theoretical insights explain this instability, and how do WGANs and spectral normalisation address it?
3. Why have diffusion models replaced GANs for image generation? What are diffusion models' disadvantages (latency, diversity control, intellectual property)?

---

## Lecture 9: Reinforcement Learning — Learning from Rewards in an Uncertain World

Reinforcement learning studies agents that learn from scalar rewards, balancing exploration (trying new actions to discover their consequences) and exploitation (choosing actions known to yield high rewards). The **MDP framework** defines (S, A, P, R, γ): states S, actions A, transition probabilities P(s'|s,a), rewards R(s,a), and discount factor γ ∈ [0,1]. The agent seeks a policy π maximising the expected discounted return V^π(s) = E[Σₜ γᵗRₜ|s₀=s]. The **value function** V^π(s) gives the expected return from state s under policy π, and the **action-value function** Q^π(s,a) gives the expected return from state s, taking action a, then following π. Both satisfy Bellman equations: V^π(s) = Σₐ π(a|s)Σ_{s'} P(s'|s,a)[R(s,a) + γV^π(s')], and Q^π(s,a) = Σ_{s'} P(s'|s,a)[R(s,a) + γΣ_{a'} π(a'|s')Q^π(s',a')]. The optimal value function V* maximises over all policies.

**Dynamic programming** solves MDPs when the model (P, R) is known. Policy iteration alternates between policy evaluation (computing V^π) and policy improvement (acting greedily with respect to V^π). Value iteration applies the Bellman optimality operator V*(s) = maxₐ Σ_{s'} P(s'|s,a)[R(s,a) + γV*(s')] until convergence. Asynchronous variants update states in any order, converging under the same conditions. These methods are model-based and computationally prohibitive for large state spaces (the "curse of dimensionality").

**Q-learning** (Watkins, 1989) is an off-policy TD algorithm that learns the optimal action-value function without knowing the model: Q(s,a) ← Q(s,a) + α[R + γmax_{a'}Q(s',a') − Q(s,a)]. It requires only experience tuples (s,a,r,s') and converges to Q* under standard stochastic approximation conditions. **DQN** (Mnih et al., 2015) extends Q-learning to high-dimensional states (raw pixels) via neural networks, stabilised by experience replay (storing transitions in a buffer and sampling mini-batches) and target networks (a separate network for computing targets, updated periodically). DQN achieved human-level performance on 29/49 Atari games, demonstrating that deep RL could learn directly from pixels. Double DQN (van Hasselt et al., 2016) addresses overestimation by decoupling action selection from action evaluation. Dueling DQN (Wang et al., 2016) separates state value and advantage streams.

**Policy gradient methods** learn π_θ directly. The policy gradient theorem (Sutton et al., 2000) establishes: ∇θJ(θ) = E[∇θlogπ_θ(a|s)·Q^π(s,a)]. **REINFORCE** (Williams, 1992) is the simplest algorithm, using Monte Carlo returns. Variance is reduced by baselines (subtracting a state-dependent value), advantage functions (A(s,a) = Q(s,a) − V(s)), and actor-critic methods (which learn both policy and value function). **PPO** (Schulman et al., 2017) constrains policy updates via clipping: L^CLIP(θ) = Ê[min(rₜ(θ)Âₜ, clip(rₜ(θ), 1−ε, 1+ε)Âₜ)], preventing destructively large updates. PPO is the default for RLHF (Reinforcement Learning from Human Feedback) training of large language models in 2040, where a reward model trained on human preferences guides the language model toward helpful, harmless, and honest outputs. On the Mimir Cluster, students implement tabular Q-learning, cart-pole balancing with DQN, and basic RLHF with a reward model on a small language model.

**Required Reading:**
- Sutton & Barto, *Reinforcement Learning: An Introduction* (2nd ed., 2018/2040), chs. 3–6, 8–9, 13
- Mnih et al., "Human-Level Control Through Deep Reinforcement Learning," *Nature* 518 (2015): 529–533
- Schulman et al., "Proximal Policy Optimization Algorithms," arXiv:1707.06347 (2017)
- Ouyang et al., "Training Language Models to Follow Instructions with Human Feedback," *NeurIPS '22* (2022)

**Discussion Questions:**
1. Q-learning is off-policy: it can learn the optimal policy while following a different (e.g., exploratory) policy. What are the advantages and dangers of off-policy learning?
2. Reward shaping (adding intermediate rewards) can accelerate learning but can also change the optimal policy. How does potential-based reward shaping avoid this problem?
3. RLHF trains large language models to be "helpful, harmless, and honest." What.reward hacking behaviours might emerge, and how can they be detected?

---

## Lecture 10: Generalisation, Regularisation, and the Science of Making Models Work

Generalisation — performing well on unseen data — is the central challenge of machine learning. A model that achieves zero training error but poor test error has overfit the idiosyncrasies of the training set. **Regularisation** encompasses all techniques that improve generalisation by constraining, perturbing, or augmenting the learning process. The classical taxonomy includes: explicit regularisation (penalties added to the loss, such as L₂ weight decay), implicit regularisation (side effects of algorithms like SGD that bias toward flat minima), and data regularisation (augmentation, dropout, noise injection).

**L₂ regularisation** (weight decay) adds λ||w||² to the loss, shrinking weights and producing smoother functions. **L₁ regularisation** adds λΣ|wⱼ|, promoting sparsity. **Elastic Net** combines both. For neural networks, weight decay interacts subtly with adaptive optimisers: AdamW (Loshchilov & Hutter, 2019) decouples weight decay from the gradient update (applying it directly to weights rather than through the loss), yielding better generalisation than L₂ regularisation with Adam. **Dropout** (Srivastava et al., 2014) randomly zeroes hidden units with probability p during training, forcing the network to learn redundant representations. At test time, all units are active and outputs are scaled by p. Dropout approximates model averaging over 2^n thinned networks and provides exponential regularisation.

**Data augmentation** is perhaps the most effective regulariser for vision and language tasks. Basic geometric augmentations (random crops, horizontal flips, colour jitter) expand the training distribution. **MixUp** (Zhang et al., 2018) creates virtual examples: x̃ = λxᵢ + (1−λ)xⱼ, ỹ = λyᵢ + (1−λ)yⱼ for λ ~ Beta(α,α). **CutMix** (Yun et al., 2019) replaces image patches. **RandAugment** (Cubuk et al., 2020) automates policy search. **Adversarial training** (Madry et al., 2018) augments with worst-case perturbations: min_θ E[max_{||δ||≤ε} L(θ, x+δ, y)], improving robustness at the cost of standard accuracy and computational expense. **Label smoothing** (Szegedy et al., 2016) replaces hard labels with soft targets: y_soft = (1−ε)y_hard + ε/K, preventing overconfident predictions and improving calibration.

**Early stopping** monitors validation loss and halts training when it begins to increase, selecting the model at the validation minimum. This implicitly regularises by limiting the number of gradient steps, and has a PAC-Bayesian guarantee (the number of epochs acts as a complexity parameter). **Batch normalisation** (Ioffe & Szegedy, 2015) normalises activations to zero mean and unit variance within each mini-batch, reducing internal covariate shift and allowing higher learning rates. However, BN also acts as an implicit regulariser (the noise from varying batch statistics prevents overfitting) and interacts poorly with small batches.

**Cross-validation** estimates generalisation error by partitioning data into k folds, training on k−1 and evaluating on the held-out fold, repeating for all folds. K-fold CV provides an unbiased estimate of generalisation error, but the variance of the estimate depends on k and sample size. Leave-one-out CV (k = n) is approximately unbiased but high-variance; k = 5 or 10 is standard practice. Bootstrap .632 estimates combine training error and leave-one-out error with theoretical corrections. **Hyperparameter optimisation** ranges from grid search (exhaustive but expensive) to random search (Bergstra & Bengio, 2012, more efficient for insensitive parameters) to Bayesian optimisation (sequential model-based optimisation using GP surrogates or Tree-Parzen Estimators). In 2040, multi-fidelity methods (Successive Halving, Hyperband, BOHB) allocate more resources to promising configurations, reducing total compute by orders of magnitude.

The theoretical understanding of generalisation in deep learning has evolved dramatically. Classical VC-dimension bounds predicted that networks with millions of parameters should overfit catastrophically — yet they don't. **Norm-based bounds** (Bartlett et al., 2017) show that generalisation depends on the norms of weight matrices, not the number of parameters. **PAC-Bayesian bounds** (McAllester, 1999) bound generalisation in terms of the KL divergence between the posterior and prior over weights. **Information-theoretic bounds** connect generalisation to the mutual information between the training data and the learned parameters. **The neural tangent kernel** (Jacot et al., 2018) shows that infinitely wide networks trained with gradient descent converge to kernel regression with a specific kernel determined by the architecture and initialisation — providing exact generalisation guarantees in the infinite-width limit. Each of these perspectives illuminates a different facet of the puzzle, and no single theory yet fully explains deep learning's empirical generalisation.

**Required Reading:**
- Goodfellow, Bengio & Courville, *Deep Learning* (2016/2040), ch. 7
- Zhang et al., "mixup: Beyond Empirical Risk Minimization," *ICLR '18* (2018)
- Bartlett et al., "Spectrally-Normalized Margin Bounds for Neural Networks," *NeurIPS '17* (2017)
- Jiang et al., "Fantastic Generalization Measures and Where to Find Them," *ICLR '20* (2020)

**Discussion Questions:**
1. Dropout approximates model averaging over an ensemble of 2^n thinned networks. Why is it effective despite being a crude approximation?
2. Classical theory predicts overfitting for over-parameterised networks, yet deep learning works. Which of the modern generalisation theories (norm-based, PAC-Bayesian, NTK) best explains this, and why?
3. Data augmentation creates "virtual" training examples. Is this altering the data distribution, the loss function, or the model's inductive bias? How does MixUp's linear interpolation change the answer?

---

## Lecture 11: Evaluation, Fairness, and Responsible Machine Learning

Model evaluation extends far beyond accuracy. **Precision** (TP/(TP+FP)) measures the fraction of positive predictions that are correct — critical when false positives are costly. **Recall** (TP/(TP+FN)) measures the fraction of actual positives that are detected — critical when false negatives are costly. **F1** (harmonic mean of precision and recall) balances both. **AUROC** (Area Under the Receiver Operating Characteristic) measures the tradeoff across all classification thresholds, providing a threshold-independent metric. **AUPRC** (Area Under the Precision-Recall Curve) is preferred for imbalanced datasets where the positive class is rare, because it is sensitive to performance on the minority class. **Confusion matrices** decompose errors by class, revealing patterns invisible to aggregate metrics. For regression, **MAE** is robust to outliers, **MSE** penalises large errors, and **R²** measures explained variance.

**Calibration** asks whether predicted probabilities reflect true frequencies: a model predicting 0.7 should be correct 70% of the time over many predictions. **Expected Calibration Error** (ECE) bins predictions by confidence and measures the average deviation between confidence and accuracy. **Reliability diagrams** visualise this per-bin. Temperature scaling (Platt, 1999) and isotonic regression recalibrate poorly calibrated models. In 2040, calibrated uncertainty is essential for high-stakes applications (medical diagnosis, autonomous driving, loan approval) where knowing *how confident* the model is matters as much as its prediction.

**Fairness** in machine learning is not a purely technical property — it requires contextual, normative judgment. **Demographic parity** requires equal positive prediction rates across groups: P(ŷ=1|A=a) = P(ŷ=1|A=b). **Equalised odds** requires equal true positive and false positive rates across groups: P(ŷ=1|Y=y,A=a) = P(ŷ=1|Y=y,A=b). **Predictive parity** requires equal precision across groups. **Individual fairness** requires that similar individuals (under a task-specific similarity metric) receive similar predictions. Chouldechova (2017) and Kleinberg et al. (2016) independently proved that these fairness criteria are mutually incompatible when base rates differ across groups — a fundamental impossibility result that forces explicit value judgments about which notion of fairness to prioritise. **Intersectional fairness** considers the compounding effects of multiple protected attributes.

**Algorithmic bias** arises from biased training data (historical discrimination encoded in labels), biased feature selection (proxy variables that correlate with protected attributes), and biased evaluation (metrics that don't capture harms to marginalised groups). Mitigation strategies include: pre-processing (reweighting, resampling, feature modification), in-processing (adversarial debiasing, fairness constraints in the loss function), and post-processing (threshold adjustment per group). The **fairness-accuracy tradeoff** is real but often overstated: debiasing methods frequently improve accuracy on minority groups without degrading overall accuracy. In 2040, the Yggdrasil Fairness Audit Toolkit provides automated auditing pipelines that evaluate models across multiple fairness metrics, intersectional subgroups, and distribution shifts — flagging disparities before deployment.

**Explainability** methods complement fairness by making model decisions interpretable. **LIME** (Ribeiro et al., 2016) fits local linear approximations to explain individual predictions. **SHAP** (Lundberg & Lee, 2017) provides globally consistent local explanations via Shapley values. **Counterfactual explanations** (Wachter et al., 2018) identify the smallest change to input features that would alter the prediction: "your loan would have been approved if your income were $5,000 higher." **Concept-based explanations** (Kim et al., 2018, TCAV) test whether high-level concepts (e.g., "striped patterns" or "professional settings") influence predictions. The European Union's AI Act (2024) mandates explainability for high-risk AI systems, making these methods not merely academic but legally required. At Yggdrasil, students audit real-world datasets (COMPAS recidivism, FICO credit scoring, medical imaging across demographic groups) using the Fairness Audit Toolkit, developing practical skills alongside theoretical understanding.

**Required Reading:**
- Barocas, Hardt & Narayanan, *Fairness and Machine Learning* (2019/2040), chs. 1–4, 7–8
- Chouldechova, "Fair Prediction with Disparate Impact," *Big Data* 5:2 (2017): 153–163
- Wachter et al., "Counterfactual Explanations Without Opening the Black Box," *Harvard Journal of Law & Technology* 31:2 (2018): 841–887
- Jiang et al., "Predicting the Generalization Gap in Deep Neural Networks," *NeurIPS '19* (2019)

**Discussion Questions:**
1. Demographic parity, equalised odds, and predictive parity are mutually incompatible when base rates differ. Which should we prioritise in criminal justice, hiring, and medical diagnosis, and why?
2. Is algorithmic bias primarily a data problem, a model problem, or a societal problem? How does the answer change the design of mitigation strategies?
3. Counterfactual explanations are intuitive but can be misleading. What are their limitations, and when are they genuinely helpful?

---

## Lecture 12: The Frontiers of Machine Learning — Foundation Models, Self-Supervised Learning, and the Architecture of Intelligence

The machine learning landscape of 2040 is dominated by **foundation models** — large-scale models pre-trained on massive datasets using self-supervised objectives, then adapted to downstream tasks via fine-tuning, prompting, or in-context learning. The term, coined by Bommasani et al. (2021), captures the shift from training specialist models for individual tasks to training general-purpose models that serve as the foundation for many applications. The **scaling laws** (Kaplan et al., 2020; Hoffmann et al., 2022) governing these models reveal smooth power-law relationships between model performance (cross-entropy loss), dataset size, and compute budget: L(N) ∝ N^{−α} for model parameters, L(D) ∝ D^{−β} for dataset size, and optimal allocation follows "Chinchilla scaling" — training a 70B parameter model on 1.5T tokens outperforms a 280B model on 300T tokens given the same compute. These laws have transformed model development from alchemy to engineering, enabling predictable performance improvements.

**Self-supervised learning** (SSL) generates supervisory signals from the data itself, eliminating the need for labelled datasets. In NLP, **masked language modelling** (Devlin et al., 2019, BERT) predicts randomly masked tokens, learning bidirectional representations. **Autoregressive language modelling** (Brown et al., 2020, GPT) predicts the next token, learning unidirectional but generative representations. **Prefix LM** (Raffel et al., 2020, T5) combines both. In vision, **contrastive learning** (Chen et al., 2020, SimCLR; He et al., 2020, MoCo) learns by pulling augmented views of the same image together and pushing different images apart. **Non-contrastive methods** (Grill et al., 2020, BYOL; Chen & He, 2021, DINO) avoid negative pairs through asymmetric architectures, stop-gradients, or centreing. **Masked image modelling** (He et al., 2022, MAE) applies the BERT principle to vision, predicting masked patches from visible ones.

**Reinforcement Learning from Human Feedback** (RLHF) aligns foundation models with human values and preferences. The pipeline: (1) train a reward model on human preference comparisons (given two outputs, which is better?); (2) optimise the policy (language model) using PPO to maximise the reward while staying close to the reference model via a KL penalty. **Direct Preference Optimisation** (DPO; Rafailov et al., 2023) eliminates the reward model entirely, directly optimising the policy from preference data using a closed-form solution to the KL-constrained reward maximisation problem. **Constitutional AI** (Bai et al., 2022) uses the model itself to generate critiques and revisions based on a set of principles (the "constitution"), reducing the need for human labour in the alignment process.

**Parameter-efficient fine-tuning** (PEFT) adapts foundation models to downstream tasks without updating all parameters. **LoRA** (Hu et al., 2022) adds low-rank matrices ΔW = BA where B ∈ ℝ^{d×r} and A ∈ ℝ^{r×k} with r ≪ d,k, reducing trainable parameters by 10,000× with negligible quality loss. **Adapter layers** insert small bottleneck modules between Transformer layers. **Prefix tuning** prepends trainable "virtual tokens" to the input. **Prompt tuning** learns continuous embeddings that condition the frozen model. In 2040, multi-task LoRA allows a single model to serve thousands of fine-tuned capabilities by loading the appropriate low-rank matrices at inference time.

The frontier challenges of 2040 include: **mechanistic interpretability** — reverse-engineering the computational circuits inside neural networks (Elhage et al., 2022; Olsson et al., 2022), identifying features, heads, and circuits that implement reasoning, induction, and retrieval; **scaling laws for reasoning** — determining whether current scaling laws hold for multi-step reasoning or whether new dimensions (chain-of-thought length, tool-use frequency) emerge; **compositional generalisation** — building models that systematically combine learned primitives to solve novel combinations (the "systematicity" challenge; Lake & Baroni, 2018); **causal representation learning** — learning representations that support causal, not merely correlational, reasoning (Schölkopf et al., 2021); and **efficiency** — making trillion-parameter models tractable through mixture-of-experts routing, speculative decoding, quantisation (4-bit, 2-bit, sub-1-bit), and hardware-software co-design. The Mimir Research Cluster is actively investigating these questions, with students contributing to open-source experiments on the Huginn-8B model family.

This course has traversed the arc from classical learning theory (PAC, VC dimension, bias-variance) through the algorithmic foundations (linear models, SVMs, ensemble methods) to the deep learning revolution (CNNs, RNNs, Transformers) and the modern era of foundation models, self-supervised learning, and alignment. The principles endure: generalisation requires inductive bias, data quality matters more than model size, and evaluation must be coupled with fairness and responsibility. The algorithms change — from perceptrons to Transformers — but the fundamental tension between expressiveness and tractability, between data and knowledge, between capability and safety, remains the defining challenge of our field.

**Required Reading:**
- Bommasani et al., "On the Opportunities and Risks of Foundation Models," arXiv:2108.07258 (2021)
- Hoffmann et al., "Training Compute-Optimal Large Language Models," arXiv:2203.15556 (2022)
- Ouyang et al., "Training Language Models to Follow Instructions with Human Feedback," *NeurIPS '22* (2022)
- Rafailov et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model," *NeurIPS '23* (2023)
- Elhage et al., "Transformer Circuits," Transformer Circuits Thread (2022–2040)

**Discussion Questions:**
1. Scaling laws suggest that performance improves smoothly with compute and data. Does this imply that "intelligence" is merely a matter of scale, or are there qualitative transitions that scaling laws fail to predict?
2. Self-supervised learning learns representations without labels. What are the limits of this paradigm — what kinds of knowledge cannot be extracted from self-supervised objectives alone?
3. RLHF aligns models with human preferences, but whose preferences? What governance structures should determine the "constitution" in Constitutional AI?

---

## Final Examination Preparation

The final examination for CS207 emphasises conceptual understanding, mathematical reasoning, and practical judgement. The format is choose 4 of 8 essay questions, with each response expected to demonstrate depth of understanding, mathematical precision where relevant, and critical reasoning about tradeoffs and limitations.

### Sample Essay Questions

1. **Generalisation in Over-Parameterised Models.** Classical statistical learning theory predicts that models with more parameters than training samples should overfit catastrophically. Describe the double descent phenomenon and explain at least three modern theoretical frameworks (norm-based, PAC-Bayesian, neural tangent kernel) that attempt to explain why deep networks generalise despite extreme over-parameterisation. Which framework do you find most compelling, and why?

2. **The Kernel-Neural Network Correspondence.** SVMs with RBF kernels and deep neural networks both learn nonlinear decision boundaries, but they differ fundamentally in how they construct feature spaces. Compare and contrast the inductive biases of kernel methods and neural networks. When would you prefer one over the other? Discuss the neural tangent kernel as a bridge between these paradigms.

3. **Ensemble Methods: Why Redundancy Works.** Random forests average over high-variance trees; gradient boosting sequentially corrects errors. Explain why ensembling reduces error in theory (bias-variance decomposition) and practice (competition results). What happens when ensemble members are correlated? How does SHAP provide post-hoc interpretability for ensembles, and what are its limitations?

4. **From Attention to Transformers.** Trace the evolution from recurrent hidden states (RNN, LSTM) through attention mechanisms (Bahdanau) to full self-attention (Transformer). What problem does each innovation solve? Why does self-attention outperform recurrence despite O(n²) complexity? Discuss at least two efficient attention approximations and their tradeoffs.

5. **Generative Models: VAEs, GANs, and Diffusion.** Compare the mathematical foundations, training dynamics, and output quality of variational autoencoders, generative adversarial networks, and diffusion models. Why have diffusion models become dominant for image generation in 2040? Under what circumstances would you still choose a VAE or GAN?

6. **Fairness impossibility and Practical Tradeoffs.** Prove or argue that demographic parity, equalised odds, and predictive parity cannot all hold simultaneously when base rates differ across groups. For each of three application domains (criminal justice, hiring, medical diagnosis), argue which fairness criterion should take priority and defend your choice with ethical reasoning.

7. **Reinforcement Learning from Human Feedback.** Describe the RLHF pipeline (SFT → reward model → PPO). What are the failure modes of RLHF (reward hacking, sycophancy, mode collapse)? How does Direct Preference Optimisation eliminate the reward model? Discuss the theoretical advantages and practical limitations of DPO compared to RLHF.

8. **Scaling Laws and the Future of ML.** Explain Kaplan et al.'s scaling laws and the Chinchilla paradigm shift. What do scaling laws predict about the capabilities of models trained with 100× more compute? What do they fail to predict? Argue for or against the proposition that "intelligence is primarily a function of scale — all that is needed is more data and more compute."

### Research Paper Prompt (Alternative to Essay Questions)

For students choosing the research paper option: select a recent result (2023–2040) in machine learning that challenges or extends a foundational concept from this course. Write a 15–20 page paper that: (a) clearly explains the original concept and its historical context; (b) presents the new result with mathematical detail; (c) analyses what assumptions the new result relaxes or strengthens; (d) discusses practical implications for the design of ML systems; and (e) identifies open questions. Acceptable topics include: mechanistic interpretability of specific Transformer circuits, conformal prediction and distribution-free uncertainty quantification, state-space models as alternatives to attention, multi-modal foundation models, or causal representation learning. Submit a one-paragraph proposal by Week 10.