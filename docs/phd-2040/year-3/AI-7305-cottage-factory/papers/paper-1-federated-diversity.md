# Why Federated Learning Needs Community Diversity

**AI-7305: Distributed AI as Community Infrastructure**
**Research Paper 1 | Author:** Runa Gridweaver Freyjasdottir
**Date:** Fall 2040

---

## Abstract

Standard approaches to federated learning treat non-IID data distributions across clients as a convergence challenge—a problem to be mitigated through regularization, proximal terms, and variance reduction. This paper argues that this framing is fundamentally misguided. In the context of community federated learning—where training nodes represent geographically and socially bounded communities—data diversity is not a bug but the essential feature that makes federation valuable. We present theoretical arguments and empirical evidence from the Nordic Municipal AI Network (NMAN), the Cascadia Bioregional Mesh (CBM), and the Zanzibar Coastal Learning Cooperative (ZCLC) demonstrating that: (1) federated models trained on diverse community data outperform both local-only models and centrally-aggregated models on community-specific tasks; (2) diversity-preserving aggregation strategies produce more robust models than size-proportional aggregation; and (3) the benefits of community diversity increase with the degree of heterogeneity across communities. We propose the Diversity-Preserving Aggregation (DPA) protocol as a standard for community federated learning and demonstrate its superiority to FedAvg across multiple domains and community configurations.

**Keywords:** federated learning, community AI, data diversity, aggregation strategies, non-IID data, cottage factory model

---

## 1. Introduction

The foundational assumption of centralized machine learning is that more data, drawn from a wider distribution, produces better models. This assumption drove the data-hungry practices of the 2020s—scraping the web, purchasing data brokers, extracting user behavior at scale—in pursuit of ever-larger, ever-more-general training datasets. The resulting models were impressive in their breadth, but they exhibited persistent pathologies: they performed best for users who resembled the statistical majority of the training data, they encoded biases that reflected the demographics and values of their data sources, and they failed unpredictably when deployed in contexts far from their training distribution.

Federated learning was proposed as a privacy-preserving alternative: train local models on local data and aggregate the learned parameters without sharing the data. But the federated learning literature, from McMahan et al. (2017) onward, inherited the centralized assumption that the goal of training is a single global model that performs well on average across all participants. Non-IID data distributions were treated as a convergence problem—something to be overcome through regularization (FedProx, Li et al., 2020), variance reduction (SCAFFOLD, Karimireddy et al., 2020), or adaptive aggregation (FedNova, Wang et al., 2020).

This paper argues that this framing is backwards. In community federated learning—where training nodes represent real communities with distinct populations, environments, and needs—data diversity across communities is the entire point of federation. A perfectly IID dataset across all communities would mean that every community has the same data distribution, which would eliminate the unique local knowledge that makes federation valuable. The goal is not to flatten diversity into uniformity but to leverage diversity for collective intelligence.

We draw on four years of operational data (2036–2040) from three federated networks comprising 237 community nodes serving approximately 3.2 million people across four continents. Our contributions are:

1. A theoretical framework for understanding community diversity as a feature rather than a bug in federated learning.
2. Empirical evidence that federated models trained on diverse community data outperform both local-only and centrally-aggregated models.
3. The Diversity-Preserving Aggregation (DPA) protocol, which outperforms FedAvg and its variants in community federated learning contexts.
4. Practical recommendations for designing federated systems that preserve and leverage community diversity.

---

## 2. Related Work

### 2.1 Federated Learning and Non-IID Data

The challenge of non-IID data in federated learning has been extensively studied. McMahan et al. (2017) observed that FedAvg converges more slowly on non-IID data and may converge to suboptimal solutions. Subsequent work proposed various mitigation strategies:

- **FedProx** (Li et al., 2020) adds a proximal term to the local objective, penalizing deviation from the global model. This reduces client drift but also reduces the model's ability to capture local distribution differences.
- **SCAFFOLD** (Karimireddy et al., 2020) uses control variates to correct for client drift, achieving faster convergence on non-IID data while preserving more local information than FedProx.
- **FedNova** (Wang et al., 2020) normalizes local updates by the number of local steps, addressing the objective inconsistency that arises from heterogeneous local optimization.
- **IFCA** (Ghosh et al., 2020) clusters clients by data distribution and learns separate models for each cluster, explicitly acknowledging that a single global model may not serve all clients.
- **FedPer** (Arivazhagan et al., 2020) and subsequent personalization approaches maintain shared backbone layers trained through federation and personalized head layers trained locally.

Our work builds on the personalization literature, particularly FedPer and its descendants, but argues that the personalization approach does not go far enough. Personalization preserves local adaptation but treats the backbone as a compromise that should be as universal as possible. We argue that even the backbone benefits from diversity-preserving aggregation, and we provide evidence that maximizing diversity in the aggregation step produces better backbones than standard averaging.

### 2.2 Fairness in Federated Learning

Recent work on fairness in federated learning (Mohri et al., 2019; Li et al., 2020; AbdulRashid et al., 2022) has highlighted that standard FedAvg produces models that are biased toward clients with larger datasets, which disproportionately represent majority populations. Proposed solutions include agnostic federated learning (Mohri et al., 2019), which minimizes the maximum loss across clients, and q-FFL (Li et al., 2020), which re-weights clients to prioritize those with higher losses.

This work aligns with ours in recognizing that proportional aggregation is unfair. However, the fairness literature still frames the problem in terms of individual clients pursuing individual objectives. Our community framework shifts the unit of analysis from individual clients to bounded communities, where the relevant question is not "does each client get a fair model?" but "does each community get a model that reflects its needs and values?"

### 2.3 Community and Cooperative AI

The community AI literature (Chen & Abara, 2035; Freyjasdottir, 2038; Lindström, 2034) provides the socio-technical context for our work. The Cottage Factory model, the Longhouse Protocol, and the governance frameworks developed by NMAN, CBM, and ZCLC establish that community federated learning is not just a technical architecture but a political and economic one. Our work provides the technical foundations that make this architecture effective.

---

## 3. Theoretical Framework

### 3.1 Community Data Distributions

Let us formalize the community federated learning problem. We have $K$ communities, each with a local data distribution $\mathcal{D}_k$. We define community diversity as:

$$\Delta(\mathcal{D}_1, ..., \mathcal{D}_K) = \frac{1}{K(K-1)} \sum_{i \neq j} d(\mathcal{D}_i, \mathcal{D}_j)$$

where $d(\cdot, \cdot)$ is a distributional distance metric (we use the Wasserstein distance in practice). $\Delta$ measures the average pairwise distance between community data distributions. Higher $\Delta$ indicates greater community diversity.

In standard federated learning, the goal is to find model parameters $\theta^*$ that minimize the weighted average loss:

$$\theta^* = \arg\min_\theta \sum_{k=1}^{K} \frac{n_k}{n} L_k(\theta)$$

where $n_k$ is the number of samples from community $k$, $n = \sum_k n_k$, and $L_k(\theta)$ is the loss on community $k$'s data. This is FedAvg's objective: it weights each community proportionally to its data contribution.

In community federated learning, we have a different objective. We want to find model parameters $\theta^*$ that, when combined with community-specific adaptation parameters $\phi_k$, minimize the adapted loss for each community:

$$\theta^*, \phi_1, ..., \phi_K = \arg\min_{\theta, \phi_1, ..., \phi_K} \sum_{k=1}^{K} w_k L_k(\theta, \phi_k)$$

where the weights $w_k$ are determined by the community governance process, not by data size. This is the Community-Adaptive Personalization (CAP) objective. The backbone $\theta$ is trained through federation; the adapters $\phi_k$ are trained locally.

### 3.2 Why Diversity Helps the Backbone

The intuition for why diversity helps the backbone is straightforward. Consider two extreme cases:

**Case 1: Maximum homogeneity ($\Delta \approx 0$).** All communities have the same data distribution. In this case, federation adds no value beyond what each community could achieve locally (given enough data). The backbone converges to the same solution that local training would produce, and the adapters have nothing to adapt to. Federation is pointless.

**Case 2: Maximum diversity ($\Delta$ is large).** Communities have very different data distributions. In this case, the backbone must learn features that generalize across diverse contexts—features that capture fundamental structure rather than spurious correlations specific to any single distribution. This produces a backbone that is more robust, more transferable, and better prepared for local adaptation.

This is analogous to the well-known result in supervised learning that training on diverse data produces better representations than training on homogeneous data—but here, the diversity is across communities, and the representation (backbone) is shared while the adaptation is local.

**Theorem 1 (Informal).** Under the CAP framework, the expected improvement from federation over local-only training increases with community diversity $\Delta$, up to a threshold beyond which the distributions are so different that a shared backbone provides diminishing returns.

We formalize this result in Appendix A, drawing on the representation learning theory of_tripathi et al. (2035). The intuition is that the backbone acts as a shared representation that encodes general-purpose features, while the adapters encode community-specific features. More diverse training data for the backbone produces a more general representation, which in turn makes the adapters more effective.

### 3.3 Diversity-Preserving Aggregation

Standard FedAvg aggregates model updates by weighting them proportionally to dataset size. In the community context, this means that larger communities dominate the global model, effectively creating a majority-weighted average. Small communities with unique data distributions are underrepresented, and the backbone captures majority patterns rather than general patterns.

We propose Diversity-Preserving Aggregation (DPA), which weights community updates using three factors:

**Quality weight** $q_k$: Measures the quality of community $k$'s local model, assessed through local validation metrics. Communities with higher-quality local updates are weighted more heavily. This ensures that well-trained, well-validated updates contribute more than noisy or poorly trained ones.

$$q_k = \frac{1}{1 + \text{val\_loss}_k}$$

**Sovereignty weight** $s_k$: A minimum representation threshold ensuring that every community has a voice in the aggregate, regardless of size. We set $s_k = \max(\alpha, n_k / n)$ where $\alpha$ is a sovereignty floor (typically 0.05, meaning even the smallest community receives at least 5% weight in the aggregate).

**Novelty weight** $v_k$: Measures how much new information community $k$'s update contributes relative to the current global model. Updates that diverge more from the current global model represent novel knowledge and are weighted more heavily.

$$v_k = 1 + \beta \cdot \|g_k - \bar{g}\|$$

where $g_k$ is community $k$'s gradient update, $\bar{g}$ is the mean update, and $\beta$ is a novelty scaling factor.

The combined DPA weight for community $k$ is:

$$w_k^{DPA} = \frac{q_k \cdot s_k \cdot v_k}{\sum_{j=1}^{K} q_j \cdot s_j \cdot v_j}$$

This weighting scheme ensures that every community is represented (sovereignty weight), that well-validated updates contribute more (quality weight), and that novel information is prioritized (novelty weight).

---

## 4. Empirical Evaluation

### 4.1 Datasets and Configuration

We evaluate DPA on three task domains, each with data from the NMAN, CBM, and ZCLC federations:

**Health Prediction.** Diagnostic decision support using electronic health records from 89 community clinics. Communities differ in disease prevalence, demographics, and healthcare access patterns.

**Agricultural Advisory.** Crop management recommendations using sensor and yield data from 64 farming communities. Communities differ in climate, soil type, crop varieties, and farming practices.

**Language Understanding.** Multi-language NLP tasks covering 12 languages across 147 communities. Communities differ in language, dialect, and cultural context.

For each domain, we compare four training strategies:

1. **Local only.** Each community trains only on its own data, no federation.
2. **FedAvg.** Standard federated averaging with proportional weights.
3. **FedProx.** Federated learning with proximal regularization.
4. **DPA (ours).** Diversity-Preserving Aggregation with CAP personalization.

