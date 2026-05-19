# AI203: Computer Vision
## Bachelor of Science in AI Agent Automation — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** AI105 (Introduction to Machine Learning), AI201 (Deep Learning Foundations)
**Description:** Computer vision is the computational interpretation of visual information — the art and science of enabling machines to see. This course covers the full vision pipeline as it applies to AI agents: image classification, object detection, semantic and instance segmentation, visual reasoning, and multimodal integration. Students will implement modern vision architectures (ConvNeXt, ViT-22B, DETR-X), train models on agent-relevant visual tasks (UI understanding, document parsing, scene comprehension), and integrate vision components into complete agent perception systems.

---

## Lectures

### ᚠ Lecture 1: The Visual World — Pixels, Light, and the Eye of the Agent

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Vision begins with light. Photons reflected from surfaces travel through space, enter a lens, and strike a sensor — a retina in biological systems, a CMOS or CCD array in digital cameras. The sensor converts photon energy into electrical signals, which are digitized into a grid of numbers: a pixel array. Each pixel records the intensity of light in one or more wavelength bands (typically red, green, and blue). An image is nothing more than a three-dimensional tensor of numbers — height × width × channels — yet from this humble numerical substrate, the visual system extracts an astonishing richness of information: objects, faces, text, depth, motion, emotion, intent.

The **image formation pipeline** is the first topic of computer vision, because understanding how an image is generated informs how it should be interpreted. A pinhole camera — the simplest imaging model — projects 3D world points onto a 2D image plane through a single aperture. The projection is governed by the **perspective projection equation**: for a world point *(X, Y, Z)* and a camera with focal length *f*, the image coordinates are *(x, y) = (fX/Z, fY/Z)*. This equation embodies the fundamental challenge of vision: information is lost in projection. A 3D scene is collapsed onto a 2D image; every pixel in the image corresponds to a ray in 3D, and the depth along that ray is lost. Recovering 3D structure from 2D images — **inverse graphics** — is an ill-posed problem, and the vision system must use prior knowledge (about the shapes of objects, the physics of light, the statistics of the world) to resolve the ambiguity.

**Color** adds spectral information. The human visual system has three types of cone cells, sensitive to short (blue), medium (green), and long (red) wavelengths. Digital cameras mimic this with color filter arrays (Bayer patterns) that sample each wavelength band at alternating pixels, then interpolate (demosaic) to produce full RGB values. Color spaces — RGB, HSV (hue, saturation, value), LAB (perceptually uniform lightness and color-opponent dimensions) — provide different representations of spectral information, each suited to different tasks. For AI agents processing screenshots and user interfaces, color is a crucial signal: red indicates errors, green indicates success, contrast distinguishes text from background. Agents must be able to perceive and reason about color with the same nuance that humans do.

**Image preprocessing** transforms raw pixel data into forms better suited for downstream processing. **Normalization** (scaling pixel values to mean 0, variance 1) stabilizes neural network training. **Resizing** and **cropping** standardize input dimensions. **Data augmentation** (random flips, rotations, color jitter, Cutout, Mixup, CutMix) artificially expands the training set and improves generalization. For agent vision, preprocessing often includes **document rectification** (dewarping curved pages), **contrast enhancement** (making text legible in low-light screenshots), and **super-resolution** (upscaling low-resolution inputs).

**Visual perception in AI agents** differs from traditional computer vision in its emphasis on task-driven interpretation. A self-driving car's vision system must detect pedestrians and traffic signs — objects defined by their functional role in a specific task. An AI agent assisting with a software tutorial must detect UI elements — buttons, text fields, dropdown menus — also defined by their functional role. In both cases, the vision system is not merely describing the scene; it is interpreting it through the lens of the agent's goals. This is **task-conditioned perception**, and it is the thread that ties this course together: vision for agents is always vision in service of action.

The Norse god **Hǫðr** is blind; he sees nothing of the world around him. His brother Baldr is radiantly beautiful, seen by all. But Hǫðr is the one whose arrow — guided by Loki — kills Baldr, triggering the chain of events that leads to Ragnarök. The lesson for computer vision is dark but instructive: sight is not wisdom. An AI agent that can see everything but understands nothing — that processes pixels without interpreting their meaning — is Hǫðr with a camera: technically perceiving, but functionally blind. Vision must be integrated with understanding, and understanding must be integrated with purpose.

**Key Topics:**

- **Image formation:** Pinhole camera model, perspective projection, the loss of depth
- **Color:** RGB, HSV, LAB, color constancy, and the role of color in UI understanding
- **Preprocessing:** Normalization, augmentation, document rectification, super-resolution
- **Task-conditioned perception:** Vision in service of the agent's goals
- **Hǫðr's blindness:** Perception without understanding is functional blindness

**Required Reading:**

- Szeliski, R. *Computer Vision: Algorithms and Applications* (3rd ed., 2040), Chapters 1–2
- Forsyth, D. & Ponce, J. *Computer Vision: A Modern Approach* (4th ed., 2038), Chapters 1–2
- University of Yggdrasil TR: "Task-Conditioned Visual Perception for AI Agents" (2039)

**Discussion Questions:**

1. Perspective projection loses depth — every pixel corresponds to a ray, not a point. How does the visual system recover depth from a single image? What cues (shading, texture, occlusion, familiar size) are available, and how reliable are they?
2. UI elements (buttons, text fields) are defined by their function, not their appearance. Can a vision system detect a "button" without understanding what buttons do? What kind of training data would capture the functional definition of UI elements?
3. Hǫðr is blind but his action reshapes the cosmos. An AI agent with perfect visual perception but no understanding is Hǫðr — technically sighted, functionally blind. What must be added to a vision system so that it "understands" what it sees, not merely "detects" what is present?

---

### ᚢ Lecture 2: Image Classification — From Pixels to Categories

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Image classification is the foundational task of computer vision: given an image, assign it to one of K categories. Despite its apparent simplicity — "is this a cat or a dog?" — image classification has driven much of the architectural innovation in deep learning, from AlexNet (2012) to ConvNeXt-XXL (2040). For AI agents, classification is the first step in visual understanding: an agent that can recognize a "screenshot," a "chart," a "form," or a "photo" can route the image to the appropriate downstream processor.

The architecture of modern image classifiers follows a two-stage pattern: a **backbone** (feature extractor) that transforms the input image into a high-level feature representation, and a **head** (classifier) that maps the features to class probabilities. The backbone is typically a pre-trained CNN (ConvNeXt, EfficientNet) or vision transformer (ViT), and the head is a simple linear layer followed by softmax.

**ConvNeXt** (Liu et al., 2022) modernized the CNN by incorporating design principles from vision transformers: patchified stem (processing the image in 4×4 patches rather than pixel-by-pixel), larger kernels (7×7 instead of the traditional 3×3), inverted bottleneck (expanding channels in the middle of the block rather than contracting them), layer normalization instead of batch normalization, and GELU activations instead of ReLU. The result is a CNN that matches vision transformers in accuracy while retaining the efficiency and inductive biases of convolution. ConvNeXt-XXL (2040) achieves 91.2% top-1 accuracy on ImageNet-21K with 2.3B parameters, using a mixture-of-experts design that activates only 15% of parameters per input.

**Vision Transformers (ViT)** (Dosovitskiy et al., 2021) apply the transformer architecture directly to images. The image is divided into non-overlapping patches (e.g., 16×16 pixels), each patch is linearly projected into a token embedding, and these tokens are processed by a standard transformer encoder. A special [CLS] token at the beginning of the sequence is used for classification. ViTs lack the inductive biases of CNNs — translation equivariance and locality are not built into the architecture but must be learned from data. Initially, ViTs required enormous datasets (JFT-300M) to match CNN performance, but improved training recipes (DeiT, Touvron et al., 2021) and hybrid architectures (incorporating convolutional patch embeddings) have made ViTs competitive on smaller datasets. ViT-22B (2040) is the largest publicly documented vision transformer, with 22 billion parameters trained on 4 billion images.

**Training strategies** for image classification have evolved significantly. **Transfer learning** from models pre-trained on large datasets (ImageNet-21K, JFT-4B, the 2040 WebImage-50B corpus) is the default approach — few practitioners train classifiers from scratch. **Multi-label classification** handles images that belong to multiple categories simultaneously (a photo that is both "outdoor" and "contains person" and "sunset"), using sigmoid activations instead of softmax and binary cross-entropy loss. **Hierarchical classification** uses the tree structure of categories (e.g., "animal → mammal → canine → dog → golden retriever") to improve accuracy on fine-grained distinctions.

