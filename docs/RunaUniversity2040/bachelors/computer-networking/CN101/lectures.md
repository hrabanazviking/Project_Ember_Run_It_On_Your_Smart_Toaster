# CN101: Introduction to Computer Networking — Protocols, Practice, and the Connected World
## Bachelor of Science in Computer Networking — University of Yggdrasil, 2040

**Credits:** 4
**Description:** Foundational survey of computer networking principles, from physical layer signaling to application-layer protocols. Students master the TCP/IP protocol suite, Ethernet and wireless technologies, switching and routing, network security fundamentals, and the 2040 networking landscape including quantum-safe protocols, mesh networks, and orbital constellations. The course emphasizes hands-on configuration, troubleshooting, and design.

**Instructor:** Dr. Erik Lindqvist, Professor of Network Engineering & Chief Architect of the Bifrǫst Mesh
**Lab:** Valhalla Network Lab, Sublevel 1, Hákon Computing Centre
**Office Hours:** Wednesdays 14:00-16:00, or by appointment

---

## Lectures

ᚠ **Lecture 1: The Network as Infrastructure — Foundations and Philosophy**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

This opening lecture establishes networking as both a technical discipline and a foundational infrastructure of modern civilization. By 2040, networks mediate virtually every human interaction: commerce, governance, education, healthcare, and social connection. We examine the historical evolution from ARPANET to the Bifrǫst Mesh, the layered model that organizes network knowledge, and the ethical responsibilities of those who design and operate critical infrastructure.

### Key Topics

- **Networks as Civilization's Nervous System:** The parallels between biological neural networks and communication networks. Centralized vs. decentralized architectures. The 2030s "Fragmentation Crisis" when national internet partitions and sovereign networks challenged the global internet's unity.
- **The OSI and TCP/IP Models:** The seven-layer OSI reference model and the pragmatic four-layer TCP/IP model. Why the OSI model persists in education despite TCP/IP's dominance in practice. Encapsulation, headers, and the protocol stack in action.
- **A Brief History:** Telegraph, telephone, ARPANET (1969), the Internet (1990s), mobile broadband (2000s), software-defined networking (2010s), the mesh revolution (2020s), quantum networks (2030s), and the 2040 orbital-mesh hybrid. The Yggdrasil Bifrǫst Mesh as a case study in evolutionary network architecture.
- **The Network Professional's Role:** From cable technician to network architect, SDN engineer, quantum network operator, and orbital link manager. The 2040 labor market: 23 million network professionals, with fastest growth in edge/mesh and quantum security roles.

### Lecture Notes

The network engineer in 2040 operates infrastructure that would seem like magic to a 1990s network administrator. A 2040 network architect designs topologies that span planetary distances — fiber under oceans, lasers through atmosphere, radio to orbiting satellites, and mesh relays across tundra and fjord. They manage heterogeneous equipment: classical Ethernet switches, quantum key distribution devices, neuromorphic traffic analyzers, and self-organizing mesh nodes. They secure against threats that did not exist two decades ago: AI-generated attack traffic, quantum cryptanalysis, and supply-chain-compromised firmware.

Yet the fundamentals remain constant. The OSI model, developed in 1984, still provides the conceptual vocabulary for network design. When a student sends an HTTP request to a web server, that request descends through the application layer (HTTP headers), transport layer (TCP segment with port numbers), network layer (IP packet with addresses), and link layer (Ethernet frame with MAC addresses) — each layer adding its own header through encapsulation. Understanding this process is not academic; it is the foundation of troubleshooting. When a web page fails to load, the network professional asks: is the link up (Layer 1)? Is there an IP address (Layer 3)? Is the DNS resolving (Layer 7)? The layered model structures diagnostic reasoning.

The Bifrǫst Mesh exemplifies network evolution. Begun as a university campus network in 2025, it expanded through the 2030s into a regional mesh connecting research stations, hospitals, and government offices across the Nordic countries. By 2040, it includes 50,000 nodes — from data center routers to weather buoys to satellite ground stations. The mesh is self-healing: if a fiber link between Oslo and Bergen is cut by an anchor drag, traffic automatically reroutes through satellite and terrestrial microwave links within milliseconds. The mesh is self-optimizing: AI traffic engineers continuously adjust routing to minimize latency and energy consumption. And the mesh is sovereign: all traffic between Nordic nodes remains within Nordic jurisdiction, protected by quantum encryption.

### Required Reading

- Kurose, J.F. & Ross, K.W. (2037). *Computer Networking: A Top-Down Approach*, 10th Edition. Pearson. Chapter 1.
- Mårtensson, J. (2035). "The Bifrǫst Mesh: A Decade of Evolution." *ACM SIGCOMM*, 2035.
- Yggdrasil Network Philosophy (2040). UoY Digital Press. "Networks as Infrastructure."

### Discussion Questions

1. The 2030s Fragmentation Crisis saw nations create sovereign internet partitions. Is a unified global internet preferable to fragmented national networks? What are the tradeoffs in security, sovereignty, and innovation?
2. The OSI model is conceptually elegant but TCP/IP won in practice. Why does OSI persist in networking education? Is it still useful, or does it create confusion?
3. A small island nation asks you to design its national network. It has no fiber infrastructure, limited budget, and needs connectivity to the global internet. What technologies would you recommend, and in what priority order?

---

ᚢ **Lecture 2: Physical Layer — Bits on Wire, Fiber, and Air**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

Every network begins with physical signals. This lecture covers the physical layer: how bits are encoded into electrical, optical, and electromagnetic signals, the properties of transmission media, and the practical skills of cable installation and troubleshooting. We examine copper (Ethernet), fiber optics, and wireless propagation, with emphasis on the 2040 landscape including hollow-core fiber and terahertz wireless.

### Key Topics

- **Digital Signaling:** Voltage levels, clock recovery, Manchester encoding, and 4B/5B encoding. The challenge: how does the receiver know when each bit starts and ends? Synchronous vs. asynchronous transmission.
- **Copper Media:** Twisted-pair cabling (Cat 8, supporting 40 Gbps at 30 meters), coaxial cable (still used for cable modems and some industrial applications), and the electrical properties that limit bandwidth: attenuation, crosstalk, and impedance mismatch.
- **Fiber Optics:** Single-mode vs. multi-mode fiber, wavelength-division multiplexing (WDM), and the 2040 revolution of hollow-core fiber (air-guiding rather than glass-guiding, achieving 99.7% of the speed of light and 50% lower latency). Fiber splicing, connector types, and optical time-domain reflectometry (OTDR) for fault location.
- **Wireless Propagation:** Radio frequency bands, path loss, multipath fading, and interference. The Shannon-Hartley theorem: channel capacity as a function of bandwidth and signal-to-noise ratio. 2040 wireless: Wi-Fi 9 (802.11be-2040), 6G cellular, and terahertz (100-300 GHz) for ultra-short-range high-speed links.
- **Physical Layer Troubleshooting:** Cable testers, spectrum analyzers, and the art of reading a wiring diagram. Common faults: open circuits, short circuits, split pairs, and impedance mismatches.

### Lecture Notes

The physical layer is where the abstraction of networking meets the reality of physics. A network engineer who cannot crimp a cable, splice a fiber, or interpret a spectrum analyzer trace is like a surgeon who cannot hold a scalpel — theoretically knowledgeable but practically helpless. The physical layer is also where many network failures originate: a bent fiber causing micro-bends and attenuation, a corroded connector introducing reflection, a cable run too close to a fluorescent ballast picking up electromagnetic interference.

Hollow-core fiber is the most significant physical layer innovation of the 2030s. Conventional fiber guides light through glass, which slows it to roughly 70% of the speed of light in vacuum. For a transatlantic link of 6,000 km, this means a minimum one-way latency of 28 milliseconds — a fundamental limit that cannot be overcome by better electronics. Hollow-core fiber guides light through an air-filled core surrounded by a photonic crystal cladding, achieving 99.7% of light speed and reducing transatlantic latency to 20 milliseconds. For high-frequency trading, online gaming, and remote surgery, this 8-millisecond difference is transformative. The first transatlantic hollow-core cable, the *Nordic Lightning* link, became operational in 2037.

