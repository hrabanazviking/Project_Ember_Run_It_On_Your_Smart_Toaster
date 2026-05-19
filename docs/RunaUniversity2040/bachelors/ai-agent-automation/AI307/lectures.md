# AI307: Edge Deployment & Model Optimization
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** AI201 (Deep Learning Foundations), AI205 (Agent Architecture Design)
**Description:** The cloud is not always available. The network is not always reliable. The latency is not always acceptable. Edge deployment — running AI models and agent systems on local devices rather than remote servers — is essential for applications that require real-time response, operate in disconnected environments, or must keep data local for privacy. This course covers the full pipeline of deploying AI models to edge devices: model optimization (quantization, pruning, distillation), hardware-aware design (understanding the constraints of edge processors), inference frameworks (ONNX Runtime, TensorFlow Lite, Core ML), agent architectures for edge (frugal agents, on-device LLMs, hybrid cloud-edge), and the engineering challenges of maintaining and updating edge-deployed systems. Students will optimize, deploy, and maintain a complete agent system on a Raspberry Pi-class device, learning that the art of edge deployment is not making models smaller but making them *just small enough* while preserving the intelligence that makes them useful.

> *"The axe that fells the tree need not be heaviest — it need only be sharp enough."* — The edge model that runs on device need not be largest — it need only be smart enough.

---

## Lectures

### ᚠ Lecture 1: The Edge Imperative — Why the Cloud Is Not Enough

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The cloud revolution transformed computing. Organizations that once maintained server rooms moved their workloads to AWS, Azure, and GCP, gaining elasticity, scalability, and access to GPU clusters that no on-premises data center could match. The AI revolution was built on this cloud foundation — the massive language models of the 2020s and 2030s were trained on cloud GPU clusters and served from cloud data centers. The assumption was universal: if you need AI, you call the cloud.

But the cloud assumption has limits — and those limits are increasingly the places where AI matters most:

**Latency.** Cloud inference has round-trip latency: the data must travel from the device to the cloud, the model must process it, and the result must travel back. On a fast network, this takes 50–200ms for a single inference. But for real-time applications — autonomous driving (where 100ms can be the difference between a near-miss and a collision), surgical robotics (where 50ms can determine the success of a procedure), and industrial control (where 10ms is the control loop for a manufacturing line) — cloud latency is unacceptable. The edge, by contrast, can process inference in 1–10ms on local hardware, enabling real-time response that the cloud simply cannot provide.

**Connectivity.** Not all environments have reliable internet connectivity. A ship at sea, a drone over the Arctic, a mining operation underground, an agricultural sensor in a remote valley, a military unit in a communications-denied environment — these are not edge cases; they are the cases where AI augmentation is most valuable. An agent system that ceases to function without cloud connectivity is a liability in these environments, not an asset. Edge-deployed models continue to function regardless of network availability.

**Privacy.** Data processed in the cloud traverses networks and resides on servers the data owner does not control. For many applications — medical diagnosis, legal review, personal assistance, intelligence analysis — sending data to the cloud is prohibited by regulation, policy, or user preference. Edge deployment keeps data on the device, under the user's control, compliant with GDPR, HIPAA, and other data sovereignty requirements. The 2040 regulatory environment has tightened significantly: the EU AI Act, China's Personal Information Protection Law, and the US AI Accountability Act all impose strict data residency requirements that make cloud processing of sensitive data increasingly difficult.

**Cost.** Cloud inference is priced per token and per GPU-hour. An agent system that makes 100 inference calls per minute over a 24-hour period costs $50–500/day on cloud GPUs. The same system running on a $200 edge device costs $0/day after the initial hardware purchase. For applications with high inference volume and long deployment lifetimes, the cost savings of edge deployment are substantial.

**Sovereignty.** In an era where AI capabilities are strategic assets, dependency on cloud providers creates sovereignty risks. An organization whose AI capabilities can be disabled by a cloud provider's outage, pricing change, or policy decision is not sovereign. Edge deployment gives the organization control over its own AI infrastructure, independent of external providers.

The **edge imperative** — the growing recognition that cloud-only AI is insufficient — is driving a paradigm shift in AI engineering. The 2040 landscape is not cloud-or-edge; it is cloud-and-edge, with AI workloads distributed across the continuum from cloud data centers to edge devices. The engineering challenge is determining which workloads run where, how to optimize models for the edge, and how to coordinate cloud and edge systems to deliver the best user experience.

The Norse concept of **heimr** — the world, the home, the place where one dwells — captures the edge imperative. The cloud is like Valhalla: powerful, well-provisioned, and always available to those who can reach it. But most of the world is not Valhalla. Most of the world is Miðgarðr — the middle ground, the place where people live, the place where decisions need to be made in real time with whatever resources are at hand. An AI that only works in Valhalla is an AI that does not work in Miðgarðr. The edge imperative is the demand that AI work in Miðgarðr — on the ship, in the field, underground, on the device — not just in the data center.

**Key Topics:**

- The cloud assumption and its limits: latency, connectivity, privacy, cost, sovereignty
- Latency-critical applications: autonomous driving, surgical robotics, industrial control
- Connectivity-denied environments: ships, drones, mines, remote agriculture, military
- Privacy and data sovereignty: GDPR, HIPAA, EU AI Act, data residency requirements
- Cost comparison: cloud vs. edge for high-volume, long-lifetime deployments
- The cloud-edge continuum: distributed AI workloads, not cloud-or-edge but cloud-and-edge
- Heimr: AI that works in Miðgarðr, not just in Valhalla

**Required Reading:**

- Shi, W. et al. "Edge Computing: Vision and Challenges" (2016), *Mobile Networks and Applications*
- Zhou, Z. et al. "Edge Intelligence: Paving the Last Mile of Artificial Intelligence with Edge Computing" (2019), *Proceedings of the IEEE*
- University of Yggdrasil TR: "The Heimr Architecture: Edge-First AI for Connectivity-Denied Environments" (2040)

**Discussion Questions:**

1. The cloud provides virtually unlimited compute; the edge provides limited but immediate compute. How should an agent system decide which computations to perform on the edge (low latency, limited power) and which to offload to the cloud (high latency, abundant power)? Design a decision framework that accounts for latency requirements, connectivity availability, privacy constraints, and compute budget.
2. Privacy is often cited as a reason for edge deployment, but edge devices are also vulnerable — they can be stolen, physically tampered with, or compromised through side channels. Is edge deployment actually more private than cloud deployment, or does it just shift the attack surface? Under what conditions is edge deployment the privacy-preferred option?
3. Heimr — the world where one dwells — suggests that the "right place" for computation is where the user is, not where the data center is. But what if the user is in a place with good connectivity and no privacy constraints? Is there still a reason to deploy on the edge in such environments, or is the edge imperative only relevant for environments with poor connectivity or strict privacy requirements?

---

### ᚢ Lecture 2: Model Quantization — Sharpening the Axe

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A large language model like GPT-7 (175B parameters) requires approximately 350GB of memory in its native FP32 (32-bit floating-point) representation. Even a smaller model like Llama-3-8B requires 32GB in FP32. An edge device — a Raspberry Pi 6, a Jetson Orin Nano, a Snapdragon X Elite laptop — typically has 8–16GB of shared CPU/GPU memory. The model cannot fit. **Quantization** is the art of reducing the memory footprint and computational cost of a neural network by representing its weights and activations with fewer bits, without (or with minimal) loss of accuracy.

The fundamental insight of quantization is that neural networks are **over-parameterized** — they contain far more numerical precision than they need. A weight of 0.00031415926 stored in FP32 uses 32 bits to represent a value that is, for practical purposes, equivalent to 0.00031 stored in 8 bits (INT8 quantization). The extra precision is wasted on noise that the network cannot use and does not need. Quantization compresses the model by reducing this wasted precision, trading a small amount of information for a large reduction in memory and compute.

**Quantization levels.** The 2040 quantization landscape offers several precision levels:

**FP32** (32-bit floating point): The baseline. Every weight and activation is stored as a 32-bit floating-point number. Highest accuracy, highest memory and compute cost. Used only in training and in inference on high-end data center GPUs.