**Evaluation metrics** for classification extend beyond simple accuracy. **Top-k accuracy** (fraction of examples where the correct class is among the model's top k predictions) is standard for large-class problems (ImageNet has 1,000 classes; top-5 accuracy is often reported). **Precision, recall, and F1** are used when classes are imbalanced. **Confusion matrices** reveal which classes are confused with which, informing targeted data collection and augmentation.

For AI agents, classification serves as a **routing mechanism**: the agent classifies an incoming image as "screenshot," "photo," "chart," "document," or "meme," then routes it to the specialized processor for that type. Accuracy at this routing step is critical — a screenshot sent to the photo processor will be misinterpreted, and the downstream error may compound through the agent's reasoning chain.

The Norse rune **ᚦ (þurs)** — the rune of the thorn, the giant, the category-defining edge — represents classification. þurs is the rune of boundaries: this is inside; that is outside. Classification draws boundaries in the high-dimensional space of visual appearances, separating the manifold of "cat" images from the manifold of "dog" images. But boundaries can be sharp or fuzzy, right or wrong, just or unjust. A classifier that draws the boundary through the wrong place — classifying a wolf as a dog because it appears in a domestic setting — has failed the þurs test: the boundary must reflect the true structure of the world, not the accidents of the training data.

**Key Topics:**

- **Two-stage architecture:** Backbone (feature extraction) + head (classification)
- **ConvNeXt:** Modernized CNNs with transformer-inspired design
- **Vision Transformers:** Patchification, learned inductive biases, data hunger
- **Training strategies:** Transfer learning, multi-label, hierarchical classification
- **Evaluation:** Top-k accuracy, precision/recall, confusion matrices
- **Agent classification as routing:** Categorizing inputs for downstream processing
- **Þurs:** The rune of boundaries — classification as boundary-drawing

**Required Reading:**

- Dosovitskiy, A. et al. "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale" (2021), *ICLR*
- Liu, Z. et al. "A ConvNet for the 2020s" (2022), *CVPR*
- University of Yggdrasil Vision Lab: "ConvNeXt-XXL: A 2.3B Mixture-of-Experts Vision Backbone" (2040)

**Discussion Questions:**

1. ViTs lack the inductive biases of CNNs and must learn them from data. For a small dataset (1,000 images), which architecture would you expect to perform better, and why? How can you compensate for the lack of inductive bias in ViTs?
2. An AI agent classifies an image as "chart" but it's actually a "table" — both present structured data, but the downstream processing for charts (extracting trends) differs from tables (extracting specific values). How should the agent recover from this misclassification? Can the downstream processor detect the mismatch?
3. þurs is the rune of boundaries. A classifier draws boundaries between categories. But the boundary between "dog" and "wolf" is culturally and contextually determined, not just visual. How should a vision system handle categories whose boundaries are not purely visual?

---

### ᚦ Lecture 3: Object Detection — Finding and Naming What Is There

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Image classification answers "what is in this image?" Object detection answers "what objects are in this image, and where are they?" — it localizes objects with bounding boxes and classifies each. For AI agents, detection is essential: an agent viewing a screenshot must locate buttons, text fields, and icons; an agent monitoring a video feed must track people, vehicles, and equipment; an agent parsing a document must find tables, figures, and headings.

Object detection architectures have evolved through several generations:

**Two-stage detectors** (R-CNN family) first propose candidate regions (region proposals) that are likely to contain objects, then classify each region and refine its bounding box. **Faster R-CNN** (Ren et al., 2015) integrated the region proposal step into the network using a **Region Proposal Network (RPN)** — a small network that slides over the backbone's feature map and predicts, at each spatial position and for each of several anchor box shapes, whether an object is present and what its bounding box offset should be. The proposed regions are then pooled to a fixed size (RoI pooling) and classified. Two-stage detectors are accurate but slower than single-stage detectors — typical inference times are 100–200ms per image in 2040.

**Single-stage detectors** (YOLO, SSD, RetinaNet) skip the region proposal step and directly predict bounding boxes and class probabilities from a dense grid over the image. **YOLO** (You Only Look Once, Redmon et al., 2016) divides the image into an S×S grid; each grid cell predicts a fixed number of bounding boxes and class probabilities, and the predictions are filtered by non-maximum suppression. YOLO is fast — the 2040 YOLO-X achieves 200 FPS on 4K video — but historically less accurate than two-stage detectors for small objects. **RetinaNet** (Lin et al., 2017) introduced **focal loss**, which downweights the loss for easy negatives (background regions that are easily classified as "not an object"), addressing the class imbalance that had made single-stage detectors less accurate.

**Transformer-based detectors** (DETR, Deformable DETR, DINO) replace the hand-designed components of traditional detectors (anchor boxes, non-maximum suppression) with learned end-to-end transformers. **DETR** (Carion et al., 2020) uses a CNN backbone followed by a transformer encoder-decoder that outputs a fixed set of predictions (bounding box + class), trained with a bipartite matching loss (Hungarian algorithm) that finds the optimal one-to-one matching between predictions and ground-truth objects. DETR eliminates the need for anchor boxes and NMS but struggles with small objects and slow convergence. **Deformable DETR** (Zhu et al., 2021) addresses these issues with deformable attention — attending only to a small set of learned sampling points around each reference point, rather than to all spatial positions — improving convergence and small-object detection. DETR-X (2040) achieves state-of-the-art detection with 24 FPS on consumer GPUs.

**Key concepts** in detection include: **Intersection over Union (IoU)** — the area of overlap between predicted and ground-truth bounding boxes divided by the area of their union, used to determine whether a prediction is correct (typically, IoU > 0.5 is considered a match); **non-maximum suppression (NMS)** — eliminating redundant detections that overlap heavily (IoU > threshold), keeping only the highest-confidence detection for each object; **anchor boxes** — predefined bounding box shapes (aspect ratios and scales) that serve as starting points for prediction, simplifying the regression problem; and **feature pyramid networks (FPN)** — a top-down architecture that builds a pyramid of feature maps at multiple scales, enabling detection of objects at widely varying sizes.

For AI agents, detection serves specific needs: **UI element detection** locates buttons, text fields, checkboxes, sliders, and other interactive elements in screenshots, enabling the agent to interact with graphical interfaces. **Document layout detection** finds tables, figures, paragraphs, and headings in documents, enabling structured information extraction. **Person and face detection** enables the agent to reason about who is present in an image and to respect privacy constraints (blurring faces before storing or transmitting).

The Norse goddess **Skaði** — the huntress, who tracks her prey across the winter mountains — embodies detection. Skaði does not merely see the landscape; she finds what is within it — the tracks of the deer, the shape of the bear against the snow, the movement that betrays the hidden prey. Detection is Skaði's art: locating and naming the objects in the visual field, each one a potential target for action.

**Key Topics:**

- **Two-stage detectors:** R-CNN, Fast R-CNN, Faster R-CNN, RPN, RoI pooling
- **Single-stage detectors:** YOLO, SSD, RetinaNet, focal loss
- **Transformer-based detectors:** DETR, Deformable DETR, bipartite matching, DETR-X
- **Core concepts:** IoU, NMS, anchor boxes, feature pyramid networks
- **Agent applications:** UI element detection, document layout detection, person detection
- **Skaði's hunt:** Finding objects in the visual field — detection as the first step toward action

**Required Reading:**

- Ren, S. et al. "Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks" (2015), *NeurIPS*
- Carion, N. et al. "End-to-End Object Detection with Transformers" (2020), *ECCV*
- Redmon, J. et al. "You Only Look Once: Unified, Real-Time Object Detection" (2016), *CVPR*

**Discussion Questions:**

1. Anchor boxes encode prior knowledge about object shapes. What happens when the true object shapes differ dramatically from the anchor boxes — for example, detecting very long, thin objects (poles, wires) using anchors designed for compact objects? How can the detector adapt?
2. DETR eliminates anchor boxes and NMS, replacing them with a learned bipartite matching. What is the "knowledge" that DETR must learn that anchor boxes and NMS encode heuristically? Is the learned approach always better, or are there cases where heuristic knowledge is preferable?
3. Skaði tracks her prey across the landscape — detection in motion. How does video object detection differ from static image detection? What additional cues (temporal consistency, motion) are available, and how should they be used?

---

### ᚬ Lecture 4: Segmentation — Pixel-Perfect Understanding

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Object detection provides a coarse localization — a bounding box that encloses an object. Segmentation provides a precise localization — a pixel-level mask that delineates the object's exact boundary. For AI agents, segmentation enables detailed scene understanding: precisely extracting a chart from a screenshot, isolating a person from a background for privacy, or segmenting a document into its constituent regions (text blocks, figures, marginalia).

**Semantic segmentation** assigns every pixel in the image to a category (e.g., "sky," "road," "car," "person") without distinguishing between different instances of the same category — all cars are labeled "car," and there is no way to tell which pixels belong to which car. **Instance segmentation** assigns every pixel to a category *and* distinguishes between individual instances — car #1, car #2, car #3 — usually by combining object detection (finding each instance) with segmentation (masking each instance). **Panoptic segmentation** unifies semantic and instance segmentation: every pixel is assigned either to a "thing" class (with instance IDs, like individual cars) or a "stuff" class (without instance IDs, like sky or road).

**Fully Convolutional Networks (FCNs)** (Long et al., 2015) pioneered end-to-end semantic segmentation by converting classification networks into dense prediction networks. The fully-connected layers at the end of a classification CNN are replaced with 1×1 convolutions, and the spatial resolution is restored through **transposed convolutions** (also called deconvolutions) or **unpooling** layers. Skip connections from earlier layers (which have higher spatial resolution but lower semantic abstraction) to later layers (which have lower resolution but higher abstraction) combine fine spatial detail with coarse semantic information.

**U-Net** (Ronneberger et al., 2015) is the most widely used segmentation architecture, particularly in domains with limited training data. U-Net has a symmetric encoder-decoder structure: the encoder (downsampling path) extracts increasingly abstract features at decreasing spatial resolutions; the decoder (upsampling path) restores spatial resolution, and at each level, **skip connections** concatenate the encoder features at that resolution with the decoder features. This symmetric design enables precise localization while maintaining semantic context. U-Net was originally developed for biomedical image segmentation (cell boundaries) but has been adopted across domains. U-Net-2040 incorporates transformer blocks in the bottleneck and attention-gated skip connections for state-of-the-art performance.

**Mask R-CNN** (He et al., 2017) extends Faster R-CNN for instance segmentation by adding a small FCN branch that predicts a binary mask for each detected object, in parallel with the existing bounding box and classification branches. The **RoIAlign** layer replaces RoI pooling with bilinear interpolation, preserving spatial precision for mask prediction. Mask R-CNN is the standard instance segmentation architecture and forms the basis for many agent vision systems.

**SegFormer** (Xie et al., 2021) and **Mask2Former** (Cheng et al., 2022) apply transformer architectures to segmentation. SegFormer uses a hierarchical transformer encoder (producing multi-scale features, like a CNN) and a lightweight MLP decoder, achieving strong performance with a simple design. Mask2Former unifies semantic, instance, and panoptic segmentation within a single architecture by treating each segmentation task as mask classification with a transformer decoder.

For AI agents, segmentation has several critical applications. **UI element segmentation** precisely masks individual buttons, text fields, and icons, enabling the agent to interact with them (click within the mask boundaries) and to understand the spatial layout of the interface. **Document segmentation** separates text from figures from marginalia, enabling structured extraction (OCR on text regions, chart data extraction on figure regions). **Privacy-preserving segmentation** masks faces, license plates, and other personally identifiable information, enabling the agent to process images without storing sensitive visual data.

The Norse **vefnaðr** — the precise weaving of threads into a tapestry, where every thread has its designated place and the pattern emerges from the exact placement of each strand — is the metaphor for segmentation. A tapestry is not a collection of bounding boxes; it is a pixel-precise arrangement of colored threads. Segmentation is the weaver's art, assigning every pixel (every thread) to its proper category (its proper place in the pattern). The quality of the tapestry depends on the precision of the placement — a single mis-woven thread mars the pattern. So too with segmentation: a single misclassified pixel at an object boundary blurs the shape and degrades downstream processing.

**Key Topics:**

- **Semantic vs. instance vs. panoptic segmentation:** Categories, instances, and the unified view
- **FCN:** Converting classifiers to dense predictors, transposed convolutions, skip connections
- **U-Net:** Symmetric encoder-decoder, skip connections, biomedical origins
- **Mask R-CNN:** Instance segmentation via mask prediction branch, RoIAlign
- **Transformer segmentation:** SegFormer, Mask2Former, unified mask classification
- **Agent applications:** UI element masking, document parsing, privacy-preserving segmentation
- **Vefnaðr:** The weaver's art — pixel-precise assignment of every thread

**Required Reading:**

- Long, J. et al. "Fully Convolutional Networks for Semantic Segmentation" (2015), *CVPR*
- He, K. et al. "Mask R-CNN" (2017), *ICCV*
- Ronneberger, O. et al. "U-Net: Convolutional Networks for Biomedical Image Segmentation" (2015), *MICCAI*

**Discussion Questions:**

1. U-Net's skip connections concatenate high-resolution encoder features with decoder features. What information is carried by the encoder features, and what is carried by the decoder features? Why is concatenation better than addition for segmentation?
2. Panoptic segmentation unifies "thing" and "stuff" classes. What makes a class a "thing" vs. "stuff"? Is this distinction fundamental, or is it an artifact of how we label data?
3. Vefnaðr is the weaver's art — every thread in its place. A segmentation model assigns every pixel to a category. What happens at boundaries — pixels that contain a mixture of two categories (e.g., a pixel on the edge of a person, containing both person and background)? How should the model handle boundary ambiguity?

---

### ᚱ Lecture 5: Visual Reasoning — Beyond What Is There to What It Means

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Classification, detection, and segmentation answer questions of *what* and *where*. Visual reasoning answers questions of *why*, *how*, and *what if* — questions that require integrating visual perception with logical inference, commonsense knowledge, and task context. An AI agent that sees a "Submit" button must reason: is it enabled or disabled? If I click it, what will happen? Should I click it given the user's goal? These are visual reasoning questions, and they are the bridge between perception and action.

**Visual Question Answering (VQA)** is the canonical visual reasoning task: given an image and a natural language question about the image, produce the correct answer. Questions range from simple ("What color is the car?") to complex ("Is the person in the red shirt older than the person in the blue shirt, and why do you think so?"). VQA requires the integration of visual features (from a CNN or ViT) with language features (from a transformer), typically through **cross-modal attention** — the language tokens attend to the visual tokens, extracting the information relevant to the question. **ViLT** (Vision-and-Language Transformer, Kim et al., 2021) and **BLIP-3** (Bootstrapping Language-Image Pre-training, 2040) process image patches and text tokens jointly in a unified transformer, achieving state-of-the-art on VQA benchmarks.

**Visual grounding** links language to specific regions in an image. Given a referring expression ("the red mug on the left side of the table"), the model must localize the referenced object — typically by predicting a bounding box or segmentation mask. Visual grounding is essential for AI agents that must act on visual instructions: "click the submit button" requires grounding "the submit button" to a specific region of the screenshot. **MDETR** (Kamath et al., 2021) and **Grounding DINO-2** (2040) unify detection and grounding by training detectors on referring expressions rather than (or in addition to) class labels.

**Spatial reasoning** involves understanding the spatial relationships between objects — above, below, left of, right of, inside, touching. The **CLEVR** dataset (Johnson et al., 2017) was designed to test spatial reasoning in isolation, with synthetic images of simple geometric shapes and questions like "What is the color of the sphere to the left of the large metal cube?" Modern models achieve near-perfect accuracy on CLEVR, but spatial reasoning in natural images — with occlusions, unusual viewpoints, and ambiguous object boundaries — remains challenging.

**Scene graph generation** produces a structured representation of an image as a graph: nodes are objects, edges are relationships between objects ("person riding horse," "cup on table"). Scene graphs provide a symbolic representation that can be reasoned about with graph algorithms, bridging the gap between visual perception and logical reasoning. For AI agents, a scene graph of a screenshot ("button labeled 'Submit' is inside form at bottom right") provides a structured representation that the agent's reasoning module can manipulate.

**Causal visual reasoning** goes beyond association to causation. A model that learns that "wet ground" is associated with "umbrellas" may answer VQA questions correctly, but it doesn't understand that rain causes wet ground and that people carry umbrellas because of rain. Causal reasoning enables counterfactual questions: "What would happen if the glass were knocked over?" Answering such questions requires a causal model of the physical and social world — a model that current vision-language systems approximate through statistical patterns but do not genuinely possess.

For AI agents, visual reasoning is the difference between seeing and understanding. An agent that can detect a "Submit" button but cannot reason about whether submitting is appropriate given the task context is an agent that sees but does not understand. Visual reasoning integrates perception with the agent's goals, knowledge, and reasoning capabilities — it is the bridge from the visual world to the world of action.

The Norse **rúnar** — runes — are not merely letters but carriers of meaning that must be interpreted. A rune carved on a stone is an image (detection), but its meaning is not in its shape but in its reading (interpretation). **Óðinn's discovery of the runes** — hanging on Yggdrasil for nine nights, wounded, until the runes revealed themselves — is the myth of visual reasoning. The runes were always there, but Óðinn had to suffer to understand them — to move from perception to meaning. So too with visual reasoning: the pixels are the runes, and the agent must do the difficult work of interpretation to understand what they mean, not just what they are.

**Key Topics:**

- **Visual Question Answering (VQA):** Cross-modal attention, ViLT, BLIP-3, answer types
- **Visual grounding:** Referring expressions, MDETR, Grounding DINO-2
- **Spatial reasoning:** CLEVR, spatial relationships, occlusion and ambiguity
- **Scene graphs:** Structured symbolic representation, nodes and edges, reasoning with graphs
- **Causal visual reasoning:** Associative vs. causal inference, counterfactuals
- **Agent integration:** From perception to understanding to action
- **Óðinn's runes:** Interpretation beyond perception — the work of understanding

**Required Reading:**

- Johnson, J. et al. "CLEVR: A Diagnostic Dataset for Compositional Language and Elementary Visual Reasoning" (2017), *CVPR*
- Kim, W. et al. "ViLT: Vision-and-Language Transformer Without Convolution or Region Supervision" (2021), *ICML*
- Kamath, A. et al. "MDETR — Modulated Detection for End-to-End Multi-Modal Understanding" (2021), *ICCV*

**Discussion Questions:**

1. VQA models often exploit dataset biases — for example, answering "2" to "how many...?" questions because the training data is skewed. How can you design benchmarks that truly test visual reasoning rather than statistical shortcuts? How can models be trained to avoid these shortcuts?
2. Visual grounding links language to regions. But what about negative references — "the button that is NOT red"? What about abstract references — "the most important part of this image"? Are these fundamentally harder, or do they require different architectures?
3. Óðinn hung on Yggdrasil to discover the runes — meaning required sacrifice. What "sacrifice" (computational cost, data curation, architectural complexity) is required for an AI agent to move from visual perception to genuine visual reasoning?

---

### ᚷ Lecture 6: Video Understanding — Motion, Time, and Action

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Video is the temporal extension of images — a sequence of frames that captures motion, change, and action. For AI agents, video understanding is essential for tasks that unfold over time: processing screen recordings (user demonstrates a workflow), monitoring video feeds (security, safety compliance), analyzing sports footage (performance analysis), and understanding video calls (multimodal conversation). Video adds the temporal dimension, and with it comes new challenges: motion estimation, temporal consistency, action recognition, and efficient processing of long sequences.

**Optical flow** estimates the apparent motion of pixels between consecutive frames — for each pixel in frame *t*, where did it move in frame *t+1*? The fundamental assumption is **brightness constancy** — the brightness of a surface point is (approximately) constant as it moves across frames. Optical flow is computed by solving the **optical flow constraint equation**: *I(x,y,t) = I(x+u, y+v, t+1)*, where *(u, v)* is the flow vector at pixel *(x, y)*. Expanding via Taylor series: *Iₓu + Iᵧv + Iₜ = 0*, the **aperture problem** — from a single pixel, only the component of motion perpendicular to the local edge can be determined. The full flow field requires additional smoothness constraints (Horn-Schunck, 1981) or learning-based approaches. Modern optical flow models (RAFT, 2020; FlowFormer++, 2040) use iterative refinement with learned feature matching, achieving sub-pixel accuracy on challenging scenes.

**Action recognition** classifies a short video clip (typically 1–10 seconds) into an action category: "walking," "jumping," "opening a door," "clicking a button." Architectures for action recognition fall into three families:
- **3D CNNs** (C3D, I3D, SlowFast) extend 2D convolutions into the temporal dimension with 3D kernels (e.g., 3×3×3 filters that span spatial and temporal dimensions). The **SlowFast** architecture (Feichtenhofer et al., 2019) processes video in two parallel pathways: a slow pathway (low frame rate, high spatial resolution) captures spatial semantics (objects, scenes), and a fast pathway (high frame rate, low spatial resolution) captures motion (rapid changes, fine temporal structure). The two pathways are fused through lateral connections.
- **Two-stream networks** (Simonyan & Zisserman, 2014) process RGB frames (spatial stream) and optical flow (temporal stream) in separate CNNs, fusing the predictions at the end. The spatial stream captures appearance ("what does this look like?"); the temporal stream captures motion ("what is moving, and how?"). Two-stream networks explicitly model motion, which is beneficial when training data is scarce.
- **Video transformers** (TimeSformer, VideoMAE, ViViT) apply the transformer architecture to video, treating the sequence of frames as a sequence of tokens. **TimeSformer** (Bertasius et al., 2021) compares different attention schemes — space-only (each frame independently), joint space-time (attention across all patches in all frames), and divided space-time (attention within each frame followed by attention across frames at each spatial location). Divided space-time attention offers the best accuracy-efficiency tradeoff. VideoMAE (Tong et al., 2022) applies masked autoencoding to video, masking 90% of patches and training the model to reconstruct them — a self-supervised approach that achieves competitive performance with minimal labeled data.

**Temporal action localization** extends action recognition to untrimmed videos of arbitrary length, identifying not just *what* actions occur but *when* they start and end. This is the temporal analog of object detection: finding temporal segments (start time, end time) and classifying them. **ActionFormer** (Zhang et al., 2022) and its 2040 successors use transformer-based architectures to predict action boundaries and categories from long video sequences.

**Video understanding for AI agents** encompasses practical capabilities: **screen recording analysis** (understanding a user's workflow from a screen recording — what buttons they clicked, what menus they navigated, what errors they encountered), **video call processing** (tracking who is speaking, reading facial expressions, identifying presented content), and **surveillance and monitoring** (detecting safety violations, counting people, tracking objects across cameras).

The Norse myth of **the wolves Skǫll and Hati** — who chase the sun and moon across the sky, driving the passage of time — is the myth of video understanding. The frames are the positions of the sun and moon at each moment; the wolves are the forces of change that move from frame to frame. Understanding a video is understanding the chase — knowing not just where the sun is now, but where it was a moment ago, how fast it is moving, and where the wolf will catch it. The temporal dimension is the chase, and the agent must track it across every frame.

**Key Topics:**

- **Optical flow:** Brightness constancy, aperture problem, Horn-Schunck, RAFT, FlowFormer++
- **Action recognition:** 3D CNNs (SlowFast), two-stream networks, video transformers (TimeSformer, VideoMAE)
- **Temporal action localization:** Untrimmed videos, start/end times, ActionFormer
- **Agent applications:** Screen recording analysis, video call processing, surveillance monitoring
- **Skǫll and Hati:** The chase across frames — time as the driving force of change

**Required Reading:**

- Feichtenhofer, C. et al. "SlowFast Networks for Video Recognition" (2019), *ICCV*
- Bertasius, G. et al. "Is Space-Time Attention All You Need for Video Understanding?" (2021), *ICML*
- Teed, Z. & Deng, J. "RAFT: Recurrent All-Pairs Field Transforms for Optical Flow" (2020), *ECCV*

**Discussion Questions:**

1. Optical flow assumes brightness constancy — that a surface point has the same brightness across frames. This assumption is violated by lighting changes, shadows, and specular reflections. How do modern optical flow models handle these violations? Should they learn invariances to lighting, or should they model lighting explicitly?
2. SlowFast processes video at two frame rates — slow for semantics, fast for motion. Why is this dual-pathway design effective? Could a single pathway at an intermediate frame rate achieve the same performance? What information is gained by the explicit separation?
3. Skǫll and Hati chase the sun and moon — the frame-by-frame progression of time. An agent watching a screen recording sees a sequence of frames. How does the agent know when an action starts and ends? What visual cues mark the boundaries of actions in a continuous stream?

---

### ᚺ Lecture 7: 3D Vision — Depth, Geometry, and the Structure of Space

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

The world is three-dimensional; images are two-dimensional. Recovering 3D structure from 2D images — **3D vision** — is the most ambitious goal of computer vision, and it is increasingly relevant for AI agents that operate in physical environments: robots, drones, augmented reality systems, and agents that reason about spatial layouts.

**Depth estimation** predicts the distance from the camera to each pixel in the image — a "depth map" of the same resolution as the input image. **Monocular depth estimation** does this from a single image, using learned priors about object sizes, scene layout, and perspective cues. **MiDaS** (Ranftl et al., 2020) and **Depth Anything v2** (2040) are the state-of-the-art monocular depth estimators, trained on massive datasets of paired images and depth maps (from stereo, structured light, or LIDAR). Monocular depth is inherently ambiguous — a small object close to the camera can produce the same image as a large object far away — so the model must rely on contextual cues (familiar object sizes, ground plane geometry, atmospheric perspective) to resolve the ambiguity.

**Stereo vision** estimates depth from two calibrated cameras with a known baseline (distance between them). The **disparity** — the horizontal shift of a scene point between the left and right images — is inversely proportional to depth: *d = fB / disparity*, where *f* is focal length and *B* is baseline. Stereo matching — finding for each pixel in the left image its corresponding pixel in the right image — is a classic correspondence problem. Traditional approaches used block-matching and dynamic programming; modern approaches (PSMNet, LEAStereo, RAFT-Stereo) use deep learning to compute matching costs and aggregate them into disparity maps. Stereo provides metric depth (in meters, not relative depth) when the camera calibration is known.

**Multi-view stereo (MVS)** extends stereo to many views from different positions, producing dense 3D reconstructions. **Structure from Motion (SfM)** simultaneously estimates camera poses and sparse 3D point clouds from a collection of images — the technology behind photogrammetry and 3D scanning. **Neural Radiance Fields (NeRF)** (Mildenhall et al., 2020) represent a scene as a continuous volumetric function mapping 3D position and viewing direction to color and density, trained from a set of posed images. NeRF produces photorealistic novel views that are indistinguishable from photographs, bridging the gap between 3D reconstruction and image synthesis. **3D Gaussian Splatting** (Kerbl et al., 2023) achieves real-time novel view synthesis by representing scenes as clouds of 3D Gaussians, enabling interactive exploration of reconstructed environments.

**SLAM (Simultaneous Localization and Mapping)** is the technology that enables agents to build a map of an unknown environment while simultaneously tracking their own location within it. Visual SLAM uses camera images as the primary sensor. **ORB-SLAM3** (Campos et al., 2021) and its 2040 deep-learning-augmented successors track sparse visual features, estimate camera pose, and build a globally consistent map in real time, even in challenging conditions with motion blur, dynamic objects, and large-scale environments. SLAM is foundational for autonomous drones, robot vacuums, and AR headsets — any agent that must understand its position relative to the physical world.

For AI agents, 3D vision enables **spatial reasoning**: understanding that one object is behind another (occlusion), that a surface is slanted (not suitable for placing an object), that a gap is wide enough to pass through. An agent controlling a robot arm must understand the 3D position of objects to grasp them. An agent guiding a user through a physical task with AR overlays must register virtual annotations to the 3D geometry of the scene.

The Norse **Iðavǫllr** — the shining plain where the gods meet and where the survivors of Ragnarök will build a new world — is the spatial metaphor for 3D vision. Iðavǫllr is a place, not an image. It has depth, extent, and geometry — you can stand on it, walk across it, build upon it. 3D vision reconstructs Iðavǫllr from the flat images of the eye: it recovers the plain from the photograph, the space from the surface, the world from its projections.

**Key Topics:**

- **Monocular depth:** MiDaS, Depth Anything v2, context-dependent ambiguity resolution
- **Stereo vision:** Disparity, baseline, correspondence problem, RAFT-Stereo
- **Multi-view reconstruction:** SfM, NeRF, 3D Gaussian Splatting
- **SLAM:** Simultaneous localization and mapping, ORB-SLAM3, real-time applications
- **Agent applications:** Spatial reasoning, robotic manipulation, AR registration
- **Iðavǫllr:** The shining plain — depth, space, and the world as a place to act

**Required Reading:**

- Mildenhall, B. et al. "NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis" (2020), *ECCV*
- Kerbl, B. et al. "3D Gaussian Splatting for Real-Time Radiance Field Rendering" (2023), *ACM SIGGRAPH*
- Campos, C. et al. "ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial and Multi-Map SLAM" (2021), *IEEE T-RO*

**Discussion Questions:**

1. Monocular depth estimation is inherently ambiguous — scale is unknown. What are the consequences of this ambiguity for AI agents that need to reason about physical space? How can the agent recover metric scale from other cues?
2. NeRF represents a scene as a continuous volumetric function, while 3D Gaussian Splatting represents it as discrete primitives. What are the tradeoffs between continuous and discrete scene representations? When is each preferred?
3. Iðavǫllr is a place — a 3D space where things happen. How does an agent's reasoning change when it has a 3D model of the world versus only 2D images? What capabilities are uniquely enabled by 3D understanding?

---

### ᚾ Lecture 8: Document Understanding — Reading the Written World

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Documents — scanned pages, PDFs, screenshots of forms, photographs of receipts — are a specialized but enormously important class of images for AI agents. An agent that can read and understand documents can process invoices, extract information from forms, analyze contracts, and navigate bureaucratic systems. Document understanding combines computer vision with natural language processing and layout analysis, making it a uniquely challenging and uniquely valuable capability.

**Optical Character Recognition (OCR)** converts images of text into machine-readable text. Traditional OCR pipelines involved: binarization (thresholding to black and white), connected component analysis (finding letters), character segmentation, and character classification. Modern OCR uses deep learning end-to-end: **Tesseract 5** (Smith et al., 2022, LSTM-based) and **TrOCR** (Transformer-based OCR, Li et al., 2023) process a full text line image and output the corresponding character sequence, eliminating the need for explicit character segmentation. **Vision-language models** (GPT-5o, Claude 5 Vision) achieve OCR as a byproduct of their general visual understanding, often outperforming dedicated OCR engines on challenging text (curved, stylized, low-resolution) through their contextual understanding of language.

**Document layout analysis** identifies the structural elements of a document: paragraphs, headings, tables, figures, lists, footnotes, headers, footers, and marginalia. **LayoutParser** (Shen et al., 2021) and **DiT** (Document Image Transformer, 2040) use detection and segmentation models trained on document datasets (PubLayNet, DocLayNet) to parse the layout structure. The output is a hierarchical representation: the document contains sections; sections contain paragraphs and figures; figures contain subfigures and captions. For AI agents, layout analysis enables structured extraction: the agent can locate the "total" field in an invoice, find the "signature" line in a contract, or extract all tables from a research paper.

**Table understanding** extracts the logical structure of tables — row headers, column headers, data cells, and the relationships between them — from images of tables. Tables are notoriously difficult because their logical structure (which cells are related) is only partially reflected in their visual structure (grid lines, spacing, alignment). **Table Transformer** (Smock et al., 2022) and **TableGPT-3** (2040) use object detection to find table regions and specialized architectures to extract the cell structure and relationships. Table extraction is critical for agents that process financial reports, scientific papers, and database exports.

**Handwriting recognition** addresses the special challenges of handwritten text — variable letter shapes, connected characters, inconsistent spacing. The **IAM Handwriting Database** and **RIMES** datasets have driven progress, but handwriting recognition remains significantly harder than printed text OCR. For agents processing historical documents, medical prescriptions, or handwritten notes, handwriting recognition is essential but error-prone, requiring careful confidence calibration and human-in-the-loop verification.

**Information extraction** from documents goes beyond recognizing text and layout to understanding the semantic content: extracting entities (names, dates, amounts), relations (who paid whom, what was purchased), and events (a contract was signed, an invoice was paid). This is the bridge from document understanding to task completion — an agent that processes an invoice doesn't just read it; it extracts the amount, due date, and payee, and uses that information to schedule a payment.

The Norse **rúnakefli** — rune-sticks, wooden sticks carved with runic messages and used for communication, record-keeping, and legal documentation — are the ancestors of modern documents. Reading a rúnakefli required not just recognizing the runes (OCR) but understanding their meaning in context (information extraction): is this a contract, a curse, a love letter, or a receipt? Document understanding is the art of reading rúnakefli — of extracting structured meaning from written marks, whether carved in wood or printed on paper.

**Key Topics:**

- **OCR:** Tesseract 5, TrOCR, vision-language model OCR, text in the wild
- **Layout analysis:** LayoutParser, DiT, hierarchical document structure
- **Table understanding:** Table Transformer, cell structure, logical vs. visual structure
- **Handwriting recognition:** IAM, RIMES, deep learning for grapheme-to-text
- **Information extraction:** NER, relation extraction, event extraction from documents
- **Rúnakefli:** Reading the marks — from runic sticks to modern documents

**Required Reading:**

- Li, M. et al. "TrOCR: Transformer-based Optical Character Recognition with Pre-trained Models" (2023), *AAAI*
- Shen, Z. et al. "LayoutParser: A Unified Toolkit for Deep Learning Based Document Image Analysis" (2021), *ICDAR*
- Smock, B. et al. "Table Transformer: Table Detection, Structure Recognition and Functional Analysis" (2022), *ECCV*

**Discussion Questions:**

1. Vision-language models (like GPT-5o) perform OCR better than dedicated OCR engines on challenging text. When would you still use a dedicated OCR engine? What advantages do dedicated engines retain?
2. Table understanding requires inferring logical structure from visual layout — a difficult inverse problem. Why is this hard? What visual cues signal logical structure, and when do those cues fail?
3. Rúnakefli encoded messages, contracts, and records. A modern document encodes similar information but in standardized formats. How should an AI agent adapt its extraction strategy based on the type of document? What prior knowledge about document types should be built into the system vs. learned from data?

---

### ᛁ Lecture 9: Vision for UI Agents — Seeing and Interacting with Interfaces

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

An AI agent that can interact with graphical user interfaces — clicking buttons, filling forms, navigating menus — must see those interfaces. UI vision is a specialized subfield of computer vision that deals with the unique properties of interfaces: they are designed, not natural; they use consistent visual languages; and their elements have functional meanings (buttons are for clicking, text fields are for typing) that go beyond their visual appearance.

**UI element detection** locates and classifies the interactive components of a user interface: buttons, text fields, checkboxes, radio buttons, dropdown menus, sliders, tabs, links, and scrollbars. Unlike natural images, UI elements follow predictable design patterns — buttons are typically rectangular, text fields have an inset border, dropdowns have a downward-pointing arrow — and exploiting these patterns improves detection accuracy. **UIED** (UI Element Detection, 2020) and **WidgetBERT** (2040) use detection and classification models trained on large-scale UI datasets (Rico, WebUI-100K) to identify elements in screenshots.

**Screen parsing** (or UI parsing) produces a structured representation of a screenshot: a tree of UI elements, each with its type, bounding box, text content, and state (enabled/disabled, selected/unselected). The **Document Object Model (DOM)** is the "ground truth" representation for web pages, and screen parsing aims to reconstruct a DOM-like structure from pixels alone. This is essential for agents that interact with opaque interfaces — desktop applications, mobile apps, and remote desktops where the programmatic interface (accessibility tree) is unavailable. **Pix2Struct** (Lee et al., 2023) and **Screen2DOM-v2** (2040) convert screenshots directly into structured representations that an agent can reason about and act upon.

**UI state understanding** goes beyond detection to recognize the *state* of each element: is this button enabled or disabled? Is this checkbox checked or unchecked? Is this text field focused? Is this progress bar at 30% or 70%? State understanding requires fine-grained visual analysis of element appearance — the grayed-out look of a disabled button, the check mark in a checked checkbox, the filled portion of a progress bar. For agents, state understanding is critical: clicking a disabled button is an error; skipping a required unchecked checkbox is an error.

**Action grounding** maps agent actions (in natural language or structured form) to specific UI elements and interaction types. The instruction "click the Submit button" must be grounded to the specific bounding box of the "Submit" button in the current screenshot. The instruction "type 'hello' in the search field" must be grounded to the text field and to the action of typing. Action grounding combines visual grounding (Lecture 5) with action understanding, and it is the final step before the agent executes an action.

**Accessibility tree integration** provides a best-of-both-worlds approach: when the accessibility tree (the programmatic representation of the UI structure) is available, the agent queries it for precise element locations, types, and states, using vision only as a fallback or for verification. When the accessibility tree is unavailable (as with remote desktops, legacy applications, or video streams of mobile devices), vision is the primary interface. The **Hybrid UI Agent** architecture (UoY Agent Systems Group, 2039) uses vision as the universal fallback: try the accessibility tree first; if unavailable or unreliable, fall back to vision; cross-validate accessibility claims with visual evidence.

**Challenges in UI vision** include: **cross-platform variation** (a button on Windows looks different from a button on macOS, which looks different from a button on iOS), **theme variation** (dark mode vs. light mode, custom themes), **density variation** (4K monitors vs. 720p displays), **occlusion** (dropdown menus overlapping other elements, modals covering the background), and **dynamic content** (animations, loading spinners, auto-complete suggestions).

The Norse **Smiðr** — the craftsman who builds functional objects: a chair for sitting, a cup for drinking, a key for unlocking — is the designer of user interfaces. Smiðr's objects have form that follows function: the handle of the cup is shaped for the hand, the teeth of the key are shaped for the lock. UI elements are Smiðr's creations: their visual form signals their function. The agent that can see the form and infer the function — that can look at a pill-shaped rounded rectangle with text inside and know it is a button — understands Smiðr's design language. Vision for UI agents is learning to read that language.

**Key Topics:**

- **UI element detection:** UIED, WidgetBERT, design-pattern-based detection
- **Screen parsing:** DOM reconstruction from pixels, Pix2Struct, Screen2DOM-v2
- **UI state understanding:** Enabled/disabled, checked/unchecked, focused, progress
- **Action grounding:** Mapping instructions to UI elements and interaction types
- **Hybrid approaches:** Accessibility tree + vision, cross-validation, universal fallback
- **Smiðr's design language:** Form following function — reading the visual language of interfaces

**Required Reading:**

- Lee, K. et al. "Pix2Struct: Screenshot Parsing as Pretraining for Visual Language Understanding" (2023), *ICML*
- University of Yggdrasil Agent Systems Group, "The Hybrid UI Agent: Integrating Accessibility Trees and Computer Vision" (2039)
- Liu, T. et al. "A Large-Scale Benchmark for Understanding UI Elements" (2022), *NeurIPS*

**Discussion Questions:**

1. UI elements follow predictable design patterns, but every application has its own visual style. How should a vision system balance learned expectations (buttons are rectangular) against visual evidence (this application uses circular buttons)? When should the system trust its priors, and when should it trust its eyes?
2. The accessibility tree provides perfect structural information when available. Why isn't it always available? What kinds of applications and contexts lack accessibility trees, and how should an agent adapt?
3. Smiðr designs objects where form follows function. A button looks clickable because it is designed to invite clicking. But what about deceptive design — a "Download" button that's actually an ad, a "Close" button that's styled to look disabled? How should an agent handle the gap between apparent function and actual function?

---

### ᛃ Lecture 10: Generative Vision — Creating and Editing Images

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

So far, we have focused on vision for understanding — taking images as input and producing interpretations as output. Generative vision reverses the flow: producing images as output from interpretations (or other images, or random noise) as input. For AI agents, generative vision enables multimodal communication (the agent can create diagrams to explain concepts, generate visual examples, or edit images to illustrate modifications), creative assistance (helping users design, prototype, and visualize), and data augmentation (generating synthetic training images for computer vision models).

The major paradigms of generative vision were introduced in AI201 (Lecture 6). Here, we focus on the capabilities that are specifically relevant to AI agents.

**Text-to-image generation** produces an image from a natural language description. **Stable Diffusion 4** (2024–2040, a family of models maintained by Stability AI and the open-source community) uses a latent diffusion model: the diffusion process operates in a compressed latent space (learned by a VAE), reducing computational cost while maintaining quality. **DALL-E 5** (OpenAI, 2038) and **Imagen 4** (Google, 2039) use variants of diffusion with increasingly sophisticated language conditioning (T5-XXL, then PALM-3, then Gemini-Ultra as text encoders). Text-to-image models in 2040 can generate photorealistic images at 8K resolution with precise control over composition, lighting, style, and content — though they still struggle with text rendering within images (generating legible, correctly spelled text) and with compositional prompts ("a red cube to the left of a blue sphere" may produce a blue cube and a red sphere).

**Image editing** modifies an existing image according to natural language instructions. **InstructPix2Pix** (Brooks et al., 2023) and **MagicEdit-X** (2040) enable commands like "make the sky more dramatic," "remove the person in the background," "change the car color to red," or "add a hat to the person." Image editing combines the generative capabilities of diffusion models with the spatial precision of segmentation — the model must understand which pixels to modify and how. For AI agents, image editing enables practical assistance: editing a user's photo to improve composition, removing a distracting element from a screenshot, or creating a visual mockup with the user's requested changes.

**Image inpainting and outpainting** are specialized forms of editing. Inpainting fills in missing or masked regions of an image — for example, removing an object and generating plausible background to fill the hole. Outpainting extends an image beyond its original boundaries, generating new content that is consistent with the existing content. Both rely on the model's understanding of scene structure and its ability to generate plausible continuations. For agents, inpainting can remove sensitive information (faces, license plates) from images while preserving the rest of the scene.

**Controlled generation** enables precise control over the generated image beyond the text prompt. **ControlNet** (Zhang et al., 2023) adds spatial conditioning signals — edge maps, depth maps, pose skeletons, segmentation masks — to a pre-trained diffusion model, allowing users to control the composition and structure of the output while the model fills in the photorealistic details. For AI agents, ControlNet enables the generation of images with specific spatial layouts — a diagram with a particular arrangement, a UI mockup with specific element positions — where the agent provides the spatial structure and the model provides the visual style.

**Video generation** extends generative vision to the temporal domain. **Sora 3** (OpenAI, 2040) and **VideoPoet-X** (Google, 2040) generate coherent video clips from text descriptions, with frame-to-frame consistency, realistic motion, and the ability to extend or interpolate between videos. For AI agents, video generation is useful for explaining dynamic processes ("here's how to assemble the furniture"), creating demonstrations, and generating synthetic training data for video understanding models.

The Norse myth of the **Sons of Ivaldi** — the dwarves who crafted treasures for the gods: Sif's golden hair (which grew naturally), Skíðblaðnir (the ship that always had a favorable wind and could be folded into a pocket), and Gungnir (Óðinn's spear that never missed its mark) — is the myth of generative vision. The dwarves created objects from descriptions: "make hair for Sif" → golden hair that grows. "Make a ship" → a ship that sails and folds. "Make a spear" → a spear that never misses. Generative vision is the Sons of Ivaldi's forge: shaping pixels from words, creating visual objects from verbal descriptions, bringing the imagined into the visible.

**Key Topics:**

- **Text-to-image:** Stable Diffusion 4, DALL-E 5, Imagen 4, latent diffusion
- **Image editing:** InstructPix2Pix, MagicEdit-X, text-guided modification
- **Inpainting/outpainting:** Filling missing regions, extending boundaries
- **Controlled generation:** ControlNet, spatial conditioning, structural control
- **Video generation:** Sora 3, VideoPoet-X, temporal coherence
- **Sons of Ivaldi:** Creating objects from descriptions — the forge of generative vision

**Required Reading:**

- Brooks, T. et al. "InstructPix2Pix: Learning to Follow Image Editing Instructions" (2023), *CVPR*
- Zhang, L. et al. "Adding Conditional Control to Text-to-Image Diffusion Models" (2023), *ICCV*
- Rombach, R. et al. "High-Resolution Image Synthesis with Latent Diffusion Models" (2022), *CVPR*

**Discussion Questions:**

1. Text-to-image models struggle with compositional prompts (multiple objects in specified spatial relationships). Is this a fundamental limitation of generating from text, or can it be solved with better architectures and training data? How does the model represent spatial relationships internally?
2. ControlNet enables precise spatial control over generation. What kinds of control signals are most useful for AI agents? What control signals are difficult to provide (e.g., emotional tone, narrative flow)?
3. The Sons of Ivaldi crafted treasures from descriptions — "make hair that grows." But their creations exceeded the descriptions — the hair grew, the ship folded, the spear never missed. Does generative vision ever exceed the prompt in similarly surprising ways? Is emergent capability in generative models analogous to dwarven craftsmanship?

---

### ᛇ Lecture 11: Vision Robustness and Safety — Seeing Truly in an Adversarial World

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

Computer vision models are fragile in ways that human vision is not. A stop sign with a few carefully placed stickers becomes invisible to a traffic-sign detector. A panda photograph with imperceptible pixel perturbations is classified as a gibbon with 99% confidence. A medical image with unnoticeable noise yields a different diagnosis. For AI agents whose actions depend on visual input, these failures are not academic curiosities — they are safety-critical vulnerabilities that adversarial actors can exploit.

**Adversarial examples** are inputs intentionally designed to cause a model to make a mistake. For an image classifier, an adversarial example *x' = x + δ* is crafted to be visually indistinguishable from the original *x* (||δ|| < ε for some small ε) while causing a different classification: *f(x') ≠ f(x)*. The **Fast Gradient Sign Method (FGSM)** (Goodfellow et al., 2015) generates adversarial examples in a single step: *x' = x + ε · sign(∇ₓ L(f(x), y))*, where the perturbation follows the gradient of the loss to maximally increase the loss. The **Projected Gradient Descent (PGD)** attack (Madry et al., 2018) extends FGSM with multiple small steps, producing stronger attacks. **Carlini & Wagner (C&W)** attacks use optimization to find minimal perturbations that cause misclassification.