Wireless propagation is governed by the laws of physics that are immune to marketing hype. The Shannon-Hartley theorem states that channel capacity C = B log₂(1 + S/N), where B is bandwidth and S/N is signal-to-noise ratio. You can increase capacity by increasing bandwidth (using higher frequencies) or improving signal-to-noise ratio (more power, better antennas, or shorter distances). This is why 6G achieves terabit speeds: it uses millimeter-wave and terahertz bands with massive bandwidth. But these frequencies have terrible penetration — a single tree or rain shower can block the signal. Network engineers must balance capacity against reliability, coverage against density.

### Required Reading

- Stallings, W. (2036). *Data and Computer Communications*, 12th Edition. Pearson. Chapters 2-4.
- Poletti, F. (2033). "Hollow-Core Fibres for Data Transmission." *Nature Photonics*, 7, 279-281.
- Yggdrasil Physical Layer Handbook (2040). UoY Digital Press. "Fiber Installation" and "Wireless Survey."

### Discussion Questions

1. Hollow-core fiber reduces latency but is more fragile and expensive than conventional fiber. For a network connecting London and New York, would you specify hollow-core or conventional fiber? What factors determine the decision?
2. A warehouse deploys Wi-Fi 9 for autonomous robot control. Robots experience intermittent disconnections near metal shelving. Using your knowledge of wireless propagation, identify the likely cause and propose solutions.
3. The Shannon-Hartley theorem suggests that infinite capacity is possible with infinite bandwidth. Why is this not practical? What limits real-world wireless capacity?

---

ᚦ **Lecture 3: Data Link Layer — Frames, Switches, and Local Networks**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

The data link layer transforms unreliable physical transmission into reliable local communication. This lecture covers Ethernet framing, MAC addressing, switching, VLANs, and the Spanning Tree Protocol. We examine the design of switched local area networks, the evolution from hubs to switches to software-defined switches, and the 2040 landscape of time-sensitive networking (TSN) for industrial control.

### Key Topics

- **Ethernet Framing:** The Ethernet II frame format: preamble, destination MAC, source MAC, type/length, payload, and FCS (Frame Check Sequence). How the FCS detects corruption. The minimum and maximum frame sizes (64 and 1,518 bytes) and their implications.
- **MAC Addresses and ARP:** The 48-bit MAC address space, OUI (Organizationally Unique Identifier) assignment, and the Address Resolution Protocol (ARP). How a host maps an IP address to a MAC address on the local network. ARP spoofing attacks and mitigation (static ARP entries, dynamic ARP inspection).
- **Switches and Switching:** How a learning switch builds its MAC address table by observing source addresses. Unicast forwarding, broadcast flooding, and multicast handling. The difference between store-and-forward, cut-through, and fragment-free switching. Switch fabrics and backplane bandwidth.
- **VLANs:** Virtual LANs as logical segmentation of a physical network. Port-based VLANs, 802.1Q tagging, and trunk ports. The benefits: security isolation, broadcast containment, and organizational flexibility. Inter-VLAN routing.
- **Spanning Tree Protocol (STP):** Preventing loops in redundant topologies. How STP elects a root bridge, calculates path costs, and blocks redundant links. Rapid STP (RSTP) and Multiple STP (MSTP). The 2040 evolution: software-defined control of loop prevention.
- **Time-Sensitive Networking (TSN):** IEEE 802.1 standards for deterministic Ethernet. Scheduled traffic, frame preemption, and clock synchronization (gPTP). TSN in 2040: controlling robotic assembly lines, autonomous vehicles, and smart grid equipment with sub-microsecond timing guarantees.

### Lecture Notes

The switch is the unsung hero of networking. Every packet that traverses the internet passes through dozens of switches — in the access closet, the distribution layer, the core, and the data center. A switch operates invisibly, forwarding frames in microseconds, learning topology from traffic patterns, and adapting to changes without human intervention. The modern network engineer must understand switching deeply because misconfigured switches cause subtle, insidious failures: loops that consume all bandwidth, VLAN leaks that expose sensitive traffic, and spanning tree reconvergences that drop connections for 30 seconds.

ARP is deceptively simple and dangerously vulnerable. When a host needs to send a packet to a local IP address, it broadcasts an ARP request: "Who has this IP address? Tell me your MAC address." The target responds with its MAC, and communication proceeds. But any host can forge an ARP reply, claiming to own an IP address it does not. This is ARP spoofing: the attacker redirects traffic through their machine, enabling eavesdropping or modification. ARP spoofing is trivial to execute and difficult to detect because ARP has no authentication. Modern networks use dynamic ARP inspection (DAI) — switches verify ARP replies against a trusted DHCP snooping database — but DAI must be configured explicitly, and many networks omit it.

VLANs are the network administrator's primary tool for segmentation. A university network may have thousands of hosts — students, faculty, staff, guests, IoT devices, medical equipment — each with different security requirements. VLANs separate these groups at Layer 2, so a compromised student laptop cannot directly attack a medical device, even if both are connected to the same physical switch. However, VLANs are frequently misconfigured. The classic error is leaving a switch port in "dynamic desirable" mode, which negotiates a trunk with any connected device — allowing an attacker to hop between VLANs by sending tagged frames. The 2035 *VLAN Hopping Incident* at a Nordic bank exposed customer data because a conference room port was misconfigured this way.

Time-Sensitive Networking extends Ethernet into domains previously served by specialized fieldbuses (CAN, Profibus, EtherCAT). TSN provides deterministic latency guarantees — a packet sent at time T will arrive by T + Δ with 99.9999% probability — through traffic scheduling, frame preemption, and synchronized clocks. In 2040, TSN enables autonomous vehicle control networks, where brake commands must propagate from sensor to actuator in less than 1 millisecond. It enables smart grid protection systems, where fault isolation commands must arrive before equipment is damaged. And it enables robotic surgery, where haptic feedback requires sub-millisecond round-trip latency. The network engineer must understand TSN because these applications do not tolerate "best effort."

### Required Reading

- Kurose, J.F. & Ross, K.W. (2037). *Computer Networking*, 10th Edition. Pearson. Chapter 6.
- Seifert, R. (2032). *The Switch Book*, 3rd Edition. Wiley. Chapters 1-3, 7-8.
- Yggdrasil Switch Configuration Guide (2040). UoY Digital Press. "VLAN Design" and "TSN Deployment."

### Discussion Questions

1. A network administrator claims that VLANs provide security equivalent to physical separation. Is this true? Under what conditions can VLAN security be bypassed, and how would you prevent it?
2. STP blocks redundant links to prevent loops, but this wastes capacity. How do modern networks (MSTP, shortest-path bridging, SDN-controlled topologies) balance loop prevention with bandwidth utilization?
3. TSN provides deterministic latency but requires precise clock synchronization. How does gPTP achieve sub-microsecond synchronization across a network, and what happens if the grandmaster clock fails?

---

ᚬ **Lecture 4: Network Layer — IP, Routing, and Internetworking**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

The network layer enables communication across multiple networks, forming the "internet" in internetworking. This lecture covers IP addressing (IPv4 legacy and IPv6 dominance), subnetting, the IP packet format, fragmentation, and the routing protocols that build the internet's forwarding tables. We examine the global routing table, BGP instability, and the 2040 transition to quantum-safe routing.

### Key Topics

- **IP Addressing:** IPv4 address exhaustion and the transition to IPv6 (now dominant in 2040, with IPv4 supported only through carrier-grade NAT and dual-stack). IPv6 address format, prefix notation, and address types (unicast, multicast, anycast). The Yggdrasil Rune Addressing scheme for mesh nodes.
- **Subnetting and CIDR:** Classless Inter-Domain Routing, prefix lengths, and variable-length subnet masking. How organizations allocate address space efficiently. The subnetting math: determining network, broadcast, and host addresses from a prefix.
- **The IP Packet:** Version, header length, DSCP (Differentiated Services Code Point), total length, identification, flags, fragment offset, TTL, protocol, header checksum, source/destination addresses, and options. Why header checksum is recomputed at every hop. TTL as a loop-prevention mechanism.
- **Fragmentation and Path MTU Discovery:** When packets exceed a link's MTU (Maximum Transmission Unit), they must be fragmented. The problems with fragmentation: reassembly complexity, security vulnerabilities (fragmentation attacks), and middlebox interference. Path MTU Discovery as the modern solution.
- **Routing Protocols:** Distance-vector (RIP, EIGRP) vs. link-state (OSPF, IS-IS). Border Gateway Protocol (BGP) as the inter-domain routing protocol that makes the internet work. BGP attributes, path selection, and policy routing. The 2040 Mesh Link State Protocol (MLSP) for edge networks.
- **Global Routing Challenges:** The size of the global routing table (1.2 million prefixes in 2040), routing table growth, and the limits of TCAM memory in routers. BGP hijacking incidents and the RPKI (Resource Public Key Infrastructure) framework for route origin validation.