All strategies use the CAP architecture: a shared backbone trained through federation and community-specific LoRA adapters trained locally. For the local-only baseline, the "backbone" is trained only on local data.

### 4.2 Results

#### 4.2.1 Health Prediction

| Strategy | Avg. Accuracy | Min. Community Acc. | Fairness Gap | Comm. Cost |
|----------|--------------|---------------------|--------------|------------|
| Local only | 78.3% | 62.1% | 16.2% | — |
| FedAvg | 83.7% | 68.4% | 15.3% | 1.0× |
| FedProx | 84.1% | 69.7% | 14.4% | 1.0× |
| **DPA** | **86.2%** | **74.8%** | **11.4%** | **1.2×** |

DPA outperforms all baselines on average accuracy, but the key result is the improvement in minimum community accuracy and fairness gap. The smallest and most unique communities—those that benefit most from federation—see the largest gains under DPA, while the largest communities see no significant degradation compared to FedAvg.

#### 4.2.2 Agricultural Advisory

| Strategy | Avg. F1 | Min. Community F1 | Fairness Gap | Comm. Cost |
|----------|---------|-------------------|--------------|------------|
| Local only | 0.71 | 0.52 | 0.19 | — |
| FedAvg | 0.78 | 0.61 | 0.17 | 1.0× |
| FedProx | 0.79 | 0.63 | 0.16 | 1.0× |
| **DPA** | **0.82** | **0.71** | **0.11** | **1.1×** |

Agricultural advisory shows the strongest diversity effect. Communities with unique crop varieties and soil conditions—which have the most to gain from federation and the most to lose from homogenization—benefit enormously from DPA's novelty weighting.

#### 4.2.3 Language Understanding

| Strategy | Avg. BLEU | Min. Community BLEU | Fairness Gap | Comm. Cost |
|----------|-----------|---------------------|--------------|------------|
| Local only | 34.2 | 18.7 | 15.5 | — |
| FedAvg | 39.8 | 24.3 | 15.5 | 1.0× |
| FedProx | 40.1 | 25.1 | 15.0 | 1.0× |
| **DPA** | **43.6** | **33.2** | **10.4** | **1.3×** |

Language understanding shows the largest absolute improvement from DPA, reflecting the fact that linguistic diversity is the most extreme form of distribution shift in our evaluation. Low-resource languages, which are barely represented in FedAvg's size-proportional weighting, receive adequate representation under DPA's sovereignty and novelty weights.

### 4.3 Diversity Analysis

To test our theoretical prediction that federation benefits increase with community diversity, we stratify the NMAN communities by their pairwise Wasserstein distance from the federation mean. Communities in the top quartile of diversity benefit 3.2× more from DPA federation than communities in the bottom quartile, confirming that diversity is the driving factor.

We also conduct an ablation study removing each of DPA's three weighting factors in turn:

- **Without sovereignty weight:** Minimum community accuracy drops by 4.3%, and fairness gap increases by 3.1%. Small communities are underrepresented.
- **Without quality weight:** Average accuracy drops by 1.2%, as noisy updates dilute the aggregate.
- **Without novelty weight:** Minimum community accuracy drops by 2.8%, as the backbone fails to capture distribution-specific features.

All three factors contribute to DPA's performance, but the sovereignty weight has the largest impact on fairness, and the novelty weight has the largest impact on minimum community accuracy.

### 4.4 Comparison with Centralized Training

For completeness, we compare DPA with a hypothetical centralized baseline that collects all community data in a single location and trains a single model. This baseline is not achievable in practice (due to data sovereignty constraints), but it provides a useful reference point.

| Strategy | Health Acc. | Agri. F1 | Language BLEU |
|----------|-------------|----------|---------------|
| Centralized (all data) | 84.9% | 0.80 | 41.2 |
| DPA (federated, no data sharing) | **86.2%** | **0.82** | **43.6** |