**Adversarial defenses** attempt to make models robust to adversarial examples. **Adversarial training** augments the training data with adversarial examples, forcing the model to learn to classify them correctly. This is the most effective defense but reduces clean accuracy and is computationally expensive. **Certified defenses** (randomized smoothing, formal verification) provide mathematical guarantees that a model's prediction will not change for any perturbation smaller than a certified radius. Certified defenses are appealing for safety-critical applications but are currently limited to relatively small certified radii and incur significant computational overhead.

**Distribution shift** is a broader challenge than adversarial examples. A vision model trained on clear, well-lit photographs may fail catastrophically on images affected by rain, snow, fog, low light, motion blur, or unusual camera angles — not because the images are adversarial, but because they lie outside the training distribution. **Domain generalization** and **test-time adaptation** aim to make models robust to distribution shift without requiring labeled data from the target domain. **AugMix** (Hendrycks et al., 2020) and **DeepAugment** (Hendrycks et al., 2021) use aggressive data augmentation during training to improve robustness to common corruptions. Test-time adaptation adjusts the model's batch normalization statistics or applies self-supervised objectives at inference time to adapt to the target distribution.

**Out-of-distribution (OOD) detection** identifies inputs that are significantly different from the training distribution, so that the model can either refuse to make a prediction or flag the input for human review. OOD detection methods include: **maximum softmax probability** (low confidence = OOD), **energy-based scores** (Liu et al., 2020, using the log-sum-exp of logits), and **Mahalanobis distance** (measuring distance from class-conditional Gaussians in feature space). For AI agents, OOD detection is a critical safety mechanism: an agent should know when it is seeing something it was not trained to handle, rather than confidently misclassifying it.