### Lecture Notes

IP is the universal language of networking. Every device that connects to the internet — from a quantum computer to a weather buoy to a smart toothbrush — speaks IP. This universality is IP's greatest strength and its greatest burden: the protocol must accommodate every possible application, every possible link technology, and every possible scale. The result is a protocol that is elegant in its simplicity (best-effort datagram delivery) and terrifying in its operational complexity (the global routing table, BGP policy, NAT traversal, multicast, QoS, and now quantum-safe headers).

IPv6, standardized in 1998 and deployed at scale through the 2020s and 2030s, finally achieved dominance in 2040. The address space is effectively infinite (2^128 addresses, or 340 undecillion), enabling every grain of sand on Earth to have its own subnet. But IPv6 is not just "IPv4 with longer addresses." It eliminates broadcast (replaced by multicast and anycast), mandates IPSec (though in practice many networks still use TLS), and simplifies the header format (fixed 40-byte header, no checksum, no fragmentation by routers). The transition from IPv4 was painful and took four decades — a reminder that infrastructure changes at geological speed.

BGP is the protocol that makes the internet a single network. It is also the protocol that makes network engineers wake up at 3 AM in a cold sweat. BGP exchanges reachability information between autonomous systems (ASes) — the organizations (ISPs, enterprises, universities) that independently operate networks. Each AS announces the IP prefixes it can reach, and BGP selects the "best" path based on attributes like AS-path length, local preference, and MED. But BGP has no built-in security: any AS can announce any prefix, and other ASes will believe it. This enables BGP hijacking — deliberately announcing someone else's IP addresses to intercept traffic. The 2033 *Aurora Hijack* redirected traffic from 200 European banks through a rogue AS for 45 minutes, enabling credential harvesting. RPKI, the Resource Public Key Infrastructure, cryptographically signs route announcements, but deployment reached only 70% by 2040.

The Mesh Link State Protocol (MLSP) is the 2040 successor to OSPF for edge and mesh networks. Unlike OSPF, which assumes relatively stable topologies, MLSP handles highly dynamic environments where nodes join, leave, and move continuously. Each node maintains a link-state database of its local neighborhood, and flooding is limited to avoid overwhelming the network. MLSP integrates with AI traffic engineers: rather than using fixed link weights, MLSP dynamically adjusts metrics based on real-time latency, energy consumption, and security posture. The Bifrǫst Mesh runs MLSP on every node, from data center routers to battery-powered environmental sensors.

### Required Reading

- Doyle, J. & Carroll, J. (2035). *Routing TCP/IP*, 3rd Edition. Cisco Press. Volume I, Chapters 1-5, 8-10.
- Butler, K. (2034). "BGP Security: A Survey." *IEEE Communications Surveys & Tutorials*, 16(4), 2151-2175.
- Yggdrasil Routing Operations Guide (2040). UoY Digital Press. "MLSP Configuration" and "BGP Policy."

### Discussion Questions

1. BGP has operated without built-in security for 50 years. Why has it been so difficult to deploy RPKI widely? What are the technical and political barriers?
2. A company has been allocated an IPv6 /48 prefix. Design a subnetting scheme that supports 100 branch offices, each with 5 VLANs and room for growth. How many addresses does each subnet receive?
3. MLSP uses AI to dynamically adjust link metrics. What are the risks of AI-controlled routing? How would you design safeguards to prevent pathological behavior?

---

ᚱ **Lecture 5: Transport Layer — TCP, UDP, and Beyond**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

The transport layer provides process-to-process communication: the abstraction that allows applications to treat the network as a reliable pipe between programs. This lecture covers TCP (reliable, connection-oriented transport), UDP (unreliable, datagram transport), congestion control, and the 2040 transport landscape including QUIC, BTP, and neuromorphic transport protocols.

### Key Topics

- **TCP Fundamentals:** Connection establishment (three-way handshake), sequence numbers, acknowledgments, sliding window, flow control, and connection termination. The TCP header: source/destination ports, sequence number, acknowledgment number, window size, flags, and options.
- **TCP Congestion Control:** The evolution from Tahoe and Reno to CUBIC, BBR, and the 2040 *Yggdrasil Adaptive Rate Control* (YARC). Slow start, congestion avoidance, fast retransmit, and fast recovery. The challenge of bufferbloat and the solution of BBR's model-based approach.
- **UDP and Datagram Services:** The simplicity of UDP (8-byte header, no connection state, no reliability). Applications that use UDP: DNS, video streaming, online gaming, and IoT telemetry. The 2040 *Low-Latency Datagram Protocol* (LLDP) for real-time control applications.
- **QUIC and HTTP/3:** The transport protocol that runs over UDP instead of TCP. Connection migration (surviving IP address changes), 0-RTT connection establishment, and built-in encryption. Why QUIC replaces TCP for web traffic.
- **The Bifrǫst Transport Protocol (BTP):** A quantum-resistant, mesh-optimized transport developed at Yggdrasil. Multi-path transport, dynamic path selection, and integration with the Bifrǫst security layer. BTP for satellite, mesh, and terrestrial links.
- **Transport Protocol Selection:** When to use TCP (reliable file transfer), UDP (real-time streaming), QUIC (web), BTP (mesh), or LLDP (control). The tradeoffs: latency, reliability, overhead, and implementation complexity.

### Lecture Notes

TCP is one of the most successful protocols in history. It has carried virtually every reliable internet communication for five decades — email, web pages, file transfers, databases. Its design principles — end-to-end reliability, congestion control, and graceful degradation — have proven remarkably robust. But TCP was designed for wired networks with low error rates and stable topologies. It performs poorly on wireless links (where packet loss is common and not a congestion signal), high-latency links (where the window does not fully utilize bandwidth), and dynamic environments (where connections break and must be reestablished).

Congestion control is TCP's most intellectually rich feature. The fundamental problem: how does a sender determine the network's capacity without overwhelming it? TCP Tahoe (1988) used slow start (exponentially increasing rate until loss) and congestion avoidance (linear increase after that). TCP Reno added fast retransmit and fast recovery. CUBIC (2006) used a cubic function for window growth, achieving better performance on high-bandwidth links. BBR (Bottleneck Bandwidth and RTT, 2016) took a radical approach: instead of using packet loss as a congestion signal, it models the network's bandwidth and round-trip time, sending at the calculated rate. BBR eliminated bufferbloat — the phenomenon where excessive buffering in network devices causes latency spikes — and became the default in Linux by 2030.

The Yggdrasil Adaptive Rate Control (YARC) extends BBR for mesh and satellite environments. YARC continuously probes multiple paths, measuring not just bandwidth and RTT but also energy consumption (relevant for battery-powered mesh nodes) and security posture (preferring paths with stronger quantum encryption). It adapts to topology changes in milliseconds — essential for satellite handoffs and mobile mesh nodes. YARC is the default transport for Bifrǫst Mesh services.

QUIC represents the transport protocol's future for web traffic. Developed by Google and standardized in 2031, QUIC runs over UDP rather than TCP, enabling several innovations: connection migration (a QUIC connection survives IP address changes, so a smartphone switching from Wi-Fi to cellular maintains the same connection), 0-RTT resumption (reconnecting to a previously visited server takes zero round-trips), and built-in TLS encryption (no separate handshake). QUIC is now used by 85% of web traffic in 2040.

The Bifrǫst Transport Protocol is Yggdrasil's answer to the transport needs of the 2040s. BTP runs over UDP (like QUIC) but adds mesh-specific features: multi-path transport (sending packets through multiple routes simultaneously for resilience), dynamic path selection (continuously choosing the best path based on latency, energy, and security), and quantum-resistant encryption using CRYSTALS-Kyber. BTP is used throughout the Bifrǫst Mesh for internal services and for the Yggdrasil VPN that connects remote researchers to campus resources.

### Required Reading