**FP16 / BF16** (16-bit floating point): Half-precision. FP16 uses 5 exponent bits and 10 mantissa bits; BF16 uses 8 exponent bits and 7 mantissa bits. BF16 has a wider dynamic range (matching FP32's exponent range) but lower precision in the mantissa. Most modern GPU inference uses BF16 or FP16. Memory and compute are halved compared to FP32. Accuracy loss is negligible for most models.

**INT8** (8-bit integer): The workhorse of edge inference. Every weight and activation is stored as an 8-bit integer. Memory and compute are reduced by 4x compared to FP32 (and by 2x compared to FP16). Accuracy loss is typically less than 1% for well-quantized models, though outlier weights and activations can cause larger degradations if not handled carefully.

**INT4** (4-bit integer): Aggressive quantization for maximum compression. Memory is reduced by 8x compared to FP32. Accuracy loss is more significant — typically 1–5% for language models, depending on the quantization method. INT4 quantization requires sophisticated techniques (GPTQ, AWQ, or the University of Yggdrasil's Greið-method) to preserve accuracy.

**Mixed-precision** quantization uses different precision levels for different parts of the model. The first and last layers of a language model, which tend to be more sensitive to quantization error, may be kept in FP16 or INT8, while the middle layers are quantized to INT4. Mixed-precision quantization achieves near-INT4 memory savings with near-INT8 accuracy.

**Quantization methods.** The choice of quantization method matters as much as the choice of precision level:

**Post-training quantization (PTQ)** quantizes a pre-trained model without retraining. PTQ is fast, simple, and requires no training data. It works by collecting calibration data (a small set of representative inputs), running it through the FP32 model, recording the range of activations at each layer, and then mapping the FP32 weights and activations to the target integer range using the recorded ranges. PTQ is the default method for INT8 and is effective for BF16 and FP16. For INT4, PTQ can be more challenging because the reduced precision makes the quantization mapping more sensitive to the calibration data.

**Quantization-aware training (QAT)** trains the model with quantization effects simulated during the forward pass. The model learns to account for the information loss that quantization will introduce, producing weights that are more robust to quantization. QAT produces higher-accuracy quantized models than PTQ, especially at aggressive precision levels (INT4, INT3), but it requires a full training run with quantization simulation, which is computationally expensive and requires training data and infrastructure.

**GPTQ** (Frantar et al., 2023) is an advanced PTQ method for language models that uses approximate second-order information (the Hessian of the layer-wise reconstruction error) to determine the optimal quantization for each weight. GPTQ分组量化weights in small groups and adjusts the unquantized weights to compensate for the quantization error, producing INT4 and INT3 models with remarkably low accuracy loss. By 2040, GPTQ and its successors have become the standard for aggressive model quantization.

**AWQ** (Activation-Aware Weight Quantization, Lin et al., 2023) observes that not all weights are equally important — a small percentage of "salient" weights (those that correspond to large activations) disproportionately affect model quality. AWQ protects these salient weights by quantizing them at higher precision or applying per-channel scaling to reduce their quantization error, while aggressively quantizing the remaining weights. AWQ achieves INT4 accuracy that approaches INT8 by allocating precision where it matters most.

**The Greið-method** (University of Yggdrasil, 2040) is a novel quantization approach inspired by the Norse concept of **greiði** — the craft of making things fit, of adjusting and shaping until the work is right. The Greið-method combines activation-aware weight quantization with layer-wise mixed-precision selection and context-dependent calibration. Rather than applying a single quantization scheme to the entire model, the Greið-method analyzes each layer's sensitivity to quantization error and selects the optimal precision level for that layer, producing models where sensitive layers retain higher precision while robust layers are aggressively quantized. The result is a quantized model that is, bit-for-bit, more accurate than uniform-precision alternatives.

The Greið-method also introduces **context-dependent calibration**: using calibration data that matches the deployment context. A model deployed for code generation uses code-heavy calibration data; a model deployed for conversation uses dialogue-heavy calibration data. Context-dependent calibration ensures that the quantization mapping preserves accuracy for the specific distribution of activations the model will encounter in production, rather than optimizing for a general distribution that may not match the deployment context.

**Quantization trade-offs.** The fundamental trade-off of quantization is accuracy vs. efficiency. Lower precision means less memory, faster inference, and lower power consumption — but also less information per weight, which means lower accuracy. The art of quantization is finding the "just small enough" point — the lowest precision at which the model retains acceptable accuracy for the application.

The trade-off is not uniform across applications. A code-generation model that must produce syntactically correct code is more sensitive to quantization error than a retrieval model that must produce approximately relevant results. A conversational agent that must maintain coherence across long conversations is more sensitive to accumulated quantization error than a single-turn QA model. The edge deployment engineer must understand the application's accuracy requirements and choose the quantization level accordingly.

The Norse metaphor of **sharpening the axe** captures the quantization impulse perfectly. The axe that fells the tree need not be heaviest — it need only be sharp enough. A 32-bit weight is a heavy axe; a 4-bit weight is a sharp axe. The heavy axe has more material, but the sharp axe cuts more efficiently because every bit of its material is in the right place. Quantization is the art of making the model sharper, not smaller — finding the precision at which every bit contributes to accuracy, and discarding the rest.

**Key Topics:**

- Quantization overview: reducing precision to reduce memory and compute
- Precision levels: FP32, FP16/BF16, INT8, INT4, mixed-precision
- Post-training quantization (PTQ): fast, simple, adequate for INT8
- Quantization-aware training (QAT): more accurate, requires retraining
- Advanced methods: GPTQ, AWQ, the Greið-method
- Context-dependent calibration: matching calibration data to deployment context
- Quantization trade-offs: accuracy vs. efficiency, application-specific requirements
- Sharpening the axe: making the model just sharp enough, not just small enough

**Required Reading:**

- Frantar, E. et al. "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers" (2023), *ICLR*
- Lin, J. et al. "AWQ: Activation-Aware Weight Quantization for LLM Compression and Acceleration" (2023), *MLSys*
- University of Yggdrasil TR: "Greið: Context-Dependent Mixed-Precision Quantization for Edge-Deployed Language Models" (2040)

**Discussion Questions:**

1. The Greið-method uses context-dependent calibration — matching the calibration data to the deployment context. But what if the deployment context changes? A model quantized for code generation is deployed for conversation. Does the quantization degrade, and if so, how should the edge system handle context shifts that were not anticipated during quantization?
2. INT4 quantization achieves 8x memory reduction over FP32 — but at what cost? Is there a "quantization floor" below which further precision reduction produces unacceptable accuracy loss regardless of the method? What determines this floor — the model architecture, the task, or the data distribution?
3. Sharpening the axe implies that there is an optimal point where the axe is sharp enough but not over-sharpened (which makes the edge brittle). What is the analogous "brittle point" in quantization — the precision level below which quantization error starts to compound catastrophically rather than degrade gracefully?

---

### ᚦ Lecture 3: Pruning, Sparsity, and Structured Compression — Carving the Runestone

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Quantization reduces the precision of each weight. **Pruning** reduces the number of weights entirely. A neural network with 175 billion parameters contains only a fraction of "useful" parameters — the rest are redundant, near-zero, or functionally equivalent to other weights. Pruning identifies and removes these redundant weights, producing a smaller, faster model that retains most of the original's accuracy.

The theoretical foundation for pruning is the **lottery ticket hypothesis** (Frankle & Carlin, 2019): within any randomly-initialized neural network, there exists a sparse subnetwork — a "winning ticket" — that, when trained in isolation, achieves comparable accuracy to the full network. The winning ticket is hidden among the full network's parameters, and training the full network essentially discovers it. Pruning is the art of finding the winning ticket — or, more practically, of removing the parameters that are not part of the winning ticket.

**Unstructured pruning** removes individual weights, wherever they are in the network, based on their magnitude or importance. A weight with a value close to zero contributes little to the output and can be removed with minimal impact. Unstructured pruning produces a **sparse model** — a model where many weights are zero — that can be stored in compressed form (storing only the non-zero weights and their indices) and computed efficiently using sparse matrix operations. The compression ratio of unstructured pruning can be extreme: a 95% sparse model stores only 5% of the original weights.

But unstructured pruning has a significant practical limitation: **sparse computation is inefficient on modern hardware**. GPUs and TPUs are designed for dense matrix multiplication — they achieve high throughput by processing matrices in contiguous blocks. Sparse matrices, with their irregular patterns of non-zero elements, cannot be processed efficiently on hardware optimized for dense operations. A 95% sparse model that requires only 5% of the memory may require 50% or more of the compute, because the hardware cannot efficiently skip the zero elements. This is the **sparse computing gap**: the gap between the theoretical savings of sparsity and the practical savings achievable on current hardware.

**Structured pruning** addresses the sparse computing gap by removing entire structures — neurons, attention heads, layers — rather than individual weights. Structured pruning produces a **dense but smaller model** that can be computed efficiently on standard hardware. Removing an entire attention head from a transformer eliminates 64 × (d_model) parameters and the corresponding computation, with no sparse overhead. Removing an entire MLP neuron eliminates d_model parameters and computation. Structured pruning achieves lower compression ratios than unstructured pruning (you can't remove 95% of the attention heads without severe accuracy loss), but the practical speedups are often greater because the resulting model is dense and hardware-friendly.

The 2040 pruning landscape offers several approaches:

**Magnitude pruning.** The simplest method: remove the weights with the smallest absolute value. Magnitude pruning assumes that small weights contribute little to the output. This assumption is approximately true but can fail — some small weights are critical for specific features, and removing them causes disproportionate accuracy loss. Magnitude pruning is fast, simple, and requires no training data, making it suitable for post-training pruning.

**Gradient-based pruning.** Remove the weights whose removal causes the smallest increase in the loss function, as estimated by the gradient. Gradient-based pruning uses the Taylor expansion of the loss function to approximate the impact of removing each weight, pruning those with the smallest estimated impact. Gradient-based pruning is more accurate than magnitude pruning (it directly measures impact on the loss) but requires a forward and backward pass through the model, making it more expensive.

**Attention head pruning.** A transformer-specific structured pruning method: remove entire attention heads that contribute least to the model's output. Research (Michel et al., 2019) showed that many attention heads in transformer models can be removed with minimal accuracy impact — some heads are "redundant" and can be pruned without retraining. Attention head pruning is particularly effective for language models, where the attention mechanism is the primary computational bottleneck.

**Layer dropping.** A radical structured pruning method: remove entire layers from the model. Research (Fan et al., 2020) showed that dropping alternating layers from a transformer has a surprisingly small impact on accuracy, because adjacent layers often learn similar features and can partially compensate for each other's removal. Layer dropping achieves the most aggressive compression (removing N layers reduces the model size by N/d_ratio) but also the largest accuracy impact and is best suited for models with significant redundancy in their layer representations.

**The runestone metaphor.** Pruning a neural network is like carving a runestone from a rough block of granite. The raw granite contains the runestone within it — every line, every curve, every rune — but it is buried in excess material. The carver's art is not adding material but removing it: chiseling away the excess to reveal the pattern underneath. The unstructured pruner is a fine chisel, removing individual grains of granite to reveal the fine details of the runes. The structured pruner is a coarse chisel, removing entire sections of granite to reveal the major shapes. Both produce the same runestone, but the coarse chisel is faster (it removes more material per stroke) and the fine chisel is more precise (it preserves detail that the coarse chisel would destroy). The art of pruning is knowing when to use which chisel — and when the runestone is sharp enough.

**Key Topics:**

- Pruning overview: removing redundant weights to reduce model size and compute
- The lottery ticket hypothesis: sparse subnetworks that match full-network accuracy
- Unstructured pruning: individual weight removal, sparse models, the sparse computing gap
- Structured pruning: removing neurons, heads, layers — dense but smaller models
- Magnitude pruning, gradient-based pruning, attention head pruning, layer dropping
- The runestone metaphor: chiseling away excess to reveal the pattern

**Required Reading:**

- Frankle, J. & Carlin, M. "The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks" (2019), *ICLR*
- Michel, P. et al. "Are Sixteen Heads Really Better than One?" (2019), *ICLR*
- Fan, A. et al. "Reducing Transformer Depth on Demand with Structured Dropout" (2020), *ICLR*
- University of Yggdrasil TR: "Runestone Pruning: Structured Compression for Edge-Deployed Transformers" (2040)

**Discussion Questions:**

1. The lottery ticket hypothesis suggests that sparse subnetworks exist within trained models that match full-network accuracy. But finding the winning ticket requires training the full network first, then pruning it. If we could find the winning ticket before training, we could train only that subnetwork — achieving massive training savings. Why is finding the winning ticket before training so difficult? Is it fundamentally harder than finding it after training?
2. The sparse computing gap means that unstructured pruning's theoretical savings don't translate to practical speedups on current hardware. Should the hardware be redesigned to support sparse computation efficiently, or should pruning methods be redesigned to produce dense-efficient structures? What would hardware that natively supports sparse computation look like?
3. Layer dropping achieves aggressive compression by removing entire transformer layers. But adjacent layers often learn different features — layer 5 might learn local syntax while layer 6 learns discourse structure. Removing layer 5 might not affect syntactic performance much (other layers can compensate), but it might affect features that layer 6 depends on. How should we evaluate whether a layer is truly redundant and can be safely dropped?

---

### ᚬ Lecture 4: Knowledge Distillation — The Apprentice Learns from the Master

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Quantization and pruning make an existing model smaller and faster. **Knowledge distillation** takes a different approach: instead of compressing a large model, it trains a small model to mimic the large model's behavior. The large model is the **teacher** — a large, accurate, but computationally expensive model that runs in the cloud. The small model is the **student** — a compact, efficient model that can run on the edge. The student learns not from the raw training data but from the teacher's outputs, which contain the teacher's knowledge in a form that is easier for the student to learn.

The key insight of knowledge distillation, introduced by Hinton, Vinyals, and Dean (2015), is that the teacher's **soft labels** — its probability distribution over all classes — contain more information than the **hard labels** — the single correct class provided by the training data. Consider a teacher model classifying an image: the hard label says "this is a cat," but the soft labels might say "this is a cat with probability 0.85, a dog with probability 0.10, a rabbit with probability 0.04, and a fox with probability 0.01." The soft labels encode the teacher's knowledge that the image is most likely a cat, but it also looks somewhat like a dog and a little like a rabbit. This "dark knowledge" — the relationships between classes that the teacher has learned — is far more informative than the hard label alone.

**The distillation process.** Knowledge distillation works as follows:

1. **Train the teacher model** on the training data using standard methods. The teacher is typically a large model (e.g., a 70B-parameter transformer) that achieves high accuracy but is too large for edge deployment.

2. **Generate teacher outputs** for the training data (and optionally for additional augmented data). The teacher's outputs include the soft probability distribution over all classes, not just the predicted class.

3. **Train the student model** using a combined loss function: (a) the **distillation loss**, which measures the difference between the student's soft output distribution and the teacher's soft output distribution, typically using Kullback-Leibler (KL) divergence, and (b) the **student loss**, which measures the difference between the student's output and the hard labels, typically using cross-entropy. The combined loss is: L = α · L_distill + (1 - α) · L_student, where α is a hyperparameter that controls the balance between learning from the teacher and learning from the ground truth.

4. **Tune the temperature** parameter, which controls the "softness" of the teacher's output distribution. Higher temperature produces softer distributions (probabilities are more evenly spread across classes), which contain more dark knowledge but less information about the correct class. Lower temperature produces sharper distributions (probabilities are concentrated on the predicted class), which contain less dark knowledge but more signal about the correct answer. The optimal temperature depends on the student model's capacity and the difficulty of the task.

**Distillation for language models.** The 2040 state of knowledge distillation for language models has evolved significantly since Hinton et al.'s original formulation. Language models are not classifiers — they don't produce a probability distribution over a fixed set of classes — but autoregressive generators that produce a probability distribution over the vocabulary at each token. Distillation for language models uses several extensions:

**Logit-based distillation.** The student is trained to match the teacher's logit distribution at each token position. The distillation loss measures the KL divergence between the teacher's logit distribution and the student's logit distribution, temperature-scaled and softened. Logit-based distillation captures the teacher's uncertainty about each token and the relationships between tokens that the teacher considers plausible.

**Feature-based distillation.** The student is trained to match the teacher's intermediate representations — the hidden states at each layer — in addition to the output logits. Feature-based distillation transfers not just the teacher's output knowledge but its internal representations, which capture the teacher's understanding of the input at multiple levels of abstraction. Feature-based distillation is particularly effective when the student model has a similar architecture to the teacher (e.g., both are transformers) but fewer layers and smaller hidden dimensions.

**Progressive distillation.** The student is distilled from a sequence of teachers of decreasing size. A 70B teacher distills a 13B intermediate model; the 13B model distills a 3B student. Progressive distillation produces better results than direct distillation from 70B to 3B because the intermediate teacher's outputs are easier for the small student to learn — the distribution gap between 13B and 3B is smaller than the gap between 70B and 3B.

**Task-specific distillation.** The teacher is fine-tuned on the target task before distillation, and the student is distilled from the fine-tuned teacher. Task-specific distillation produces a student that is specialized for the target task and achieves higher task accuracy than a general-purpose student, at the cost of reduced performance on other tasks. For edge deployment, task-specific distillation is often preferred — the edge model needs to perform well on its specific task, not on every possible task.

**The Norse metaphor of apprenticeship.** Knowledge distillation is the digital equivalent of the Norse apprenticeship system — the **sveinakerfi** — in which a young craftsman learned not from books but from a master. The apprentice did not study the raw materials (the hard labels); he watched the master work and learned the master's technique, judgment, and implicit knowledge (the soft labels). The master blacksmith does not just tell the apprentice "make a sword" (hard label); he shows the apprentice how to hold the hammer, how to judge the temperature of the steel by its color, how to quench at the right moment — the dark knowledge that cannot be captured in a specification but can be observed in the master's work. The student model, like the apprentice, learns from observing the teacher's behavior, not from the raw data alone.

But the apprentice cannot learn everything the master knows. The apprentice's sword will never be quite as good as the master's — the apprentice's hammer stroke is less precise, the apprentice's judgment of temperature is less accurate, the apprentice's timing is less perfect. The same is true of knowledge distillation: the student model will never match the teacher's accuracy, but it can come remarkably close — a 3B student distilled from a 70B teacher can achieve 95–98% of the teacher's accuracy on the target task, at 1/20th of the computational cost.

**Key Topics:**

- Knowledge distillation: training a small model to mimic a large model's behavior
- Soft labels and dark knowledge: the teacher's probability distribution as a richer training signal
- The distillation process: teacher training, output generation, student training with combined loss
- Temperature scaling: controlling the softness of the teacher's distribution
- Extensions for language models: logit-based, feature-based, progressive, and task-specific distillation
- The sveinakerfi metaphor: the apprentice learns from observing the master's technique, not from raw materials
- The accuracy gap: the student will never match the teacher, but can come remarkably close

**Required Reading:**

- Hinton, G., Vinyals, O. & Dean, J. "Distilling the Knowledge in a Neural Network" (2015), *arXiv:1503.02531*
- Sanh, V. et al. "DistilBERT: A Distilled Version of BERT" (2019), *NeurIPS Workshop*
- University of Yggdrasil TR: "Sveinn Distillation: Progressive Task-Specific Distillation for Edge-Deployed Agents" (2040)

**Discussion Questions:**

1. The student model will never match the teacher's accuracy. But the student runs on the edge, where the teacher cannot. How should the edge deployment engineer evaluate the "good enough" threshold? Is 95% of teacher accuracy sufficient? 98%? 90%? What factors determine the threshold, and how should the engineer measure it in practice?
2. Progressive distillation (70B → 13B → 3B) produces better students than direct distillation (70B → 3B) because the distribution gap is smaller. But progressive distillation requires training the intermediate model (13B), which is an additional cost. When is progressive distillation worth the additional cost, and when is direct distillation sufficient?
3. The apprentice metaphor suggests that the student learns more from the teacher's behavior than from the raw data. But what if the teacher has bad habits — systematic biases or errors that the student will also learn? How can distillation avoid transferring the teacher's errors along with its knowledge?

---

### ᚱ Lecture 4: Inference Frameworks and Runtime Optimization — The Rider and the Steed

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

A quantized, pruned, and distilled model is useless if it cannot be executed efficiently on the target hardware. **Inference frameworks** are the software layer that translates the model's mathematical operations into hardware-specific instructions that maximize the device's computational capabilities. The same model can run 2–10x faster on one framework than another, purely because of how the framework maps the model to the hardware. The choice of inference framework is as important as the choice of quantization method — it is the difference between a skilled rider on a fast horse and a skilled rider on a slow horse.

The 2040 inference framework landscape is dominated by several key players:

**ONNX Runtime** (Microsoft, 2019–). ONNX (Open Neural Network Exchange) is a model format that decouples the training framework (PyTorch, TensorFlow, JAX) from the inference runtime. ONNX Runtime loads ONNX-format models and executes them on a wide range of hardware (CPU, GPU, NPU, FPGA) using hardware-specific execution providers (CUDA, TensorRT, OpenVINO, CoreML, ROCm). ONNX Runtime provides graph optimization (operator fusion, constant folding, dead code elimination), quantization support (dynamic and static), and an extensive operator set. It is the most portable inference framework and the default choice for cross-platform edge deployment.

**TensorRT** (NVIDIA, 2016–). TensorRT is NVIDIA's high-performance deep learning inference optimizer and runtime. It takes a model (ONNX, TensorFlow, or native PyTorch), optimizes the computation graph for NVIDIA GPUs, applies layer fusion, kernel auto-tuning (selecting the fastest kernel for each operator based on the GPU architecture), and produces an optimized inference engine. TensorRT supports INT8 and FP16 quantization with calibration, and it achieves the highest inference throughput on NVIDIA GPUs. TensorRT's limitation is its hardware specificity — it only runs on NVIDIA GPUs.

**TensorFlow Lite** (Google, 2017–). TensorFlow Lite (TFLite) is Google's lightweight inference framework for mobile and embedded devices. TFLite provides a flatbuffer model format, a lightweight interpreter, hardware delegation (GPU delegate, NPU delegate, NNAPI delegate), and support for INT8, INT4, and FP16 quantization. TFLite is optimized for ARM Cortex CPUs, Adreno GPUs, and Android NNAPI accelerators. It is the standard for Android and Raspberry Pi deployment.

**Core ML** (Apple, 2017–). Core ML is Apple's on-device inference framework for iOS, macOS, watchOS, and visionOS. Core ML provides model conversion from TensorFlow, PyTorch, and ONNX; hardware-accelerated execution on Apple Silicon (Neural Engine, GPU, CPU); and support for INT8 and FP16 quantization. Core ML's strength is its tight integration with Apple's hardware and software ecosystem; its limitation is its platform specificity (Apple devices only).

**llama.cpp** (Gerganov et al., 2023–). llama.cpp is an open-source C/C++ inference engine for LLMs that runs on CPU, GPU, and Apple Silicon with minimal dependencies. llama.cpp supports GGML quantization formats (Q4_0, Q4_1, Q5_0, Q5_1, Q8_0, and the newer K-quants), KV cache optimization, and batched inference. By 2040, llama.cpp has become the standard for running LLMs on edge devices — it is used in ÞingAI, Ollama, LM Studio, and most on-device inference projects.

**Runtime optimization techniques.** Beyond the choice of framework, several runtime techniques improve inference speed and memory usage:

**Operator fusion.** Multiple sequential operators (e.g., Convolution → BatchNorm → ReLU) are fused into a single operator that is executed in one kernel call, eliminating intermediate memory reads and writes. Operator fusion reduces memory bandwidth consumption and kernel launch overhead, and it is one of the most effective optimization techniques. Most inference frameworks perform operator fusion automatically during graph optimization.

**KV cache optimization.** In autoregressive language models, the KV (key-value) cache stores the attention keys and values from previous tokens to avoid recomputing them at each step. The KV cache is the primary memory bottleneck in LLM inference — it grows linearly with sequence length and can consume more memory than the model weights themselves. Techniques like PagedAttention (vLLM, 2023), which manages the KV cache in virtual memory pages to reduce fragmentation, and KV cache quantization (storing the cache in INT8 or INT4), significantly reduce KV cache memory.

**Batched inference.** Processing multiple requests simultaneously (batching) amortizes the fixed cost of model loading and kernel launch across multiple inferences, improving throughput. Batched inference increases latency for individual requests but increases throughput for the system as a whole. For edge deployment, batched inference is most relevant when the edge device serves multiple users or handles multiple concurrent tasks.

**Speculative decoding.** A small "draft" model generates candidate tokens, which are then verified by the large "target" model. If the draft model's tokens are correct, they are accepted; if not, the target model regenerates from the last correct token. Speculative decoding reduces latency (the draft model generates tokens faster than the target model) while maintaining the target model's accuracy. The technique is particularly effective when the draft model is much smaller than the target model (e.g., a 1B draft model for a 13B target model) and when the acceptance rate is high (the draft model's predictions are often correct).

The Norse metaphor of **the rider and the steed** (riddari ok hestr) captures the relationship between the model and the inference framework. The model is the rider — it knows the path, it directs the journey, it makes the decisions. The inference framework is the steed — it provides the speed, the endurance, the power to cover the ground. A great rider on a slow steed will lose the race; a great steed with a poor rider will wander aimlessly. Only when the rider and steed are well-matched — the model optimized for the hardware, the framework optimized for the model — does the edge deployment achieve its full potential.

**Key Topics:**

- Inference frameworks: the software layer between model and hardware
- ONNX Runtime: portable, cross-platform, hardware-agnostic
- TensorRT: high-performance NVIDIA-specific optimization
- TensorFlow Lite: lightweight mobile and embedded inference
- Core ML: Apple ecosystem inference
- llama.cpp: open-source LLM inference for edge devices
- Runtime optimization: operator fusion, KV cache optimization, batched inference, speculative decoding
- The rider and the steed: model and framework must be well-matched for optimal performance

**Required Reading:**

- ONNX Runtime documentation (2024), Microsoft
- Kwon, W. et al. "Efficient Memory Management for Large Language Model Serving with PagedAttention" (2023), *SOSP*
- Leviathan, Y. et al. "Fast Inference from Transformers via Speculative Decoding" (2023), *ICML*
- University of Yggdrasil TR: "Riddari: Matching Models to Hardware for Optimal Edge Inference" (2040)

**Discussion Questions:**

1. ONNX Runtime is portable but not the fastest on any single hardware platform. TensorRT is the fastest on NVIDIA GPUs but doesn't run on other hardware. Is it worth maintaining ONNX Runtime as the portable option, or should edge deployments target specific hardware platforms with optimized frameworks? What are the trade-offs between portability and performance?
2. Speculative decoding uses a small draft model to accelerate a large target model. But the draft model consumes additional memory and compute — it must be loaded alongside the target model. For an edge device with limited memory, is the memory overhead of the draft model worth the latency improvement? Under what conditions does speculative decoding provide net benefit?
3. The rider and steed metaphor suggests that the model and framework must be well-matched. But what happens when the hardware changes — a new generation of edge devices with different capabilities? Should the model be re-optimized for each new hardware generation, or should the framework abstract away the hardware differences?

---

### ᚴ Lecture 5: Hardware-Aware Neural Architecture Design — Forging the Blade

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The previous lectures focused on optimizing existing models — quantizing, pruning, and distilling them to fit on edge hardware. This lecture takes a fundamentally different approach: **designing models from the ground up for edge deployment**. Rather than taking a large cloud model and compressing it, we design small models that are inherently efficient on edge hardware. This is hardware-aware neural architecture design — the art of creating models that match the computational profile of the target device.

The key insight of hardware-aware design is that different hardware platforms have different computational characteristics. A model that runs efficiently on a data-center GPU (where memory bandwidth is abundant and matrix multiplications are fast) may run inefficiently on an edge CPU (where memory bandwidth is scarce and vector operations are slower). The optimal model for one hardware platform is not the optimal model for another. **Hardware-aware design** takes the target hardware's computational profile as a first-class constraint and designs the model to exploit the hardware's strengths and avoid its weaknesses.

**Edge hardware profiles.** The 2040 edge hardware landscape includes several categories:

**Smartphones (Snapdragon X Elite, Apple A20).** CPU: 8–12 cores, ARM architecture. GPU: Integrated Adreno or Apple GPU. NPU: 45–75 TOPS. RAM: 8–16GB shared. Strengths: moderate compute, good memory bandwidth, dedicated NPU for matrix operations. Weaknesses: limited RAM (shared with OS), thermal throttling under sustained load, limited model size.

**Edge AI modules (Jetson Orin Nano, Coral Edge TPU, Raspberry Pi 6 with AI accelerator).** CPU: 4–8 cores, ARM or RISC-V. GPU: Integrated or none (TPU only). NPU: 20–100 TOPS (Jetson Orin Nano: 40 TOPS). RAM: 4–16GB. Strengths: low power (5–15W), compact form factor, dedicated AI accelerator. Weaknesses: limited compute for non-AI workloads, software support varies.

**Laptops with NPU (Intel Meteor Lake, Qualcomm Snapdragon X).** CPU: 8–14 cores, x86 or ARM. GPU: Integrated or discrete. NPU: 10–45 TOPS. RAM: 16–32GB. Strengths: versatile compute, good development environment, sufficient RAM for 3–7B models. Weaknesses: NPU limited to small models, GPU memory shared with display.

**Industrial edge servers (NVIDIA Jetson AGX Orin, Intel Movidius VPU cluster).** CPU: 8–12 cores, ARM or x86. GPU: Dedicated (Orin: 2048 CUDA cores). NPU: 200+ TOPS. RAM: 32–64GB. Strengths: high compute, sufficient RAM for 13B+ models, industrial-grade reliability. Weaknesses: higher power consumption (30–60W), larger form factor, higher cost.

**Hardware-aware design principles.** Each hardware profile has different constraints, and the optimal model architecture varies accordingly:

**Compute-bound vs. memory-bound.** Edge CPUs are typically **memory-bandwidth-bound** — they can compute faster than they can fetch data from RAM, so the bottleneck is the weight matrix loading, not the arithmetic. For memory-bound hardware, the optimal model has fewer parameters (less data to fetch) and deeper but narrower layers (less activation memory per layer). Edge NPUs and TPUs are typically **compute-bound** — they can fetch data faster than they can process it, so the bottleneck is the arithmetic, not the data. For compute-bound hardware, the optimal model has more parameters but fewer numerical operations per parameter (e.g., grouped convolutions, sparse attention).

**Kernel utilization.** Hardware accelerators achieve peak throughput only when their compute units are fully utilized. A matrix multiplication kernel achieves peak FLOPS only when the matrix dimensions are multiples of the hardware's tile size (e.g., 128×128 on the Jetson's Tensor Cores). Hardware-aware models choose layer dimensions that maximize kernel utilization — dimensions that are multiples of the hardware's tile size — even if this means slightly different dimensions than the standard transformer architecture.

**Attention mechanism design.** The standard multi-head attention (MHA) mechanism is O(n²) in sequence length and requires storing the full attention matrix in memory. For edge hardware with limited memory, quadratic attention is a bottleneck. Hardware-aware alternatives include: **Multi-Query Attention (MQA)**, which shares the key and value projections across all heads, reducing the KV cache size by a factor of num_heads; **Grouped-Query Attention (GQA)**, which shares key-value projections within groups of heads, providing a trade-off between MHA (full sharing) and MQA (single shared projection); and **Linear Attention**, which replaces the softmax with a kernel function, reducing the complexity to O(n) at the cost of approximating the attention weights.

**Architecture search for edge.** Neural Architecture Search (NAS) automates the design of hardware-aware models. NAS algorithms search the space of possible architectures (layer types, dimensions, connections) for the architecture that maximizes accuracy subject to hardware constraints (latency ≤ T, memory ≤ M, power ≤ P). The Once-for-All (OFA) network (Cai et al., 2020) trains a "super-network" that contains many sub-networks of different sizes, and then selects the optimal sub-network for each hardware target by searching over the sub-networks that meet the hardware constraints. Differentiable NAS (DARTS, Liu et al., 2019) makes the architecture search differentiable, enabling gradient-based optimization of the architecture alongside the weights.

The Norse metaphor of **forging the blade** (smíða sverð) captures hardware-aware design. A blade is forged for a specific purpose: a delicate rapier for dueling, a heavy axe for splitting wood, a curved seax for close combat. The smith does not take a universal blade and try to make it work for every purpose — that would produce a blade that is adequate for everything and excellent for nothing. Instead, the smith forges each blade for its specific purpose, choosing the steel, the length, the weight, and the edge geometry to match the task. The hardware-aware model designer, like the smith, forges each model for its specific hardware — choosing the architecture, the dimensions, and the operations to match the computational profile of the target device.

**Key Topics:**

- Hardware-aware design: designing models for the target hardware, not compressing cloud models for edge
- Edge hardware profiles: smartphones, edge AI modules, laptops with NPU, industrial edge servers
- Compute-bound vs. memory-bound: matching model architecture to hardware bottleneck
- Kernel utilization: choosing layer dimensions that maximize hardware utilization
- Attention mechanism design: MHA, MQA, GQA, linear attention — reducing memory for edge
- Neural Architecture Search (NAS): automated design for hardware constraints
- Forging the blade: each model for its purpose, each blade for its task

**Required Reading:**

- Cai, H. et al. "Once-for-All: Train One Network and Specialize It for Efficient Deployment" (2020), *ICLR*
- Liu, H. et al. "DARTS: Differentiable Architecture Search" (2019), *ICLR*
- Shazeer, N. "Fast Transformer Decoding: One Write-Head is All You Need" (2019), *arXiv:1911.02150*
- University of Yggdrasil TR: "Sverð: Hardware-Aware Architecture Design for Edge-Deployed Language Models" (2040)

**Discussion Questions:**

1. The OFA super-network contains many sub-networks, each optimized for a different hardware target. But training the super-network is expensive. When is it worth the investment to train a super-network that supports multiple hardware targets, versus training a specialized model for each target individually?
2. MQA and GQA reduce the KV cache size by sharing key-value projections across heads, but they also reduce the model's representational capacity. Where is the trade-off? For what tasks is the reduced capacity acceptable, and for what tasks is full MHA essential?
3. Forging a blade for a specific purpose produces a better blade for that purpose but a worse blade for other purposes. The same is true for hardware-aware models — they are optimal for one hardware target but may not run well on others. How should we handle the diversity of edge hardware? Should we design one model per hardware category, or should we design a single model that runs "well enough" on all hardware?

---

### ᚻ Lecture 6: On-Device LLMs — Bringing Mímir's Well to the Village

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The previous lectures have treated the edge model as a classification engine — a system that takes input and produces output, optimized for throughput and latency. But the 2040 edge deployment challenge is not just about running a classifier on a device; it is about running a **language model** — an LLM — on the device. On-device LLMs enable agents that operate without cloud connectivity: agents that can hold conversations, answer questions, write code, reason about problems, and perform complex tasks, all on the local device, without sending data to the cloud.

Running an LLM on an edge device is fundamentally different from running a classifier. An LLM is **autoregressive**: it generates one token at a time, and each token depends on all previous tokens. Autoregressive generation introduces two challenges that classifiers do not face:

**Memory footprint.** The KV cache for an autoregressive model grows linearly with the sequence length. For a 7B-parameter model generating a 2048-token sequence with 32 heads and a head dimension of 128, the KV cache requires 2 × 32 × 128 × 2048 × 2 bytes (FP16) = 32MB per sequence. For a 4096-token sequence, it requires 64MB. For a batch of 4 concurrent sequences, it requires 256MB — on a device with 8GB of shared RAM, this consumes 3% of total memory just for the KV cache. KV cache management is the primary memory bottleneck for on-device LLMs.

**Latency.** Autoregressive generation is inherently sequential: each token must be generated before the next token can begin. The latency of each token depends on the model size, the hardware, and the precision. A 7B model in INT4 quantization running on a Jetson Orin Nano generates approximately 15–25 tokens per second — fast enough for interactive chat but too slow for real-time code completion or latency-sensitive agent tasks. A 3B model in INT4 on the same hardware generates 30–50 tokens per second, which is fast enough for most interactive applications.

The 2040 landscape of on-device LLMs offers several model families specifically designed for edge deployment:

**Small language models (SLMs).** Models in the 1–3B parameter range, trained on curated high-quality data with knowledge distillation from larger teachers. SLMs like Phi-4-mini (1.5B), Gemma-2-2B, and the University of Yggdrasil's **Heimdallr-2B** are designed from the ground up for edge deployment: they use GQA to reduce KV cache, rotary position embeddings (RoPE) for flexible context lengths, and SwiGLU activation for efficient computation. SLMs achieve impressive performance on targeted tasks (question answering, summarization, code completion) but lack the broad knowledge and reasoning capability of larger models.

**Medium language models (MLMs).** Models in the 7–13B parameter range, designed as general-purpose on-device models. MLMs like Llama-3-8B, Mistral-7B, and the University of Yggdrasil's **Valkyrie-9B** offer a balance between capability and efficiency: they are small enough to run on edge devices with 8–16GB RAM (with INT4 or INT8 quantization) and large enough to perform well on a wide range of tasks. The 7–13B range is the current "sweet spot" for on-device LLMs — small enough for edge, large enough for general intelligence.

**Mixture-of-experts (MoE) models.** Models that use a sparse mixture of experts to achieve high capability with low per-token compute. An MoE model with 4 experts and 2 active experts per token has 4x the parameters of a dense model but only 2x the per-token compute, because only 2 experts are activated for each token. Edge-deployed MoE models like Mixtral-8x7B (activated 2 of 8 experts, 13B active parameters per token) achieve near-13B-dense-model performance with 7B-dense-model compute, at the cost of 4x the memory for storing all experts.

**Hybrid cloud-edge models.** Models that run partially on the edge and partially in the cloud, depending on the task difficulty and the available connectivity. The edge model handles easy, latency-sensitive tasks (short responses, routine queries, simple tool calls). The cloud model handles difficult, latency-tolerant tasks (complex reasoning, long-form generation, knowledge-intensive queries). The hybrid model maximizes the advantages of both: the low latency and offline capability of the edge, and the high capability of the cloud. The University of Yggdrasil's **Heimdallr-Valkyrie** system uses a Heimdallr-2B edge model for routine tasks and a Valkyrie-9B cloud model for complex tasks, with an intelligent router that sends each query to the appropriate model based on estimated difficulty.

The Norse metaphor of **Mímir's well** captures the challenge of on-device LLMs. Mímir's well (Mímisbrunnr) is the well of wisdom, from which Odin sacrificed his eye to drink. The wisdom of the well is vast and deep — like the knowledge encoded in a large language model. But the well is far away, at the root of Yggdrasil, and not everyone can travel to it. Bringing Mímir's well to the village — running the model on a local device, where everyone can access it — requires compressing the well's wisdom without losing its essence. The small model at the village well doesn't contain all of Mímir's wisdom, but it contains enough for most daily needs, and it's always there when the village needs it, even when the road to the well is washed out (the network is down).

**Key Topics:**

- On-device LLMs: running language models on edge devices without cloud connectivity
- Autoregressive generation challenges: KV cache memory, sequential token generation latency
- Small language models (SLMs): 1–3B, targeted tasks, Phi-4-mini, Heimdallr-2B
- Medium language models (MLMs): 7–13B, general-purpose, Llama-3-8B, Valkyrie-9B
- Mixture-of-experts (MoE): high capability, low per-token compute, Mixtral-8x7B
- Hybrid cloud-edge models: easy tasks on edge, hard tasks on cloud, intelligent routing
- Mímir's well: bringing deep wisdom to the village, compressed but sufficient

**Required Reading:**

- Touvron, H. et al. "LLaMA: Open and Efficient Foundation Language Models" (2023), *arXiv:2302.13971*
- Jiang, A.Q. et al. "Mixtral of Experts" (2024), *arXiv:2401.04088*
- University of Yggdrasil TR: "Heimdallr-Valkyrie: Hybrid Cloud-Edge Agent Architecture with Intelligent Routing" (2040)

**Discussion Questions:**

1. The hybrid cloud-edge model sends easy tasks to the edge and hard tasks to the cloud. But the router — the component that decides which tasks are easy and which are hard — is itself a model that must run on the edge. If the router makes mistakes (sending a hard task to the edge or an easy task to the cloud), the system's overall performance degrades. How should the router's accuracy be evaluated, and what is the acceptable error rate for task routing?
2. MoE models achieve high capability with low per-token compute, but they require storing all experts in memory. On a device with 8GB of RAM, a Mixtral-8x7B model in INT4 requires approximately 14GB — more than the device can hold. Is MoE viable for edge deployment, or is the memory overhead of inactive experts too high? Are there MoE variants that reduce the memory footprint?
3. Mímir's well is at the root of Yggdrasil, far from the village. But what if the village needs wisdom that the village well doesn't have? In the hybrid model, the cloud is always available for hard queries. But in a connectivity-denied environment, the cloud is not available. Should the edge model be designed to recognize its own limitations and gracefully decline tasks it cannot handle, or should it attempt hard tasks and risk producing low-quality outputs?

---

### ᚾ Lecture 7: Frugal Agents — Intelligence on a Budget

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An on-device LLM is a powerful component, but it is not an agent. An agent uses the LLM as a reasoning engine but also orchestrates tool calls, manages memory, maintains state, and coordinates with other agents. Each of these additional functions consumes resources — memory for the state, compute for the orchestration, bandwidth for the tool calls, and storage for the memory. A **frugal agent** is an agent system designed to operate within the resource constraints of an edge device — limited RAM, limited compute, limited power, limited storage — while preserving as much of the agent's intelligence as possible.

The 2040 definition of a frugal agent is one that operates on a device with no more than 8GB of RAM, no more than 15 watts of power consumption, and no guaranteed network connectivity. The frugal agent must make intelligent decisions about when to spend resources (use the LLM for complex reasoning, call a cloud API for knowledge-intensive tasks) and when to conserve them (use a cached response, defer a task until connectivity is restored, run a lightweight local model instead of the full LLM).

**Frugal agent architecture.** The architecture of a frugal agent differs from a cloud agent in several key respects:

**Tiered reasoning.** The frugal agent does not use the LLM for every decision. Simple decisions — "Is this a greeting?" "Does this message require an urgent response?" "Is this a question I've answered before?" — are handled by lightweight classifiers that run in microseconds on the CPU. Medium decisions — "What is the user asking?" "Which tool should I call?" — are handled by the on-device SLM. Complex decisions — "How should I reason about this problem?" "What is the best plan for this task?" — are handled by the on-device MLM (if it fits) or offloaded to the cloud (if connectivity is available). The tiered reasoning architecture ensures that the LLM is invoked only when it is needed, conserving compute and memory for the tasks that genuinely require intelligent reasoning.

**Adaptive context management.** The LLM's context window is a scarce resource on edge devices. A 7B model with a 4096-token context window uses approximately 1GB of RAM just for the KV cache at maximum context. The frugal agent must manage the context window carefully: summarizing old conversation turns to free space, compressing tool outputs before inserting them into context, and pruning irrelevant context to focus on what matters. The University of Yggdrasil's **MuninnFrugal** context manager (inspired by the AI303 memory architecture) maintains three context tiers: active context (the current turn and the most recent 2–3 turns, kept verbatim), compressed context (the previous 5–10 turns, compressed to summary), and retrieved context (longer-term memories, retrieved from local storage on demand).

**Local-first tool execution.** Cloud agents can call any tool at any time — the cloud provides unlimited compute and network connectivity. Frugal agents must prioritize local tools that run on the device without network access: local file operations, local calculations, local calendar and contacts access, local database queries, and on-device models for classification, entity recognition, and sentiment analysis. Cloud tools (web search, cloud API calls, cloud model inference) are available only when connectivity permits and are treated as luxury resources, not defaults.

**Opportunistic cloud offloading.** When connectivity is available, the frugal agent can offload compute-intensive tasks to the cloud. But connectivity may be intermittent — available for a few minutes, then lost for hours. The frugal agent must be opportunistic: when connectivity is available, it sends queued tasks to the cloud and caches results for later use; when connectivity is lost, it continues operating with local resources. The opportunistic offloading architecture is inspired by the Norse concept of **haf og himinn** — the sea and the sky. The sea (the cloud) provides abundant resources but is not always accessible; the sky (the edge) is always present but provides limited resources. The skilled sailor (the frugal agent) uses the sea when it is calm and the wind is favorable, and relies on the sky for navigation when the sea is rough.

**Energy-aware scheduling.** Edge devices have limited battery life, and LLM inference is energy-intensive. A 7B model generating 20 tokens per second on a Jetson Orin Nano consumes approximately 10W — draining a 20Wh battery in 2 hours of continuous inference. The frugal agent must schedule inference to maximize battery life: batching inference requests to reduce the overhead of model loading, deferring non-urgent inference to when the device is charging, and using the SLM for routine tasks to conserve the MLM's compute for important tasks.

**Offline resilience.** The frugal agent must function without network connectivity. This means that all critical functionality — conversation, task execution, memory retrieval, tool use — must work without the cloud. The cloud provides additional capability (knowledge-intensive reasoning, web search, cloud-based tools) but is not required for the agent to function. The offline-resilient agent degrades gracefully: full capability with cloud connectivity, reduced but functional capability without.

The Norse metaphor of the **knarr** — the cargo vessel used for coastal trading voyages — captures the frugal agent's design philosophy. The knarr was not the fastest ship (that was the longship), nor the largest (that was the ocean-going trader). It was the most practical ship for its purpose: seaworthy enough for the open ocean, shallow-drafted enough for coastal harbors, capacious enough for cargo, and economical enough for a small crew to operate. The knarr did not try to be the best at everything; it was the best at being good enough for its specific context. The frugal agent, like the knarr, is not the most powerful agent — it is the most practical agent for the edge context: seaworthy enough for real tasks, economical enough for limited resources, and resilient enough for intermittent connectivity.

**Key Topics:**

- Frugal agents: intelligent agent systems designed for edge resource constraints
- Tiered reasoning: lightweight classifiers → SLM → MLM → cloud, using each tier only when needed
- Adaptive context management: active, compressed, and retrieved context tiers
- Local-first tool execution: prioritizing on-device tools over cloud tools
- Opportunistic cloud offloading: use the cloud when available, operate locally when not
- Energy-aware scheduling: batching inference, deferring tasks, conserving battery
- Offline resilience: full capability with cloud, functional capability without
- The knarr: practical, seaworthy, economical — the best at being good enough for the context

**Required Reading:**

- Xu, J. et al. "A Survey on Resource-Efficient Machine Learning: From Models to Systems" (2023), *ACM Computing Surveys*
- University of Yggdrasil TR: "Knarr: Frugal Agent Architecture for Edge Deployment with Intermittent Connectivity" (2040)

**Discussion Questions:**

1. The tiered reasoning architecture uses lightweight classifiers for simple decisions, the SLM for medium decisions, and the MLM for complex decisions. But the decision "which tier should handle this input?" is itself a decision that must be made quickly and with minimal compute. How should the router between tiers be designed? A learned model would add compute overhead; a rule-based system might be too rigid. What is the right balance?
2. Energy-aware scheduling defers non-urgent inference to when the device is charging. But the user may not want their agent to be less capable when the battery is low — they may need the agent precisely when they are away from a charger. How should the agent communicate its resource constraints to the user? Should it notify the user that it's running in power-saving mode, or should it silently reduce its capability?
3. The knarr is designed for a specific context — coastal trading. When the context changes (e.g., the agent is moved from a smartphone to an industrial edge server), should the frugal agent architecture adapt, or should it stay optimized for the original context? How can a frugal agent be designed to be context-adaptive without becoming too expensive to deploy?

---

### ᛁ Lecture 8: Agent State Management on Edge — The Memory Chest in the Longship

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An agent without memory is stateless — it treats every interaction as a blank slate, forgetting everything the moment the context window fills. An agent with memory (as discussed in AI303) accumulates knowledge about the user, the environment, and its own history across interactions. But memory is expensive — vector databases, knowledge graphs, and episodic stores consume RAM, storage, and compute. On an edge device with 8GB of shared RAM and 64–256GB of flash storage, the agent's memory must be carefully managed to fit within the device's constraints while preserving the memories that matter.

**Edge memory architecture.** The edge memory architecture differs from the cloud memory architecture in three key respects:

**Capacity.** The edge device has 8–16GB of RAM and 64–256GB of flash storage. The cloud has 64–512GB of RAM and petabyte-scale storage. The edge memory system must be aggressively smaller — storing fewer memories, compressing stored memories more aggressively, and evicting memories more readily when capacity is reached.

**Latency.** The edge memory system must respond in real-time — the agent's context window waits for no one. Cloud memory systems can tolerate 10–100ms retrieval latency because the overall cloud inference latency is 50–500ms. Edge memory systems must retrieve in 1–5ms because the overall edge inference latency is 10–50ms. This rules out large vector databases with expensive similarity search — the edge memory system must use smaller, faster retrieval methods.

**Durability.** Cloud memory systems store data on replicated servers with automatic failover. Edge memory systems store data on a single device that can be lost, damaged, or reset. The edge memory system must handle data durability gracefully: local backups, cloud sync when available, and recovery procedures when data is lost.

The 2040 edge memory architecture, as implemented in ÞingAI Edge, has four layers:

**L0: Context window.** The active context — the current conversation turn and the most recent 2–3 turns, stored in the LLM's KV cache. This is the fastest and most expensive memory: KV cache at FP16 requires 1 byte per parameter per token (plus activations), so a 4096-token context for a 7B model requires roughly 500MB of RAM. The context window is the agent's working memory (Lecture 2 of AI303), and it is managed by the same hierarchical summarization techniques (raw → summarized → indexed) that are used in cloud agents.

**L1: On-device vector store.** A small vector database (built on sqlite-vss or Qdrant-lite) stored on the device's flash storage. The on-device store holds the agent's episodic memory (conversation summaries, tool call results, important facts) as vector embeddings with metadata. Retrieval uses approximate nearest neighbor (ANN) search with HNSW (hierarchical navigable small world) indexing, which achieves sub-millisecond retrieval for databases up to 100K vectors. The on-device store is the agent's primary episodic and semantic memory (Lectures 3–4 of AI303) for offline operation.

**L2: On-device knowledge graph.** A lightweight knowledge graph (built on RDF-lite or custom JSON-LD) stored on the device's flash storage. The knowledge graph holds the agent's semantic memory — facts about the user, the environment, and the agent's own capabilities — in a structured format that supports logical queries. The on-device knowledge graph is small (typically 1K–10K triples) but high-value, representing the agent's most important knowledge in a form that can be queried without ambiguity.

**L3: Cloud-synced memory.** When connectivity is available, the agent syncs its local memory with a cloud storage service (S3, Google Cloud Storage, or a private endpoint). The cloud store holds the agent's complete memory history — all conversations, all tool calls, all facts — and enables the agent to recover its memory if the device is lost or reset. The cloud sync is bidirectional: the agent pushes new memories to the cloud and pulls memories from the cloud when it encounters gaps in its local store.

**Memory management on edge.** The edge memory system must manage three scarce resources: RAM (for the context window and the vector store index), flash storage (for the vector database and knowledge graph), and compute (for embedding, retrieval, and summarization). Memory management policies determine which memories to keep, which to evict, and which to compress:

**Relevance scoring.** Every memory has a relevance score that reflects how likely it is to be useful in the current context. The relevance score is computed as a weighted combination of recency (how recently the memory was created), frequency (how often it has been retrieved), importance (how important the agent judged it at creation time), and contextual similarity (how semantically similar it is to the current query). Memories with low relevance scores are candidates for eviction.

**Tiered eviction.** When the on-device store reaches capacity, the system evicts the lowest-relevance memories, first compressing them (summarizing a conversation into a single sentence) and then, if compression is insufficient, deleting them entirely. Evicted memories are synced to the cloud before deletion, so they can be retrieved later if connectivity is available.

**Importance tagging.** The agent tags each memory with an importance level (critical, high, medium, low) at creation time. Critical memories (the user's preferences, the agent's core instructions, safety-critical facts) are never evicted; high-importance memories are evicted only when storage is critically low; medium and low-importance memories are evicted freely. Importance tagging ensures that the agent never forgets what it absolutely must remember, even when storage is scarce.

The Norse metaphor of the **memory chest in the longship** (minningaskip) captures the edge memory challenge. A longship on a long voyage carries a memory chest — a wooden box containing the most important items: the map, the tools, the spare parts, the ritual objects. The chest is not large enough to hold everything the crew might need; it holds only what they *must* have. The rest of their supplies are stored in the cargo hold or left behind at the settlement. The memory chest is the L1 and L2 memories: the most important facts and episodes, stored on the device, always available. The cargo hold is the L3 memory: the complete history, stored in the cloud, available when connectivity permits. The frugal agent, like the longship's captain, must decide what goes in the chest (keep on device) and what goes in the hold (sync to cloud) — and what gets left behind (evict entirely).

**Key Topics:**

- Edge memory architecture: capacity, latency, durability constraints
- L0 context window: active context in KV cache, hierarchical summarization
- L1 on-device vector store: episodic memory, ANN search, sub-millisecond retrieval
- L2 on-device knowledge graph: semantic memory, logical queries, structured facts
- L3 cloud-synced memory: full history, bidirectional sync, recovery
- Memory management: relevance scoring, tiered eviction, importance tagging
- The minningaskip: the memory chest holds only what must be kept

**Required Reading:**

- AI303 Lecture Notes (Memory Systems for Persistent Agents), Lectures 1–4
- Johnson, J. et al. "Billion-Scale Similarity Search with GPUs" (2019), *IEEE Transactions on Big Data*
- University of Yggdrasil TR: "Minningaskip: Edge Memory Architecture for Frugal Agents with Limited Storage" (2040)

**Discussion Questions:**

1. The relevance score combines recency, frequency, importance, and contextual similarity. But these factors can conflict: a memory that was created long ago (low recency) but is very important (high importance) and very similar to the current query (high contextual similarity) should arguably be kept. How should the edge agent weight these factors? Should the weights be fixed or adaptive?
2. The cloud-synced memory store enables the agent to recover its memory if the device is lost. But the cloud store also raises privacy concerns — the agent's memories include personal information about the user. How should the agent encrypt and protect the cloud store? What are the trade-offs between security (encrypting everything) and usability (being able to search the cloud store without decrypting everything)?
3. The minningaskip holds only the most important items. But importance is subjective — what the agent's designer thinks is important may not match what the user thinks is important. Should the user be able to tag memories as important, overriding the agent's importance assessment? How should the agent communicate its memory limitations to the user without overwhelming them with technical details?

---

### ᛃ Lecture 9: Model Update and Version Management — Reforging the Sword Without Breaking It

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Edge-deployed models, like all software, need to be updated. Security vulnerabilities are discovered, bugs are fixed, new capabilities are developed, and the data distribution shifts over time. But updating a model on an edge device is fundamentally different from updating a model in the cloud. In the cloud, the model is updated on the server and all users get the new version simultaneously. On the edge, each device must download the update, install it, and switch to the new version — all while the agent continues to serve the user. The edge model update must be **atomic** (the model is either the old version or the new version, never a hybrid), **efficient** (the update should minimize the bandwidth and storage required), and **graceful** (the update should not interrupt the agent's operation).

The challenges of edge model updates are:

**Bandwidth.** A 7B-parameter model in INT4 quantization requires approximately 3.5GB of storage. A full model update means downloading 3.5GB over whatever network connection is available — which may be a slow cellular connection, an intermittent Wi-Fi connection, or, in the worst case, no connection at all. Full model updates are impractical for devices on constrained networks.

**Atomicity.** The model update must be atomic: the agent must not be in a state where some layers are the old version and some are the new version. Atomicity requires either double-buffering (storing both the old and new models simultaneously, which doubles the storage requirement) or staged updates (downloading the update in stages and applying it atomically at the end).

**Backward compatibility.** The new model must be backward-compatible with the old model's memory. If the agent has stored episodic memories and knowledge graph triples that were created by the old model, the new model must be able to read them. If the new model uses a different tokenizer, a different embedding dimension, or a different knowledge schema, the stored memories become incompatible. Backward compatibility must be designed into the update process.

**Rollback.** If the new model is worse than the old model — it produces lower-quality outputs, it has a new bug, or it is incompatible with the agent's tools — the device must be able to roll back to the old model. Rollback requires keeping the old model available until the new model has been validated, which means the device must store both models temporarily, or the old model must be recoverable from a backup.

The 2040 best practices for edge model updates address these challenges:

**Delta updates.** Rather than downloading the entire new model, the device downloads only the **delta** — the difference between the old model and the new model. If only 5% of the model's weights have changed, the delta is 5% of the full model size. Delta updates dramatically reduce bandwidth requirements (from 3.5GB to 175MB in this example). Delta updates require that the device know the version of the current model and that the update server generate a diff between the current version and the target version. The **bsdiff** and **xdelta** algorithms produce efficient binary diffs for model weights.

**LoRA (Low-Rank Adaptation) updates.** LoRA (Hu et al., 2022) adds low-rank adaptation matrices to the model's weight matrices, enabling fine-tuning with a small number of additional parameters. A LoRA update adds 1–10MB of parameters to a 7B model — a fraction of the full model size. LoRA updates are ideal for task-specific adaptation (e.g., fine-tuning the model for a specific user's preferences) and for incremental capability updates (e.g., adding support for a new tool). LoRA updates can be applied without modifying the base model, enabling atomic rollback (just remove the LoRA adapter).

**Staged rollout.** New model versions are rolled out to a small percentage of devices first (canary deployment), monitored for quality and compatibility, and then gradually rolled out to all devices. Staged rollout reduces the risk of a bad update affecting all devices simultaneously. If the canary deployment detects quality degradation or compatibility issues, the rollout is paused and the affected devices are rolled back.

**Over-the-air (OTA) updates with verification.** The device downloads the update in the background, verifies its integrity (checksum or signature), and applies it during a maintenance window (e.g., while the device is charging and connected to Wi-Fi). The OTA update system verifies that the new model produces acceptable outputs (using a validation set) before switching to it. If the validation fails, the update is rejected and the device continues with the old model.

The Norse metaphor of **reforging the sword** (endursmíða sverð) captures the model update challenge. A sword that has been damaged or dulled must be reforged — heated, hammered, and quenched — to restore its edge. But the reforging must not break the sword. The smith must heat the metal hot enough to reshape it, but not so hot that it loses its temper. The smith must hammer the edge thin enough to sharpen it, but not so thin that it becomes brittle. And the smith must quench the blade at exactly the right moment, or the steel will crack. The edge model update, like the reforged sword, must improve the model without breaking it — adding new capabilities without disrupting old ones, fixing bugs without introducing regressions, and updating the architecture without losing backward compatibility.

**Key Topics:**

- Edge model update challenges: bandwidth, atomicity, backward compatibility, rollback
- Delta updates: downloading only the diff between old and new models
- LoRA updates: low-rank adaptation matrices for efficient task-specific updates
- Staged rollout: canary deployment, monitoring, gradual rollout
- Over-the-air updates with verification: background download, integrity check, validation
- Reforging the sword: improving the model without breaking it

**Required Reading:**

- Hu, E.J. et al. "LoRA: Low-Rank Adaptation of Large Language Models" (2022), *ICLR*
- MosaicML. "Streaming Updates for Edge-Deployed Models" (2023), *MosaicML Technical Report*
- University of Yggdrasil TR: "Endursmíða: Atomic Model Updates for Edge-Deployed Agents with LoRA and Delta Updates" (2040)

**Discussion Questions:**

1. Delta updates require the update server to generate a diff between the current version and the target version. But if the device has version N and the server has versions N+1 through N+K, the server must generate K different deltas (one for each possible current version). How should the update server manage the combinatorial explosion of version deltas? Is it practical to store deltas for every version pair, or should the server use a different approach?
2. LoRA updates are small and atomic, but they only fine-tune the model — they don't change the base model's architecture or knowledge. When is a LoRA update sufficient, and when is a full model update necessary? Design a decision procedure that determines whether a given update should be implemented as a LoRA adapter or a full model replacement.
3. Staged rollout reduces the risk of a bad update, but it also delays the rollout of good updates. The first 1% of devices to receive the update are essentially canaries — they take the risk so the remaining 99% don't have to. Is this fair? How should the canary devices be selected — randomly, voluntarily, or based on device characteristics?

---

### ᛞ Lecture 10: Edge Security and Privacy — The Shield Wall at the Border

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Edge deployment moves data and computation from the cloud to the device. This is a privacy benefit (user data stays on the device) and a security challenge (the device is in the user's hands, where it can be physically accessed, reverse-engineered, and tampered with). The cloud security model assumes that the server is in a controlled environment, behind firewalls, with professional administration. The edge security model assumes that the device is in an uncontrolled environment, in the user's hands, where the user (or an attacker with physical access) can inspect, modify, and exploit the model and its data.

The 2040 edge security landscape addresses several threat models:

**Model extraction.** An attacker with access to the edge device extracts the model weights, enabling them to replicate the model on their own hardware, study its behavior, and exploit its vulnerabilities. Model extraction is a concern for proprietary models whose value lies in the weights themselves. Defense against model extraction includes: obfuscation (making the weights difficult to extract), encryption (storing the weights in encrypted form and decrypting them in the trusted execution environment), and licensing (legal agreements that prohibit reverse engineering).

**Adversarial inputs.** An attacker crafts inputs designed to cause the model to produce incorrect or harmful outputs. Adversarial attacks range from simple prompt injection (inputs that override the model's instructions) to sophisticated gradient-based attacks (inputs designed to maximize the model's loss function). Edge-deployed models are more vulnerable to adversarial inputs than cloud models because the attacker has local access to the model and can test inputs rapidly without rate limiting.

**Data extraction.** An attacker with access to the edge device extracts the user's personal data from the model's memory stores — conversations, preferences, tool outputs, and other sensitive information stored in the vector database and knowledge graph. Defense against data extraction includes: encryption at rest (the data is encrypted on the device's storage), access controls (the agent only retrieves data when the user is authenticated), and data minimization (the agent stores only the data it needs, deleting the rest).

**Model tampering.** An attacker modifies the model weights on the device, causing the model to produce adversarial outputs — incorrect medical advice, biased recommendations, or injected misinformation. Model tampering is particularly dangerous in applications where the model's recommendations have real-world consequences (medical diagnosis, financial advice, legal guidance). Defense includes: model integrity verification (checksums that detect unauthorized modifications), secure boot (the device only runs software that is cryptographically signed by the manufacturer), and remote attestation (the device proves to a server that it is running an untampered model).

**Privacy-preserving techniques.** Edge deployment is inherently privacy-preserving because user data stays on the device. But privacy is not binary — even on-device data can be compromised. Additional privacy-preserving techniques for edge deployment include:

**Federated learning.** The model is updated using data from many devices, but the data never leaves the devices. Each device trains a local model update on its own data, sends only the gradient update (not the raw data) to a central server, and receives an aggregated update from the server. Federated learning preserves data privacy at the cost of communication overhead and the need to aggregate updates from heterogeneous data distributions.

**Differential privacy.** The model's training and inference are perturbed with calibrated noise to ensure that the model's outputs do not reveal individual data points. Differential privacy provides a mathematical guarantee that the model's behavior is approximately the same whether or not any individual's data is included in the training set. The cost of differential privacy is reduced model accuracy — the noise that protects privacy also degrades performance.

**Homomorphic encryption.** The model performs inference on encrypted data without decrypting it, producing an encrypted result that only the user can decrypt. Homomorphic encryption preserves data privacy even from the model itself, but it incurs a significant computational overhead (10–1000x slower than unencrypted inference), making it impractical for real-time edge applications in 2040 but promising for future hardware.

The Norse metaphor of the **shield wall** (skjaldborg) captures the edge security challenge. The shield wall was the Vikings' primary defensive formation — a line of warriors holding their shields edge-to-edge, creating a barrier that protected the warriors behind it. The shield wall was not impregnable — a determined attacker could break through — but it made attack costly enough that most enemies chose not to try. The edge security model, like the shield wall, cannot make the device impregnable — a determined attacker with physical access can eventually extract the model and data — but it can make attack costly enough that most attackers choose not to try. The shield wall is not a single shield but a formation: multiple layers of defense (obfuscation, encryption, access controls, integrity verification) that must be breached sequentially. Each layer raises the cost of attack, and the cumulative cost of breaching all layers exceeds the value of the extracted model and data for most attackers.

**Key Topics:**

- Edge security challenges: model extraction, adversarial inputs, data extraction, model tampering
- Privacy-preserving techniques: federated learning, differential privacy, homomorphic encryption
- Model protection: obfuscation, encryption, secure boot, remote attestation
- Data protection: encryption at rest, access controls, data minimization
- The shield wall: layered defense, each layer raising the cost of attack
- The inherent privacy benefit of edge deployment: data stays on the device

**Required Reading:**

- McMahan, B. et al. "Communication-Efficient Learning of Deep Networks from Decentralized Data" (2017), *AISTATS*
- Dwork, C. "Differential Privacy" (2006), *ICALP*
- University of Yggdrasil TR: "Skjaldborg: Layered Security Architecture for Edge-Deployed AI Agents" (2040)

**Discussion Questions:**

1. Model extraction is a concern for proprietary models, but the open-source community argues that models should be freely available. Is model extraction actually a security threat, or is it a business model threat? Does the answer change if the model is proprietary because it contains confidential training data (e.g., medical records)?
2. The shield wall is not impregnable — it merely raises the cost of attack. But for a sophisticated attacker (a nation-state, a well-funded competitor), no amount of obfuscation and encryption will prevent model extraction. Is edge deployment fundamentally insecure for high-value proprietary models? Are there applications where cloud deployment is the only secure option?
3. Federated learning preserves data privacy but introduces a new attack vector: model poisoning. A malicious device can submit a corrupted gradient update that degrades the model's performance for all users. How should a federated learning system detect and exclude poisoned updates?

---

### ᛗ Lecture 11: Performance Evaluation and Benchmarking — The Vel in the Test

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

How do we know if an edge deployment is successful? The cloud model runs in a controlled environment with abundant resources; the edge model runs in a constrained environment with limited resources. The same model that achieves 95% accuracy on a cloud benchmark may achieve 90% on the edge (due to quantization), generate responses 5x slower (due to hardware limitations), and consume 10x less energy (due to efficient edge hardware). Evaluating edge deployment requires a different set of metrics than evaluating cloud deployment — metrics that account for the resource constraints, the operational context, and the user experience of edge operation.

**Accuracy metrics.** The standard ML accuracy metrics — accuracy, precision, recall, F1, BLEU, ROUGE, MMLU, HumanEval — measure the quality of the model's outputs. For edge-deployed models, these metrics must be evaluated **after** quantization, pruning, and distillation, not before. The accuracy gap between the cloud model and the edge model is the primary measure of optimization quality — a quantized model that retains 98% of the cloud model's accuracy is a success; one that retains only 80% is a failure, regardless of how much memory it saves.

The 2040 benchmarking standard for edge LLMs includes:

**MMLU (Massive Multitask Language Understanding).** A benchmark of 57 subjects ranging from STEM to humanities, testing the model's breadth of knowledge and reasoning ability. MMLU is the standard benchmark for comparing LLM accuracy across models and sizes.

**HumanEval and MBPP.** Code generation benchmarks that test the model's ability to write correct Python functions. HumanEval tests function-level generation; MBPP (Mostly Basic Python Problems) tests broader Python programming ability.

**MT-Bench.** A multi-turn conversational benchmark that evaluates the model's ability to hold a coherent, informative conversation across multiple turns. MT-Bench is the standard benchmark for evaluating LLM agents in conversational settings.

**AgentBench.** A benchmark for evaluating the complete agent system — model plus memory plus tool use plus self-correction. AgentBench tests the agent's ability to complete multi-step tasks that require planning, tool calls, and error recovery. For edge agents, AgentBench is the most relevant benchmark because it evaluates the full system, not just the model.

**Performance metrics.** Accuracy is necessary but not sufficient. An edge deployment must also meet performance targets:

**Latency.** Time from input to first token (time-to-first-token, TTFT) and time per token (inter-token latency, ITL). TTFT depends on the model size, the batch size, and the hardware; ITL depends on the same factors plus the KV cache size. For interactive applications, TTFT should be under 500ms and ITL should be under 50ms (corresponding to 20+ tokens per second).

**Throughput.** Tokens per second per watt (tokens/W), measuring the energy efficiency of inference. Throughput per watt is the primary metric for battery-powered edge devices, where inference time is limited by available energy, not just available compute.

**Memory footprint.** Peak RAM usage during inference, including model weights, KV cache, and intermediate activations. Memory footprint determines the maximum model size that can run on a given device. A model that requires 10GB of RAM cannot run on a device with 8GB, regardless of its accuracy.

**Model size on disk.** The storage required for the model weights, in MB or GB. Disk size determines whether the model can be stored on the device's flash storage alongside the OS, applications, and user data.

**Power consumption.** The average power draw during inference, measured in watts. Power consumption determines the battery life impact of continuous inference. A model that draws 10W on a device with a 20Wh battery will drain the battery in 2 hours of continuous use.

**Edge-specific benchmarks.** In addition to standard benchmarks, edge deployment requires evaluating metrics that are specific to the edge context:

**Offline accuracy.** The model's accuracy when no cloud connectivity is available. Offline accuracy is typically lower than cloud-assisted accuracy because the edge model has access to fewer tools and less knowledge. The gap between online and offline accuracy is the cost of edge autonomy.

**Connectivity resilience.** The agent's ability to maintain functionality when connectivity is intermittent. Resilience is measured by the percentage of tasks that can be completed during connectivity outages of various durations (5 minutes, 30 minutes, 2 hours, indefinite).

**Cold start time.** The time from agent launch to first response. Cold start time includes model loading (from flash to RAM), KV cache initialization, and first inference. For edge devices, cold start can be 5–30 seconds, depending on model size and hardware. Warm start (reusing a loaded model) is faster but requires keeping the model in RAM, which consumes memory even when the agent is idle.

**Battery impact.** The percentage of battery consumed per hour of active agent use. Battery impact is the metric that matters most to mobile users — if the agent drains the battery by 20% per hour of use, it will be disabled within hours. A target of ≤5% per hour is considered acceptable for most mobile applications.

The Norse metaphor of the **vel** — the practice weapon used by Viking warriors to test their skills without risk of serious injury — captures the purpose of benchmarking. The vel is not the real fight; it is the test before the fight, the structured evaluation that reveals strengths and weaknesses. A warrior who skips the vel and goes straight to the fight may discover too late that his shield arm is weak or his footwork is slow. Similarly, an edge deployment that skips benchmarking and goes straight to production may discover too late that its latency is too high, its battery impact is too severe, or its offline accuracy is too low. The benchmark is the vel — the test that reveals the deployment's readiness before it faces the real fight of production use.

**Key Topics:**

- Accuracy metrics: MMLU, HumanEval, MT-Bench, AgentBench
- Performance metrics: latency (TTFT, ITL), throughput per watt, memory footprint, disk size, power consumption
- Edge-specific metrics: offline accuracy, connectivity resilience, cold start time, battery impact
- The vel: benchmarking as the practice test before the real fight of production

**Required Reading:**

- Hendrycks, D. et al. "Measuring Massive Multitask Language Understanding" (2021), *ICLR*
- Zheng, L. et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (2023), *NeurIPS*
- Liu, X. et al. "AgentBench: Evaluating LLMs as Agents" (2023), *ICLR*
- University of Yggdrasil TR: "Vel Bench: Edge-Specific Benchmarking for On-Device Agent Systems" (2040)

**Discussion Questions:**

1. AgentBench evaluates the complete agent system (model + memory + tools + self-correction) on a set of predefined tasks. But real-world edge agents operate in environments that are much more diverse and unpredictable than the benchmark tasks. How can we design benchmarks that approximate the diversity and unpredictability of real-world edge deployment without creating an infinite test suite?
2. Battery impact is measured as "percentage of battery consumed per hour of active agent use." But users don't use agents continuously for an hour — they use agents in bursts (a 30-second question, a 5-minute task, a 2-minute conversation). How should battery impact be measured for realistic usage patterns? Does the "per hour" metric overestimate or underestimate the real battery impact?
3. The vel is a practice weapon — it tests the warrior's skills without the risk of the real fight. But the vel is also an idealized test — it doesn't capture the chaos, fear, and unpredictability of the real fight. Similarly, benchmarks are idealized tests that don't capture the unpredictability of real-world deployment. How should we account for the gap between benchmark performance and production performance?

---

### ᛟ Lecture 12: The Future of Edge Intelligence — From the Hearth to the Horizon

**Course:** AI307 — Edge Deployment & Model Optimization
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

We began this course with the edge imperative: the cloud is not always available, not always fast enough, not always private enough, and not always cheap enough. The edge is where AI must live — in the field, on the road, in the factory, on the device. We have spent eleven lectures learning how to make AI live on the edge: how to compress it (quantization, pruning, distillation), how to run it (inference frameworks, hardware-aware design), how to give it memory (edge memory architecture), how to make it frugal (tiered reasoning, local-first tools), how to keep it current (delta updates, LoRA), how to keep it safe (shield walls), and how to test it (benchmarking).

Now we look to the future. Where is edge intelligence going? What will the edge look like in 5, 10, 20 years? And what are the unsolved problems that the next generation of edge AI engineers — your generation — will need to address?

**Edge-native models.** The first generation of edge models was compressed cloud models — take a large model and make it smaller. The next generation will be **edge-native models**: models designed from the ground up for edge hardware, with architectures, training procedures, and data curation optimized for the constraints of edge devices. Edge-native models will not be smaller versions of cloud models; they will be different architectures that exploit the edge's unique advantages (low latency, data locality, privacy) rather than fighting its disadvantages (limited RAM, limited compute, intermittent connectivity). The Heimdallr-2B and Valkyrie-9B models mentioned in this course are early examples of edge-native design; future edge-native models will be even more specialized.

**On-device learning.** Current edge models are frozen at deployment — their weights are set during training and do not change during use. The next generation of edge models will learn on-device, adapting to the user's preferences, communication style, and task patterns over time. On-device learning uses techniques like LoRA fine-tuning, prompt tuning, and in-context learning to personalize the model without changing the base weights. The challenge is that on-device learning must be done with the device's limited compute and memory, without access to the full training dataset, and without compromising the model's general capabilities. The University of Yggdrasil's **MuninnAdapt** system uses LoRA adapters that are trained on the user's local data and stored on the device, enabling personalization without cloud connectivity.

**Edge-cloud symbiosis.** The current model of edge-cloud interaction is hierarchical: the edge handles easy tasks, the cloud handles hard tasks. The next generation will be **symbiotic**: the edge and cloud will cooperate on every task, sharing computation, knowledge, and context in real-time. The edge model handles the low-latency, privacy-sensitive parts of the task (understanding the user's intent, generating the immediate response); the cloud model handles the high-compute, knowledge-intensive parts (retrieving relevant information, verifying the response, updating the model). The symbiotic model is not edge-or-cloud but edge-and-cloud, each doing what it does best.

**Neuromorphic edge.** The current edge hardware uses von Neumann architecture — a CPU/GPU/NPU that fetches instructions and data from memory, executes them, and writes results back. Neuromorphic processors (Intel Loihi, IBM TrueNorth, BrainChip Akida) use a fundamentally different architecture inspired by biological neural networks: spiking neurons that communicate through events rather than fetching data from memory. Neuromorphic processors achieve orders-of-magnitude improvements in energy efficiency (10–1000x fewer joules per inference) at the cost of programming complexity and limited model support. By 2040, neuromorphic edge processors are beginning to appear in sensor nodes, wearable devices, and embedded controllers — applications where energy efficiency is critical and the models are small and specialized.

**Federated intelligence.** Beyond a single edge device, the next generation of edge intelligence envisions **federated intelligence**: multiple edge devices cooperating to perform tasks that no single device can handle alone. A fleet of agricultural sensors cooperates to analyze crop health across a field. A team of medical devices cooperates to diagnose a patient's condition. A network of autonomous vehicles cooperates to navigate a city. Federated intelligence requires new coordination protocols (how do the devices communicate?), new security models (how do they trust each other?), and new optimization objectives (they optimize for the collective, not the individual). The Þing Architecture from AI305 provides the coordination framework; the challenge is extending it to federated settings with heterogeneous devices and intermittent connectivity.

**The longship and the horizon.** The Norse longship was not the end of exploration — it was the means. With the longship, the Norse reached Iceland, Greenland, Vinland, and Constantinople. They did not stop building ships when they reached Iceland; they built better ships and went further. The edge devices of 2040 are the longships of AI — they carry intelligence to places the cloud cannot reach. But they are not the destination; they are the means. The future of edge intelligence is a fleet of longships — diverse, specialized, cooperating — carrying intelligence ever further from the data center, ever deeper into the field, ever closer to the user.

The horizon is not the end of the journey. Beyond the horizon, there is another horizon, and another beyond that. Each generation of edge intelligence will extend the reach of AI a little further — from the smartphone to the sensor node, from the sensor node to the embedded controller, from the embedded controller to the neuromorphic chip, from the neuromorphic chip to something we cannot yet imagine. The longship sails on.

**Key Topics:**

- Edge-native models: designed for the edge, not compressed from the cloud
- On-device learning: personalization without cloud connectivity (LoRA, prompt tuning)
- Edge-cloud symbiosis: cooperation on every task, not just offloading hard tasks
- Neuromorphic edge: spiking neurons, event-driven computation, energy efficiency
- Federated intelligence: multiple edge devices cooperating on collective tasks
- The longship and the horizon: each generation extends the reach of AI further

**Required Reading:**

- All previous lectures — this lecture synthesizes the entire course
- Davies, M. et al. "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning" (2018), *IEEE Micro*
- University of Yggdrasil TR: "Longship Fleet: Federated Intelligence Architecture for Heterogeneous Edge Devices" (2040)

**Discussion Questions:**

1. On-device learning personalizes the model to the user's preferences and patterns. But personalization can also create filter bubbles — the model becomes so adapted to the user that it only shows them what they already agree with. How should the edge agent balance personalization (adapting to the user) with serendipity (showing the user new perspectives)? Is there an optimal level of personalization beyond which the model becomes an echo chamber?
2. Neuromorphic processors achieve dramatic energy savings but require fundamentally different programming models and model architectures. Should the edge AI community invest in neuromorphic computing — with its steep learning curve and limited model support — or should it continue optimizing von Neumann architectures for energy efficiency? Under what conditions is neuromorphic computing worth the investment?
3. Federated intelligence envisions multiple edge devices cooperating. But cooperation requires trust, and trust requires verification. How can a device verify that another device's computation is correct without re-executing it (which would negate the benefit of distribution)? Is there a lightweight verification mechanism that enables trust without excessive overhead?

---

## Final Examination Preparation

### Format

The final examination for AI307 will consist of **8 essay questions**, from which students must choose **4** to answer. Each essay should be 1500–2500 words and should demonstrate mastery of the course material, including the ability to apply concepts from the lectures to novel scenarios, to compare and contrast different approaches, and to critically evaluate trade-offs. Students are expected to cite specific lecture material, required readings, and technical frameworks discussed in the course.

### Essay Questions

1. **Full-Stack Edge Deployment Design.** You are tasked with deploying a conversational AI agent on a Raspberry Pi 6 with 16GB RAM and a Coral Edge TPU accelerator (40 TOPS). The agent must hold conversations, answer questions, access the user's local calendar and files, and operate without cloud connectivity. Design a complete edge deployment for this agent, specifying: the model architecture and size, the quantization level, the inference framework, the memory architecture (L0–L3), the frugal agent architecture (tiered reasoning, local-first tools), and the update strategy. Justify each choice with reference to the hardware constraints and the application requirements. How does your design compare to a cloud-only deployment in terms of latency, privacy, and offline capability?

2. **The Accuracy-Efficiency Frontier.** Plot the accuracy-efficiency frontier for on-device LLMs: for each quantization level (FP16, INT8, INT4, mixed-precision), what is the expected accuracy (on MMLU, HumanEval, or AgentBench) and the expected efficiency (tokens/second, memory footprint, power consumption) on a Jetson Orin Nano? Discuss the trade-offs at each point on the frontier. If you could only choose one quantization level for a general-purpose edge agent, which would you choose and why? In your answer, use the Norse metaphor of sharpening the axe — what is the "sharp enough" point for the axe, and what is the "just small enough" point for the model?

3. **Privacy vs. Capability in Edge Deployment.** An edge-deployed medical assistant must choose between using a local model (which preserves patient privacy but has limited medical knowledge) and a cloud model (which has extensive medical knowledge but sends patient data to the cloud). Design a hybrid architecture that maximizes both privacy and capability. Under what conditions should the hybrid architecture use the local model, and under what conditions should it use the cloud model? How should the architecture handle the transition between local and cloud inference when the patient's data is particularly sensitive? In your answer, relate your design to the Norse metaphor of Mímir's well — what wisdom should stay in the village, and what wisdom should require a journey to the well?

4. **LoRA Personalization and the Filter Bubble.** On-device learning personalizes the edge model using LoRA adapters trained on the user's local data. But personalization can create filter bubbles — the model becomes so adapted to the user that it only reinforces existing preferences and viewpoints. Propose a personalization architecture that balances adaptation (the model learns the user's preferences) with diversity (the model occasionally introduces new perspectives). How should the architecture determine when to personalize and when to diversify? What is the cost of diversification in terms of user satisfaction? In your answer, relate the personalization-diversity trade-off to the Norse concept of wyrd — does the user's wyrd (accumulated preferences) constrain the agent's behavior, or can the agent introduce new threads into the web?

5. **Federated Intelligence for Agricultural Monitoring.** A network of 50 agricultural sensors deployed across a 1000-hectare farm must cooperate to analyze crop health, detect pest infestations, and optimize irrigation. Each sensor has a small edge model (1B parameters), a camera, and intermittent LoRa connectivity to a central gateway. Design a federated intelligence architecture for this system, specifying: the model architecture on each sensor, the communication protocol between sensors, the coordination mechanism (Þing Architecture or alternative), the update strategy (federated learning or centralized updates), and the security model. How does your design handle sensors with different capabilities (some sensors are older and less capable)? How does it handle intermittent connectivity (some sensors may be disconnected for hours)?

6. **Benchmarking Edge Agents.** Design a comprehensive benchmark for evaluating edge-deployed AI agents. Your benchmark should measure: accuracy (on downstream tasks), latency (TTFT and ITL), throughput (tokens/second/watt), memory footprint (peak RAM usage), battery impact (percentage per hour of use), offline capability (percentage of tasks completable without cloud), and connectivity resilience (task completion rate during connectivity outages). How would you weight these metrics for different application domains (medical, personal assistant, industrial, agricultural)? Propose a single composite score — the "Vel Score" — that combines the metrics into a meaningful overall evaluation. How should the Vel Score be interpreted by edge deployment engineers?

7. **The Shield Wall and the Open Source.** A leading AI company is considering releasing its edge model as open source, allowing anyone to inspect, modify, and redistribute the model weights. The model was trained on proprietary data, and the company is concerned that releasing the weights will enable competitors to replicate their technology. However, the company is also committed to transparency and reproducibility in AI. Propose a release strategy that balances these concerns. Consider: model obfuscation, data licensing, differential privacy, partial release (releasing only the inference code, not the weights), and federated learning as alternatives. In your answer, relate the release strategy to the Norse concept of the shield wall — how much defense is enough, and when does defense become counterproductive by preventing the community from building on the model?

8. **Research Paper: Edge-Native Agent Architecture.** Write a research paper (3000–4000 words) proposing a novel architecture for an edge-deployed AI agent that is designed from the ground up for edge constraints. Your architecture should address at least four of the following: model selection and quantization, memory management (L0–L3), frugal reasoning (tiered architecture), local-first tools, opportunistic cloud offloading, energy-aware scheduling, or federated intelligence. Your paper should: (a) describe the architecture in detail, (b) explain how the components interact, (c) identify the key design decisions and their trade-offs, (d) propose an evaluation methodology, and (e) relate the architecture to the Norse metaphors discussed in the course (heimr, Mímir's well, the knarr, the minningaskip, the shield wall, the vel). This is your opportunity to synthesize the course material into an original contribution — forge your own sword.

---

*ᚠᚢᚦᚬᚱᚴᚼᚾᛁᛃᛗᛚᛞᛟ*

*Heill er sá er máli kunnr*
*ok slæg hjálm sær.*

— Hávamál, st. 155

*Blessed is he who knows the words*
*and the craft of the helm.*