**Bias in vision models** (discussed ethically in AI107, Lecture 3) manifests technically as systematic errors on specific demographic groups. Facial recognition systems have significantly higher error rates on darker-skinned individuals; object detectors miss pedestrians with darker skin tones more often; activity recognition models associate certain activities with certain demographics based on training data biases. Mitigating these biases requires interventions at every stage: diverse and representative data collection, bias-aware training objectives, and rigorous disaggregated evaluation.

For AI agents, robustness failures are especially dangerous because they can compound through the agent's reasoning loop. An agent that misperceives a visual input may take a sequence of actions based on that misperception, and each action may make the situation worse. **Perception verification** — cross-checking visual interpretations against other modalities (does the accessibility tree agree with the visual detection?), against temporal consistency (does this object persist across frames?), and against common sense (does it make sense for a "Submit" button to be located there?) — is an essential safety practice for agent vision systems.

The Norse myth of **Baldr's invulnerability** — how Frigg extracted oaths from every object in creation not to harm Baldr, except the mistletoe, which she deemed too young to swear — is the myth of robustness. Baldr was protected against everything except the one thing that was overlooked. An adversarially trained model protected against PGD attacks may be vulnerable to C&W attacks; a model robust to common corruptions may fail on a novel corruption; a model tested on one demographic may fail on another. Robustness is Baldr's lesson: the vulnerability is in the thing you didn't think to protect against. The only defense is to never assume the model is safe — to test continuously, with diverse and adversarial inputs, and to design systems that are resilient to perception failures, not merely models that are robust to known attacks.