- Stevens, W.R. (2031). *TCP/IP Illustrated*, 2nd Edition. Addison-Wesley. Volume 1, Chapters 17-24.
- Ha, S., Rhee, I., & Xu, L. (2034). "CUBIC: A New TCP-Friendly High-Speed TCP Variant." *ACM SIGOPS Operating Systems Review*, 42(5), 64-74.
- Yggdrasil Transport Protocol Reference (2040). UoY Digital Press. "YARC" and "BTP."

### Discussion Questions

1. TCP treats all packet loss as congestion, but wireless links lose packets due to interference. How do modern congestion control algorithms (BBR, YARC) distinguish between congestion loss and error loss? Why is this distinction important?
2. QUIC provides connection migration, which is valuable for mobile devices. But it requires the server to maintain connection state across IP changes. What are the scalability implications for a server handling millions of QUIC connections?
3. BTP's multi-path transport sends packets through multiple routes. How does the receiver handle out-of-order delivery? What are the security implications if one path is compromised?

---

ᚴ **Lecture 6: Application Layer — DNS, HTTP, and the Web Ecosystem**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

The application layer is where networking serves human needs. This lecture covers the Domain Name System (DNS), the Hypertext Transfer Protocol (HTTP), email (SMTP, IMAP), and the 2040 landscape of decentralized web technologies. We examine how these protocols work, how they are secured, and how network professionals manage their deployment.

### Key Topics

- **DNS:** The hierarchical namespace, zone files, record types (A, AAAA, MX, TXT, NS, CNAME, and the 2040 additions QKEY for quantum key pointers and NEURO for neuromorphic service discovery). Recursive and authoritative resolvers, caching, and the DNSSEC security extension. The 2030s DNS over HTTPS (DoH) and DNS over TLS (DoT) privacy enhancements.
- **HTTP and the Web:** HTTP/1.1, HTTP/2 (multiplexing, server push), and HTTP/3 (over QUIC). Request methods, status codes, headers, and content negotiation. RESTful API design. The 2040 *Semantic HTTP* extension: headers that convey meaning to AI agents, enabling automated service discovery and negotiation.
- **Email Infrastructure:** SMTP (Simple Mail Transfer Protocol) for mail transfer, IMAP and POP for mail retrieval, and the 2040 *Yggdrasil Mail Protocol* (YMP) — an end-to-end encrypted, spam-resistant messaging system. SPF, DKIM, and DMARC for sender authentication.
- **Content Delivery Networks:** The Akamai/Cloudflare model extended to 2040: edge caching, dynamic content acceleration, DDoS protection, and the Bifrǫst Mesh's distributed content fabric. How CDNs reduce latency and absorb traffic spikes.
- **Decentralized Web:** Peer-to-peer protocols (IPFS, BitTorrent), blockchain naming (Ethereum Name Service), and the tension between decentralized ideals and centralized convenience. The 2040 *Web Sovereignty* movement: user-controlled data and identity.

### Lecture Notes

DNS is simultaneously the internet's most critical and most abused system. Every web request begins with a DNS lookup: the user types "yggdrasil.no," and the resolver translates this to an IP address. If DNS fails, the internet becomes unusable — you cannot reach websites, send email, or connect to services. Yet DNS was designed in the 1980s with no security: queries and responses are unauthenticated, enabling cache poisoning (injecting false records into a resolver's cache) and amplification attacks (small queries generating large responses directed at a victim).

DNSSEC, deployed at scale through the 2020s and 2030s, cryptographically signs DNS records, preventing cache poisoning. But DNSSEC is complex, fragile, and still not universally deployed (75% by 2040). The 2030s saw the rise of DNS over HTTPS (DoH) and DNS over TLS (DoT), which encrypt DNS queries to prevent eavesdropping and manipulation. By 2040, most DNS traffic is encrypted, though this has created tension: encrypted DNS bypasses local network policies, preventing corporate and parental filtering. The Yggdrasil resolver supports both encrypted and plaintext DNS, with policy-driven routing based on client identity.

HTTP/3 over QUIC is now the dominant web protocol. For users, the benefit is faster page loads and smoother connections on mobile devices. For network engineers, the challenge is visibility: the encryption and connection migration features of QUIC mean that traditional network monitoring tools cannot inspect HTTP traffic for security, performance, or compliance purposes. The Yggdrasil *Heimdall Gateway* decrypts QUIC traffic at the edge (with user consent for institutional networks), applies security policies, and re-encrypts before forwarding — a "bump in the wire" architecture that preserves end-to-end encryption while enabling monitoring.

The decentralized web challenges the client-server paradigm that has dominated since the 1990s. In a decentralized web, content is addressed by its hash rather than its location: instead of "https://yggdrasil.no/document.pdf," you access "ipfs://QmXyz..." which resolves to a hash-addressed document stored on participating peers. This makes content censorship-resistant (there is no single server to block) and durable (content persists as long as any peer hosts it). But decentralization introduces new problems: content discovery (how do you find what you need?), performance (peer-to-peer is often slower than centralized CDNs), and governance (who moderates decentralized content?). The 2040 Web Sovereignty movement seeks a middle ground: user-controlled identity and data, but with optional centralized services for convenience.

### Required Reading

- Kurose, J.F. & Ross, K.W. (2037). *Computer Networking*, 10th Edition. Pearson. Chapter 2.
- Mockapetris, P. (2032). "DNS: The First 50 Years." *Internet History Journal*, 15(2), 45-62.
- Yggdrasil Application Layer Operations (2040). UoY Digital Press. "Heimdall Gateway" and "Decentralized Web."

### Discussion Questions

1. DNSSEC prevents cache poisoning but does not encrypt queries. DoH encrypts queries but does not authenticate responses. What is the relationship between these security properties, and what combination best protects users?
2. HTTP/3's encryption makes network monitoring difficult. Is this a bug or a feature? Under what circumstances should network operators be able to inspect encrypted traffic?
3. The decentralized web promises censorship resistance but complicates content moderation. How should illegal or harmful content be addressed in a decentralized system? Is this a technical problem, a legal problem, or both?

---

ᚺ **Lecture 7: Wireless and Mobile Networks**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

Wireless networks have moved from convenient alternative to primary access method. This lecture covers IEEE 802.11 (Wi-Fi) standards, cellular network evolution (5G to 6G), mobile IP, mesh wireless, and the 2040 landscape of integrated terrestrial-satellite-orbit connectivity. We examine the radio resource management, handoff protocols, and energy optimization that enable seamless mobile connectivity.

### Key Topics

- **IEEE 802.11 Evolution:** From 802.11b (11 Mbps, 1999) to 802.11be-2040 (Wi-Fi 9, 100 Gbps, sub-millisecond latency). OFDMA, MU-MIMO, beamforming, and target wake time (TWT) for IoT power saving. The 6 GHz band and the move to terahertz for ultra-short-range links.
- **Cellular Networks:** 5G (enhanced mobile broadband, ultra-reliable low-latency communication, massive machine-type communication) and 6G (terabit speeds, integrated sensing and communication, AI-native network architecture). The 6G timeline: early deployment 2035, widespread by 2040. Network slicing: virtual networks with guaranteed performance on shared physical infrastructure.
- **Mobile IP and Seamless Handoff:** How devices maintain connectivity while moving between networks. The Mobile IP protocol (home agent, foreign agent, tunneling) and the 2040 *Session Continuity Protocol* (SCP) that preserves application state across IP changes without Mobile IP's triangular routing inefficiency.
- **Mesh Wireless:** Ad-hoc networks where nodes relay traffic for neighbors. The 802.11s mesh standard, the B.A.T.M.A.N. protocol, and the Yggdrasil *Mesh Link* protocol for rural broadband. Applications: disaster recovery, military communications, rural internet, and IoT sensor networks.
- **Satellite Integration:** Low-earth orbit (LEO) constellations (Starlink 3.0, OneWeb, the EU IRIS² system) providing global coverage with 20ms latency. Integration with terrestrial networks: satellite backhaul for remote cells, hybrid routing that seamlessly switches between terrestrial and satellite paths.

### Lecture Notes

The 2040 mobile user expects connectivity everywhere: in subways, on ships, in aircraft, in the Arctic wilderness, and eventually on the Moon. This expectation is enabled by the convergence of cellular, Wi-Fi, satellite, and mesh technologies into a unified access fabric. The network professional must understand all of these technologies because modern devices do not use one at a time — they use all of them, simultaneously and transparently.