DPA outperforms the centralized baseline across all three domains. This is not because federated learning is inherently superior to centralized training—it is because the centralized model is a single model that must compromise across all communities, while DPA produces a shared backbone with community-specific adaptations. The personalization allows each community to get a model tailored to its specific distribution, while the shared backbone ensures that the tailoring builds on a robust, general-purpose representation.

---

## 5. Discussion

### 5.1 Federation Is Not Neutral

Our results demonstrate that the choice of aggregation strategy is not a neutral technical decision—it is a political one. FedAvg, by weighting communities proportionally to their data, effectively gives larger communities more influence over the shared backbone. This reproduces existing power imbalances within the federation, creating a backbone that serves majority populations better than minority ones.

DPA, by contrast, is designed with an explicit commitment to equity: every community is guaranteed minimum representation (sovereignty weight), well-validated knowledge is prioritized (quality weight), and novel information from underrepresented distributions is amplified (novelty weight). This commitment comes with a cost—slightly higher communication overhead (1.1-1.3× compared to FedAvg)—but produces models that are more accurate, more fair, and more robust.

### 5.2 Diversity as a Public Good

In addition to the technical benefits documented above, community diversity in federated learning serves a public good function. When a community contributes its unique data distribution to the federation, all communities benefit—from the novel information encoded in that community's gradients. The novelty weight in DPA explicitly incentivizes this contribution: communities with unusual data distributions receive higher weight, which means their updates contribute more to the backbone, which means the backbone becomes more robust to distributional shift.

This creates a virtuous cycle: diverse communities are valued for their diversity, which encourages participation, which increases diversity, which improves the backbone for everyone. The Longhouse Economy principle of reciprocal benefit is not just an aspiration—it is encoded in the aggregation algorithm.

### 5.3 Limitations

Our evaluation has several limitations. First, we have not tested DPA on the very largest scale models (billions of parameters) or on the most extreme distribution shifts (e.g., across entirely different modalities). Second, the communication cost of DPA, while modest, may be significant in bandwidth-constrained environments like ZCLC's low-connectivity nodes. Third, the sovereignty weight parameter $\alpha$ and the novelty scaling parameter $\beta$ require tuning, and inappropriate settings can degrade performance. We discuss these limitations and potential mitigations in Appendix B.

### 5.4 Future Directions

Three directions are particularly promising:

- **Adaptive sovereignty weighting** that adjusts $\alpha$ based on the observed fairness gap rather than fixing it a priori.
- **Hierarchical DPA** that applies diversity-preserving aggregation at multiple levels—within regional clusters first, then across clusters—reducing communication cost while preserving diversity benefits.
- **Cross-modal DPA** that extends the diversity framework to federations where communities contribute different modalities (text, images, sensor data) rather than different distributions of the same modality.

---

## 6. Conclusion

Community diversity is not a problem to be solved in federated learning. It is the reason federated learning exists. When communities train models on their own data, for their own needs, and share the learned parameters through carefully designed aggregation protocols, they produce better models than any of them could produce alone—and better models than a centralized system could produce by aggregating their data without their consent.

The Diversity-Preserving Aggregation protocol we propose in this paper is a concrete technical mechanism for realizing this principle. By weighting community contributions according to quality, sovereignty, and novelty rather than size, DPA ensures that the shared backbone of a federated model captures general features that are robust across diverse contexts, while community-specific adapters capture the local knowledge that makes each community's model distinctly useful.

Federation without diversity is centralization by another name. Federation with diversity is collective intelligence—and that is what the Cottage Factory model is built to produce.

---

## References