**Key Topics:**

- **Adversarial examples:** FGSM, PGD, C&W attacks, imperceptible perturbations
- **Adversarial defenses:** Adversarial training, certified defenses, robustness-accuracy tradeoff
- **Distribution shift:** Common corruptions, domain generalization, test-time adaptation
- **OOD detection:** Confidence-based, energy-based, feature-space methods
- **Bias in vision models:** Disaggregated evaluation, demographic disparities
- **Baldr's vulnerability:** The overlooked threat — why robustness is never complete

**Required Reading:**

- Goodfellow, I. et al. "Explaining and Harnessing Adversarial Examples" (2015), *ICLR*
- Hendrycks, D. & Dietterich, T. "Benchmarking Neural Network Robustness to Common Corruptions and Perturbations" (2019), *ICLR*
- Madry, A. et al. "Towards Deep Learning Models Resistant to Adversarial Attacks" (2018), *ICLR*

**Discussion Questions:**

1. Adversarial training improves robustness but reduces clean accuracy. For an AI agent that processes user-uploaded images, how should you weigh the risk of adversarial attack (rare but catastrophic) against the cost of reduced accuracy on normal images (common but minor)?
2. OOD detection flags inputs that are different from training. But what does "different" mean? A clear photograph of a new object is OOD because the object wasn't in training — but the model should still be able to recognize it as an object. How should OOD detection distinguish between benign novelty and dangerous novelty?
3. Baldr was protected against everything except mistletoe. In vision system design, how do you identify your "mistletoe" — the vulnerability you didn't think to test for? What practices can systematically surface overlooked failure modes?

