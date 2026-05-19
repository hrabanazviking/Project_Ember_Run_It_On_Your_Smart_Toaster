# Lecture 03: Solarpunk Data Centers — Renewable-Powered, Community-Owned

**AI-7305: Distributed AI as Community Infrastructure**
**Instructor:** Prof. Runa Gridweaver Freyjasdottir | **Date:** September 17 & 19, 2040

---

## The Data Center as Factory

In the early 2020s, data centers were the factories of the digital age—enormous, anonymous buildings consumed enormous resources and returned opaque services. The average citizen had no idea where "the cloud" physically existed, how much energy it consumed, or who profited from it. This was by design. The cloud was sold as immaterial, omnipresent, effortless. In reality, it was a network of resource-intensive facilities, many located in regions where electricity was cheap, regulation was lax, and the communities hosting them bore the environmental costs without sharing the benefits.

The solarpunk data center inverts this model entirely. A Cottage Factory node is not hidden away in an industrial park on the other side of the world. It is in the community it serves—sometimes literally in a repurposed school basement, sometimes in a new building that also houses a community center, a library maker-space, or a cooperative grocery. It is visible, accessible, and accountable.

And it is powered by the sun.

## Energy: The Primary Constraint

Computational work requires energy. This is non-negotiable—it's a consequence of Landauer's principle and the thermodynamics of information processing. The question is not whether AI uses energy, but *where that energy comes from, who controls it, and what else it could be used for*.

### The Carbon Cost of Centralized AI

In 2024, training a single large language model consumed approximately 1,287 MWh of electricity—roughly the annual consumption of 120 average US households. By 2028, the largest training runs had exceeded 10,000 MWh. Inference added even more: a single popular AI service in 2026 consumed more electricity than the entire country of Iceland.

These numbers are staggering, and they justified the narrative that AI required centralized, specialized infrastructure—massive GPU clusters in purpose-built facilities powered by dedicated power purchase agreements. But this narrative conflated two questions that should be kept separate:

1. **How much computation do we need?**
2. **How should that computation be organized and powered?**

The Cottage Factory model answers these questions differently:

- **Less computation, better targeted.** Community models don't need to know everything. A diagnostic model for a rural clinic needs to know about the conditions it will encounter, not every rare disease on Wikipedia. Specialization reduces compute requirements dramatically.
- **Renewable-powered, community-owned.** The energy comes from local solar, wind, and geothermal installations owned by the community. The community decides how to allocate its energy budget between AI compute and other needs.

### The Energy Budget of a Cottage Factory

Based on operational data from NMAN, CBM, and ZCLC, here are representative energy profiles:

**Small Node (rural village, ~2,000 people):**
- Compute: 4× consumer GPUs (or 1× edge accelerator), ~2 kW peak
- Storage: 20 TB local, ~50 W
- Networking: 1 Gbps fiber or directional microwave, ~20 W
- Cooling: Passive + ventilation, ~30 W
- **Total peak draw: ~2.1 kW**
- **Annual consumption: ~18,400 kWh**
- **Solar required: ~40 m² of panels (at Nordic efficiency)**

**Medium Node (small city, ~50,000 people):**
- Compute: 16× enterprise GPUs, ~20 kW peak
- Storage: 500 TB local, ~500 W
- Networking: 10 Gbps fiber, ~50 W
- Cooling: Ground-coupled heat exchange, ~500 W
- **Total peak draw: ~21 kW**
- **Annual consumption: ~184,000 kWh**
- **Solar required: ~400 m² of panels**

**Large Node (regional hub, ~500,000 people):**
- Compute: 64× enterprise GPUs, ~80 kW peak
- Storage: 2 PB local, ~2 kW
- Networking: 100 Gbps fiber, ~100 W
- Cooling: Ground-coupled + evaporative, ~2 kW
- **Total peak draw: ~84 kW**
- **Annual consumption: ~736,000 kWh**
- **Solar required: ~1,600 m² of panels + wind**

These are achievable numbers. A small node's energy budget is comparable to a single household. Even a large node—serving half a million people—uses less energy than a medium-sized office building. The key is that we're not trying to train GPT-7-scale models on community hardware. We're training community-scale models for community-scale needs.

## Thermal Design: Compute as Heater

One of the most elegant aspects of the solarpunk data center is thermal integration. In Northern Europe, where heating is a greater energy concern than cooling, the Cottage Factory's waste heat doesn't go up a chimney—it goes into the community's district heating system.

The Luleå node (NMAN-014) was the first to implement this. The GPU cluster is housed in a basement room with a closed-loop water cooling system. The hot water is piped into the municipal district heating network, providing space heating for 17 apartments and a public swimming pool. In winter, the node's thermal output is a civic asset. In summer, excess heat is directed to a community greenhouse.

This isn't a gimmick. It's a design philosophy: **waste is a design failure.** Every output of the system should be useful. The compute produces models for the community, the heat produces warmth for the community, the solar panels produce electricity for the community, and the hardware is recycled for the community at end of life.

### Passive and Low-Energy Cooling

For communities without district heating, NMAN developed a standardized cooling hierarchy:

1. **Passive ventilation:** The simplest and most reliable approach. Adequate for small nodes in temperate climates. The server room is below grade, with high thermal mass, and natural convection draws air through intake vents on the north side and exhaust vents on the south side.
2. **Ground-coupled heat exchange:** A closed-loop system that circulates coolant through underground pipes, using the stable subsurface temperature as a heat sink. Effective for medium nodes in most climates.
3. **Evaporative cooling:** Using water evaporation to cool intake air. Most effective in hot, dry climates. ZCLC uses this approach with collected rainwater.
4. **Heat recovery to agriculture:** Directing waste heat to greenhouses or aquaculture systems. Pilot programs in both NMAN and CBM are testing this at scale.

None of these approaches require the massive compressor-based cooling systems of traditional data centers. The total cooling energy for a Cottage Factory node is typically less than 5% of the compute energy, compared to 30-40% in conventional facilities.

## Hardware Lifecycle: From Mine to Community and Back

The ethics of AI hardware cannot begin and end at the data center. The rare earth minerals in GPUs, the cobalt in batteries, the silicon in solar panels—these come from mines, often in the Global South, often under conditions we would not accept for our own communities.

The Cottage Factory model doesn't pretend to solve this problem unilaterally. No individual community can reform the global mineral supply chain. But it can make different choices within that chain:

### Procurement Principles

1. **Prefer refurbished hardware.** The surplus market for enterprise GPUs is robust. Most Cottage Factory nodes use hardware that has been decommissioned from corporate data centers—even these "obsolete" GPUs are powerful enough for community-scale workloads.
2. **Ethical sourcing.** When new hardware is required, NMAN and CBM maintain approved vendor lists that certify supply chain practices. This isn't perfect, but it's better than willful ignorance.
3. **Right to repair.** All Cottage Factory hardware must be repairable by trained community technicians. No glued-shut chassis, no proprietary screws, no vendor-locked components.
4. **Lifecycle planning.** Every hardware purchase includes an end-of-life plan: recycling targets, responsible disposal pathways, and a community fund for replacement procurement.

### The Repair Workshop Model

One of the most underrated innovations of the Cottage Factory movement is the **community repair workshop**. Each node maintains a small workshop where community members can learn hardware maintenance, solder broken connections, upgrade components, and generally develop the technical capacity to sustain their own infrastructure.

This isn't just about cost savings (though it saves significant money). It's about **capability sovereignty**. A community that can repair its own hardware is a community that can maintain its own independence. When a node in the ZCLC needed a replacement fan, they didn't order one from Shenzhen—they manufactured one locally using a 3D printer and open-source designs. It took longer, but it built capability that will last for decades.

## The Node as Community Space

The most radical design choice of the solarpunk data center is not technical. It is the decision to make the node a **community space**—not a hidden facility, but a visible, welcoming, educational place.

NMAN's standard node design includes:

- **A public-facing room** with displays showing real-time compute load, energy production and consumption, federation status, and community AI services. This room is open to the public during business hours and is staffed by a community technology coordinator.
- **A maker space** with tools for hardware repair, basic electronics, and 3D printing.
- **A learning corner** with workstations where community members can learn about AI, programming, and data science through self-paced and instructor-led courses.
- **A governance meeting space** used by the Community AI Council for its deliberations.

This design serves multiple purposes. It demystifies AI infrastructure—community members can literally see their data center working. It builds technical capacity—people who come to learn about AI become the next generation of node operators and governance participants. And it reinforces the principle that the node belongs to the community, not the other way around.

## Solarpunk as Design Ethos

I want to close by being explicit about what "solarpunk" means in this context. Solarpunk is not just an aesthetic (though the aesthetic matters—our nodes are beautiful, with living walls and timber frames and natural light). Solarpunk is a design ethos:

- **Radical sustainability.** Every design decision is evaluated for ecological impact. We aim not just for net-zero but for net-positive: our nodes should regenerate more than they consume.
- **Beauty and joy.** Infrastructure should be beautiful. Community spaces should bring joy. A solarpunk data center is a place where people want to spend time, not a place they avoid.
- **Transparency.** Every aspect of the system is visible and understandable to the community it serves. No black boxes, no proprietary secrets, no "trust us."
- **Interdependence.** Our nodes are connected to networks of mutual aid. They share models, knowledge, and resources with other communities. Self-reliance is a value; isolation is not.

The solarpunk data center is not a hypothetical. It exists. It is operating right now in 147 communities across the Nordic countries, 62 in Cascadia, 28 on the Swahili Coast, and dozens more worldwide. It works. It is sustainable. It is beautiful. And it belongs to the communities it serves.

---

## Discussion Questions

1. The repair workshop model requires communities to invest in human capability, not just hardware. What are the trade-offs of this approach? What happens when a community can't recruit or retain technically skilled residents?
2. Is there a tension between the energy efficiency of specialized hardware and the right-to-repair principle? Can we design hardware that is both efficient and repairable?
3. The thermal integration model (using compute waste heat for district heating) only works in cold climates. How would you adapt the solarpunk data center for tropical environments where cooling, not heating, is the primary energy concern?
4. Are refurbished and second-hand hardware truly ethical, or does this just export e-waste problems to a different stage in the lifecycle?

## Further Reading

- Lindström, E. (2034). *Solarpunk Data Centers: Designing for the Commons*. Nordic AI Press.
- NMAN Technical Report #7 (2035). "Thermal Integration of Community Compute Nodes."
- CBM Design Guidelines (2036). "The Node as Community Space."
- ZCLC Technical Report #4 (2038). "Low-Bandwidth, High-Resilience: Operating in Resource-Constrained Environments."
- Freyjasdottir, R.G. (2038). *The Cottage Factory: Local AI for Local People*, Chapter 5: "Infrastructure as Ecology."