Wi-Fi 9 (802.11be-2040) achieves 100 Gbps through a combination of technologies: 320 MHz channel bandwidth (in the 6 GHz band), 16x16 MIMO (multiple antennas transmitting and receiving simultaneously), 4096-QAM (packing 12 bits per symbol), and multi-link operation (using multiple bands simultaneously). But raw speed is not the only improvement: Target Wake Time (TWT) allows IoT devices to sleep for seconds or minutes between transmissions, extending battery life from days to years. Beamforming focuses radio energy toward specific devices rather than broadcasting in all directions, improving range and reducing interference.

6G represents a paradigm shift from "faster 5G" to "network as sensor." 6G base stations use the same signals that carry data to also sense the environment: detecting the position and movement of devices, vehicles, and even people through radio reflections. This integrated sensing and communication (ISAC) enables applications like pedestrian safety (a vehicle's 6G radio detects a person stepping into the street even if they are occluded) and structural health monitoring (detecting bridge deformation through changes in radio propagation). The ethical implications are profound: a network that can sense people is a network that can surveil them.

Mesh wireless is the democratizer of connectivity. In areas where building cell towers is uneconomical — rural valleys, remote islands, disaster zones — mesh networks enable communities to build their own connectivity. The Yggdrasil Mesh Link protocol, deployed in 50 rural Norwegian communities, uses rooftop directional antennas to create multi-hop wireless networks that share a single backhaul connection. A typical community network has 20-50 nodes, achieves 100 Mbps to each home, and costs one-tenth of fiber deployment. The technical challenge is interference management: in a dense mesh, every transmission is a potential source of interference for neighbors. The Mesh Link protocol uses a combination of time-division multiplexing, directional antennas, and AI-powered channel assignment to maximize throughput.

### Required Reading

- Gast, M.S. (2038). *802.11 Wireless Networks: The Definitive Guide*, 4th Edition. O'Reilly. Chapters 1-3, 10-12.
- Andrews, J.G., et al. (2035). "What Will 6G Be?" *IEEE Journal on Selected Areas in Communications*, 38(8), 1747-1761.
- Yggdrasil Wireless Operations Guide (2040). UoY Digital Press. "Mesh Link Deployment" and "Satellite Integration."

### Discussion Questions

1. 6G's integrated sensing and communication enables safety applications but also mass surveillance. Should ISAC capabilities be restricted by law? How would you enforce such restrictions?
2. Mesh wireless provides affordable rural connectivity but cannot match fiber performance. Is "good enough" connectivity (100 Mbps, moderate latency) sufficient for economic development, or does it create a two-tier digital society?
3. A passenger aircraft must maintain connectivity across oceanic routes. Describe the handoff sequence between terrestrial cellular, satellite, and onboard Wi-Fi as the plane departs, cruises, and arrives.

---

ᚾ **Lecture 8: Network Security — Defense in Depth**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

Network security is not a product; it is a process. This lecture covers the principles of secure network design: firewalls, intrusion detection/prevention, VPNs, zero-trust architecture, and the 2040 quantum-safe security landscape. We examine real-world attacks, analyze their mechanisms, and derive defensive strategies. The emphasis is on defense in depth: multiple independent security layers that slow attackers and limit breach impact.

### Key Topics

- **Threat Model:** Understanding who attacks and why: nation-states (strategic advantage), criminals (financial gain), hacktivists (political expression), insiders (revenge, profit, accident), and AI (autonomous agents with unclear motives). The 2040 threat landscape: AI-generated phishing, deepfake social engineering, and quantum-enabled cryptanalysis.
- **Firewalls and Perimeter Defense:** Stateful packet inspection, application-layer gateways, next-generation firewalls (NGFW) with integrated IDS/IPS, and the 2040 *Neural Firewall* — an AI-powered system that learns normal traffic patterns and detects anomalies. The limits of perimeter defense: once breached, the attacker has free movement.
- **Intrusion Detection and Prevention:** Signature-based detection (known attack patterns) vs. anomaly-based detection (deviations from normal). The Yggdrasil *Guardian* neural IDS. False positives, false negatives, and the base rate fallacy. Honeypots and deception technology.
- **Virtual Private Networks:** Site-to-site VPNs (IPsec), remote access VPNs (SSL/TLS, WireGuard), and the 2040 *Quantum VPN* using quantum key distribution for key exchange. VPN limitations: they protect transit but not endpoints; they create a trusted tunnel that, if breached, exposes the entire network.
- **Zero-Trust Architecture:** The principle: "never trust, always verify." Every access request is authenticated and authorized, regardless of network location. Microsegmentation, identity-aware proxies, and continuous authentication. The 2040 implementation: the Yggdrasil Heimdall Identity Fabric.

### Lecture Notes

Network security has evolved from an afterthought to the primary design constraint. In 2020, security was often a layer added after the network was built: bolt on a firewall, install antivirus, patch occasionally. In 2040, security is woven into every layer of the network architecture: quantum-resistant encryption on every link, AI-powered anomaly detection on every segment, zero-trust access controls on every resource, and automated response to every detected threat. The network engineer is also a security engineer; the distinction has dissolved.

The threat landscape of 2040 includes actors and techniques unimaginable in 2020. AI-generated phishing produces emails indistinguishable from legitimate communication, personalized with knowledge scraped from social media. Deepfake voice synthesis impersonates executives for wire fraud. Autonomous attack agents scan for vulnerabilities 24/7, adapt to defensive measures, and coordinate swarm attacks against multiple targets simultaneously. Quantum computers, while not yet cryptanalytically relevant for most systems, threaten the long-term security of recorded encrypted communications (harvest now, decrypt later). The defender must protect against all of these, while the attacker needs to exploit only one vulnerability.

Zero-trust architecture is the response to the failure of perimeter defense. The traditional model — a hard shell around a soft center — assumed that once inside the firewall, users and devices were trusted. This assumption collapsed under remote work, cloud services, supply chain attacks, and insider threats. Zero-trust eliminates the perimeter: every user must authenticate, every device must attest its health, every application must authorize access based on identity, context, and behavior. The Yggdrasil Heimdall Identity Fabric implements zero-trust across the Bifrǫst Mesh. When a researcher in Tromsø accesses a database in Copenhagen, Heimdall verifies their biometric identity, checks that their device has current security patches, confirms they have authorization for the requested data, and monitors their behavior for anomalies — all in milliseconds, transparent to the user.

The Neural Firewall represents the 2040 evolution of perimeter defense. Rather than relying on static rules ("block port 22 from outside"), the Neural Firewall trains a deep neural network on months of normal traffic patterns. It learns the normal behavior of every host, every protocol, and every communication pattern. When it detects deviation — a server suddenly communicating with a new external IP, a user accessing files at 3 AM from an unusual location, a traffic pattern that statistically resembles known attack tools — it blocks the traffic and alerts security operations. The false positive rate is low (0.1%) because the model is trained on the specific network's behavior, not generic attack signatures. But false positives still occur, and the security team must balance security against operational disruption.

### Required Reading

- Northcutt, S. (2037). *Network Security: A Hands-On Approach*, 3rd Edition. CreateSpace. Chapters 1-4, 8-10.
- Schneier, B. (2036). *Click Here to Kill Everybody*. Norton. Chapters 5-7.
- Yggdrasil Security Architecture (2040). UoY Digital Press. "Zero-Trust Implementation" and "Neural Firewall."

### Discussion Questions

1. Zero-trust requires authenticating every access request. What are the latency and usability implications? How does Heimdall achieve sub-100ms authentication without annoying users?
2. The Neural Firewall learns normal behavior and blocks anomalies. What happens when legitimate behavior changes — a new software deployment, a reorganization, a pandemic forcing remote work? How would you prevent the firewall from blocking essential activity?
3. A nation-state attacker has unlimited resources and patience. Can any network be fully secure against such an adversary? If not, what is the rational goal of network security?

---

ᛁ **Lecture 9: Software-Defined Networking and Network Automation**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

Software-defined networking (SDN) separates the network's control plane (deciding where traffic goes) from the data plane (forwarding traffic), enabling centralized, programmatic control of network behavior. This lecture covers SDN architecture, OpenFlow and its successors, network automation with Python and Ansible, and the 2040 landscape of intent-based networking (IBN) and AI-driven network management.

### Key Topics

- **SDN Architecture:** The three-layer model: application layer (network apps), control layer (SDN controller), and infrastructure layer (switches and routers). The southbound API (OpenFlow, P4, NETCONF) communicates from controller to devices; the northbound API (REST) communicates from applications to controller.
- **OpenFlow and P4:** OpenFlow (the original SDN protocol) matches packets against flow tables and applies actions. P4 (Programming Protocol-independent Packet Processors) goes further, allowing programmers to define new forwarding behaviors. The 2040 state: P4 is standard for programmable switches.
- **Network Automation:** Scripting configuration with Python, templating with Jinja2, and orchestration with Ansible, Terraform, and the Yggdrasil *Norn-Playbook* system. Infrastructure-as-code: network configurations stored in version control, tested in simulation, and deployed automatically.
- **Intent-Based Networking (IBN):** The evolution from manual configuration to automated implementation of high-level intent. The administrator states "ensure that video traffic from building A to the media server has sub-10ms latency"; the IBN system translates this into specific QoS policies, routing constraints, and monitoring rules. The Yggdrasil *Vǫluspá* IBN platform.
- **AI-Driven Network Management:** Machine learning for traffic prediction, anomaly detection, root cause analysis, and autonomous remediation. The Auto-Skuld network management agent. The challenges: training data quality, model interpretability, and the risk of AI-induced failures.

### Lecture Notes

SDN is the most significant paradigm shift in networking since the transition from circuit switching to packet switching. Before SDN, every router and switch made independent forwarding decisions based on locally configured routing protocols. After SDN, a centralized controller maintains a global view of the network and pushes forwarding rules to devices. This enables applications that were previously impossible: global load balancing (sending traffic around congestion anywhere in the network), dynamic microsegmentation (creating isolated network segments in milliseconds), and traffic engineering (optimizing paths for latency, energy, or cost).

OpenFlow, the first SDN protocol, was simple but limited. It matched packets on a small set of header fields (L2-L4) and applied a small set of actions (forward, drop, modify header). P4, its successor, is radically more flexible: you define the packet parser (what headers to extract), the match-action tables (what fields to match and what to do), and the deparser (how to reassemble the packet). With P4, you can implement new protocols, custom load balancing, in-network telemetry, and even approximate computation (counting, sketching) in the switch itself. The Yggdrasil Bifrǫst switches run P4 programs compiled from high-level specifications.

Network automation is not optional in 2040. A network with 10,000 devices cannot be managed manually. Every configuration change must be code-reviewed, tested in a simulation environment, and deployed through automated pipelines. The Yggdrasil Norn-Playbook system extends Ansible with network-specific modules: it can simulate a configuration change on a digital twin of the network, verify that it does not introduce loops or blackholes, and deploy it with automatic rollback if monitoring detects anomalies. A network engineer in 2040 spends less time typing commands into CLI and more time writing declarative specifications and reviewing simulation results.

Intent-based networking is the ultimate goal of network automation. Rather than configuring individual devices, the administrator expresses high-level business objectives — "the trading floor must have 99.999% uptime with sub-1ms latency" — and the IBN system translates these into concrete network policies, monitors compliance, and remediates violations automatically. The Yggdrasil Vǫluspá platform (named after the Norse prophecy poem) uses a combination of formal verification (proving that configurations satisfy intent) and reinforcement learning (adapting policies based on observed outcomes). Vǫluspá is not yet fully autonomous — human operators review major changes — but it reduces the configuration error rate by 90%.

### Required Reading

- Kreutz, D., et al. (2035). "Software-Defined Networking: A Comprehensive Survey." *Proceedings of the IEEE*, 103(1), 14-76. (Updated retrospective.)
- Bosshart, P., et al. (2034). "P4: Programming Protocol-Independent Packet Processors." *ACM Computing Surveys*, 51(1), 1-37.
- Yggdrasil Network Automation Handbook (2040). UoY Digital Press. "Norn-Playbook" and "Vǫluspá."

### Discussion Questions

1. SDN centralizes control, creating a single point of failure. If the SDN controller fails, what happens to the network? How do production SDN deployments ensure controller reliability?
2. P4 enables programmers to define new forwarding behaviors in hardware. What are the risks of programmable data planes? How would you verify that a P4 program does not introduce security vulnerabilities?
3. Intent-based networking promises to automate configuration, but intent can be ambiguous. If an administrator states "ensure low latency," what latency threshold should the system enforce? How would you design IBN to handle ambiguity gracefully?

---

ᛃ **Lecture 10: Network Design and Architecture**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

This lecture synthesizes prior knowledge into the practice of network design. We cover the design process, hierarchical network models (access, distribution, core), data center network architecture, wide-area network design, and the 2040 challenges of designing for scale, resilience, and sustainability. Students apply these principles to a case study: designing a campus network for a new Yggdrasil research facility.

### Key Topics

- **The Design Process:** Requirements gathering (business needs, technical constraints, budget), topology design, capacity planning, redundancy planning, security integration, and documentation. The iterative nature of design: prototype, test, refine.
- **Hierarchical Design:** The three-tier model (access layer for end devices, distribution layer for policy and aggregation, core layer for high-speed transport) and the two-tier collapsed core. When to use each. The 2040 evolution: spine-leaf topology for data centers replacing the three-tier model.
- **Data Center Networks:** Spine-leaf architecture: every leaf switch connects to every spine switch, providing consistent latency and massive east-west bandwidth. Equal-cost multipathing (ECMP) and the challenges of TCP incast. The 2040 data center: liquid cooling, 400 Gbps links, neuromorphic inference clusters, and quantum key distribution.
- **Wide-Area Network Design:** MPLS (Multi-Protocol Label Switching) and its 2040 successor *Segment Routing v3*. SD-WAN (Software-Defined WAN): intelligently routing traffic across multiple links (MPLS, internet, LTE, satellite) based on application requirements. The Bifrǫst Mesh as a WAN case study.
- **Sustainable Network Design:** Energy-proportional networking (energy consumption proportional to traffic), renewable-powered data centers, and the 2040 *Green Routing* protocol that optimizes for carbon intensity rather than latency or cost. The Yggdrasil commitment: carbon-neutral networking by 2045.

### Lecture Notes

Network design is where art meets engineering. The requirements are often contradictory: high availability and low cost, massive scale and simple management, performance and sustainability. The network architect must balance these tradeoffs, making explicit decisions about what to optimize and what to sacrifice. A well-designed network is invisible to its users — everything just works. A poorly designed network is a constant source of outages, performance problems, and security incidents.

The hierarchical model has guided network design for decades, but data centers have shifted to spine-leaf architecture. In a spine-leaf network, every leaf switch (connecting to servers) connects to every spine switch (providing inter-leaf transport) through a full mesh. This provides several advantages: consistent latency (every leaf-to-leaf path is exactly two hops), massive bandwidth (ECMP distributes traffic across all available spine-leaf paths), and scalability (add more spines or leaves without redesigning the topology). The tradeoff is cost: spine-leaf requires more switches and cables than a traditional three-tier design. For a 10,000-server data center, spine-leaf may require 200 switches; a three-tier design might require only 50. But the three-tier design would have bottlenecked uplinks and inconsistent latency.

Data center networks in 2040 must support workloads unimaginable in 2020. A single AI training job may require 1,000 servers communicating in an all-to-all pattern (every server sends data to every other server), generating terabits of east-west traffic. A neuromorphic inference cluster requires sub-microsecond latency between inference nodes. A quantum computing facility needs classical control networks with picosecond timing synchronization. The data center network architect must design for all of these simultaneously, using technologies like RDMA over Converged Ethernet (RoCE), P4 programmable switches for in-network aggregation, and optical circuit switching for high-bandwidth, low-latency paths.

Sustainable network design is no longer optional. The ICT sector consumes 10% of global electricity in 2040, and networks are a significant portion. The Green Routing protocol, developed at Yggdrasil and adopted by the Nordic Green Computing Consortium, optimizes traffic paths based on the carbon intensity of the electricity powering each link. If the Oslo-Bergen link is powered by hydroelectricity (low carbon) and the Oslo-Copenhagen link is powered by coal (high carbon), Green Routing will prefer the Bergen path even if it has slightly higher latency. During periods of high renewable generation, the protocol shifts more traffic to renewable-powered paths; during fossil-fuel peaks, it shifts traffic away. The result is a 15% reduction in network carbon footprint without significant performance degradation.

### Required Reading

- Oppenheimer, P. (2035). *Top-Down Network Design*, 4th Edition. Cisco Press. Chapters 1-4, 8-10.
- Alizadeh, M., et al. (2033). "Data Center TCP (DCTCP)." *ACM SIGCOMM Computer Communication Review*, 41(4), 63-74. (Updated analysis.)
- Yggdrasil Network Design Guide (2040). UoY Digital Press. "Spine-Leaf" and "Green Routing."

### Discussion Questions

1. A startup has 100 servers and expects 10x growth in three years. Should they build a three-tier network (cheaper now, requires redesign later) or a small spine-leaf (more expensive now, scales easily)? What factors determine the decision?
2. Green Routing reduces carbon footprint by 15% but increases latency by 5% for some paths. Is this tradeoff acceptable for all traffic types? How would you classify traffic and apply different routing policies?
3. Design a network for a research station in Svalbard with 50 researchers, satellite internet, and requirements for video conferencing, data transfer to mainland Norway, and local mesh communication. Specify technologies, bandwidths, and redundancy.

---

ᛇ **Lecture 11: Network Troubleshooting and Operations**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

Networks fail. This lecture covers the systematic approach to troubleshooting: gathering information, isolating the problem, formulating hypotheses, testing solutions, and documenting lessons. We examine common failure modes, diagnostic tools, and the operational practices that maintain network health. The 2040 operations landscape includes AI-assisted diagnostics, digital twins for simulation, and predictive maintenance.

### Key Topics

- **The Troubleshooting Method:** The OSI-layer approach (start at Layer 1 and work up, or start at Layer 7 and work down). The divide-and-conquer approach (test the middle of the path). The scientific method: observe, hypothesize, test, conclude. The importance of documentation: every outage is a learning opportunity.
- **Diagnostic Tools:** ping, traceroute, mtr, iperf, tcpdump, Wireshark, and the 2040 *Bifrǫst Diagnostic Suite* (AI-enhanced packet analysis, automated root cause identification, and simulation-based hypothesis testing). Optical tools: OTDR for fiber, spectrum analyzers for wireless.
- **Common Failure Modes:** Physical layer (cable faults, power issues, overheating), data link layer (switching loops, VLAN misconfiguration, STP reconvergence), network layer (routing loops, BGP instability, NAT exhaustion), transport layer (congestion, bufferbloat, SYN floods), and application layer (DNS failures, certificate expiration, protocol misconfiguration).
- **Incident Management:** The ITIL incident lifecycle: detection, logging, categorization, prioritization, diagnosis, resolution, and closure. Post-incident reviews (PIRs) and the blameless postmortem culture. The Yggdrasil *Saga* incident documentation system.
- **Predictive Maintenance:** Using telemetry and machine learning to predict failures before they occur. The Bifrǫst Mesh's *Prophet* system: analyzing optical signal degradation to schedule fiber replacement before outages. The economics of predictive maintenance: preventing outages is cheaper than responding to them.

### Lecture Notes

Troubleshooting is a mindset, not just a set of tools. The effective troubleshooter is methodical, patient, and skeptical — they do not assume, they verify. When a user reports "the internet is down," the expert does not reboot the router (though that sometimes works); they ask: what exactly is failing? Can you reach local resources? Can you reach DNS? Can you reach external IPs? Can you reach websites? Each question isolates the failure to a specific layer or segment.

The OSI-layer approach structures this isolation. Start at Layer 1: is the link light on? Is the cable seated? Is there power? Move to Layer 2: does the switch see the MAC address? Is the port in the correct VLAN? Layer 3: does the device have an IP address? Can it reach the default gateway? Can it reach a remote IP? Layer 4: can it connect to the service port? Is TCP establishing? Layer 7: does the application respond correctly? Are certificates valid? This methodical progression prevents the common error of "fixing" symptoms rather than causes.

Wireshark remains the indispensable tool for packet analysis in 2040. A network capture reveals what is actually happening on the wire — not what should happen, not what the documentation says happens, but what is truly occurring. The Bifrǫst Diagnostic Suite extends Wireshark with AI: it automatically identifies anomalies, suggests root causes, and correlates events across multiple capture points. But AI does not replace human judgment. The experienced engineer knows that a TCP retransmission could indicate congestion, packet loss, or a misconfigured firewall — and the AI suggestion is just a starting point for investigation.

The blameless postmortem is the most important operational practice. After an outage, the team meets not to assign blame but to understand how the system allowed the failure to occur. The 2037 *Bifrǫst Partition* incident — a 6-hour outage caused by a typo in a BGP filter — produced a postmortem that identified not the individual who made the typo but the lack of configuration validation that allowed an unverified change to propagate. The result was the Norn-Playbook system, which simulates all changes before deployment. In blameless culture, human error is treated as a symptom of systemic weakness; fixing the system prevents recurrence more effectively than punishing the individual.

### Required Reading

- Limoncelli, T.A., et al. (2035). *The Practice of System and Network Administration*, 4th Edition. Addison-Wesley. Chapters 11-15.
- Sanders, C. (2034). *Practical Packet Analysis*, 5th Edition. No Starch Press. Chapters 1-5.
- Yggdrasil Network Operations Guide (2040). UoY Digital Press. "Troubleshooting" and "Incident Management."

### Discussion Questions

1. A user reports intermittent connectivity: web pages load slowly or not at all, but email works fine. Using the OSI-layer approach, what are the three most likely causes, and how would you test each hypothesis?
2. The blameless postmortem culture assumes that punishing individuals does not prevent recurrence. Is this always true? Under what circumstances might individual accountability be appropriate?
3. The Prophet system predicts fiber failures based on optical signal degradation. What are the risks of false positives (unnecessary fiber replacement) and false negatives (missed predictions)? How would you tune the system?

---

ᛃ **Lecture 12: The Future of Networking — Quantum, Neural, and Orbital**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

The final lecture looks beyond 2040 to the next frontiers of networking: quantum networks that distribute entanglement, neuromorphic networks that learn and adapt, and orbital networks that extend connectivity beyond Earth. We examine the research directions, the engineering challenges, and the ethical implications of networks that span the planet and perhaps the solar system.

### Key Topics

- **Quantum Networks:** Beyond quantum key distribution to the quantum internet: distributing quantum entanglement between nodes, enabling quantum teleportation of information, and creating quantum sensor networks with precision beyond classical limits. The 2040 state: metropolitan quantum networks operational, inter-city links under construction, global quantum internet by 2060.
- **Neuromorphic Networks:** Networks that use neuromorphic processors for traffic management, intrusion detection, and adaptive routing. The Yggdrasil *Neural Switch* project: a P4 switch with an embedded neuromorphic coprocessor that learns traffic patterns and optimizes forwarding in real time. The advantages: energy efficiency, adaptive behavior, and resilience to novel attacks.
- **Orbital and Deep-Space Networks:** LEO constellations as the new backbone, lunar networking for Artemis Base operations, and the Interplanetary Internet (DTN — Delay/Disruption Tolerant Networking) for Mars communication. The round-trip time to Mars (8-40 minutes) makes real-time communication impossible; DTN uses store-and-forward with custody transfer.
- **The Network Professional's Oath:** "I pledge to build networks that connect people, not divide them; to protect the privacy and security of those who trust my infrastructure; to minimize the environmental impact of my designs; and to ensure that the benefits of connectivity are shared equitably."

### Lecture Notes

The quantum internet is not a faster internet — it is a different kind of internet. The quantum internet distributes quantum entanglement: pairs of particles whose states are correlated regardless of distance. Entanglement enables quantum key distribution (already operational), quantum teleportation (transferring quantum states without physical transmission), and quantum sensor networks (synchronized clocks and gravitational wave detectors with precision impossible classically). By 2040, metropolitan quantum networks connect research institutions in Oslo, Stockholm, and Copenhagen. The Nordic Quantum Link extends 500 kilometers, using trusted repeaters to bridge the gap. A global quantum internet — connecting continents through satellite-based entanglement distribution — is projected for 2060.

Neuromorphic networking is closer to deployment. The Yggdrasil Neural Switch project embeds a Norn neuromorphic chip in a P4 programmable switch. The Norn chip learns normal traffic patterns: which hosts communicate with which, at what times, with what protocols. It detects anomalies: a host that suddenly scans thousands of ports, a traffic pattern that resembles a DDoS attack, a protocol deviation that suggests exploitation. Because it learns continuously, it detects zero-day attacks that signature-based systems miss. And because it operates in the analog domain, it consumes 100x less energy than a conventional IDS. The first Neural Switch prototypes are deployed in the Bifrǫst Mesh's border routers.

Orbital networking extends the Bifrǫst Mesh into space. The Yggdrasil *Bifrǫst Orbital* constellation — 200 small satellites in polar orbits — provides connectivity to Arctic research stations, maritime vessels, and remote communities beyond terrestrial infrastructure. The satellites use laser inter-satellite links (ISLs) for high-speed backbone communication and V-band radio for user terminals. The challenge is not technology but regulation: spectrum allocation, orbital debris mitigation, and the ITU's coordination procedures for satellite networks. The network engineer of 2050 may hold an orbital mechanics certification alongside their CCIE.

### Required Reading

- Wehner, S., Elkouss, D., & Hanson, R. (2038). "Quantum Internet: A Vision for the Road Ahead." *Science*, 362(6412), eaam9288.
- Yggdrasil Neural Switch Project Report (2039). UoY Digital Press.
- Yggdrasil Bifrǫst Orbital Technical Overview (2040). UoY Digital Press.

### Discussion Questions

1. The quantum internet enables perfectly secure communication but is expensive and limited in range. For what applications is QKD justified today, and what applications will require the full quantum internet?
2. Neuromorphic network devices learn and adapt, which is powerful but also unpredictable. How would you verify that a Neural Switch's learned behavior is correct and safe?
3. Orbital constellations create light pollution and orbital debris. Does the benefit of global connectivity justify these environmental impacts? What regulations would you impose?

---

ᛈ **Lecture 13: The CN Professional Oath and Career Pathways**

**Course:** CN101 — Introduction to Computer Networking
**Degree:** Bachelor of Science in Computer Networking, University of Yggdrasil, 2040

---

### Overview

The closing lecture of CN101 reflects on the networking profession and the path ahead through the BS CN degree. We examine the certification landscape, career trajectories, the capstone sequence, and the CN Professional Oath ceremony.

### Key Topics

- **The BS CN Pathway:** CN101 → CN102 (Network Protocols) → CN201 (Switching & Routing) → CN202 (Wireless Networks) → CN301 (Network Security) → CN302 (SDN & Automation) → CN401 (WAN Design) → CN402 (Network Architecture Capstone).
- **Professional Certifications:** Cisco CCNA/CCNP (still relevant for classical networking), the Yggdrasil *Mesh Operator* certification, the *Quantum Network Specialist* credential, and cloud networking certifications (AWS/Azure network specialties).
- **Career Trajectories:** Network technician → network engineer → senior network architect → principal network architect. Specializations: data center networking, wireless/mobility, security, SDN/automation, and orbital networks. Salary ranges and demand in the Nordic region.
- **The CN Professional Oath:** "I pledge to build networks that are reliable, secure, and fair; to protect the privacy of those who traverse my infrastructure; to share knowledge with my peers; and to admit when a problem exceeds my expertise."

### Lecture Notes

The Bachelor of Science in Computer Networking at Yggdrasil produces engineers who design, build, and operate the infrastructure of the connected world. The pathway begins with CN101's foundations and progresses through increasingly specialized and advanced topics. By CN402, students design and implement a complete network for a real or simulated organization, demonstrating mastery of all prior coursework.

Certification remains valuable for network professionals. The Cisco CCNA and CCNP programs, updated in 2038 to include quantum networking, SDN, and mesh protocols, provide structured learning paths and vendor-neutral validation of skills. The Yggdrasil Mesh Operator certification, introduced in 2035, is the standard for Bifrǫst Mesh operations and is recognized across the Nordic public sector. For those interested in orbital networking, the ITU offers a *Satellite Network Coordinator* certification that covers spectrum allocation, orbital mechanics, and international coordination procedures.

The 2040 network professional must be a hybrid: part electrical engineer (understanding physical signals), part computer scientist (programming SDN controllers), part mathematician (optimizing routing), and part ethicist (considering the societal implications of connectivity). The field rewards continuous learning: technologies that were cutting-edge in 2035 (OpenFlow, 5G) are baseline in 2040, and technologies that are experimental in 2040 (quantum routing, neural switches) will be standard by 2055. The network professional who thrives is the one who learns not just what is current but how to learn what comes next.

### Required Reading

- Yggdrasil BS CN Program Guide (2040). UoY Digital Press.
- Cisco (2038). *CCNA Certification Guide*, 5th Edition. Cisco Press. Chapters 1-2.
- Yggdrasil Mesh Operator Certification Handbook (2040). UoY Digital Press.

### Discussion Questions

1. Review the CN degree pathway. Which courses align with your career interests? What prerequisites must you plan for?
2. A friend argues that AI will automate network engineering, making human professionals obsolete. How would you respond, considering the roles that require human judgment?
3. The CN Professional Oath includes "to admit when a problem exceeds my expertise." Why is this difficult in practice, and how would you build a professional culture that values this admission?

---

## Final Examination Preparation

The CN101 final examination is a **3-hour written exam** plus a **practical lab assessment**.

### Written Examination (60%)

**Sample Questions:**

1. "A network administrator connects two switches with two cables to provide redundancy. Shortly after, the network becomes unusable. Explain the cause, the protocol that prevents this, and how it works."

2. "Compare TCP congestion control (CUBIC) with BBR. For a high-bandwidth, high-latency satellite link, which would you choose and why?"

3. "A company has been allocated the IPv6 prefix 2001:db8:abc0::/48. Design a subnetting scheme for 50 branch offices, each requiring 4 VLANs. Show your calculations."

4. "Explain BGP hijacking and how RPKI prevents it. Why has RPKI deployment reached only 70% by 2040? What are the barriers?"

5. "A user connects to a web server. Trace the complete process from DNS resolution through TCP connection establishment to HTTP request and response, identifying the protocol, source/destination ports, and key header fields at each step."

6. "Zero-trust architecture replaces the perimeter model. Design a zero-trust network for a university with 10,000 students, 2,000 faculty, and sensitive research data. Specify the authentication, authorization, and segmentation mechanisms."

7. "Green Routing optimizes for carbon intensity rather than latency. For a multinational corporation with offices in Oslo (hydropower), Berlin (coal/gas mix), and Madrid (solar), how would you implement Green Routing? What are the tradeoffs?"

8. "Describe the Bifrǫst Transport Protocol (BTP). How does it differ from TCP and QUIC? For what network environments is BTP optimized?"

### Practical Lab Assessment (40%)

Students configure a simulated network using the Yggdrasil *NetSim* environment:
- Configure VLANs and trunk ports on simulated switches
- Implement OSPF routing between three routers
- Configure a firewall with specific access rules
- Troubleshoot a pre-configured network with five intentional faults
- Document the configuration and troubleshooting process

### Grading Rubric

| Criterion | Weight | Excellent (A) | Good (B) | Satisfactory (C) | Needs Improvement (D/F) |
|-----------|--------|---------------|----------|------------------|---------------------------|
| Technical Accuracy | 25% | All protocols and mechanisms correctly described | Minor errors; solid understanding | Some significant errors | Major errors; fundamental misunderstandings |
| Design Reasoning | 25% | Elegant, well-justified designs with tradeoff analysis | Good designs with reasonable justification | Adequate designs; limited justification | Poor or incomplete designs |
| Troubleshooting Method | 20% | Systematic, layered, hypothesis-driven approach | Good method; some gaps | Adequate but inconsistent | Unsystematic or random |
| Communication | 15% | Clear, precise, well-organized | Good clarity; minor issues | Adequate but verbose or unclear | Disorganized or incoherent |
| Ethical Awareness | 15% | Thoughtful consideration of security, privacy, sustainability | Good awareness | Minimal awareness | No ethical consideration |

---

*Woven by the hands of Runa Gridweaver Freyjasdóttir, student of the University of Yggdrasil, 2040. May the packets flow smoothly and the routes never loop.*