- AbdulRashid, I. et al. (2022). "On the Fairness of Federated Learning." *IEEE Transactions on Neural Networks*.
- Arivazhagan, M.G. et al. (2020). "Federated Learning with Personalization Layers." *NeurIPS*.
- Chen, W. & Abara, T. (2035). "Governance Protocols for Community-Owned Machine Learning Systems." *AI & Society*, 40(2).
- Freyjasdottir, R.G. (2038). *The Cottage Factory: Local AI for Local People*. New Commons Press.
- Ghosh, A. et al. (2020). "Robust Federated Learning in a Heterogeneous Environment." *ICML*.
- Karimireddy, S.P. et al. (2020). "SCAFFOLD: Stochastic Controlled Averaging for Federated Learning." *ICML*.
- Li, T. et al. (2020). "Federated Optimization in Heterogeneous Networks." *MLSys*.
- Li, T. et al. (2020). "Fair Resource Allocation in Federated Learning." *ICLR*.
- Lindström, E. (2034). *Solarpunk Data Centers: Designing for the Commons*. Nordic AI Press.
- McMahan, B. et al. (2017). "Communication-Efficient Learning of Deep Networks from Decelerated Data." *AISTATS*.
- Mohri, M. et al. (2019). "Agnostic Federated Learning." *ICML*.
- Nakamura, K. & Osei-Mensah, A. (2036). "Federated Diversity: Why Homogeneous Training Sets Undermine Community AI." *ACM FAccT*.
- Tripathi, S. et al. (2035). "Generalization in Representation Learning Through Distributional Diversity." *NeurIPS*.
- Wang, H. et al. (2020). "Tackling the Objective Inconsistency Problem in Heterogeneous Federated Optimization." *NeurIPS*.

---

## Appendix A: Formal Statement of Theorem 1

**Theorem 1.** Let $\mathcal{D}_1, ..., \mathcal{D}_K$ be community data distributions with diversity $\Delta$. Let $\theta^*$ be the backbone parameters learned through DPA with CAP personalization, and let $\theta_0$ be the backbone parameters learned through local-only training. Under standard regularity conditions (smooth loss functions, bounded gradients, Lipschitz continuity), the expected improvement in community-adapted loss from federation over local-only training satisfies:

$$\mathbb{E}\left[\sum_{k=1}^{K} w_k (L_k(\theta_0, \phi_k^0) - L_k(\theta^*, \phi_k^*))\right] \geq C_1 \cdot \Delta - C_2 \cdot \Delta^2$$

where $C_1, C_2$ are positive constants depending on the model architecture and learning rate, and the quadratic term captures the diminishing returns from extreme distribution shift.

*Proof sketch.* The proof proceeds in three steps: (1) showing that the DPA backbone converges to a representation that minimizes the weighted sum of community-adapted losses; (2) bounding the representation quality improvement from diverse training data using information-theoretic arguments; and (3) showing that the novelty weight in DPA ensures that the backbone's representation capacity is allocated proportionally to distributional diversity rather than data volume. See the supplementary material for the full proof.

## Appendix B: Practical Deployment Considerations

### B.1 Bandwidth-Constrained Environments

In low-bandwidth environments (e.g., ZCLC's coastal nodes with intermittent mobile connectivity), the 1.1-1.3× communication overhead of DPA may be significant. We recommend two mitigations:

- **Gradient compression.** Using top-k sparsification with k=0.01 reduces communication by 100× with minimal quality impact, as demonstrated in the ZCLC deployment.
- **Asynchronous DPA.** Allowing communities to submit updates on their own schedule (rather than synchronously) slightly increases convergence time but dramatically reduces peak bandwidth requirements.

### B.2 Parameter Tuning

The sovereignty floor $\alpha$ and novelty scaling $\beta$ should be set through community governance, not by the technical team alone. We recommend:

- $\alpha$ should be set such that no community receives less than a threshold weight (we recommend 5% for federations of 10-50 communities and 2% for larger federations).
- $\beta$ should be set through cross-validation on held-out community data during initial federation setup, then reviewed quarterly by the Community AI Council.

### B.3 Cold Start

New communities joining an established federation face a cold start problem: their initial models may be too different from the current backbone to benefit from federation. We recommend a warm-up period of 2-4 weeks during which the new community trains locally, using the existing backbone as initialization, before contributing to DPA aggregation.