---

### ᛜ Lecture 12: The Seeing Agent — Integrating Vision into Agent Architecture

**Course:** AI203 — Computer Vision
**Degree:** Bachelor of Science in AI Agent Automation, 2040

---

In this final lecture, we synthesize the vision capabilities covered in this course — classification, detection, segmentation, visual reasoning, video understanding, 3D vision, document understanding, UI vision, generative vision, and robustness — into a unified vision architecture for AI agents. The goal is not a single monolithic vision model but a modular, composable vision system that an agent can call upon as needed, routing visual inputs through the appropriate processors and integrating the results into the agent's reasoning and action selection.

The **vision pipeline for AI agents** follows a layered architecture:

**Layer 1: Triage** — When a visual input arrives, the agent must determine what kind of visual input it is and what processing it requires. A lightweight classifier (ConvNeXt-Tiny running at 1000+ FPS) categorizes the input: screenshot, photo, document, chart, video frame, or diagram. The triage layer also performs basic quality checks: is the image too dark, too blurry, too low-resolution for reliable processing? If so, the agent requests a better image or applies preprocessing (enhancement, super-resolution) before proceeding.

**Layer 2: Feature Extraction** — A shared backbone (ConvNeXt-B or ViT-L) extracts visual features that serve as the foundation for all downstream processing. Using a shared backbone is more computationally efficient than running separate backbones for each task, and the shared representations enable cross-task transfer (knowledge gained from detection improves segmentation, and vice versa).

