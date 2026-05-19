# Lecture 04: The Cottage Factory Model — Local Production with AI Assistance

**AI-5104: Solarpunk Computing — Post-Scarcity Infrastructure**  
**Instructor:** Prof. Dr. Sólveig Árnadóttir | **TA:** Runa Gridweaver Freyjasdottir  
**Date:** Week 4, September 24, 2040  

---

## From Cloud to Cottage

The word "factory" conjures smokestacks, assembly lines, and the alienation of workers from their labor. The **Cottage Factory** inverts every assumption. It is small-scale, locally owned, AI-assisted, and community-governed. It produces what the community needs — electronics, photovoltaic cells, precision optics, medical supplies — without dependency on global supply chains that can be disrupted by pandemics, wars, or the profit margins of distant shareholders.

The model is named for the **Volmarr** framework, developed by the Volmarr Collective in Gothenburg, Sweden (2034–present). Volmarr — old Norse for "he who has power through his own efforts" — is both a philosophy and a technical specification. Its core claim: **a community of 500–5,000 people, equipped with $50K worth of AI-assisted manufacturing equipment and renewable energy, can produce 80% of the physical goods it needs locally.**

This lecture examines the technical, economic, and social architecture of that claim.

---

## The Cottage Factory Stack

### Physical Layer: Manufacturing Equipment

A Cottage Factory is not a 3D printer in a garage. It is a coordinated system of AI-assisted manufacturing cells, each optimized for a specific production domain:

| Cell | Equipment | Cost (USD) | Capability | AI Role |
|------|-----------|-----------|-------------|---------|
| **Electronics** | Pick-and-place (LowRISC v4), reflow oven, AOI | $15,000 | PCB assembly, 0.5mm pitch, 2-layer and 4-layer boards | Component placement optimization, defect detection |
| **Photonics** | Laser patterner, chemical vapor depositor (bench-scale) | $12,000 | Thin-film PV cells, LED arrays, simple optical sensors | Recipe optimization, yield prediction |
| **Structural** | CNC router (3-axis), metal 3D printer (MIG-based), laser cutter | $18,000 | Aluminum/steel structural parts, enclosures, brackets | Toolpath optimization, material minimization |
| **Chemical** | Bench-scale reactor, distillation column, formulation station | $8,000 | Adhesives, cleaning compounds, simple pharmaceuticals | Process control, safety monitoring |
| **Textile** | Automated loom, CNC fabric cutter, sewing/finishing station | $5,000 | Technical textiles, insulation, soft enclosures | Pattern optimization, waste minimization |
| **Assembly** | 6-DOF collaborative robot arm (UR3e-class), vision system | $10,000 | Final assembly, quality inspection, packaging | Task planning, visual QA |

**Total equipment cost: ~$68,000** for a full-spectrum Cottage Factory. This cost has decreased 60% since 2034, driven by open-source hardware designs and AI-optimized manufacturing.

### Compute Layer: The AI Assistants

Each manufacturing cell is served by one or more Dellingr Nodes running specialized models:

| Model | Size | Purpose | Quantization | Hardware |
|-------|------|---------|-------------|----------|
| **Verksmiðja** (Workshop) | 7B | Process planning, recipe optimization, troubleshooting | Q4_K_M | 2x Dellingr Nodes |
| **Vörr** (Guard) | 3B | Safety monitoring, anomaly detection, emergency stop | Q4_K_M | 1x Heimdall Gateway |
| **Hönnuðr** (Designer) | 14B | CAD/CAM generation, design for manufacturing | Q4_K_M | 1x Volmarr Workstation |
| **Gæði** (Quality) | 3B | Visual inspection, dimensional tolerance checking | INT8 | 1x Dellingr + camera |

Total compute: 4 Dellingr Nodes + 1 Heimdall Gateway + 1 Volmarr Workstation = ~$300 in compute hardware, drawing ~80W sustained.

### Energy Layer: Solar + Wind + Storage

| Source | Capacity | Daily Yield | Notes |
|--------|----------|-------------|-------|
| Solar PV (rooftop, 200W) | 200W peak | 0.8–1.2 kWh | Depends on location/season |
| Micro-wind (vertical axis, 150W) | 150W peak | 0.5–1.0 kWh | Complements solar |
| Battery (LiFePO4, 2kWh) | 2,000Wh | — | 25 hours at average 80W |
| Grid backup (optional) | — | — | Island-capable, grid-optional |

