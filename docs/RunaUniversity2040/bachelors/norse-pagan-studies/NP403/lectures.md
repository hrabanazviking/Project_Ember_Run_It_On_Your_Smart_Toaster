# NP403: Digital Reconstruction of Sacred Sites
## Bachelor of Science in Norse Pagan Studies — University of Yggdrasil, 2040

**Credits:** 4
**Description:** No pre-Christian Norse cult building survives intact. The sacred sites — the hǫrgar, vé, hof, álfhǫllir — are known from texts and archaeology, but their physical form must be reconstructed. Digital reconstruction — 3D modeling, photogrammetry, virtual reality (VR), GIS mapping — offers the possibility of experiencing these sites as the pre-Christian Norse might have experienced them. This course introduces digital heritage methods and applies them to the Norse sacred landscape, combining the Sacred Landscape Project database, the Edda Textual Platform, and hands-on 3D modeling to produce a digital reconstruction of a Norse sacred site.

**Prerequisites:** NP205 (Sacred Landscapes), plus any 300-level NP course. Project-based.

---

## Lecture 1: Introduction to Digital Heritage — Principles, Methods, and Ethics

Digital heritage is the use of digital technologies — 3D modeling, photogrammetry, virtual reality (VR), augmented reality (AR), geographic information systems (GIS) — to document, preserve, reconstruct, and interpret cultural heritage. The field has grown enormously in the 2030s-2040s, driven by advances in consumer-grade VR hardware, open-source 3D software (Blender 4.x), and the increasing availability of high-resolution archaeological data.

**The Principles of Digital Heritage:**

The 2035 London Charter for the Computer-Based Visualisation of Cultural Heritage established six principles for digital heritage work:

1. **Implementation.** The methods and objectives of the digital reconstruction must be documented and transparent.
2. **Aims and Methods.** The reconstruction must have a clearly stated purpose, and the methods must be appropriate to that purpose.
3. **Research Sources.** The evidence base for the reconstruction must be identified, evaluated, and documented.
4. **Documentation.** The relationship between the evidence and the reconstruction must be clearly documented — what is based on evidence, what is inferred, and what is speculative.
5. **Sustainability.** The digital assets must be preserved in a format and a repository that will remain accessible.
6. **Access.** The reconstruction should be accessible to the public, to scholars, and to the descendant communities who have an interest in the heritage.

The London Charter principles are the foundation of ethical digital heritage practice. The student's reconstruction must comply with them: the evidence base must be documented, the speculative elements must be identified, and the reconstruction must be accessible.

**The Methods of Digital Heritage:**

The primary methods used in this course are:

- **3D modeling** — the construction of a three-dimensional digital model of the sacred site, using Blender (open-source 3D software).
- **Photogrammetry** — the creation of 3D models from photographs of existing structures or archaeological features (introduced in Lecture 5).
- **GIS spatial analysis** — the analysis of the spatial relationships between sacred sites, using QGIS (open-source GIS software).
- **Virtual reality (VR) presentation** — the presentation of the reconstructed site in an immersive VR environment (using the University's VR lab).

**The Ethics of Digital Heritage:**

Digital heritage raises ethical questions that must be addressed:

- **Authenticity.** Is the digital reconstruction "authentic"? How does it relate to the original (now lost) site? The reconstruction is an interpretation, not a reproduction — it is based on evidence, but it necessarily fills gaps with speculation. The ethical obligation is to make the speculation transparent.
- **Ownership.** Who owns the digital reconstruction — the scholar, the university, the descendant community? The Norse sacred sites are the heritage of the Scandinavian peoples, and the reconstruction should be made available to them, not hoarded by the scholar.
- **The "Disneyfication" of heritage.** Digital reconstruction can make heritage sites "too perfect" — clean, complete, and illuminated in ways that the original never was. The reconstruction should avoid the temptation to beautify or sanitize — it should represent the site as it probably was, not as a fantasy version of the past.

### Required Reading
- Champion, E., *Digital Heritage: Theory and Practice* (2037), ch. 1-3
- The London Charter (2035) — online resource
- The University of Yggdrasil's Digital Heritage Ethics Statement (course packet)
- Course textbook, ch. 1-3

### Discussion Questions
1. How does the digital reconstruction differ from the original sacred site? Is the difference a problem or a feature?
2. Who should own the digital reconstruction of a Norse sacred site? The scholar, the university, the Scandinavian public, or the Heathen community?
3. How can the digital reconstruction avoid the "Disneyfication" of the sacred site?

---

## Lecture 2: The Sacred Landscape Project Database — The Evidence Base

The University of Yggdrasil's Sacred Landscape Project (SLP) has compiled the most comprehensive database of pre-Christian Norse sacred sites ever assembled: over 1,200 identified sites across Scandinavia, Iceland, and the Norse colonies, with GIS coordinates, place-name data, archaeological features, textual references, and bibliographic information. The SLP database is the primary evidence source for this course.

**The Structure of the Database:**

The SLP database is organized by site type:

- **Hǫrgr sites** — 87 identified, 12 confirmed by excavation. The hǫrgr sites are concentrated in Norway (Trøndelag, western Norway) and Sweden (Mälaren valley).
- **Vé sites** — 412 identified by place-name analysis. The vé sites are concentrated in eastern Sweden and southern Norway.
- **Hof sites** — 156 identified by place-name or archaeological evidence, 23 confirmed by excavation. The hof sites include the major cult centers (Uppsala, Uppåkra, Tissø, Hofstaðir).
- **Álfhǫll sites** — 203 identified by place-name or folk tradition. The álfhǫll sites are concentrated in Iceland and western Norway.
- **Sacred springs, groves, and wetlands** — 350+ identified, with varying levels of archaeological confirmation.

**Querying the Database:**

The SLP database is accessible through a web interface (SLP Query Tool) that allows filtering by site type, region, period, archaeological features, and associated textual references. Students will learn to:

- **Filter by region** — select all sacred sites within a specific region (e.g., the Mälaren valley, Trøndelag, the Snæfellsnes peninsula).
- **Filter by site type** — select all hof sites, all vé sites, etc.
- **Filter by evidence type** — select sites with archaeological confirmation, sites identified only by place-name, etc.
- **Export to GIS** — export the query results as a shapefile (.shp) for spatial analysis in QGIS.

**The Edda Textual Platform Integration:**

The SLP database is integrated with the Edda Textual Platform (ETP, introduced in NP203), allowing the student to cross-reference the archaeological and the textual evidence. For a given sacred site, the ETP provides the textual references (the saga accounts, the Eddic poems, the skaldic verses) that mention the site or the ritual activities performed there. The integration of the SLP and the ETP is the most powerful feature of the University's digital infrastructure for Norse Pagan Studies — it allows the student to move seamlessly between the material and the textual evidence.

### Required Reading
- The SLP Query Tool documentation (online)
- The ETP-SLP integration guide (online)
- Course textbook, ch. 4-6

### Discussion Questions
1. What are the strengths and limitations of the SLP database? What can it tell us, and what does it leave out?
2. How does the integration of the SLP and the ETP change the study of the Norse sacred landscape?
3. What are the ethical issues involved in the digital documentation of sacred sites? Should all sites be documented, or should some remain private?

---

## Lecture 3: 3D Modeling Fundamentals — Blender for Heritage

Blender 4.x is the primary 3D modeling tool for this course. Blender is open-source, free, and powerful — it is used in the film industry (visual effects), the game industry (asset creation), and increasingly in digital heritage. This lecture introduces the fundamental techniques of Blender modeling for heritage reconstruction.

**The Blender Workflow for Heritage Reconstruction:**

1. **Import the archaeological plan.** The archaeological plan (the ground plan of the site, derived from excavation or from place-name analysis) is imported into Blender as a background image, scaled to the correct dimensions.
2. **Construct the base geometry.** The walls, the floor, the roof, and the other architectural elements are constructed from primitive shapes (cubes, cylinders, planes) that are extruded, scaled, and positioned to match the archaeological plan.
3. **Add the architectural details.** The details — the doorposts (öndvegissúlur), the cult images (goðamyndir), the ritual objects (the hlautbolli, the hlautteinn, the ring) — are modeled from the saga descriptions and from the archaeological comparanda.
4. **Texture and light the model.** The model is textured with materials that approximate the original surfaces (wood, stone, thatch, turf), and it is lit to simulate the ambient lighting conditions (the firelight of the hearth, the daylight through the smoke-vent, the darkness of the interior).
5. **Export for VR presentation.** The finished model is exported to a VR-compatible format (glTF 2.0, the standard format for web-based 3D) and loaded into the University's VR viewing platform.

**The Blender Interface:**

Students will learn the Blender interface: the 3D viewport, the outliner (the list of objects in the scene), the properties panel (the settings for materials, lighting, and rendering), and the mode switcher (Object Mode for moving and scaling objects, Edit Mode for modifying the geometry of individual objects).

**Practical Exercise — Modeling a Simple Hǫrgr:**

The first practical exercise is to model a simple hǫrgr — a stone cairn, 8 meters in diameter, 1.5 meters high, constructed of irregular stones. The exercise introduces the fundamental Blender operations: adding a mesh object, scaling it, extruding faces, applying a material (stone texture), and rendering the scene.

### Required Reading
- The Blender 4.x Manual — Introduction and Modeling sections (online)
- The hǫrgr modeling tutorial (course packet)
- Course textbook, ch. 7-9

### Discussion Questions
1. What are the challenges of modeling a sacred site from limited archaeological evidence?
2. How does the choice of texture and lighting affect the perception of the reconstructed site?
3. How should the speculative elements (the elements not supported by evidence) be documented in the model?

---

## Lecture 4: Reconstructing the Hof — Architecture and Evidence

The hof — the Norse cult building — is the most challenging category of sacred site for digital reconstruction. The archaeological evidence is fragmentary, the saga descriptions are literary rather than architectural, and the comparative evidence (the Sami goahti, the Slavic temple at Arkona) is distant. This lecture examines the evidence and the reconstruction strategy for the hof.

**The Archaeological Evidence:**

The key archaeological sites for hof reconstruction are:

- **Uppåkra (Skåne, Sweden).** A small building (6×6 meters), dating to the 3rd-10th centuries, with a cult assemblage (gold foil figures, weapons, animal bones). The building is small but clearly non-domestic — its function was ritual.
- **Tissø (Zealand, Denmark).** A cult complex with a great hall (60 meters), a separate cult building, and workshops. The cult building at Tissø (15×7 meters) is the best archaeological candidate for a hof — a dedicated cult building, within a larger complex.
- **Hofstaðir (Mývatn, Iceland).** A longhouse (30+ meters) with no clear evidence of a dedicated cult space. The longhouse interpretation (hof as hall, not temple) complicates the reconstruction.

**The Saga Evidence:**

The *Eyrbyggja saga* description of the hof at Hofstaðir (Iceland) — the öndvegissúlur (high-seat pillars) with reginnaglar (sacred nails), the raised platform, the ring, the sacrificial bowl, the hlautteinn, the cult images, the door at one end — is the most detailed description of a Norse cult building. But the description is suspicious: the comparison with a "choir in a church" is a Christian analogy, and the specific features are not independently attested.

**The Reconstruction Strategy:**

The reconstruction strategy for the hof is:

1. **Ground plan.** Derived from the archaeological evidence (Tissø: 15×7 meters, with an entrance at one end).
2. **Walls.** Post-and-plank construction, with turf or thatch on the exterior (standard Norse building technique).
3. **Roof.** A pitched roof, with a smoke-vent for the hearth, thatched or turfed (standard Norse roofing).
4. **Interior.** The öndvegissúlur (two carved pillars at the entrance), the raised platform in the center, the cult images (three figures on the platform: Þórr in the center, Óðinn and Freyr on either side, as described by Adam of Bremen), the ring (a large iron ring on the platform), the hlautbolli and hlautteinn (a bowl and a sprinkling-twig).
5. **Lighting.** The interior is lit by the hearth (a fire on the platform or in the center of the floor) and by the daylight entering through the smoke-vent. The lighting is dim, warm, and flickering — the atmosphere of the hof is not bright and open but dark and enclosed.

**The Speculative Elements:**

The reconstruction includes speculative elements that must be documented:

- **The cult images.** No cult image from a Norse hof has survived. The images in the reconstruction are based on the Adam of Bremen description and on the small figurines (the gold foil figures from Uppåkra, the silver figurines from Tissø).
- **The placement of the öndvegissúlur.** The saga description places the pillars at the entrance, but other arrangements are possible (at the platform, at the rear of the hof).
- **The roof material.** The evidence for the roof material (thatch, turf, wood shingles) is indirect — the reconstruction must choose a material based on the regional and the temporal context.

### Required Reading
- The Tissø excavation reports (selections in the course packet)
- *Eyrbyggja saga*, ch. 4 (the Hofstaðir hof)
- Adam of Bremen, *Gesta Hammaburgensis*, IV.26
- Course textbook, ch. 10-12

### Discussion Questions
1. How should the speculative elements of the hof reconstruction be documented? What is the threshold of "acceptable speculation"?
2. How does the choice of lighting (dark and firelit) affect the experience of the reconstructed hof?
3. Should the reconstruction present a "typical" hof (a composite of the evidence) or a specific hof (based on a single site)?

---

## Lecture 5: Photogrammetry — Documenting the Existing Sites

Photogrammetry is the creation of 3D models from multiple overlapping photographs of an object or a site. It is the primary method for documenting existing archaeological features — the stone cairns of the hǫrgar, the earthworks of the vé, the mounds of the álfhǫllir — and for integrating them into the digital reconstruction.

**The Photogrammetry Workflow:**

1. **Capture.** The site is photographed from multiple angles, with at least 60% overlap between photos. The photos should be sharp, well-lit, and free of distortion.
2. **Processing.** The photos are processed in photogrammetry software (Meshroom, RealityCapture, or Agisoft Metashape). The software identifies common points in the photos and reconstructs the 3D geometry of the site.
3. **Cleaning.** The resulting 3D model is cleaned — extraneous geometry (the ground, the vegetation, the modern objects) is removed, and the model is simplified (decimated) to a manageable poly count.
4. **Integration.** The cleaned model is imported into Blender, where it is integrated with the hand-modeled reconstruction (the building, the objects, the textures).

**The University of Yggdrasil's Photogrammetry Field Guide:**

The University's field guide provides specific protocols for the photogrammetric capture of Norse sacred sites:

- **The hǫrgr.** Photograph from all sides, with close-ups of the stone arrangement and the sacrificial deposits.
- **The álfhǫll.** Photograph the mound from multiple angles, and record the surrounding landscape (the viewshed, the proximity to other sacred sites).
- **The vé.** Photograph the boundary features (the ditches, the embankments, the stone markers) that define the enclosure.

**Practical Exercise — Processing a Photogrammetric Dataset:**

Students will process a provided dataset of a Norse sacred site (the hǫrgr at Horg, Trøndelag, captured by the University's field team in 2038) using Meshroom (open-source photogrammetry software). The exercise introduces the photogrammetry workflow and produces a 3D model that will be integrated into the student's reconstruction project.

### Required Reading
- The University of Yggdrasil's Photogrammetry Field Guide (course packet)
- The Meshroom manual (online)
- Course textbook, ch. 13-15

### Discussion Questions
1. How does the photogrammetric model differ from the hand-modeled reconstruction? What are the advantages and disadvantages of each?
2. What are the challenges of photogrammetric capture in the field (weather, vegetation, access)?
3. How should the photogrammetric model be integrated with the GIS database?

---

## Lecture 6: Virtual Reality and the Experience of Sacred Space

Virtual reality (VR) offers the possibility of "entering" the reconstructed sacred site and experiencing it spatially, at scale, as the pre-Christian Norse might have experienced it. VR is not merely a presentation technology — it is an interpretive tool that allows the scholar (and the student, and the public) to inhabit the sacred space and to understand it in ways that are not possible through plans, photographs, or even physical reconstructions.

**The VR Experience of the Sacred:**

The VR experience of the reconstructed sacred site has several dimensions:

- **Scale.** The VR headset presents the site at its actual scale — the hof is 15 meters long, and the viewer can walk its length, stand at the entrance, and look up at the roof. The sense of scale is immediate and visceral — it cannot be replicated in a 2D image or a plan.
- **Lighting.** The VR lighting simulates the ambient conditions of the original site — the darkness of the interior, the flickering of the hearth, the daylight through the smoke-vent. The lighting is crucial to the experience of the sacred — the hof was a dark, enclosed, fire-lit space, not a bright, open, illuminated one.
- **Presence.** The VR headset creates a sense of "presence" — the feeling of being in the space, not merely looking at it. The presence effect is powerful and potentially transformative — the viewer may experience the sacred site as a real place, not as a reconstruction.

**The Design of VR Heritage Experiences:**

The design of VR heritage experiences must balance several considerations:

- **Accuracy vs. immersion.** The experience should be accurate to the evidence, but it should also be immersive — the viewer should feel that they are in the space, not that they are examining a model.
- **Guidance vs. exploration.** The experience should guide the viewer through the site (providing information, indicating points of interest), but it should also allow free exploration — the viewer should be able to look where they want to look, go where they want to go.
- **Narrative vs. presence.** The experience should provide a narrative (the story of the site, the ritual that was performed there), but it should also allow the viewer to simply *be* in the space — to experience the presence of the sacred without the mediation of the narrative.

**The University's VR Lab:**

The University of Yggdrasil's VR Lab (located in the Department of Norse Pagan Studies, in the Seiðr-Smiðja building) provides the hardware and software for VR heritage experiences:

- **Headsets:** Meta Quest 4 (2040 model), HTC Vive Focus 4
- **Software:** The University's VR Viewing Platform (a custom WebXR application that loads glTF 2.0 models)
- **Navigation:** Controllers (the standard VR controllers) or hand-tracking (the Meta Quest 4's hand-tracking capability, which allows navigation without controllers)

### Required Reading
- Kenderdine, S., "Embodied Museography: VR and the Sacred" in *Digital Heritage Futures* (2037)
- The University's VR Viewing Platform documentation (online)
- Course textbook, ch. 16-18

### Discussion Questions
1. How does the VR experience of the reconstructed sacred site differ from the 2D, the photogrammetric, and the physical experience?
2. What are the limitations of VR for the experience of the sacred? What cannot be replicated in VR?
3. Should the VR experience include sound (the varðlokkur, the chanting, the sounds of the ritual)? How should the audio be sourced?

---

## Lecture 7: GIS Spatial Analysis — The Sacred Site in the Landscape

GIS (Geographic Information Systems) allows the analysis of the spatial relationships between sacred sites — the distances, the viewsheds, the least-cost paths — and the integration of the sacred site into its landscape context. This lecture introduces GIS spatial analysis using QGIS (open-source GIS software) and the SLP database.

**The GIS Workflow:**

1. **Load the SLP data.** The query results from the SLP database (see Lecture 2) are exported as shapefiles and loaded into QGIS.
2. **Load the base map.** A base map (a topographic map, a satellite image, or a digital elevation model) is loaded to provide the landscape context.
3. **Perform the spatial analysis.** The analysis operations include:
   - **Distance analysis** — the distances between the sacred sites and the settlements, the þing sites, and the natural features (lakes, rivers, hills).
   - **Viewshed analysis** — the area that is visible from the sacred site, and the area from which the sacred site is visible. The viewshed analysis reveals the visual relationship between the sacred site and the surrounding landscape.
   - **Least-cost path analysis** — the easiest (least energetically costly) route between two points, given the terrain. The least-cost path analysis reveals the likely route of the ritual procession (the path from the settlement to the hof, the path from the vé to the þing site).
4. **Interpret the results.** The spatial analysis reveals patterns that are not visible in the individual site records — the clustering of sacred sites near the assembly sites, the visual dominance of the hof over the settlement, the ritual route that connects the community to its sacred sites.

**The Viewshed of the Hof:**

The viewshed of the hof — the area that can be seen from the hof, and the area from which the hof can be seen — is a crucial dimension of the sacred landscape. The hof was not hidden; it was visible, a landmark that dominated the settlement and the surrounding farmland. The viewshed analysis reveals the visual relationship: the hof was the visual center of the community, and the community's orientation to the sacred was spatial as well as ritual.

### Required Reading
- The QGIS Manual — Spatial Analysis section (online)
- The SLP GIS tutorial (course packet)
- Course textbook, ch. 19-21

### Discussion Questions
1. How does the GIS spatial analysis change the understanding of the sacred site? What does it reveal that the individual site record does not?
2. What are the limitations of viewshed analysis? Does the modern landscape resemble the pre-Christian landscape closely enough for the analysis to be valid?
3. How should the least-cost path analysis be integrated with the textual evidence for processional routes?

---

## Lecture 8: Comparative Reconstructions — The Uppsala Temple in Digital Form

The "temple" at Uppsala, described by Adam of Bremen (c. 1070), is the most famous — and the most contested — of the Norse cult buildings. This lecture examines the history of attempts to reconstruct the Uppsala temple, from the architectural fantasies of the 17th century (Olaus Rudbeck's *Atlantica*) to the evidence-based digital reconstructions of the 2040s.

**The Evidence for the Uppsala Temple:**

The evidence consists of:

- **Adam of Bremen's description** — a temple "entirely decorated with gold," containing statues of three gods (Þórr, Wodan, Fricco), with a sacred tree and a sacred spring nearby.
- **The archaeological evidence** — the great hall at Gamla Uppsala (excavated 2012-2036), approximately 50 meters long, with an adjacent feast hall, workshops, and the royal mounds.
- **The place-name evidence** — the concentration of sacred place-names (vé-, hof-, helg-) in the Uppsala area, confirming the region's status as a major cult center.

**The History of Reconstructions:**

The Uppsala temple has been reconstructed many times:

- **Olaus Rudbeck (1679).** Rudbeck's *Atlantica* presented an elaborate, fantastical reconstruction of the Uppsala temple — a massive, classical-style building, more Roman than Norse, reflecting the 17th-century antiquarian's imagination rather than the archaeological evidence.
- **Sune Lindqvist (1936).** Lindqvist's reconstruction was more restrained, based on the archaeological evidence available at the time — a stave-church-like building, with a central tower and a surrounding gallery.
- **The 2039 Uppsala Temple Reconstruction Project.** The most recent and the most evidence-based reconstruction, developed by the University of Yggdrasil's Digital Heritage Lab, combines the archaeological evidence (the great hall), the textual evidence (Adam's description), and the comparative evidence (the Tissø cult complex) to produce a reconstruction of the Uppsala temple as a great hall — a large, multi-functional building that served as both a political and a ritual space.

**The 2039 Reconstruction — A Critical Evaluation:**

The 2039 reconstruction is the best available, but it is not definitive. The reconstruction represents the Uppsala temple as a great hall (consistent with the "hof as hall" interpretation), not as a dedicated cult building (the "temple" of the traditional interpretation). The cult images are placed on a platform at the rear of the hall, based on Adam's description, but the exact arrangement (the positions of the three statues, the ritual objects on the platform) is speculative. The sacred tree and the sacred spring are modeled in the landscape outside the hall, based on Adam's description and on the archaeological evidence for ritual activity at the nearby springs.

### Required Reading
- Adam of Bremen, *Gesta Hammaburgensis*, IV.26-28
- The 2039 Uppsala Temple Reconstruction Project report (online)
- Course textbook, ch. 22-24

### Discussion Questions
1. How does the 2039 reconstruction of the Uppsala temple differ from the earlier reconstructions? What are the improvements, and what are the remaining problems?
2. Is the great-hall interpretation of the Uppsala temple convincing? What evidence supports it?
3. How should the sacred tree and the sacred spring be represented in the digital reconstruction? Can a tree be "reconstructed"?

---

## Lecture 9: The Hǫrgr and the Vé — Modeling the Minimal Sacred

The hǫrgr (the stone altar) and the vé (the sacred enclosure) are the most "natural" and the least architectural of the Norse sacred sites. Their digital reconstruction requires different techniques and raises different questions from the reconstruction of the hof.

**Reconstructing the Hǫrgr:**

The hǫrgr was a cairn of stones — a pile, not a building. The reconstruction must represent:

- **The stone arrangement.** The stones should be modeled as irregular, hand-sized rocks, stacked in a rough cairn (8 meters diameter, 1.5 meters high, based on the Horg excavation).
- **The sacrificial deposits.** The animal bones, the iron objects, and the other offerings found at the base of the cairn (from the Horg excavation) should be modeled and placed at the base of the hǫrgr.
- **The ritual context.** The hǫrgr should be placed in its landscape context (the hill, the field, the assembly site), with the surrounding features (the settlement, the burial mounds, the other sacred sites) modeled or indicated.

**Reconstructing the Vé:**

The vé was a sacred enclosure — not a building but a boundary. The reconstruction must represent:

- **The boundary.** The vé was defined by a fence, a ditch, a stone row, or a natural feature (a stream, a ridge). The reconstruction should model the boundary based on the archaeological or the place-name evidence.
- **The interior.** The vé's interior was empty of permanent structures — it was a space, not a building. The reconstruction should represent the openness of the vé — the cleared ground, the sacred natural features (the stone, the tree, the spring) that were the focus of the ritual.
- **The prohibition.** The vé was defined by what was forbidden, not by what was present. The reconstruction cannot model a prohibition, but it can suggest the sense of boundary — the transition from the profane to the sacred, the crossing of the threshold.

**The Challenge of the Minimal Sacred:**

The hǫrgr and the vé are the most "minimal" of the Norse sacred sites — the least construction, the least architecture, the least evidence. The challenge for the digital reconstruction is to represent the sacredness without over-constructing it — to let the site be what it was: a pile of stones, a boundary in the landscape, a place where the sacred was encountered not through architecture but through presence.

### Required Reading
- The Horg excavation report (2038, course packet)
- Brink, S., "Vé and Þing — Sacred Space and Assembly" (2039)
- Course textbook, ch. 25-27

### Discussion Questions
1. How can a digital reconstruction represent a sacred space that is defined by prohibition rather than by construction?
2. What is the "minimal sacred"? Does the minimalism of the hǫrgr and the vé tell us something important about the Norse understanding of the sacred?
3. How should the reconstruction handle the absence of evidence — the features that we do not know about and cannot reconstruct?

---

## Lecture 10: The Álfhǫll in 3D — Modeling the Underground Sacred

The álfhǫll — the elf-hill, the burial mound — is a liminal sacred space that is both natural (the hill, the mound) and constructed (the burial chamber, the offering site). Its digital reconstruction requires the modeling of the underground — the darkness, the enclosure, the presence of the dead.

**The Evidence for the Álfhǫll:**

The evidence consists of:

- **The saga accounts** — the mound-encounters in the *Grettis saga* (Karr the Old) and the *Hervarar saga* (Angantýr's mound), the álfhǫll sacrifice in the *Kormáks saga*.
- **The archaeological evidence** — the burial mounds of the Viking Age and earlier periods, with their internal chambers (the burial rooms, the passage graves) and their external features (the mound itself, the boundary ditches, the standing stones).
- **The place-name evidence** — the álf- and alf- toponyms that identify the mounds as the dwellings of the álfar.

**Modeling the Álfhǫll:**

The 3D model of the álfhǫll must represent:

- **The exterior.** The mound, the surrounding landscape, the boundary features, and the approach (the path, the track) that leads to the mound.
- **The interior.** The burial chamber — the dark, enclosed space, with the grave goods (the weapons, the jewelry, the food) and the body (or the absence of the body, if the draugr has risen). The interior should be dark and claustrophobic — the sense of enclosure, of being underground, of the presence of the dead.
- **The lighting.** The interior should be lit only by the light that enters through the entrance — a narrow beam of daylight, fading into the darkness of the chamber. The lighting should be eerie, suggestive, not fully revealing.

**The Challenge of Modeling the Dead:**

The digital reconstruction of the álfhǫll raises the question of representing the dead. Should the body be modeled — the skeleton, the grave goods in situ — or should the chamber be left empty, the dead absent but implied? The question is both archaeological (the evidence for the burial) and ethical (the treatment of the dead in a digital reconstruction). The University's Digital Heritage Ethics Statement recommends that the dead not be represented directly — the burial chamber should be modeled, but the body should be indicated (by the grave goods, by the depression in the floor) rather than modeled explicitly.

### Required Reading
- The Icelandic elf-mound survey (2037, course packet)
- *Grettis saga*, ch. 18-19 (Grettir and Karr)
- Course textbook, ch. 28-30

### Discussion Questions
1. Should the dead be represented in the digital reconstruction of the álfhǫll? What are the ethical considerations?
2. How can the lighting of the álfhǫll's interior convey the sense of the sacred — the darkness, the enclosure, the presence of the dead?
3. How does the digital reconstruction of the álfhǫll relate to the tradition of the draugr — the walking dead? Can a digital reconstruction represent the possibility of the dead's return?

---

## Lecture 11: Project Proposal and Peer Review Workshop

Each student will develop a digital reconstruction of a Norse sacred site, using the techniques and the evidence base studied in the course. This lecture is a workshop session: students present their project proposals and receive feedback from the instructor and their peers.

**The Project Proposal:**

The proposal (5 pages) must include:

1. **The site.** The specific sacred site to be reconstructed — identified by name, location, and SLP database ID. The site must be one for which sufficient evidence exists (archaeological, place-name, textual) to support a reconstruction.
2. **The evidence base.** The evidence for the site — the archaeological, the place-name, the textual — and the reconstruction decisions that the evidence supports (and does not support).
3. **The reconstruction plan.** The plan for the reconstruction: the model (3D, Blender), the presentation (VR, WebXR), the documentation (the written report).
4. **The speculative elements.** The elements of the reconstruction that are not supported by evidence and the justification for including them.

**The Peer Review Process:**

The proposals are circulated to the class in advance of the workshop. Each student is assigned two proposals to review, using the review criteria:

- **Feasibility.** Is the site reconstructable with the available evidence?
- **Fidelity.** Does the proposal respect the evidence, and does it clearly identify the speculative elements?
- **Interest.** Will the reconstruction illuminate the understanding of the Norse sacred landscape?

### Required Reading
- The project proposal guidelines (course packet)
- The peer review criteria (course packet)

---

## Lecture 12: Final Project Presentation and Critique

The final session is the presentation of the completed digital reconstructions. Each student presents their reconstruction (10-minute presentation, followed by 5 minutes of questions), demonstrating the model, the VR experience, and the written documentation.

**The Presentation Requirements:**

The presentation must include:

1. **The evidence base.** What evidence was used to reconstruct the site? What were the key sources (archaeological, place-name, textual), and how did they inform the reconstruction?
2. **The reconstruction decisions.** What were the major decisions made in the reconstruction process? How were the speculative elements identified and justified?
3. **The VR demonstration.** A live demonstration (or a recorded walkthrough) of the VR experience of the reconstructed site.
4. **The interpretation.** What does the reconstruction reveal about the site that was not apparent from the evidence alone? How does the reconstruction change the understanding of the Norse sacred landscape?

**The Critique:**

The presentations are followed by a critique session. The critique questions include:

- **Fidelity.** Does the reconstruction accurately represent the evidence? Are the speculative elements clearly identified?
- **Illumination.** Does the reconstruction illuminate the understanding of the site and the Norse sacred landscape?
- **Experience.** How does the VR experience of the reconstructed site compare to the 2D, the photogrammetric, and the physical experience?

**The Final Submission:**

The final project will be submitted as:

- A 3D model (Blender .blend file)
- A VR-compatible export (glTF 2.0 .glb file)
- A written report (15-20 pages) documenting the evidence base, the reconstruction decisions, the speculative elements, and the interpretive conclusions
- A presentation video (5-10 minutes) demonstrating the VR experience

### Required Reading
- The final project submission guidelines (course packet)

---

*NP403: Digital Reconstruction of Sacred Sites*
*University of Yggdrasil, 2040*
*Nornir viti ok rúnar — By the runes and the Norns*