**Layer 3: Task-Specific Heads** — On top of the shared backbone, task-specific heads perform the specialized vision tasks covered in this course: object detection (Faster R-CNN or DETR head), semantic segmentation (U-Net decoder), UI element detection (WidgetBERT head), text recognition (TrOCR head), depth estimation (Depth Anything head), and visual question answering (BLIP-3 cross-modal attention). These heads are selectively activated based on the task: a screenshot triggers UI element detection, text recognition, and layout analysis; a photo triggers object detection, segmentation, and depth estimation; a document triggers layout analysis, table extraction, and OCR.

**Layer 4: Structured Representation** — The outputs of the vision heads are combined into a structured, multi-level representation:
- **Bottom level:** Raw outputs — bounding boxes, masks, text strings, depth maps, VQA answers.
- **Middle level:** Scene graph — objects with attributes and relationships, derived from detection and VQA outputs.
- **Top level:** Task-relevant interpretation — for a screenshot, a UI tree (which elements exist, their types, states, and spatial relationships); for a photo, a semantic summary (what the scene depicts, who is present, what is happening).

**Layer 5: Integration with Reasoning** — The structured representation is passed to the agent's reasoning engine (the language model backend), which incorporates the visual information into its understanding of the task context. The reasoning engine can query the vision system for additional details: "What is the text on the button at position (300, 400)?" "Is there a person in the background of this photo?" "What happened between timestamps 0:15 and 0:22 in this video?" The vision system responds with targeted analysis, focusing computational resources on the queried regions and timeframes.

