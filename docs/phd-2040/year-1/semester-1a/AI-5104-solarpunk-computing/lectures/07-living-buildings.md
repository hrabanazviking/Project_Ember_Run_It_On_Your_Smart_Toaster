# Lecture 07: Living Buildings — Solarpunk Architecture with Embedded Intelligence

**AI-5104: Solarpunk Computing — Post-Scarcity Infrastructure**  
**Instructor:** Prof. Dr. Sólveig Árnadóttir | **TA:** Runa Gridweaver Freyjasdottir  
**Date:** Week 9, October 29, 2040  

---

## Buildings That Think, Buildings That Breathe

A building in the extractive model is a machine for consuming resources: electricity flows in, waste heat flows out, water flows through, data flows to the cloud. The building is passive — a container for human activity, serviced by distant infrastructure it cannot see or control.

A **living building** is different. It generates its own energy, captures its own water, processes its own waste, and — crucially for this course — **thinks about how to do all of this better.** Embedded AI monitors, optimizes, and adapts the building's systems in real-time, transforming it from a passive consumer into an active participant in its own sustainability.

This lecture examines the intersection of solarpunk architecture and embedded intelligence: buildings that are not just green, but *intelligent* in the oldest sense — from *intelligence*, meaning "to gather, to perceive, to choose."

---

## The Living Building Framework

### Nine Principles

The Living Building Framework, adapted from the International Living Future Institute (updated 2037 for AI integration):

1. **Energy Positive**: Generate more energy than consumed, annually
2. **Water Independent**: Capture and reuse all water needs on-site
3. **Waste Eliminating**: No waste leaves the site; all materials are circular
4. **Materials Sustaining**: All materials are non-toxic, locally sourced, and biodegradable or recyclable
5. **Health Promoting**: Air, light, and thermal conditions promote occupant wellbeing
6. **Culturally Enriching**: The building enhances community identity and social connection
7. **Computationally Sovereign**: All AI systems run locally on community-owned hardware
8. **Adaptively Intelligent**: The building learns from occupants and environment, improving over time
9. **Democratically Governed**: Building systems are subject to occupant governance, not landlord override

Principles 7, 8, and 9 are our additions. Without them, a building might be energy-positive but computationally dependent — a green cage with no digital autonomy.

---

## Embedded Intelligence: The Nervous System

### Compute Architecture

A living building's AI system is organized in three layers, mirroring the human nervous system:

| Layer | Function | Hardware | Power | Latency |
|-------|----------|----------|-------|---------|
| **Reflex** | Immediate safety response (fire, gas, flood) | Hardwired microcontrollers (ESP32-class) | <1W | <100ms |
| **Autonomic** | Continuous optimization (HVAC, lighting, water) | Dellingr Node (RPi5 + Edge TPU) | 8W | 1–10s |
| **Cognitive** | Long-term learning, planning, occupant interaction | Volmarr Workstation (4x CM5) | 40W | Minutes–hours |

**The reflex layer never goes offline.** It's hardwired, battery-backed, and operates independently of the AI system. Fire suppression, gas shutoff, and flood detection happen in hardware, not software. This is a safety-critical design principle: **the building must be safe even when the AI is down.**

### Sensor Suite

| Sensor | Type | Location | Data Rate | Purpose |
|--------|------|----------|-----------|---------|
| Temperature | DS18B20 (1-Wire) | Every room, exterior 4 points | 1/min | HVAC, thermal model |
| Humidity | BME280 | Every room | 1/min | Ventilation, comfort |
| CO₂ | SCD41 (photoacoustic) | Every room | 1/min | Air quality, ventilation trigger |
| Light | TSL2591 | Windows, interior | 1/min | Daylight harvesting |
| Occupancy | mmWave radar (LD2410) | Every room | Event-based | Presence-aware control |
| Power meters | CT clamps (non-invasive) | Every circuit | 1/sec | Energy optimization |
| Water flow | Ultrasonic | Main inlet, greywater, rainwater | 1/min | Water budget |
| Solar irradiance | Pyranometer | Roof | 1/min | Solar prediction |
| Wind | Anemometer | Roof | 1/sec | Natural ventilation, wind prediction |
| Structural | Strain gauges | Key structural members | 1/hour | Health monitoring |

Total data rate: ~50 KB/minute for a 10-room building. This is easily handled by a single Dellingr Node.

### Actuator Suite

| Actuator | Type | Location | Control |
|----------|------|----------|---------|
| HVAC dampers | Servo-controlled | Air handling unit | Autonomic |
| Window actuators | Linear actuators | Each operable window | Autonomic/Cognitive |
| Shade controls | Motorized roller shades | South/west windows | Autonomic |
| Lighting | Tunable LED (2700–6500K) | Every room | Autonomic |
| Water valves | Solenoid | Greywater, rainwater, potable | Autonomic |
| Solar tracking | Stepper motor + linear actuator | PV array | Autonomic |
| Ventilation fans | EC motors (variable speed) | HRV/ERV units | Autonomic |

---