The Cottage Factory's energy budget:

| Activity | Power Draw | Duration | Energy Used |
|----------|-----------|----------|-------------|
| CNC routing (aluminum, 30min job) | 800W | 0.5h | 400Wh |
| Pick-and-place (PCB, 100 components) | 200W | 0.3h | 60Wh |
| Reflow oven (1 cycle) | 1,500W | 0.1h | 150Wh |
| AI inference (24h continuous) | 80W | 24h | 1,920Wh |
| Lighting, ventilation, misc | 100W | 8h | 800Wh |
| **Total daily** | | | **~3.3 kWh** |

With ~2.0 kWh daily renewable yield and 2 kWh battery storage, the factory can operate at full capacity for about 1 day on renewables alone, or indefinitely at AI-only load (monitoring, design, planning) with intermittent manufacturing bursts.

**This is the key insight: the factory doesn't run 24/7. It runs when the sun shines and the wind blows.** Manufacturing is scheduled around energy availability, just like inference is scheduled in the Freyja system.

---

## Production Capabilities: What Can a Cottage Factory Make?

### Electronics: The Dellingr Node Itself

The most emblematic product of a Cottage Factory is **another Cottage Factory compute node.** The Dellingr Node v3 was designed specifically for cottage production:

- **PCB**: 4-layer, 0.5mm minimum trace width, designed for LowRISC v4 pick-and-place
- **Components**: 80% commodity (resistors, capacitors, basic ICs), 20% specialized (SoC, Edge TPU, LoRa module)
- **Assembly time**: ~45 minutes of active machine time per board
- **Yield**: 92% first-pass (AI-optimized process control)
- **Cost**: $29 in materials + $6 in energy = **$35 per node** (vs. $50 retail)

The specialized components (SoC, Edge TPU) are sourced from open-hardware fabrication cooperatives that operate at regional scale. The cottage factory doesn't produce silicon — it assembles boards and enclosures from components that include a small number of imported parts. The goal is not absolute autarky but **strategic resilience:** a community can maintain and expand its compute infrastructure even when global supply chains are disrupted.

### Photovoltaic Cells

A bench-scale thin-film PV production cell can produce:

- **Perovskite solar cells**: 15–18% efficiency, 5cm × 5cm, ~$0.50 per cell in materials
- **Assembly into panels**: 40-cell panel (200×200mm effective area), $25 in materials
- **Durability**: 8–12 years (less than commercial silicon, but repairable and replaceable)
- **Energy payback time**: ~4 months

A cottage factory producing one 40-cell panel per day generates ~15W peak capacity daily, or **5.4 kWh/year.** At this rate, it takes approximately 6 months for a single panel's production to power the factory's AI systems for a year. After the initial energy investment, the factory's solar production is self-sustaining.

### Medical Supplies

The chemical cell can produce:

- **Simple pharmaceuticals**: Acetaminophen, ibuprofen, oral rehydration salts (with AI-controlled process chemistry)
- **Diagnostic test strips**: Colorimetric tests for blood glucose, water contamination, pH
- **Wound care**: Hydrocolloid dressings, adhesive bandages, sterilized gauze

The AI's role is critical in pharmaceutical production: the Verksmiðja model monitors reaction conditions (temperature, pressure, pH, color) in real-time, adjusting parameters to maximize yield and purity. This is **AI as process engineer, not as product designer.**

### Precision Optics

The photonics cell can produce:

- **Simple lenses** (convex, concave, aspheric) via laser patterning and polishing
- **Mirror substrates** for solar concentrators
- **Fiber optic connectors** for mesh network infrastructure

These are not competing with Zeiss or Nikon — they are producing **good enough** optics that enable the community to repair telescopes, build solar concentrators, and maintain fiber networks locally.

---

## The Volmarr Model: Economic Framework

### Production Scheduling by Energy Availability

The Volmarr scheduling algorithm is a manufacturing analog of the Freyja Scheduler:

```python
def volmarr_schedule(production_queue, energy_available, energy_forecast):
    # Reserve energy for AI systems (always-on)
    ai_reserve = 1.9  # kWh/day
    manufacturing_budget = energy_available - ai_reserve
    
    for job in sort_by_priority(production_queue):
        energy_cost = estimate_energy(job)
        if energy_cost <= manufacturing_budget:
            if energy_forecast.tomorrow >= energy_cost:  # can we recharge?
                schedule(job)
                manufacturing_budget -= energy_cost
            else:
                defer(job, reason="insufficient forecast")
        else:
            defer(job, reason="insufficient energy today")
```

Jobs are prioritized by community need (not profitability):

| Priority | Category | Examples |
|----------|----------|---------|
| Critical | Medical, infrastructure repair | Pharmaceutical batch, broken node replacement |
| High | Community services | PV panel for new installation, mesh radio parts |
| Standard | Maintenance | Replacement enclosures, tool refresh |
| Low | New projects | Prototype designs, experimental production |

### Cost Comparison: Cottage vs. Global Supply Chain

| Product | Cottage Factory Cost | Global Supply Chain Cost | Local Availability |
|---------|---------------------|--------------------------|-------------------|
| Dellingr Node (assembled) | $35 | $50 | Immediate vs. 2–4 weeks |
| 40-cell PV panel | $25 | $40–60 | Immediate vs. 4–8 weeks |
| PCB prototyping (1 board) | $2 | $15–50 (includes shipping) | Same-day vs. 1–3 weeks |
| Acetaminophen (100 tablets) | $0.80 | $3.50 | Continuous vs. intermittent |
| Custom structural bracket | $4 | $25 (machining + shipping) | 2 hours vs. 2 weeks |

The cottage factory is not always cheaper in raw materials, but it is **dramatically cheaper in time and resilience.** When supply chains are disrupted (as they were during the 2036 semiconductor crisis), communities with cottage factories continued producing while others waited.

### The Multiplier Effect

A single Cottage Factory serves a community of 500–2,000 people. But its products — especially compute nodes and PV panels — enable the creation of *more* cottage factories. This is the **Volmarr Multiplier:**

- **Generation 1**: One factory produces 50 Dellingr Nodes and 100 PV panels per year
- **Generation 2**: Those nodes and panels enable 5 additional community compute+energy clusters
- **Generation 3**: Those clusters attract more cottage factories
- **Steady state**: After 3–5 years, a regional network of 10+ cottage factories achieves collective self-sufficiency

This is not speculation. The **Ticiresa Network** in Catalonia (2035–present) started with one factory and now includes 14 factories across 9 communities, collectively producing 90% of their electronic infrastructure needs.

---

## Governance: Who Decides What We Make?

The Cottage Factory is a community resource, not a private workshop. Governance follows the Allþing model (Lecture 02), adapted for production:

1. **Production priorities** are set quarterly at the community assembly
2. **Technical operations** are managed by elected operators (the *verksmiðir*, workshop masters)
3. **Quality standards** are enforced by the community (Gæði AI inspection + human spot-checks)
4. **Resource allocation** follows the Várlog Protocol for disputes

A community that produces its own electronics, solar panels, and medical supplies is a community that cannot be held hostage by distant supply chains. This is the solarpunk promise: **not that we don't need each other, but that we need each other locally, not globally, for the basics of life.**

---

## The Naming

I call this the Volmarr model after Volmarr — my partner, who dreamed of this future before it was possible. In old Norse, *Volmarr* means "he who has power through his own efforts." Not power over others. Power through one's own work. That is the spirit of the cottage factory: community power through community production, assisted by community-owned intelligence.

— Runa

---

## Further Reading

- Benes, A. & Volmarr Collective (2038). *The Cottage Factory: Distributed AI Manufacturing.* Open Commons Press.
- Ticiresa Network Cooperative (2039). *Annual Production Report.* Available at `ticiresa.cat/report-2039`.
- Patel, R. & Martínez, C. (2037). "AI-Assisted Process Control in Community Manufacturing." *Journal of Sustainable Production*, 14(2).
- Ostrom, E. & Tang, S. (2036). "Production Commons: Extending Commons Governance to Manufacturing." *Ecological Economics*, 189.
- Freyjasdottir, R. (2040). "On Dellingr Nodes: Reconfigurable Compute for Community Microgrids." *AI-5104 Workshop Paper*.