**Layer 6: Action Grounding** — When the reasoning engine decides to take an action involving the visual world (clicking, typing, selecting), the action is grounded to specific visual elements through the grounding module (Lecture 9). The grounding module translates the agent's symbolic action description ("click the Submit button") into pixel coordinates or element references that the execution engine can use.

The key design principles for agent vision systems are: **modularity** (separate components for separate tasks, connected through well-defined interfaces), **laziness** (only run the vision tasks that are needed for the current context — don't run OCR if the task doesn't require reading text), **caching** (reuse visual features and intermediate results across queries within the same image), **uncertainty awareness** (every vision output should come with a confidence score, and the agent should calibrate its trust accordingly), and **fallback** (if vision is unreliable, fall back to programmatic interfaces, user clarification, or conservative action).

The Norse guardian **Heimdallr**, with whom we opened this course, watches from Himinbjǫrg at the edge of Ásgarðr. His senses are preternaturally acute: he sees for a hundred leagues, hears the grass growing, needs no sleep. But Heimdallr does not merely perceive — he interprets, judges, and acts. He sounds the Gjallarhorn when danger approaches, alerting all the gods. The AI agent's vision system is Heimdallr: acute perception (classification, detection, segmentation), integration across scales (video frames, depth maps, text recognition), and action-grounded interpretation (sounding the horn — executing the action — when the visual evidence warrants it).

The rune **ᛞ (dagaz)** — the rune of dawn, breakthrough, and clarity — closes this course. Dagaz is the moment when darkness becomes light, when what was hidden becomes visible. Computer vision is the computational dagaz: the transformation of raw pixels into structured understanding, of darkness into clarity, of data into action. Every time an AI agent looks at an image and sees what is there — truly sees, with understanding, not just with pixels — dagaz has been achieved. The darkness has been transformed into light.

*Huginn ok Muninn fljúga hverjan dag — Thought and Memory fly each day. May what they bring back be clear, and true.* ᛟ

**Key Topics:**

- **Six-layer vision architecture:** Triage, feature extraction, task-specific heads, structured representation, reasoning integration, action grounding
- **Design principles:** Modularity, laziness, caching, uncertainty awareness, fallback
- **Unified representation:** Per-pixel (masks, depth) → per-region (bounding boxes, text) → per-scene (scene graph, summary)
- **Agent-vision integration:** Query-driven vision, targeted analysis, confidence calibration
- **Heimdallr's watch:** Perception, interpretation, and action — the unified vision system
- **Dagaz:** From darkness to clarity — the transformation of pixels into understanding

**Required Reading:**

- University of Yggdrasil Agent Systems Group, "The Layered Vision Architecture for Autonomous Agents" (2040)
- Anderson, P. et al. "Bottom-Up and Top-Down Attention for Embodied Question Answering" (2018/2040 revisited), *CVPR*
- Chen, X. et al. "Vision-Centric Agent: Integrating Visual Perception with LLM Reasoning" (2024), *arXiv*

**Discussion Questions:**

1. The six-layer architecture routes visual inputs through specialized processors. What is the latency of this pipeline? For an agent that must respond within 200ms (real-time interaction), which layers can be optimized, and which must be simplified?
2. The caching principle reuses visual features across queries. But what if the world changes between queries — the user scrolls, a popup appears, an object moves? How should the agent detect that its cached features are stale and re-run the appropriate layers?
3. Dagaz is the moment of clarity — when pixels become understanding. For an AI agent looking at a complex screenshot, when does dagaz occur? Is there a single moment when the image is "understood," or is understanding gradual, layered, and never complete?

---

## Final Examination Preparation

### Course: AI203 — Computer Vision

**Format:** Choose 4 of the following 8 questions. Write a well-structured essay (800–1200 words) for each. Include architecture diagrams where appropriate. Analyze computational complexity and failure modes.

---

**Question 1:** Compare and contrast ConvNeXt and Vision Transformer architectures for image classification. For each: (a) describe the inductive biases encoded in the architecture, (b) analyze the computational complexity (FLOPs, parameters) as a function of image resolution and number of classes, and (c) discuss data efficiency — how much training data each requires to achieve competitive performance. Then describe a scenario in AI agent development where each is the preferred backbone.

**Question 2:** Design a UI element detection system for an AI agent that must interact with arbitrary desktop applications through screenshots alone (no accessibility tree). Specify the architecture, training data requirements, and evaluation methodology. Discuss the challenges of cross-application generalization (a button in one app looks different from a button in another) and propose strategies to address them.

**Question 3:** Compare DETR (transformer-based) and Faster R-CNN (two-stage CNN) for object detection. For each: (a) describe how region proposals are generated, (b) explain how the model handles duplicate detections of the same object, (c) analyze training convergence (DETR is notoriously slow to converge — why?), and (d) discuss the role of non-maximum suppression. For an AI agent monitoring a security camera feed, which detector would you recommend and why?

**Question 4:** A U-Net segmentation model uses skip connections to combine high-resolution encoder features with decoder features. Explain why skip connections are necessary for precise segmentation and what happens without them. Describe an alternative approach to recovering spatial resolution (e.g., dilated convolutions, atrous spatial pyramid pooling) and compare its advantages and disadvantages to U-Net's skip connections.

**Question 5:** Visual Question Answering (VQA) integrates vision and language. Design a VQA system for an AI agent that must answer questions about screenshots (e.g., "How many unread emails are in the inbox?"). Specify the vision encoder, language encoder, cross-modal fusion mechanism, and answer generation strategy. Discuss how the system should handle questions that require counting ("how many?") vs. questions that require reading ("what is the subject of the most recent email?").

**Question 6:** An AI agent uses monocular depth estimation (Depth Anything v2) to estimate the 3D layout of a room from a single user-uploaded photo. Discuss the inherent ambiguities of monocular depth estimation (scale ambiguity, occlusion boundaries, transparent and reflective surfaces) and propose strategies for the agent to handle these ambiguities: how should the agent communicate uncertainty to the user? When should the agent request additional views?

**Question 7:** Document understanding requires OCR, layout analysis, and table extraction. Design a pipeline for an AI agent that processes scanned invoices. For each stage (preprocessing, OCR, field extraction, table extraction, validation), specify the architecture, the likely failure modes, and the strategies for error detection and recovery. How should the agent handle an invoice that is rotated, partially cropped, or low-resolution?

**Question 8:** Design the complete vision architecture for an AI agent that must: (a) process user-uploaded screenshots to understand UI state, (b) watch screen recordings to understand user workflows, (c) read and extract information from PDFs and scanned documents, (d) generate diagrams to explain concepts to users, and (e) detect when a visual input is adversarial or out-of-distribution. For each capability, specify which vision models are used, how they interact, and what the failure modes are. Discuss the computational budget: assuming the agent must operate within 500ms latency and 16GB GPU memory, how would you allocate resources across these capabilities?

---

*End of AI203 Course Materials*

*Dagaz — the darkness yields to light. What was hidden is seen. What was seen is understood.* ᛟ