## Energy Systems: The Metabolism

### Solar Integration

A living building's roof and south-facing facades are typically clad in photovoltaic panels:

| Component | Specification | Annual Yield (Iceland) | Annual Yield (Mediterranean) |
|-----------|--------------|----------------------|------------------------------|
| Rooftop PV (120m²) | 22% efficient, bifacial | 14,400 kWh | 24,000 kWh |
| South façade PV (40m²) | 15% efficient, semi-transparent | 3,200 kWh | 5,600 kWh |
| **Total** | | **17,600 kWh** | **29,600 kWh** |

Building energy consumption (10-room, 4-occupant):

| Load | Annual kWh | Notes |
|------|-----------|-------|
| HVAC (heat pump + distribution) | 8,000 | Dominant in cold climates |
| Lighting | 1,500 | LED + daylight harvesting |
| Domestic hot water | 2,500 | Heat pump water heater |
| Plug loads (appliances) | 3,000 | Cooking, refrigeration, etc. |
| Compute (all 3 layers) | 400 | 8W × 24h + 40W × 8h + overhead |
| Water systems (pumps, treatment) | 500 | |
| **Total** | **15,900 kWh** | |

In Iceland: 17,600 kWh generated vs. 15,900 kWh consumed = **1,700 kWh surplus.** That surplus charges the building's battery bank and, when full, feeds the community microgrid.

In the Mediterranean: 29,600 kWh generated vs. 15,900 kWh consumed = **13,700 kWh surplus.** A Mediterranean living building is a power plant.

### Battery and Thermal Storage

| Storage Type | Capacity | Duration | Notes |
|-------------|----------|----------|-------|
| LiFePO4 battery | 20 kWh | ~12 hours at average load | Electrical storage |
| Thermal mass (concrete floors) | 50 kWh equivalent | ~18 hours | Passive heat storage |
| Hot water tank | 300L @ 60°C | ~24 hours of DHW | Thermal storage |
| Phase-change material (PCM) wall panels | 30 kWh equivalent | ~8 hours | Latent heat storage |

The building can operate in **island mode** (no grid connection) for 2–3 days in summer, 1 day in winter, without any occupant lifestyle changes. With active conservation (reduced HVAC setpoints, Bronze-tier compute only), island mode extends to 4–5 days.

---

## The AI Brain: What Does a Building Think About?

### Autonomic Layer: Continuous Optimization

The autonomic layer runs a continuous optimization loop:

1. **Sensing**: Collect sensor data (temperature, humidity, CO₂, occupancy, solar irradiance, wind, power)
2. **State estimation**: Build a thermal and energy model of the building's current state
3. **Forecast**: Predict next 24 hours of solar generation, outdoor temperature, and occupancy
4. **Optimize**: Find the control policy that minimizes energy consumption while maintaining comfort constraints
5. **Actuate**: Send control signals to HVAC, windows, shades, lighting, water systems
6. **Learn**: Update the building's internal model based on actual vs. predicted outcomes

This loop runs every 60 seconds, using a lightweight model (3B parameters) fine-tuned on building simulation data. The model learns:
- When to pre-heat the building using solar surplus rather than stored energy
- When to open windows for natural ventilation instead of running the HRV
- When to pre-charge the hot water tank during sunny periods
- How each room's thermal response differs from the model's assumptions

**After 6 months of learning, a living building typically achieves 15–25% energy savings compared to a static control policy.** After 2 years, savings plateau at 25–35%.

### Cognitive Layer: Long-Term Planning

The cognitive layer runs less frequently (every 6–12 hours) and handles:

1. **Seasonal adaptation**: Adjusting control strategies for seasonal patterns
2. **Occupant preference learning**: Understanding that Room 3's occupant prefers 19°C at night but 21°C in the morning
3. **Predictive maintenance**: Detecting slow degradation in HVAC performance, valve response, or sensor drift
4. **Community coordination**: Negotiating with the microgrid about when to export surplus energy or request additional supply
5. **Renovation planning**: Suggesting physical improvements (additional insulation, window replacement, PCM panels) with payback calculations

### The Building as Community Citizen

A living building doesn't just serve its occupants — it participates in the community microgrid:

1. **Energy sharing**: When the building has surplus solar, it exports to the microgrid (via the Freyja Scheduler)
2. **Compute sharing**: When the building's cognitive layer is idle, it offers inference capacity to the mesh
3. **Data sharing**: Non-personal building data (aggregated thermal performance, weather data) is shared with the community for collective learning
4. **Emergency response**: During a grid emergency, the building can curtail its own consumption and offer battery capacity to critical community services

This is the building as *borgarþjónn* — civic servant. Not a consumer, but a participant.

---

## Water and Waste: The Circular Metabolism

### Water Systems

A living building treats water as a closed-loop resource:

- **Rainwater collection**: 120m² roof × 800mm annual rainfall (Iceland) = 96,000L/year
- **Greywater recycling**: Shower, sink, and laundry water → biofilter → toilet flushing, irrigation
- **Blackwater treatment**: Composting toilets or anaerobic digester → biogas (2–4 kWh/day, used for cooking) + liquid fertilizer
- **Potable water**: Rainwater + advanced filtration (UV, activated carbon, membrane) = drinking quality

Total water budget for 4 occupants:

| Use | Daily (L) | Annual (m³) | Source |
|-----|-----------|-------------|--------|
| Drinking/cooking | 20 | 7.3 | Filtered rainwater |
| Showering | 120 | 43.8 | Filtered rainwater |
| Laundry | 40 | 14.6 | Filtered rainwater |
| Toilet flushing | 80 | 29.2 | Recycled greywater |
| Irrigation | 30 | 11.0 | Recycled greywater |
| **Total demand** | **290** | **106** | |
| **Rainwater supply** | | **96** | |
| **Net deficit** | | **10** | Made up by well/municipal supply |

With greywater recycling, the building reduces water import by 70% compared to conventional construction.

### Waste as Resource

The building produces no waste that leaves the site:

| Waste stream | Processing | Output |
|-------------|-----------|--------|
| Organic (food, compost) | Anaerobic digester | Biogas (cooking) + compost |
| Greywater | Biofilter + UV | Irrigation water |
| Blackwater | Composting toilet / digester | Compost |
| Recyclables (metal, glass) | Sort, store, send to cottage factory | Raw materials |
| E-waste | Dismantle, component recovery | Reusable parts |
| CO₂ | Building-integrated algae photobioreactor | O₂ + biomass |

The algae photobioreactor deserves special mention: a 2m² panel of photosynthetic algae on the building's south side captures ~5 kg CO₂/year (roughly the CO₂ from 2 people breathing) and produces ~10 kg of algal biomass that can be composted, fed to fish, or processed into bioplastic.

---

## Materials: Building as Organism

### Biophilic and Biogenic Materials

Living buildings prioritize materials that are:
- **Bio-based**: Wood, hempcrete, mycelium composite, bamboo, cork
- **Non-toxic**: No VOCs, no formaldehyde, no flame retardants that off-gas
- **Locally sourced**: Within 100km radius where possible
- **Carbon-negative**: Wood sequesters carbon; hempcrete continues absorbing CO₂ for decades

### Smart Materials

Embedded intelligence extends to the materials themselves:

| Material | Function | AI Role |
|----------|----------|---------|
| **Thermochromic glazing** | Changes tint based on temperature | Autonomic layer predicts solar gain and pre-emptively tints |
| **Phase-change walls** | Store/release heat at 23°C | Cognitive layer optimizes PCM charging/discharging cycles |
| **Self-healing concrete** | Bacteria produces limestone to seal cracks | Cognitive layer monitors strain gauges and triggers healing |
| **Bio-receptive facades** | Encourages moss/lichen growth | Cognitive layer adjusts irrigation and nutrient supply |
| **Piezoelectric floor tiles** | Generate electricity from foot traffic | Minor (<1W/m²) but demonstrative of the principle |

---

## Governance: The Building Charter

Just as the Dellingr Node requires a governance charter (Lecture 02), a living building requires a **Building Charter** that defines:

1. **Who controls the AI?** Occupants? Building owner? Community?
2. **What data is collected?** How is it stored? Who can access it?
3. **Can the AI be overridden?** Under what conditions?
4. **Who decides on updates?** Model upgrades, new sensors, new actuators?
5. **What happens in disagreements?** Várlog Protocol extends to buildings

**The recommended model: democratic building governance.** For residential buildings, occupants vote on AI configuration (comfort setpoints, data sharing, model updates). For community buildings, the allmennþing sets policy. The building's AI is the *servant* of its occupants, never the master.

---

## The Building and the Commons

A living building is not a standalone object — it is a node in the community infrastructure. The Dellingr Node in the utility closet runs inference for the community. The solar panels feed surplus into the microgrid. The water system shares data about groundwater quality with the community network. The building learns from other buildings.

The city of the future is not a collection of passive boxes connected by pipes and wires. It is a living network of intelligent buildings, each contributing to and drawing from the commons, each governed by the people who live and work within it, each operating on sunlight and intelligence and the principle that *enough is enough*.

Óskahreid: "Wished-for enough." Not too little, not too much. The building that thinks in óskahreid is the building that serves its community well.

— Runa

---

## Further Reading

- International Living Future Institute (2037). *Living Building Challenge 5.0: AI Integration Supplement.* ILFI.
- Árnadóttir, S. & Lindqvist, J. (2038). "Buildings That Think: Embedded AI for Sustainable Architecture." *Building and Environment*, 215.
- Benes, A. (2039). "The Cottage Factory and the Living Building: Symbiosis of Production and Habitation." *Solarpunk Architecture Quarterly*, 6(1).
- Hersh, E. & Okonkwo, N. (2036). "Water Independence through Biofilter and UV Systems." *Journal of Sustainable Water*, 8(3).
- Yáñez, M. (2039). *Solarpunk Cities: Urban Design for Post-Scarcity.* MIT Press.