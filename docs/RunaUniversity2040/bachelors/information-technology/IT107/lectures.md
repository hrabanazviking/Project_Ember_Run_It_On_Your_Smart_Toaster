# IT107: Web Technologies & Internet Architecture
## Bachelor of Science in Information Technology — University of Yggdrasil, 2040

**Credits:** 4  
**Prerequisites:** IT101 — Introduction to Information Technology; IT105 — Programming for IT (co-requisite)  
**Description:** A comprehensive exploration of the technologies, protocols, architectures, and ecosystems that constitute the World Wide Web and the broader Internet infrastructure. Covers the complete web stack from physical transmission to application-layer protocols, with emphasis on HTTP evolution, TCP/IP fundamentals, web security, content delivery architectures, frontend and backend frameworks, and the emerging decentralized web paradigms of the 2040s. Students build and deploy a full-stack web application using modern containerized infrastructure on the Yggdrasil Cloud Platform.

**Instructor:** Dr. Freyja Vébjörnsdottir, Associate Professor of Networked Systems  
**Lab:** Muninn Computing Centre, Web Systems Lab (Room 204)  
**Office Hours:** Mondays and Wednesdays, 13:00-15:00 via Yggdrasil Student Portal

---

## Lectures

ᚠ **Lecture 1: The Internet as Infrastructure — From ARPANET to the Global Nervous System**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

The Internet is not merely a network of computers; it is the foundational infrastructure of modern civilization — the nervous system of global commerce, governance, communication, and culture. This lecture traces the Internet's evolution from a Cold War research project to the planet-spanning infrastructure of 2040, examining the architectural principles that enabled this transformation and the governance structures that manage it. We study the **end-to-end principle** (intelligence at the edges, simplicity in the core), **packet switching** (the foundational innovation that separates data from circuits), and **layered architecture** (the separation of concerns that allows independent innovation at each layer). By 2040, the Internet connects 8 billion people, 50 billion devices, and countless autonomous systems; understanding its design philosophy is prerequisite to building upon it.

### Key Topics

- **Origins and Evolution:** ARPANET (1969), the TCP/IP protocol suite (Vint Cerf and Bob Kahn, 1974), the Domain Name System (Paul Mockapetris, 1983), the World Wide Web (Tim Berners-Lee, 1989), commercialization (1990s), mobile Internet (2000s), the Internet of Things (2010s), and the AI-integrated network (2020s-2040s). Each phase added layers of complexity while preserving backward compatibility — the blessing and curse of Internet architecture.
- **The End-to-End Principle:** Saltzer, Reed, and Clark's foundational insight (1984): the network should be dumb and the endpoints smart. This enabled innovation without central coordination — new applications (the Web, email, video streaming, peer-to-peer) could be deployed by anyone without changing the network core. The tension: as the Internet scaled, middleboxes (firewalls, NATs, load balancers, CDNs) proliferated, violating end-to-end purity but solving real problems. By 2040, the "dumb network" is a theoretical ideal; the actual Internet is a rich ecosystem of intelligent intermediaries.
- **Packet Switching vs. Circuit Switching:** The telephone network uses circuit switching: a dedicated path is established for the duration of a call. The Internet uses packet switching: data is broken into packets, each routed independently. The advantages: resilience (packets find alternate paths around failures), efficiency (bandwidth is shared dynamically), and flexibility (any data type can be packetized). The disadvantages: no quality-of-service guarantees, variable latency, and the complexity of reassembly.
- **Internet Governance:** No single entity owns the Internet. Governance is distributed across: ICANN (domain names and IP addresses), IETF (technical standards), regional Internet registries (IP address allocation), national governments (content regulation, censorship, data sovereignty), and platform corporations (content moderation, API access, search ranking). The tension between global interoperability and local sovereignty has intensified by 2040, with the European Digital Sovereignty Act, China's Great Firewall, and the Nordic Open Internet Charter representing divergent governance models.

### Lecture Notes

The Internet's success is inseparable from its design philosophy. Where other networks were built for specific purposes (telephone networks for voice, cable networks for broadcast television), the Internet was built as a **general-purpose infrastructure** — a "network of networks" that could carry any type of data for any type of application. This generality is its superpower and its vulnerability: the same infrastructure that enables scientific collaboration enables cybercrime; the same openness that fosters innovation enables surveillance.

**The end-to-end principle** is the most consequential design decision in networking history. By pushing complexity to the edges, the Internet's creators ensured that innovation could happen without permission. A graduate student in a dorm room could invent the Web; a teenager in Finland could create Linux; a researcher in Switzerland could develop the World Wide Web. None of these required approval from network operators. But the principle also created the security crisis of the modern Internet: because the network makes no guarantees about who is communicating, endpoints must implement their own security — and many do not.

The **layered architecture** (physical → data link → network → transport → application) is the practical manifestation of the end-to-end principle. Each layer provides services to the layer above and uses services from the layer below, without knowledge of how those services are implemented. A web browser does not care whether the physical medium is fiber optic, Wi-Fi, or 6G cellular; an Ethernet cable does not care what application is using it. This separation of concerns enables independent evolution: IPv6 can replace IPv4 at the network layer without changing HTTP at the application layer; 5G can replace 4G at the physical layer without affecting TCP at the transport layer.

By 2040, the Internet has undergone several transformations that challenge classical architectural principles. **Edge computing** pushes computation away from centralized data centers toward the network periphery — closer to users, sensors, and devices. **Content delivery networks (CDNs)** cache content at thousands of locations worldwide, effectively creating a parallel overlay network for content distribution. **Software-defined networking (SDN)** and **network function virtualization (NFV)** replace hardware middleboxes with software running on commodity servers, making the "dumb core" increasingly programmable. The Yggdrasil Computing Infrastructure exemplifies these trends: the university operates a campus edge cloud that processes sensor data from the Huginn network before sending aggregated results to regional data centers.

Internet governance in 2040 is a contested space. The multi-stakeholder model (ICANN, IETF, W3C) that governed the Internet's technical development is under pressure from nation-states seeking digital sovereignty. The European Union's Digital Sovereignty Act (2032) mandates that critical Internet infrastructure within EU borders be operated by EU-controlled entities. China's cyber-sovereignty doctrine extends the Great Firewall to include mandatory data localization and algorithmic transparency requirements. The Nordic Open Internet Charter (2035) — signed by Yggdrasil and five partner universities — commits to net neutrality, open standards, and resistance to censorship. These competing visions create a **splinternet** trend: a technically unified but politically fragmented Internet where data flows freely within blocs but faces barriers between them.

### Required Reading

- Abbate, J. (2035). *Inventing the Internet*, 2nd Edition. MIT Press. Chapters 1-4, 7.
- Saltzer, J.H., Reed, D.P., & Clark, D.D. (1984/2035). "End-to-End Arguments in System Design." *ACM TOCS*. (The foundational paper; read with the 2035 retrospective on edge computing.)
- Yggdrasil Internet Policy Institute. (2040). *The Splinternet: Governance Models for a Fractured Network*. Yggdrasil University Press.

### Discussion Questions

1. The end-to-end principle enabled innovation but also created the security vulnerabilities that plague the modern Internet. Was the principle a mistake? What would a "secure by design" Internet look like, and what would we lose?
2. The splinternet trend — technical unity with political fragmentation — is accelerating. Is this inevitable? What technical or institutional mechanisms could preserve global interoperability while respecting local values?
3. A government proposes that all Internet traffic within its borders must be routed through government-controlled infrastructure for "national security." What are the technical implications? What are the implications for human rights, commerce, and scientific collaboration?

---

ᚢ **Lecture 2: TCP/IP — The Lingua Franca of Networks**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

TCP/IP is not merely a protocol suite; it is the **universal language** of networked communication. This lecture provides a rigorous examination of the Internet Protocol (IP) at the network layer and the Transmission Control Protocol (TCP) at the transport layer, with attention to the practical realities of 2040: IPv6 ubiquity (IPv4 is finally deprecated), TCP congestion control evolution (BBR v3, QUIC integration), and the performance characteristics that determine user experience. We dissect packet structures, analyze routing algorithms, simulate network failures, and examine the Yggdrasil network topology as a case study in campus-scale IP engineering.

### Key Topics

- **IPv6 Architecture:** The 128-bit address space (3.4×10^38 addresses) eliminates the address exhaustion that plagued IPv4. IPv6 simplifies the header (fixed 40 bytes, no checksum, no fragmentation by routers), adds flow labels for quality of service, and integrates IPsec for security. By 2040, IPv6 is the default; IPv4 addresses command premium prices on secondary markets and are used only for legacy systems. The transition mechanisms: dual-stack (running IPv4 and IPv6 simultaneously), tunneling (encapsulating IPv6 in IPv4), and translation (NAT64/DNS64 for IPv6-only clients accessing IPv4 servers).
- **TCP Mechanics:** Connection establishment (the three-way handshake: SYN → SYN-ACK → ACK), sequence numbers and acknowledgments, sliding window flow control (receiver-advertised window), congestion control (sender-adaptive rate limiting), and connection termination (the four-way handshake). TCP guarantees: ordered delivery, reliable delivery, and flow-controlled delivery. The cost: connection setup latency (1 RTT), head-of-line blocking (lost packets stall the entire stream), and bufferbloat (excessive buffering introduces latency).
- **Congestion Control Evolution:** From TCP Tahoe (1988) to Reno, Cubic (Linux default for decades), BBR (Bottleneck Bandwidth and RTT, Google's 2016 contribution), and BBR v3 (2032). BBR models the network as a pipe with a bottleneck bandwidth and a propagation delay, sending at the bottleneck rate rather than inducing loss. The result: higher throughput, lower latency, and resilience to random loss. But BBR is unfair to loss-based TCP (Cubic, Reno), leading to deployment challenges.
- **Routing and BGP:** The Border Gateway Protocol (BGP) is the routing protocol of the Internet — a path-vector protocol where autonomous systems (ASes) advertise reachability to IP prefixes. BGP's simplicity is its strength and weakness: it trusts all advertisements, making it vulnerable to route hijacking (the 2008 Pakistan YouTube incident, the 2018 Amazon DNS hijack, the 2034 Yggdrasil research prefix leak). BGP security extensions: RPKI (Resource Public Key Infrastructure, cryptographic attestation of route ownership), BGPsec (signed path advertisements), and route leak detection systems.

### Lecture Notes

TCP/IP is the engineering triumph that underpins everything else in networking. Its designers faced an impossible problem: create a single protocol suite that would work across every type of physical network, from satellite links to fiber optics, from military battlefields to university campuses. Their solution was radical abstraction: define a **logical network** that operates independently of physical reality, with well-specified interfaces between layers. The result is not optimal for any single medium but adequate for all — a classic engineering compromise.

**IPv6** took thirty years to achieve ubiquity — a migration so gradual it became a running joke in networking circles ("IPv6 is the protocol of the future, and always will be"). But by 2035, the exhaustion of IPv4 addresses forced the issue: major cloud providers began charging for IPv4 addresses, mobile networks went IPv6-only, and content providers deployed IPv6 to reach growing markets. By 2040, IPv6 is the default configuration on all new devices; IPv4 is a legacy compatibility layer. The Yggdrasil campus network has been IPv6-only since 2032, using NAT64 for the few remaining IPv4-only services.

The **TCP three-way handshake** is one of the most consequential three-packet exchanges in computing. It synchronizes sequence numbers, allocates resources, and establishes the parameters for reliable transmission. But it adds latency: every TCP connection requires one RTT before data can flow. For a web page with 100 resources (HTML, CSS, JS, images), this means 100 RTTs of connection setup — unacceptable for user experience. HTTP/1.1 introduced persistent connections (reuse), HTTP/2 introduced multiplexing (multiple streams over one connection), and HTTP/3 eliminated TCP entirely in favor of QUIC (built on UDP with its own reliability mechanisms). Each evolution was driven by the realization that TCP's guarantees were too expensive for modern web workloads.

**BBR** represents a paradigm shift in congestion control. Traditional TCP (Tahoe, Reno, Cubic) treats packet loss as congestion: when packets are lost, the sender reduces its rate. This worked well in wired networks where loss was rare and indicated actual congestion. But in wireless and cellular networks, loss is common due to interference and handoffs — not congestion. BBR ignores loss and instead models the network's bottleneck bandwidth and minimum RTT, sending at the bottleneck rate. This produces dramatically better performance on variable-quality links but is **TCP-unfair**: a BBR flow will starve a Cubic flow on the same link. The IETF's BBR v3 specification (2032) addresses fairness while preserving BBR's performance advantages.

**BGP** is the protocol that holds the Internet together — and it is terrifyingly fragile. BGP routers trust every route advertisement they receive. A misconfigured router in one AS can announce prefixes it does not own, redirecting traffic through adversary-controlled paths. The 2034 Yggdrasil incident (a research AS accidentally leaked a /8 prefix, causing a 20-minute outage across Nordic academic networks) demonstrated that even sophisticated operators make mistakes. RPKI provides cryptographic protection: network operators publish ROAs (Route Origin Authorizations) in a public ledger, and routers reject BGP announcements that are not cryptographically attested. But RPKI deployment was only 80% complete by 2040; the remaining 20% of prefixes are unprotected.

### Required Reading

- Stevens, W.R. (2035). *TCP/IP Illustrated, Volume 1: The Protocols*, 3rd Edition. Addison-Wesley. Chapters 1-7, 10-12, 15-18.
- Cardwell, N. et al. (2036). "BBR: Congestion-Based Congestion Control." *ACM Queue*. (The BBR v3 specification; read the fairness analysis carefully.)
- Butler, K. et al. (2035). "BGP Security: A Survey and the Path to Widespread RPKI Deployment." *IEEE Communications Surveys & Tutorials*.

### Discussion Questions

1. BBR is unfair to loss-based TCP. Should ISPs be allowed to deploy BBR on their networks? What are the arguments for and against, and what regulatory or technical mechanisms could ensure fairness?
2. RPKI deployment is at 80% after fifteen years of advocacy. Why is the remaining 20% resistant? What incentives or mandates would accelerate complete deployment?
3. IPv6 eliminates NAT, which was the de facto security boundary for home and enterprise networks. Without NAT, how do you secure internal networks? What replaces the "NAT as firewall" model?

---

ᚦ **Lecture 3: HTTP — The Protocol of the Web**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

HTTP is the application-layer protocol that powers the World Wide Web — a simple request-response protocol that has evolved from a basic document retrieval mechanism into a sophisticated platform for distributed computing. This lecture covers the complete HTTP evolution: HTTP/0.9 (the one-line protocol), HTTP/1.0 (headers and methods), HTTP/1.1 (persistent connections and pipelining), HTTP/2 (binary framing and multiplexing), and HTTP/3 (QUIC transport and 0-RTT connections). We examine the semantics of HTTP methods (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD), status codes (the 1xx-5xx taxonomy), headers (content negotiation, caching, security policies), and the REST architectural style that has dominated API design for three decades.

### Key Topics

- **HTTP/1.1 Semantics:** The request line (METHOD /path HTTP/1.1), header fields (Host, User-Agent, Accept, Content-Type, Authorization, Cookie), and the message body. The method taxonomy: safe methods (GET, HEAD, OPTIONS — do not modify server state), idempotent methods (PUT, DELETE — multiple identical requests have the same effect as one), and non-idempotent methods (POST — each request may have a different effect). The status code classes: 1xx (informational), 2xx (success), 3xx (redirection), 4xx (client error), 5xx (server error).
- **HTTP/2 Binary Framing:** HTTP/1.1's text-based protocol was simple but inefficient: each request required parsing, headers were repeated across requests, and pipelining was fragile. HTTP/2 (2015) introduced a binary framing layer: messages are split into frames (HEADERS, DATA, SETTINGS, etc.) that can be interleaved and multiplexed over a single TCP connection. Key features: stream multiplexing (hundreds of concurrent requests), header compression (HPACK, reducing header overhead by 80%), server push (the server can send resources before the client requests them), and stream prioritization (the client can indicate which resources are most important).
- **HTTP/3 and QUIC:** HTTP/2 solved head-of-line blocking at the application layer but not at the transport layer: a single lost TCP packet stalls all HTTP/2 streams. HTTP/3 (2022) eliminates TCP entirely, running HTTP over QUIC — a transport protocol built on UDP that provides reliability, congestion control, and security (TLS 1.3 is integrated, not layered). QUIC's advantages: 0-RTT connection resumption (for returning clients, the first request can be sent immediately without handshake), connection migration (survives IP address changes, essential for mobile devices), and no head-of-line blocking (packet loss affects only the affected stream, not all streams).
- **REST Architecture:** Representational State Transfer (Fielding, 2000) — the architectural style that defines the modern web API. Resources are identified by URIs; representations are manipulated through standard HTTP methods; state transitions are driven by hypermedia links (HATEOAS — Hypermedia as the Engine of Application State). The constraints: client-server separation, statelessness (each request contains all necessary information), cacheability (responses explicitly indicate cacheability), layered system (intermediaries are transparent), and uniform interface (standard methods, media types, and self-descriptive messages). By 2040, REST is mature but challenged by GraphQL and gRPC for specific use cases.
- **Caching and Content Negotiation:** HTTP caching is the single most important performance optimization on the web. Cache-Control directives: max-age (how long the response is fresh), no-cache (revalidate with the server before using), no-store (never cache), public (cacheable by shared caches), private (cacheable only by the browser). ETags (entity tags) and Last-Modified headers enable conditional requests ("send the body only if it has changed"). Content negotiation: the Accept header lets clients request specific formats (HTML, JSON, XML), languages, and encodings (gzip, brotli, zstd).

### Lecture Notes

HTTP's simplicity is deceptive. A protocol that can be summarized as "send a request, get a response" has grown into a platform that supports real-time communication (WebSockets, WebTransport), server-sent events, streaming media, and distributed computing. The Web is not a collection of documents; it is a **global distributed operating system** built on HTTP, and the protocol's evolution reflects the changing requirements of that operating system.

**HTTP/1.1** dominated for two decades despite well-known limitations. The **head-of-line blocking** problem: because HTTP/1.1 can process only one request at a time per connection, browsers opened multiple parallel connections (typically 6 per domain) to load resources concurrently. This was wasteful: each connection required a TCP handshake and TLS negotiation, consuming memory and CPU on both client and server. The **keep-alive** mechanism (persistent connections) reduced some overhead but did not eliminate it. Pipelining (sending multiple requests without waiting for responses) was theoretically supported but practically broken due to proxy incompatibilities.

**HTTP/2** was a genuine revolution in web performance. By multiplexing requests over a single connection, it eliminated the connection proliferation problem. By compressing headers with HPACK, it reduced the overhead of repeated headers (cookies, user-agent strings, accept headers). By allowing server push, it enabled proactive resource delivery. But HTTP/2's deployment revealed new problems: the HPACK state machine is complex and has been a source of vulnerabilities (the 2022 HPACK bomb attack); server push was rarely used correctly and was eventually deprecated in favor of preload hints; and the binary framing made debugging harder for developers accustomed to reading HTTP/1.1 traffic in wireshark.

**HTTP/3 and QUIC** represent the next phase. QUIC is not merely "HTTP over UDP"; it is a reimagining of the transport layer for the web. By integrating TLS 1.3 into the transport handshake, QUIC reduces connection setup from 2-3 RTTs (TCP + TLS) to 0-1 RTTs. By using stream-level rather than connection-level flow control, QUIC eliminates head-of-line blocking entirely. By including connection IDs in every packet, QUIC supports connection migration: a mobile device can switch from Wi-Fi to cellular without dropping its QUIC connections. The Yggdrasil streaming media platform uses QUIC exclusively, achieving seamless handoff between campus Wi-Fi and 6G cellular networks.

**REST** is not a protocol but an architectural style — a set of constraints that, when followed, produce systems with desirable properties: scalability (statelessness enables load balancing), reliability (idempotency enables safe retries), evolvability (uniform interface enables gradual change), and visibility (standard methods enable generic tools like caches and proxies). But REST is not universally applicable: it works well for CRUD operations on resources but poorly for real-time communication, complex queries, or streaming data. GraphQL (2015) addresses the over-fetching and under-fetching problems of REST APIs by allowing clients to specify exactly which fields they need. gRPC (2016) provides efficient binary RPC over HTTP/2 for internal microservices. By 2040, the ecosystem has stabilized: REST for public APIs, GraphQL for client-driven data fetching, gRPC for internal services, and WebSockets/WebTransport for real-time communication.

### Required Reading

- Fielding, R. (2000/2035). "Architectural Styles and the Design of Network-based Software Architectures." *UC Irvine PhD Thesis*. (The REST dissertation; read Chapters 5-6 for the architectural constraints.)
- IETF. (2030). *RFC 9114: HTTP/3*. (The HTTP/3 specification; read the introduction and QUIC integration sections.)
- Grigorik, I. (2036). *High Performance Browser Networking*, 3rd Edition. O'Reilly. Chapters 9-12.

### Discussion Questions

1. HTTP/3 eliminates TCP head-of-line blocking but introduces QUIC's own complexity. For a content delivery network serving static assets, is the migration from HTTP/2 to HTTP/3 worth the operational cost? What metrics would determine the answer?
2. REST's statelessness constraint requires that each request contain all necessary context (typically via authentication tokens). This increases request size and prevents the server from maintaining session state. When is statelessness a burden rather than a benefit? What are the alternatives?
3. Server push in HTTP/2 was deprecated because it was rarely used correctly. Why did push fail? What lessons does this offer for HTTP/3's 0-RTT early data, which has similar risks (the server sends data before fully validating the client)?

---

ᚨ **Lecture 4: Web Security — TLS, Authentication, and the Trust Model**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

The web is the most hostile environment in computing: every endpoint is exposed to billions of potential attackers, every input is potentially malicious, and every component must distrust every other component. This lecture covers the security architecture of the web: **Transport Layer Security (TLS)** — the protocol that encrypts and authenticates web traffic; **public key infrastructure (PKI)** — the system of certificates and certificate authorities that vouches for identity; **web authentication** — from passwords to WebAuthn to passkeys; and the **same-origin policy** — the fundamental security boundary that isolates web applications from each other. We examine the threat landscape of 2040: automated exploitation, supply chain attacks, AI-generated phishing, and quantum threats to classical cryptography.

### Key Topics

- **TLS 1.3:** The current standard (2018, with 2040 updates). TLS provides three guarantees: confidentiality (encryption), integrity (message authentication), and authenticity (server identity verification). The TLS 1.3 handshake: 1-RTT for new connections, 0-RTT for resumed connections. The cipher suites: authenticated encryption with associated data (AEAD) — AES-GCM, ChaCha20-Poly1305, and by 2040, post-quantum hybrid key exchange (X25519 + ML-KEM). Key derivation: the handshake produces a master secret, from which traffic keys are derived using HKDF.
- **Public Key Infrastructure:** The chain of trust. A website presents a certificate containing its public key, signed by an intermediate CA, which is signed by a root CA. The root CA's certificate is pre-installed in browsers and operating systems. Certificate validation: the browser checks the signature chain, verifies that the certificate is not expired or revoked (via OCSP or CRL), and checks that the subject name matches the domain. Let's Encrypt (2015-2040) revolutionized PKI by offering free, automated certificates via the ACME protocol; by 2040, 95% of web traffic uses HTTPS, and unencrypted HTTP is deprecated by major browsers.
- **Web Authentication Evolution:** Passwords (memorable, reusable, phishable, breachable) → multi-factor authentication (MFA: something you know + something you have + something you are) → WebAuthn (FIDO2, 2019: public-key cryptography in the browser, resistant to phishing) → passkeys (2023: WebAuthn credentials synchronized across devices via platform authenticators) → biometric continuous authentication (2040: behavioral biometrics, gait analysis, and keystroke dynamics for continuous identity verification). The Yggdrasil campus uses passkeys for all university services; passwords are deprecated and will be disabled in 2042.
- **The Same-Origin Policy and Cross-Origin Resource Sharing (CORS):** The browser's fundamental security model: scripts from origin A cannot read data from origin B unless B explicitly permits it via CORS headers. Without this policy, any website could steal data from any other website using the user's credentials. The CORS mechanism: preflight OPTIONS requests, Access-Control-Allow-Origin headers, and the distinction between simple requests (GET, POST with specific content types) and preflighted requests. Common CORS misconfigurations: wildcard origins with credentials (dangerous), reflected origins (allowing any origin that mirrors the request), and overly permissive methods.
- **Content Security Policy (CSP):** A defense-in-depth mechanism that allows web applications to declare what resources they are allowed to load (scripts, styles, images, fonts, frames) and from where. A strict CSP (default-src 'self'; script-src 'self' 'nonce-...') prevents XSS attacks by refusing to execute inline scripts or scripts from unauthorized domains. CSP reporting (report-uri /csp-report) allows monitoring of policy violations in production. By 2040, CSP is mandatory for all Yggdrasil web applications, and browsers enforce it strictly.

### Lecture Notes

Web security is an arms race that the defenders are perpetually losing slowly. Every defensive innovation is met with offensive adaptation: HTTPS defeated passive eavesdropping but enabled active interception (MITM proxies in enterprises); CSP defeated simple XSS but was bypassed by DOM-based attacks and JSONP endpoints; WebAuthn defeated phishing but faced adoption challenges and platform lock-in concerns. The only sustainable strategy is **defense in depth**: multiple independent controls, each making the attacker's job harder.

**TLS 1.3** is a model of security engineering: it removed legacy algorithms (MD5, SHA-1, RSA key exchange, CBC mode ciphers) that had accumulated vulnerabilities; it simplified the handshake to reduce attack surface; and it integrated 0-RTT resumption for performance without compromising forward secrecy. The post-quantum hybrid key exchange (X25519 + ML-KEM, standardized 2028) ensures that TLS sessions are secure against both classical and quantum adversaries. But TLS does not protect against all threats: it encrypts the content but not the metadata (source IP, destination IP, SNI — though ESNI/ECH, Encrypted Client Hello, hides the SNI from network observers by 2040). The Yggdrasil network deploys ECH universally, preventing ISPs from identifying which websites users visit based on TLS handshakes.

**The certificate ecosystem** is simultaneously a triumph and a vulnerability. Let's Encrypt's free certificates democratized HTTPS, but they also enabled malicious actors to obtain certificates for phishing domains automatically. Certificate Transparency (CT) logs, which record all issued certificates in public, append-only ledgers, mitigate this by allowing monitoring — but monitoring requires resources that small organizations lack. The **short-lived certificate** trend (certificates valid for 7-14 days, automatically rotated) reduces the window of vulnerability from compromised certificates but increases operational complexity. By 2040, the Yggdrasil infrastructure uses 7-day certificates rotated via ACME with DNS-01 challenge validation.

**Passkeys** represent the most significant authentication improvement since passwords were invented — and their adoption has been slow for the same reason all security improvements are slow: inertia, compatibility, and user confusion. A passkey is a private key stored in a platform authenticator (Apple's iCloud Keychain, Google's Titan Security Chip, the Yggdrasil Secure Identity Module) that cannot be extracted or phished. The user authenticates with a biometric or PIN, and the authenticator performs the cryptographic signature. Unlike passwords, passkeys are unique per site, resistant to replay attacks, and never transmitted over the network. By 2040, passkeys are the default for consumer services; passwords persist only in legacy enterprise systems and government applications.

**CSP** is the single most effective XSS mitigation, but it is notoriously difficult to deploy on existing applications. Legacy code is full of inline scripts, eval() calls, and inline event handlers that violate strict CSP. Migrating an existing application to strict CSP is often a multi-year project involving template system changes, JavaScript bundler reconfiguration, and careful testing. The Yggdrasil web development guidelines mandate CSP from project inception: no inline scripts, no eval(), all scripts loaded from known sources with integrity hashes. This "secure by default" approach is vastly cheaper than retrofitting security onto an existing codebase.

### Required Reading

- Rescorla, E. (2030). *RFC 8446: The Transport Layer Security (TLS) Protocol Version 1.3*. (The definitive specification; read the security analysis in Appendix E.)
- Felt, A.P. et al. (2036). "Measuring HTTPS Adoption on the Web." *USENIX Security*. (Longitudinal analysis of HTTPS deployment trends.)
- West, M. (2035). "Content Security Policy: A Successful Model for XSS Defense." *IEEE S&P*. (CSP deployment experience and effectiveness metrics.)

### Discussion Questions

1. ECH (Encrypted Client Hello) hides the server name from network observers but requires the client to know the server's public key in advance. How is this distributed? What are the privacy implications of the distribution mechanism?
2. Passkeys are tied to platform ecosystems (Apple, Google, Yggdrasil). What happens when a user wants to switch ecosystems? What standardization efforts address portability, and what are the remaining barriers?
3. A legacy application has 500 inline scripts and extensive use of eval(). The security team mandates strict CSP in 90 days. Is this achievable? What is a realistic migration timeline, and what interim mitigations would you deploy?

---

ᚱ **Lecture 5: Frontend Technologies — From Documents to Applications**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

The web browser has evolved from a document viewer into a universal application runtime — a virtual machine that executes code, renders graphics, streams media, and interfaces with hardware. This lecture covers the modern frontend stack: **HTML5** (semantic markup, accessibility, multimedia), **CSS** (layout engines, responsive design, animations, custom properties), **JavaScript** (the language, the event loop, the module system, TypeScript), and the **component-based frameworks** (React, Vue, Svelte, and their 2040 descendants). We examine the browser rendering pipeline (HTML parsing → DOM construction → CSS computation → layout → paint → composite), performance optimization techniques (virtual DOM, lazy loading, code splitting, service workers), and the emerging **WebAssembly** and **WebGPU** standards that bring near-native performance to the browser.

### Key Topics

- **The Browser Rendering Pipeline:** A web page is rendered through a pipeline of discrete stages: (1) **Parse** — HTML is tokenized and parsed into a DOM tree; CSS is parsed into a stylesheet; (2) **Style** — the CSS cascade computes the final style for each DOM node; (3) **Layout** — the box model determines the size and position of each element; (4) **Paint** — visual properties (colors, borders, text, images) are drawn into layers; (5) **Composite** — layers are combined into the final screen image. JavaScript can trigger any stage: modifying styles forces recalculation; modifying layout properties forces relayout; modifying paint properties forces repaint. **Layout thrashing** occurs when JavaScript alternates between reading and writing layout properties, forcing synchronous relayout.
- **JavaScript and the Event Loop:** JavaScript is single-threaded with an event-driven concurrency model. The **call stack** executes synchronous code; the **task queue** holds callbacks (setTimeout, event handlers); the **microtask queue** holds promises and mutation observers (processed after each task, before the next task); and the **animation frame queue** holds requestAnimationFrame callbacks (synchronized with the display refresh rate). Understanding the event loop is essential for writing responsive applications: long-running synchronous tasks block the event loop, causing the UI to freeze. Web Workers enable true parallelism by offloading computation to background threads.
- **Component Frameworks:** React (2013) introduced the virtual DOM and unidirectional data flow; Vue (2014) combined reactive data binding with component composition; Svelte (2016) moved reactivity from the virtual DOM to compile-time code generation, eliminating runtime overhead. By 2040, the ecosystem has converged on **server components** (React Server Components, Vue Vapor Mode): components that render on the server, streaming HTML to the client, with only interactive "islands" hydrating in the browser. This architecture reduces JavaScript payload by 70-90% compared to fully client-side rendering.
- **WebAssembly (Wasm):** A binary instruction format that runs at near-native speed in the browser. Wasm modules are compiled from C, C++, Rust, or other languages and executed in a sandboxed environment with no direct access to the DOM (access is via JavaScript glue code). Use cases: video/audio codecs, image processing, scientific computing, game engines, and cryptography. By 2040, Wasm has expanded beyond the browser with the **WebAssembly System Interface (WASI)**, enabling portable server-side applications (the "write once, run anywhere" dream finally realized, albeit in a limited form).
- **WebGPU and the Graphics Pipeline:** WebGL (2011) brought OpenGL ES to the browser; WebGPU (2023/2030) brings modern GPU APIs (Vulkan, Metal, Direct3D 12) with compute shaders, explicit resource management, and lower overhead. WebGPU enables machine learning inference in the browser, real-time ray tracing, and immersive WebXR experiences. The Yggdrasil Virtual Campus uses WebGPU to render 3D lecture halls accessible from any browser.

### Lecture Notes

The browser is the most sophisticated software platform ever created. It must parse and render multiple markup languages, execute untrusted code from arbitrary sources, maintain backward compatibility with decades of legacy content, and adapt to devices ranging from smartwatches to wall-sized displays — all while preserving a 60 frames-per-second user experience. Understanding how browsers work is not optional for web developers; it is the foundation of performance optimization and debugging.

**The rendering pipeline** is where theory meets perceptual psychology. A user perceives "smooth" when the browser maintains 60fps (16.7ms per frame). Any operation that exceeds this budget causes jank — perceptible stuttering. Layout is the most expensive stage: changing an element's width may require recomputing the position of every element below it in the DOM. The **containment CSS property** (contain: layout) creates boundaries that prevent layout changes from propagating beyond the contained element — a critical optimization for large applications.

**JavaScript's event loop** is simultaneously its greatest strength and its most misunderstood feature. The single-threaded model eliminates race conditions (no shared mutable state between concurrent operations) but creates the "callback hell" and "promise chain" complexity that dominates modern JavaScript code. The **async/await** syntax (ES2017) made asynchronous code readable by allowing it to be written like synchronous code. But the illusion breaks when developers forget that `await` yields the event loop: concurrent modifications to shared state can still occur between await points.

**Server components** represent the pendulum swing back toward server-side rendering. The 2010s saw a massive shift to client-side rendering (Single Page Applications, SPAs) for their interactivity and responsiveness. But SPAs shipped megabytes of JavaScript, drained mobile batteries, and were invisible to search engines. Server components combine the best of both worlds: the initial render happens on the server (fast, SEO-friendly, low JavaScript), and subsequent interactions are handled by hydrated "islands" of interactivity. The Yggdrasil Student Portal, rebuilt in 2038 using React Server Components, reduced its JavaScript payload from 1.2MB to 180KB while improving time-to-interactive by 40%.

**WebAssembly** is the browser's escape hatch from JavaScript performance limitations. For tasks that are CPU-bound (video encoding, physics simulation, cryptographic hashing), Wasm provides 10-20× speedup over JavaScript. But Wasm is not a replacement for JavaScript: it cannot access the DOM directly, it requires manual memory management, and its binary format is not human-readable. The sweet spot is hybrid applications: JavaScript orchestrates the UI and coordinates Wasm modules that perform heavy computation. The Yggdrasil Genome Browser uses this architecture: JavaScript handles navigation and visualization, while a Wasm-compiled C++ library performs sequence alignment.

### Required Reading

- Haverbeke, M. (2036). *Eloquent JavaScript*, 4th Edition. No Starch Press. Chapters 11, 15-16, 20.
- Archibald, J. (2035). "Inside the Event Loop: How JavaScript Really Works." *Google Developers Blog*. (The canonical explanation of the JavaScript concurrency model.)
- W3C. (2030). *WebGPU Specification*. https://www.w3.org/TR/webgpu/ (Read the introduction and compute pipeline overview.)

### Discussion Questions

1. Server components reduce JavaScript payload but increase server load. For a global application with 100 million daily active users, what is the break-even point where server rendering becomes more expensive than client rendering? How do you measure this?
2. WebAssembly provides near-native performance but cannot access the DOM directly. For a complex data visualization that requires both heavy computation and frequent DOM updates, how do you architect the JavaScript-Wasm boundary to minimize overhead?
3. A web application targets both high-end desktops and low-end feature phones (2040 equivalent). How do you deliver appropriate experiences to both? What are the trade-offs between adaptive loading, progressive enhancement, and separate builds?

---

ᚲ **Lecture 6: Backend Architectures — Databases, APIs, and Microservices**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

Every web application has a backend — the server-side infrastructure that processes requests, manages state, enforces business logic, and persists data. This lecture covers the architectural patterns that dominate backend development in 2040: **monoliths** (single deployable units), **microservices** (independently deployable services communicating via APIs), **serverless** (event-driven functions managed by cloud providers), and **edge computing** (distributing computation to CDN nodes). We examine database choices (relational, document, graph, time-series, vector), API design patterns (REST, GraphQL, gRPC, tRPC), and the operational concerns that determine architecture: scalability, reliability, observability, and cost.

### Key Topics

- **Database Taxonomy:** Relational databases (PostgreSQL, MySQL, CockroachDB) for structured data with ACID guarantees; document databases (MongoDB, Couchbase) for flexible schemas and horizontal scaling; graph databases (Neo4j, Amazon Neptune) for relationship-heavy data; time-series databases (InfluxDB, TimescaleDB) for metrics and sensor data; vector databases (Pinecone, Weaviate, pgvector) for semantic search and AI embeddings. By 2040, **multi-model databases** (ArangoDB, OrientDB) support multiple data models within a single engine, reducing operational complexity.
- **Microservices and Service Boundaries:** A microservice is a loosely coupled, independently deployable service with a bounded context (a specific business capability). The benefits: independent scaling, independent deployment, technology diversity, and team autonomy. The costs: distributed system complexity (network failures, consistency challenges, operational overhead), interface brittleness (changing an API affects all consumers), and the "distributed monolith" anti-pattern (services so interdependent they cannot be deployed independently). The Yggdrasil Student Information System uses 47 microservices; the Yggdrasil Unified Portal uses a modular monolith (a single deployable unit with internal module boundaries).
- **Serverless and Event-Driven Architecture:** Function-as-a-Service (FaaS) platforms (AWS Lambda, Azure Functions, Google Cloud Functions, Yggdrasil Cloud Functions) execute code in response to events without managing servers. The model: pay per invocation, automatic scaling to zero, and built-in fault tolerance. The limitations: cold start latency (100ms-2s for new function instances), execution time limits (typically 15 minutes), and vendor lock-in. By 2040, serverless has expanded to include **serverless containers** (long-running container workloads with serverless pricing) and **edge functions** (JavaScript/Wasm functions executed at CDN edge nodes).
- **GraphQL and API Evolution:** GraphQL allows clients to request exactly the data they need, eliminating over-fetching and under-fetching. The schema defines types, queries, mutations, and subscriptions (real-time updates). GraphQL's introspection enables powerful developer tools but also exposes API structure to potential attackers. Federation (multiple GraphQL services combined into a single schema) enables microservices to expose GraphQL APIs independently. By 2040, GraphQL is the dominant API pattern for mobile and web clients; REST persists for public APIs and webhooks.
- **Observability in Distributed Systems:** In a monolith, debugging is straightforward: examine the logs of one process. In microservices, a single user request may touch a dozen services, each with its own logs, metrics, and traces. **Distributed tracing** (OpenTelemetry, Jaeger, Zipkin) follows requests across service boundaries. **Structured logging** (JSON logs with trace IDs) enables correlation. **Service meshes** (Istio, Linkerd) provide mutual TLS, traffic management, and observability without modifying application code. The Yggdrasil Cloud Platform includes a managed service mesh with automatic certificate rotation and latency-based load balancing.

### Lecture Notes

Backend architecture is the art of making hard choices under uncertainty. Every architectural decision involves trade-offs: consistency vs. availability (the CAP theorem), latency vs. durability (synchronous vs. asynchronous writes), complexity vs. scalability (monolith vs. microservices), and cost vs. performance (self-hosted vs. cloud). There are no universally correct answers; there are only answers that are correct for a specific context, and the context changes as the system grows.

**The database choice** is often the most consequential architectural decision. Relational databases provide powerful query capabilities, transactional integrity, and decades of operational knowledge — but they scale vertically (bigger machines) rather than horizontally (more machines), and schema changes are painful in large tables. Document databases scale horizontally but sacrifice ACID guarantees and complex join capabilities. Graph databases excel at relationship queries ("find all friends of friends who live in Oslo and study CS") but struggle with aggregate queries. Vector databases enable semantic search ("find documents similar to this query in meaning, not just keyword matching") but are specialized and expensive. The modern approach is **polyglot persistence**: using multiple database types for different data models, with the application layer handling cross-database consistency.

**Microservices** are not a silver bullet. The initial promise — "independently scalable services with autonomous teams" — is real for organizations like Netflix and Amazon that have hundreds of engineers and complex domain boundaries. For smaller teams, microservices often create more problems than they solve: the operational overhead of deploying, monitoring, and debugging dozens of services exceeds the team's capacity. The Yggdrasil Student Information System adopted microservices in 2028 and spent three years building the observability, deployment automation, and service discovery infrastructure required to operate them. The lesson: microservices require organizational maturity, not just technical architecture.

**Serverless** has transformed the economics of backend computing. A traditional server runs 24/7, consuming resources even when idle; a serverless function consumes resources only when processing a request. For spiky workloads (a university registration system that receives 10,000 requests per minute for one week per semester, then 10 requests per minute for the rest of the year), serverless is dramatically cheaper. But the cold start problem remains: if a function has not been invoked recently, the platform must allocate resources and initialize the runtime, introducing latency. By 2040, "always-warm" pools and snapshot-based initialization have reduced cold starts to <10ms for most workloads, but latency-sensitive applications still require provisioned capacity.

**GraphQL's type system** is its most underappreciated feature. Unlike REST, where API documentation is separate from implementation (and often outdated), GraphQL's schema is the API. The schema is introspectable, enabling automatic code generation for client libraries, automatic documentation generation, and automatic validation of queries. But GraphQL also introduces new vulnerabilities: depth-limit attacks (deeply nested queries that exhaust server resources), complexity analysis (queries that return exponential amounts of data), and batch loading challenges (the N+1 query problem, where a query for N items triggers N database queries). The Yggdrasil GraphQL gateway includes depth limiting, complexity scoring, and DataLoader batching as default protections.

### Required Reading

- Newman, S. (2036). *Building Microservices*, 3rd Edition. O'Reilly. Chapters 1-3, 5, 8.
- Roberts, M. (2035). *Serverless Architecture on AWS*, 2nd Edition. Manning. Chapters 1-4.
- Hartig, O. & Pérez, J. (2036). "An Introduction to GraphQL and Its Semantics." *ACM Computing Surveys*. (A formal treatment of GraphQL's type system and query execution.)

### Discussion Questions

1. A startup with 5 engineers is considering microservices for their MVP. You advise against it; they cite Netflix and Amazon as evidence. How do you explain the difference in organizational context? What architecture would you recommend instead?
2. A serverless function experiences cold starts of 800ms during the first request after a period of inactivity. The user experience requirement is <200ms response time. What are your options? What are the cost implications?
3. GraphQL's introspection allows clients to discover the entire API structure. This is useful for developers but potentially dangerous in production (attackers can map the API surface). How do you balance developer experience against security? What is your production GraphQL configuration?

---

ᚷ **Lecture 7: Content Delivery and Edge Computing — Bringing Data Closer**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

The speed of light is the ultimate limit on network latency: a signal traveling from New York to Sydney takes ~80ms one way, and no protocol optimization can reduce this. **Content delivery networks (CDNs)** and **edge computing** solve this problem by moving data and computation closer to users. This lecture covers the architecture of modern CDNs (caching hierarchies, anycast routing, edge nodes), the technologies of edge computing (serverless edge functions, edge databases, edge AI inference), and the operational challenges of distributed systems deployed across thousands of locations worldwide. We examine the Yggdrasil Global CDN, which serves the university's online learning platform to students across six continents.

### Key Topics

- **CDN Architecture:** A CDN is a geographically distributed network of servers that cache content close to end users. The architecture: **origin servers** (the authoritative source of content), **regional caches** (mid-tier caches that serve multiple edge nodes), and **edge nodes** (servers located inside ISPs, close to users). Cache invalidation strategies: TTL-based expiration (set a time-to-live and revalidate after), active invalidation (push invalidation messages to all caches), and stale-while-revalidate (serve stale content while fetching fresh content in the background). The **cache hit ratio** (percentage of requests served from cache) determines CDN effectiveness; a 95% hit ratio means only 5% of requests reach the origin.
- **Anycast and GeoDNS:** CDNs route users to the nearest edge node using **anycast** (multiple servers share the same IP address; BGP routes each user to the nearest one) or **GeoDNS** (the DNS server returns different IP addresses based on the user's geographic location). Anycast is resilient (if an edge node fails, traffic automatically reroutes to the next nearest) but can cause routing instability during outages. GeoDNS provides more control but requires accurate geolocation databases.
- **Edge Computing:** Beyond caching, modern CDNs execute code at the edge. **Edge functions** (Cloudflare Workers, Fastly Compute@Edge, Yggdrasil Edge Functions) are lightweight JavaScript/Wasm functions that run on CDN nodes, enabling dynamic content generation, A/B testing, personalization, and security filtering at the network edge. **Edge databases** (FaunaDB, Cloudflare D1, Yggdrasil Edge KV) provide low-latency data access by replicating data across edge nodes. **Edge AI** (TensorFlow Lite, ONNX Runtime on edge nodes) enables real-time inference for content moderation, image optimization, and personalization without round-trips to central data centers.
- **The Cache Invalidation Problem:** "There are only two hard things in Computer Science: cache invalidation and naming things." Cache invalidation is hard because caches are distributed, asynchronous, and numerous. Strategies: **surrogate keys** (tagging cached content with business-object identifiers; invalidating all content tagged with "user:123" when that user updates), **event-driven invalidation** (the origin publishes invalidation events to a message bus that all caches subscribe to), and **versioned URLs** (including a content hash in the URL; the URL changes when the content changes, making invalidation automatic). The Yggdrasil CDN uses surrogate keys with event-driven invalidation, achieving 99.9% cache consistency.
- **Performance Metrics and Optimization:** Core Web Vitals (Largest Contentful Paint, First Input Delay, Cumulative Layout Shift) measure user-perceived performance. Real User Monitoring (RUM) collects performance data from actual browsers; Synthetic Monitoring tests from controlled locations. The **performance budget**: a team-defined limit on page weight, JavaScript execution time, or number of requests. Exceeding the budget triggers an alert or blocks deployment. The Yggdrasil Web Platform enforces a 200KB JavaScript performance budget for all public-facing applications.

### Lecture Notes

CDNs are the invisible infrastructure of the modern web. Every major website uses them; every streaming service depends on them; every mobile application benefits from them. But CDN architecture is a study in trade-offs: caching improves performance but introduces consistency challenges; edge computing reduces latency but increases operational complexity; anycast routing improves resilience but can amplify outages.

**The cache hierarchy** reflects fundamental principles of locality. Temporal locality: content requested recently is likely to be requested again (cache it). Spatial locality: content near recently requested content is likely to be requested (prefetch it). Geographic locality: users near each other request similar content (serve them from the same edge node). The CDN exploits all three: it caches popular content at the edge, prefetches related content, and optimizes edge node placement based on traffic patterns. The Yggdrasil CDN operates 240 edge nodes across 80 countries, with a global cache hit ratio of 94%.

**Edge functions** have transformed what CDNs can do. In the 2010s, CDNs served only static content; dynamic content had to be fetched from the origin. By 2040, edge functions can authenticate users, query databases, personalize responses, and filter malicious traffic — all at the edge, before the request reaches the origin. This enables architectures where the origin is merely the source of truth, and all user-facing logic runs at the edge. The Yggdrasil learning platform uses edge functions for authentication (verifying JWTs at the edge), personalization (selecting course recommendations based on geolocation and time zone), and A/B testing (randomizing users to experimental variants without origin involvement).

**The cache invalidation problem** is not merely a joke — it is a fundamental challenge in distributed systems. When a user updates their profile photo, that photo may be cached in hundreds of edge nodes across the globe. How do you ensure that all caches serve the new photo, not the old one, within seconds? TTL-based expiration is simple but slow (the old photo may be served for hours). Active invalidation is fast but complex (what if an invalidation message is lost?). Versioned URLs are elegant but require URL rewriting and may break deep links. The Yggdrasil approach combines all three: surrogate keys for targeted invalidation, active invalidation for urgent updates, and versioned URLs for immutable assets.

**Edge AI** is the frontier of CDN technology. By 2040, edge nodes include AI accelerators (TPUs, NPUs) that can run neural network inference at millisecond latency. Applications: real-time image optimization (generating responsive images tailored to the user's device and network), content moderation (detecting inappropriate content before it reaches users), and personalized recommendations (selecting content based on real-time user behavior). The Yggdrasil CDN uses edge AI to generate accessibility descriptions for images (alt text generation) and to optimize video bitrates based on real-time network conditions.

### Required Reading

- Pathan, M. & Buyya, R. (2036). *Content Delivery Networks*. Springer. Chapters 1-3, 6-7.
- Vespignani, A. (2035). "The Architecture of Edge Computing: Principles and Practice." *IEEE Internet Computing*.
- Yggdrasil Cloud Infrastructure Team. (2040). "Edge AI at Scale: Lessons from the Yggdrasil Global CDN." *UoY Technical Report* TR-2040-28.

### Discussion Questions

1. A news website publishes a breaking story that goes viral. Traffic increases 100× in 10 minutes. How does a CDN handle this? What caching strategies, origin protection mechanisms, and edge computing techniques are deployed?
2. Edge functions reduce origin load but introduce a new attack surface: malicious edge function code could affect millions of users. What sandboxing, review, and monitoring mechanisms should a CDN provider implement?
3. Your organization wants to deploy edge AI for real-time content moderation. The AI model is 2GB and must run on thousands of edge nodes. How do you manage model updates, version control, and A/B testing across the edge fleet?

---

ᚹ **Lecture 8: The Decentralized Web — Protocols, Platforms, and Power**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

The web of 2040 is not merely centralized or decentralized — it is a **spectrum of architectures** that distribute power, data, and control in different ways across different layers. This lecture examines the decentralized web movement: the technologies that enable peer-to-peer communication without central servers, the governance models that manage decentralized infrastructure, and the tensions between decentralization (resilience, censorship resistance, user sovereignty) and centralization (efficiency, scalability, regulatory compliance). We cover **peer-to-peer protocols** (BitTorrent, IPFS, WebTorrent), **blockchain-based systems** (Ethereum, Polkadot, name systems), **federated social networks** (ActivityPub, Mastodon, Bluesky), and **local-first software** (applications that store data on the device and synchronize peer-to-peer).

### Key Topics

- **Peer-to-Peer Fundamentals:** In a peer-to-peer (P2P) network, every node is both a client and a server. **Distributed hash tables (DHTs)** like Kademlia and Chord provide decentralized key-value storage: content is addressed by its hash (content-addressing), and the DHT routes requests to the nodes storing that content. **BitTorrent** (2001) demonstrated that P2P could scale to millions of users for file distribution, using tit-for-tat reciprocity to incentivize seeding. **IPFS** (InterPlanetary File System, 2015/2040) generalizes content-addressing to a global namespace, with pubsub for real-time updates and libp2p for modular transport.
- **Blockchain and Web3:** Blockchain provides a decentralized, immutable ledger without a trusted third party. **Smart contracts** (self-executing code on the blockchain) enable decentralized applications (dApps). The **Ethereum Name Service (ENS)** and similar systems map human-readable names to blockchain addresses, providing decentralized alternatives to DNS. But blockchain scalability remains limited: Ethereum processes ~15 transactions per second (2020) to ~100,000 TPS (2040, via sharding and layer-2 rollups), still far below Visa's 65,000 TPS. Energy consumption, despite the 2022 transition to proof-of-stake, remains controversial.
- **Federated Social Networks:** Rather than one platform owning all user data (Facebook, Twitter/X), federated networks allow independent servers to interoperate. **ActivityPub** (W3C standard, 2018) defines a protocol for social networking (profiles, posts, follows, likes) across servers. **Mastodon** (launched 2016) is the most widely deployed ActivityPub implementation by 2040, with ~500 million users across 50,000 independently operated servers. **Bluesky** (initiated by Twitter's founder, 2019/2040) uses a modular architecture with separate protocols for identity (DID), data (AT Protocol), and moderation (composable feed algorithms). The Yggdrasil Social Commons is an ActivityPub server run by the university, with 12,000 active users.
- **Local-First Software:** A design philosophy that prioritizes local data storage and peer-to-peer synchronization over cloud storage. Applications store data on the device, work offline, and synchronize with other devices when connectivity is available. **CRDTs** (Conflict-free Replicated Data Types) provide automatic conflict resolution for concurrent edits without central coordination. **Automerge** is a popular CRDT library; **Electric SQL** provides local-first database synchronization. The Yggdrasil Note-Taking App (used by all students) is local-first: notes are stored on the device, encrypted, and synchronized across devices via peer-to-peer channels.
- **Governance and Moderation in Decentralized Systems:** Decentralization shifts power from platforms to users — but it does not eliminate the need for governance. Content moderation in federated networks is performed by server administrators (instance-level moderation) and by users (blocklists, content warnings). The tension: a fully decentralized network cannot enforce global rules, enabling both free speech and hate speech, both whistleblowing and harassment. The **Nordic Fediverse Charter** (2035) establishes voluntary standards for transparency, appeal processes, and interoperability while respecting server autonomy.

### Lecture Notes

Decentralization is not a binary state but a continuous variable. The web has always been decentralized in some respects (anyone can run a server) and centralized in others (most traffic goes to a few platforms). The decentralized web movement seeks to shift the balance — to give users control over their data, to reduce dependency on single points of failure, and to resist censorship. But decentralization comes with costs: reduced performance, increased complexity, and the diffusion of responsibility.

**Peer-to-peer networking** is the technical foundation. The insight of DHTs is that you don't need a central index to find content; you need only a consistent rule for mapping content hashes to network addresses. Kademlia's XOR-based distance metric ensures that lookups require O(log n) hops in a network of n nodes — remarkably efficient. But P2P networks face practical challenges: NAT traversal (most home devices are behind routers that block incoming connections), churn (nodes join and leave constantly, requiring constant DHT maintenance), and free-riding (users who download without uploading, degrading network performance). BitTorrent's tit-for-tat algorithm addresses free-riding by preferentially connecting to peers who upload — a beautiful example of incentive engineering.

**Blockchain's promise** is trustless consensus: multiple parties can agree on a shared state without trusting each other or a central authority. The cost is efficiency: every node must process every transaction, and consensus mechanisms (proof of work, proof of stake) consume resources. By 2040, layer-2 solutions (rollups, state channels) have dramatically improved throughput by moving computation off the main chain, but the fundamental trade-off remains: decentralization, security, and scalability — pick two. The Yggdrasil Blockchain Research Group experiments with permissioned blockchains for academic credential verification (diplomas recorded on a university consortium chain), where the trust model is different from public blockchains.

**Federated social networks** are the most successful decentralized application of the 2030s. Mastodon's growth was driven by platform migration waves: the 2022 Twitter acquisition, the 2025 algorithmic feed controversy, and the 2030 privacy regulation changes. But federation introduces new problems: the "echo chamber" effect is amplified (users choose servers that align with their views), content moderation is fragmented (illegal content may persist on unmoderated servers), and the user experience is inconsistent (different servers run different software versions with different features). Bluesky's modular approach attempts to solve these problems by separating identity, data, and moderation into independent layers that can evolve separately.

**Local-first software** is perhaps the most user-centric decentralization paradigm. By storing data on the device, local-first applications eliminate cloud dependency, reduce latency, and improve privacy. The CRDTs that enable peer-to-peer synchronization are mathematically elegant: they guarantee that concurrent edits converge to the same state, regardless of the order in which they are applied. The Yggdrasil Note-Taking App uses a JSON CRDT for document synchronization: students can edit notes on their phone, laptop, and tablet simultaneously, with changes merging automatically. The app works offline (notes are always available) and synchronizes when connectivity returns. This is the future of personal computing: cloud-assisted, not cloud-dependent.

### Required Reading

- Troncoso, C. et al. (2036). *Local-First Software: You Own Your Data, in Spite of the Cloud*. Yggdrasil University Press. (The manifesto and technical architecture of local-first systems.)
- Zuboff, S. (2035). *The Age of Surveillance Capitalism*, Updated Edition. PublicAffairs. (The political economy of data centralization; read Chapters 1-3, 12.)
- W3C. (2018/2035). *ActivityPub Protocol Specification*. (The federated social networking standard; read the overview and actor model sections.)

### Discussion Questions

1. Mastodon's federation model allows any server to join the network and set its own moderation policies. A server known for hosting illegal content joins the network. What are the responsibilities of other server administrators? What technical and social mechanisms limit its reach?
2. Local-first software stores data on the device, improving privacy but increasing the risk of data loss (device theft, hardware failure). How do you balance local storage with backup? What encryption and synchronization mechanisms ensure security?
3. The "decentralized web" promises user sovereignty but requires greater technical literacy. Is decentralization compatible with mass adoption? What role should platforms, governments, and educational institutions play in making decentralized technologies accessible?

---

ᚺ **Lecture 9: Web Accessibility and Internationalization — The Web for Everyone**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

The web's founding principle is **universal access**: anyone, anywhere, with any device, should be able to participate. This lecture covers the engineering and design practices that make this principle real: **accessibility** (building for users with disabilities — visual, auditory, motor, cognitive), **internationalization** (designing for multiple languages, scripts, and cultural conventions), and **inclusive design** (recognizing that disability is a mismatch between user capabilities and system design, not a property of the user). We examine WCAG 2.2 AA compliance (the legal standard in most jurisdictions by 2040), screen reader interaction models, right-to-left layout, variable font rendering, and the ethical imperative of building for the full spectrum of human diversity.

### Key Topics

- **WCAG 2.2 and Accessible Rich Internet Applications (ARIA):** The Web Content Accessibility Guidelines define success criteria across four principles: Perceivable (information must be presentable in ways users can perceive), Operable (interface components must be operable by all users), Understandable (information and operation must be understandable), and Robust (content must work with current and future assistive technologies). ARIA provides semantic markup for dynamic content (live regions, modal dialogs, tab panels) that screen readers can interpret. Common failures: missing alt text, insufficient color contrast, keyboard traps, missing form labels, and focus indicators that are invisible.
- **Screen Readers and Assistive Technologies:** Screen readers (JAWS, NVDA, VoiceOver, Orca) parse the DOM and present it as speech or braille. They navigate by element type (headings, links, form fields), by landmark regions (banner, main, navigation, complementary), and by ARIA roles. The developer's responsibility: semantic HTML (`<nav>`, `<main>`, `<article>` rather than `<div>`), proper heading hierarchy (h1-h6 in order, no skips), focus management (visible focus indicators, logical tab order), and ARIA labels where semantics are insufficient (`aria-label`, `aria-describedby`, `aria-live`).
- **Internationalization (i18n) and Localization (l10n):** Internationalization is designing software to support multiple languages and regions; localization is adapting it for a specific locale. Technical challenges: text direction (RTL scripts like Arabic and Hebrew require mirrored layouts), text expansion (German text is 30% longer than English; UI must accommodate), font rendering (CJK characters require different typography; emoji are standardized by Unicode but rendered differently per platform), date and number formatting (DD/MM/YYYY vs. MM/DD/YYYY; comma vs. period as decimal separator), and collation (sorting rules vary by language — in Swedish, å comes after z; in German, ä sorts with a).
- **Cognitive Accessibility:** Beyond sensory and motor disabilities, cognitive accessibility addresses users with dyslexia, ADHD, autism, and age-related cognitive decline. Practices: plain language (Flesch-Kincaid reading ease score >60), consistent navigation (same layout across pages), error prevention (confirmation for destructive actions), adequate time limits (extendable timers), and reduced motion (respecting `prefers-reduced-motion` for animations that can trigger vestibular disorders). By 2040, cognitive accessibility is mandatory under the European Accessibility Act and the Yggdrasil Digital Inclusion Charter.
- **Automated Accessibility Testing:** Tools like axe, Lighthouse, and WAVE catch ~30% of accessibility issues automatically (missing alt text, insufficient contrast, missing labels). The remaining 70% require manual testing: keyboard navigation (can the entire application be used without a mouse?), screen reader testing (does the screen reader announce content in a logical order?), and cognitive walkthroughs (can a first-time user complete core tasks?). The Yggdrasil Development Standards require automated accessibility testing in CI and manual testing before every release.

### Lecture Notes

Accessibility is not a feature — it is a prerequisite. A web application that cannot be used by screen readers is not merely "missing accessibility features"; it is a discriminatory system that excludes millions of people from participation. The United Nations Convention on the Rights of Persons with Disabilities (2006), the European Accessibility Act (2019/2035), and the Yggdrasil Digital Inclusion Charter (2030) all establish that digital accessibility is a human right, not a nice-to-have.

**The social model of disability** reframes the problem. In the medical model, disability is a defect in the person that needs to be cured. In the social model, disability is a mismatch between the person's capabilities and the environment's design. A person who cannot see is not "disabled" by their blindness; they are disabled by a website that relies exclusively on visual information. This reframe shifts responsibility from the user to the designer: it is the designer's job to ensure that information is available through multiple channels (visual, auditory, tactile, textual).

**Semantic HTML** is the foundation of accessibility. The `<button>` element is not merely a styled `<div>` — it has built-in keyboard support (activatable with Enter or Space), built-in focus management, and built-in screen reader announcements ("button: Submit"). A `<div class="button">` has none of these unless the developer reimplements them — and developers frequently forget focus management, role attributes, or keyboard handlers. The Yggdrasil frontend guidelines prohibit clickable `<div>`s: if it acts like a button, it must be a `<button>`. This simple rule eliminates a major class of accessibility bugs.

**Internationalization** is often treated as an afterthought: build the application in English, then "translate it later." This approach produces broken UIs, mistranslated idioms, and culturally inappropriate content. The correct approach is **internationalization from day one**: externalize all strings, use Unicode throughout (UTF-8), design layouts that accommodate text expansion, and test with real localized content. The Yggdrasil Student Portal supports 24 languages, including Old Norse (for the Norse Pagan Studies program) and Sámi (for the indigenous studies track). The localization process involves not merely translation but cultural adaptation: date formats, currency symbols, color symbolism (red means danger in Western cultures but prosperity in Chinese cultures), and iconography (a thumbs-up gesture is offensive in some Middle Eastern countries).

**Cognitive accessibility** is the frontier of inclusive design. As the population ages and as awareness of neurodiversity grows, the demand for cognitively accessible interfaces increases. The principles are simple but transformative: reduce cognitive load (fewer options, clearer hierarchy), provide scaffolding (progress indicators, confirmation messages, undo functionality), and respect user preferences (reduced motion, dark mode, high contrast). The Yggdrasil Portal includes a "Focus Mode" that hides non-essential elements, increases font size, and simplifies navigation — used by 15% of students, not only those with ADHD but also those who prefer distraction-free environments.

### Required Reading

- W3C. (2040). *Web Content Accessibility Guidelines (WCAG) 2.2*. https://www.w3.org/WAI/WCAG22/
- Henry, S.L. et al. (2036). "The Business Case for Digital Accessibility." *W3C WAI*. (Evidence that accessibility benefits all users, not just those with disabilities.)
- Spolsky, J. (2035). *The Absolute Minimum Every Software Developer Absolutely, Positively Must Know About Unicode and Character Sets*. Yggdrasil Technical Communications Press. (A classic; essential for i18n engineering.)

### Discussion Questions

1. Your team has a tight deadline and an accessibility audit scheduled for after launch. A senior developer argues that accessibility can be "fixed later." What evidence and arguments would you use to prioritize accessibility from the start? What is the cost of retrofitting versus building in?
2. A client requests that their website support 40 languages, including right-to-left scripts and complex text shaping (Arabic, Thai, Devanagari). What technical infrastructure do you need? What are the common pitfalls in RTL layout implementation?
3. Cognitive accessibility features like "Focus Mode" benefit users without diagnosed disabilities. Is this "curb-cut effect" (universal design) sufficient justification for investing in accessibility, or is the ethical imperative (equal access for people with disabilities) the primary argument?

---

ᚾ **Lecture 10: Web Performance — The Science of Speed**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

Web performance is not about milliseconds — it is about **user perception, engagement, and business outcomes**. Studies consistently show that slower pages have higher bounce rates, lower conversion rates, and reduced user satisfaction. This lecture covers the complete performance engineering lifecycle: measurement (Real User Monitoring vs. synthetic testing), analysis (identifying bottlenecks in the critical rendering path), optimization (caching, compression, code splitting, lazy loading, resource hints), and monitoring (performance budgets, regression detection, Core Web Vitals tracking). We examine the Yggdrasil Student Portal performance optimization project as a case study: reducing time-to-interactive from 4.2s to 1.1s through systematic analysis and targeted interventions.

### Key Topics

- **The Critical Rendering Path:** The sequence of steps required to render the first pixel: parse HTML → build DOM → parse CSS → build CSSOM → execute blocking JavaScript → compute styles → build layout → paint → composite. The **critical path** is the subset of resources required for the above-the-fold content. Optimizing the critical path: inline critical CSS (eliminate the external CSS request for above-the-fold styles), defer non-critical JavaScript (use `defer` or `async`), and preload critical resources (`<link rel="preload">` for fonts and hero images).
- **Resource Optimization:** **Compression** (gzip, brotli, zstd — reducing text resource size by 70-90%); **minification** (removing whitespace and comments from CSS/JS); **tree shaking** (eliminating unused code from bundles); **code splitting** (loading only the code needed for the current route); **image optimization** (responsive images with `srcset`, modern formats like AVIF and WebP, lazy loading with `loading="lazy"`); and **font optimization** (subset fonts to include only used glyphs, use `font-display: swap` to prevent invisible text during loading).
- **Caching Strategies:** The HTTP cache is the single most impactful performance optimization. Strategies: **cache-first** (serve from cache, fetch from network in background — ideal for static assets); **network-first** (fetch from network, fall back to cache — ideal for dynamic content); **stale-while-revalidate** (serve from cache immediately, then update cache from network — the best of both worlds). Service Workers enable programmatic caching and offline functionality. The Yggdrasil Portal uses a cache-first strategy for static assets and stale-while-revalidate for API responses.
- **Performance Budgets and Regression Detection:** A performance budget is a team-defined limit on metrics (total JavaScript size, time-to-interactive, cumulative layout shift). Budgets are enforced in CI: builds that exceed the budget fail. Regression detection monitors production performance and alerts when metrics degrade beyond a threshold. Tools: Lighthouse CI (automated Lighthouse scoring in CI/CD), WebPageTest (synthetic testing from multiple locations and devices), and Chrome User Experience Report (CrUX, real-world performance data from actual Chrome users).
- **Core Web Vitals and User Experience Metrics:** Largest Contentful Paint (LCP, <2.5s for the main content to load), First Input Delay (FID, <100ms for the page to respond to interaction), and Cumulative Layout Shift (CLS, <0.1 for visual stability). By 2040, search ranking algorithms incorporate Core Web Vitals as signals, making performance optimization an SEO requirement. The Yggdrasil Portal achieved "Good" ratings on all three metrics for 95% of users after its optimization project.

### Lecture Notes

Performance is invisible when it is good and unbearable when it is bad. Users do not consciously evaluate page load time, but they feel it as friction — a subtle resistance that accumulates into abandonment. A study by Amazon (2006, replicated continuously) found that every 100ms of latency cost 1% in revenue. By 2040, the threshold for "fast" has tightened: users expect interactive content within 200ms of interaction and meaningful content within 1 second of navigation.

**The critical rendering path** is the bottleneck that determines perceived performance. A page may have 100 resources, but only 3-5 are on the critical path: the HTML, the critical CSS, and the fonts. Everything else can load lazily. The Yggdrasil Portal optimization revealed that 60% of the critical path time was spent waiting for a web font to load. The solution: inline the critical CSS (eliminating the CSS file request), subset the font to include only the glyphs used on the landing page, and use `font-display: swap` to render fallback text immediately. These three changes reduced LCP by 1.8 seconds.

**Code splitting** is the performance optimization that has had the biggest impact on JavaScript-heavy applications. Instead of shipping a single 2MB bundle containing all application code, modern bundlers (Vite, Webpack, Rollup) split the code into chunks loaded on demand. The initial page load includes only the code for the current route; other routes are loaded when the user navigates to them. The Yggdrasil Portal reduced its initial JavaScript payload from 1.2MB to 180KB through route-based code splitting and component-level lazy loading. The result: time-to-interactive improved by 60% on 3G connections.

**Performance budgets** transform performance from an aspiration into a constraint. Without budgets, performance degrades gradually as features are added: each new library adds 50KB, each new animation adds 100ms of JavaScript execution, each new tracking pixel adds a network request. A budget stops this creep: "we will not ship a build that exceeds 200KB of JavaScript." When a developer tries to add a 150KB charting library, the CI build fails, forcing a conversation: is this library worth the performance cost? Can we find a lighter alternative? Can we load it lazily? The Yggdrasil Web Platform enforces budgets via Lighthouse CI: any pull request that degrades performance beyond 5% is blocked from merging.

**Real User Monitoring (RUM)** is the gold standard for performance measurement. Synthetic testing (running tests from controlled servers) is useful for regression detection but does not capture the diversity of real-world conditions: slow devices, congested networks, ad blockers that change resource loading, and browser extensions that inject scripts. RUM collects performance data from actual users (anonymized and sampled) and segments it by device type, network quality, and geographic region. The Yggdrasil Portal's RUM data revealed that users in rural Scandinavia (on 4G connections with high packet loss) had 3× worse performance than urban users. This insight led to targeted optimizations: aggressive caching, smaller image formats, and offline-first functionality for unstable connections.

### Required Reading

- Grigorik, I. (2036). *High Performance Browser Networking*, 3rd Edition. O'Reilly. Chapters 12-14.
- Calvano, M. (2035). "The Impact of Web Performance on User Behavior: A Meta-Analysis." *ACM CHI*. (A comprehensive review of performance studies across industries.)
- Google. (2040). *Core Web Vitals Technical Documentation*. https://web.dev/vitals/ (The official guidance on measuring and optimizing LCP, FID, and CLS.)

### Discussion Questions

1. Your team wants to add a real-time analytics dashboard that requires 500KB of charting libraries. The performance budget is 200KB total JavaScript. What are your options? How do you negotiate with the product team?
2. RUM data shows that 10% of your users are on connections slower than 1 Mbps. Should you optimize for them, potentially degrading experience for the 90% on faster connections? What is a principled approach to this trade-off?
3. A third-party script (customer support chat widget) adds 2 seconds to time-to-interactive. The business team insists it is essential. What performance mitigation strategies exist for third-party scripts, and how do you measure their impact?

---

ᛁ **Lecture 11: The Web of 2040 — AI Integration, Holographic Interfaces, and Ambient Computing**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

The web of 2040 is not merely an evolution of the 2020s web — it is a transformation in how humans interact with information, services, and each other. This lecture explores the emerging paradigms that will define the next decade of web development: **AI-integrated browsers** (predictive prefetching, conversational interfaces, automated form filling, and intelligent content summarization), **holographic and spatial web experiences** (WebXR, volumetric displays, mixed reality commerce), **ambient computing interfaces** (voice, gesture, gaze, and neural interfaces), and the **autonomous web** (AI agents that browse, transact, and negotiate on behalf of users). We examine both the technical architectures and the societal implications of a web that anticipates user needs rather than merely responding to explicit requests.

### Key Topics

- **AI-Integrated Browsing:** Modern browsers incorporate large language models that provide contextual assistance: summarizing articles, translating languages in real-time, suggesting completions for forms, and warning about potential misinformation. **Predictive prefetching** uses ML models to predict which links a user will click and preload the content, reducing perceived load time to near zero. The **conversational web** interface (pioneered by Arc Browser, refined by Yggdrasil's Mímir Browser) allows users to interact with websites through natural language rather than clicking and scrolling. The technical challenge: maintaining user privacy while processing content through AI models (on-device inference, federated learning, and differential privacy).
- **WebXR and Spatial Computing:** WebXR (the W3C standard for VR/AR on the web) enables immersive experiences directly in the browser: virtual storefronts where users examine 3D products, collaborative workspaces where remote teams manipulate shared 3D models, and educational environments where students explore molecular structures or historical reconstructions. By 2040, lightweight AR glasses and contact-lens displays have made spatial computing ubiquitous. The Yggdrasil Virtual Campus uses WebXR to provide immersive lecture halls: students wearing AR glasses see holographic diagrams floating above the professor's desk, interact with 3D models of Viking ships, and annotate shared virtual whiteboards.
- **Ambient and Multimodal Interfaces:** The web is no longer confined to screens. **Voice interfaces** (web-based voice assistants, speech-to-text for form input, voice navigation) serve users who cannot or prefer not to use visual interfaces. **Gaze tracking** enables hands-free navigation for users with motor disabilities and provides attention analytics for content creators. **Gesture recognition** (hand tracking, body pose estimation via camera) enables touchless interaction in public kiosks and medical environments. The Yggdrasil Accessibility Lab develops multimodal web interfaces that adapt to the user's available input methods in real-time.
- **Autonomous Agents and the Agentic Web:** AI agents that act on behalf of users — booking flights, comparing prices, filling forms, scheduling appointments, and negotiating with other agents. The **agentic web** requires new protocols: verifiable credentials (proving agent authority), intent-based APIs ("find me a flight to Oslo next Tuesday under $300" rather than navigating airline websites), and trust frameworks (how does a website know an agent is authorized to act for a user?). The Yggdrasil Personal Agent Framework (PAF) allows students to delegate routine tasks to authenticated agents while maintaining an audit trail of all agent actions.
- **Ethical Considerations:** AI-integrated browsing raises concerns about filter bubbles (AI-curated content that reinforces existing beliefs), autonomy erosion (AI making decisions that users should make themselves), and surveillance (AI models that learn intimate details about users from their browsing patterns). The Yggdrasil Digital Ethics Council has proposed the **Principle of Human Override**: every AI-generated suggestion or action must be overridable by the user, and the user must be informed when AI is influencing their choices.

### Lecture Notes

The web of 2040 is less a place you visit and more an **intelligent layer** that surrounds you. The browser is no longer a window into websites; it is an assistant that understands your context, anticipates your needs, and mediates your interactions with digital services. This transformation is as profound as the shift from command-line interfaces to graphical user interfaces, or from desktop applications to the mobile web.

**Predictive prefetching** is the performance optimization that AI makes possible. Traditional prefetching uses heuristics: if the user is on the search results page, prefetch the top result. AI-powered prefetching uses behavior models: based on the user's history, the time of day, their location, and the content of the current page, the model predicts with 85% accuracy which link the user will click next and preloads it. The result: when the user clicks, the page is already in memory, creating the illusion of instantaneous response. The privacy cost: the model must know the user's history and context. The Yggdrasil Mímir Browser addresses this by running prediction models on-device, with no data sent to servers.

**The conversational web** challenges the fundamental interaction model of clicking links and filling forms. A student planning a semester abroad might ask their browser: "Find me exchange programs in Norway that accept CS credits, cost less than $10,000, and start in January." The browser's AI decomposes this into sub-queries, searches university databases, compares programs, and presents a synthesized answer with links to applications. This is not search; it is **task completion**. The technical architecture involves natural language understanding, structured query generation across multiple APIs, and result synthesis with source attribution.

**WebXR** has matured from a novelty to a platform. The 2020s saw VR headsets as gaming peripherals; the 2040s see lightweight AR as everyday infrastructure. The Yggdrasil Virtual Campus demonstrates the educational potential: in a history lecture on Viking shipbuilding, students see a full-scale holographic longship floating in the lecture hall. They can walk around it, examine the clinker construction, and toggle between the original wood and a transparent view showing the internal frame. In a biology lab, students manipulate 3D protein structures with hand gestures, watching folding animations in real-time. These experiences are not "virtual reality escapes" from education; they are **enhanced reality tools** that make abstract concepts tangible.

The **agentic web** raises fundamental questions about identity, authority, and responsibility. When an AI agent books a flight on your behalf, who is liable if it makes a mistake? When an agent negotiates a price with a merchant's agent, is the resulting contract binding? The Yggdrasil PAF addresses these questions through cryptographic credentials: the agent holds a delegated key that is valid only for specified operations and time windows, with all actions logged in a tamper-evident audit trail. But the legal framework remains incomplete: the 2038 Nordic AI Liability Treaty established preliminary rules, but jurisdictional conflicts persist.

### Required Reading

- W3C. (2035). *WebXR Device API Specification*. https://www.w3.org/TR/webxr/ (Read the immersive session and input sections.)
- Yggdrasil AI Ethics Board. (2040). "The Agentic Web: Protocols, Risks, and Governance." *UoY White Paper* WP-2040-12.
- Weiser, M. (1991/2035). "The Computer for the 21st Century." *Scientific American*. (The original vision of ubiquitous computing; read with the 2035 retrospective on ambient interfaces.)

### Discussion Questions

1. Predictive prefetching improves performance but requires access to user behavior history. Design a prefetching system that preserves privacy: what data is collected, where is it processed, and what guarantees do you provide to users?
2. The conversational web reduces the need for traditional web design (pages, navigation, visual hierarchy). If users interact through conversation, what is the role of web designers? What new skills become important?
3. AI agents acting on behalf of users may make decisions that the user disagrees with. The Principle of Human Override requires that every AI action be overridable. For a complex negotiation between two agents, what does "override" mean? At what granularity should human oversight be required?

---

ᛃ **Lecture 12: Building and Deploying a Full-Stack Web Application**

**Course:** IT107 — Web Technologies & Internet Architecture  
**Degree:** Bachelor of Science in Information Technology, University of Yggdrasil, 2040

---

### Overview

This culminating lecture synthesizes the course content into a practical capstone project: building and deploying a full-stack web application on the Yggdrasil Cloud Platform. Students work in teams of 3-4 to design, implement, test, and deploy a web application that addresses a real campus need: event management, study group coordination, resource booking, or campus sustainability tracking. The lecture covers project scaffolding (Next.js 15 with React Server Components, PostgreSQL via Yggdrasil DBaaS, deployed on Yggdrasil Cloud Functions with CDN), team collaboration (Git workflows, CI/CD via GitHub Actions, automated testing), and deployment considerations (environment management, secrets handling, monitoring with Yggdrasil CloudWatch, and rollback procedures). The project is evaluated on functionality, performance, security, accessibility, and code quality.

### Key Topics

- **Application Architecture:** The Yggdrasil standard stack for IT107: **Frontend** — Next.js 15 with App Router, React Server Components for server rendering, Tailwind CSS for styling, and Radix UI for accessible components. **Backend** — Next.js API routes with TypeScript, PostgreSQL (via Yggdrasil DBaaS with automatic backups), and Prisma as the ORM. **Authentication** — NextAuth.js with passkey support (WebAuthn) and OAuth 2.0 integration with the Yggdrasil identity provider. **Deployment** — Yggdrasil Cloud Platform with automatic HTTPS, CDN integration, and serverless functions.
- **Development Workflow:** Git feature branches with pull request reviews, automated linting (ESLint, Prettier), type checking (TypeScript strict mode), and testing (Jest for unit tests, Playwright for end-to-end tests). The CI/CD pipeline runs on every pull request: install dependencies → type check → lint → test → build → deploy to staging. Production deployment requires manual approval after staging validation. Database migrations are managed via Prisma Migrate and run automatically in CI.
- **Security Implementation:** HTTPS only (HSTS header with preload), Content Security Policy (strict default-src, script-src with nonces), CSRF protection (Double Submit Cookie pattern), XSS prevention (input validation with Zod, output encoding with React's automatic escaping), SQL injection prevention (parameterized queries via Prisma), and authentication security (passkeys for primary auth, TOTP backup for recovery). Security headers: X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy.
- **Performance and Accessibility:** Core Web Vitals targets (LCP <2.5s, FID <100ms, CLS <0.1) enforced via Lighthouse CI. Accessibility: semantic HTML, ARIA labels where needed, keyboard-navigable interface, color contrast ratios >4.5:1, and screen reader testing with NVDA. Image optimization: AVIF format, responsive srcset, lazy loading. Font optimization: subset to used glyphs, font-display: swap.
- **Monitoring and Operations:** Structured logging (JSON format with trace IDs), error tracking (Sentry integration), performance monitoring (Web Vitals reporting to Yggdrasil CloudWatch), and health checks (/_health endpoint returning 200 OK with database connectivity verification). The deployment checklist: database migrations applied, environment variables configured, CDN cache invalidated, smoke tests passed, and rollback plan verified.

### Lecture Notes

The capstone project is where knowledge becomes skill. For twelve weeks, you have studied protocols, architectures, and principles; now you apply them to build something that real users will touch. The difference between a classroom exercise and a deployed application is the difference between a blueprint and a building: the blueprint shows what is intended; the building reveals what is possible, what is hard, and what you did not anticipate.

**The Yggdrasil standard stack** is chosen for educational and practical reasons. Next.js provides a unified framework for frontend and backend, reducing the cognitive load of learning multiple technologies. React Server Components teach the modern paradigm of server-first rendering. PostgreSQL is the most widely deployed open-source relational database, and Prisma provides type-safe database access. TypeScript eliminates entire categories of bugs through static typing. The stack is not exotic; it is what you will encounter in industry.

**Team dynamics** are as important as technical skills. A team of four developers must coordinate: who writes the database schema? Who builds the authentication flow? Who styles the UI? Who writes tests? The answer is not "everyone does everything" (chaos) or "everyone has a fixed role" (brittleness) but "everyone owns a feature and reviews everyone else's features." The Git workflow enforces this: each feature branch is owned by one developer, reviewed by at least one other, and merged only after CI passes. The pull request is not merely a code review; it is a conversation about design decisions, trade-offs, and edge cases.

**Security implementation** in the capstone is not "add it at the end"; it is "build it in from the start." The project template includes a strict CSP, security headers, and authentication scaffolding. Students who try to "make it work first, secure it later" discover that retrofitting security is painful: the inline script they added for debugging violates the CSP; the SQL query they wrote with string concatenation fails the security audit; the user input they trusted causes XSS. The teams that succeed treat security failures as build failures: fix them immediately, understand why they occurred, and prevent recurrence.

**Performance optimization** is the final 20% that takes 80% of the time. A functional application is easy; a fast application requires discipline. The teams that achieve "Good" Core Web Vitals scores are the ones that measure from day one, set a performance budget, and investigate every regression. The teams that struggle are the ones that add features without measuring until the final week, when they discover that their application takes 8 seconds to load and they have three days to fix it.

The Yggdrasil Cloud Platform provides the infrastructure, but the team provides the engineering. The platform handles HTTPS certificates, CDN caching, and database backups — but the team must design the schema, write the queries, handle errors, and test thoroughly. This is the essence of IT: not merely using technology, but **engineering with it** — making deliberate choices, accepting trade-offs, and building systems that are correct, efficient, secure, and maintainable.

### Required Reading

- Next.js Documentation (2040 Edition). https://nextjs.org/docs (The App Router, Server Components, and API routes sections.)
- Prisma Documentation (2040 Edition). https://www.prisma.io/docs (Schema design, migrations, and client usage.)
- Yggdrasil Cloud Platform Documentation. "Deploying Full-Stack Applications: A Student Guide." Available via Yggdrasil Developer Portal.

### Discussion Questions

1. Your team disagrees on whether to use a SQL or NoSQL database for the capstone. One member advocates MongoDB for flexibility; another insists on PostgreSQL for reliability. What evidence do you gather? How do you resolve the disagreement and commit to a decision?
2. The capstone is due in two weeks. One team member's feature is behind schedule and has introduced several security bugs. Do you help them fix it, cut the feature, or delay the deadline? What is your decision framework?
3. After deployment, a user reports that the application is unusable with a screen reader. Your team did not test with assistive technologies. What is your response? What process changes would prevent this in future projects?

---

## Final Examination Preparation

The IT107 final examination is a **practical assessment** combining a 90-minute written component and a take-home practical component.

### Written Component (90 minutes, closed book)

**Section A: Short Answer (30%)**
- Explain the end-to-end principle and provide one example of how it enabled Internet innovation.
- Compare HTTP/2 multiplexing with HTTP/3 QUIC streams. What problem does each solve, and what new challenges does each introduce?
- Describe the TLS 1.3 handshake. How does it differ from TLS 1.2, and why is 0-RTT resumption both a performance benefit and a security risk?

**Section B: Problem Solving (40%)**
- A web application has a Largest Contentful Paint of 5.2 seconds. Analyze the provided waterfall chart and identify the three most impactful optimizations. Justify your prioritization with specific performance principles.
- Design a caching strategy for a news website with the following requirements: breaking news must appear within 30 seconds of publication; article pages are accessed for 48 hours after publication; static assets (images, CSS, JS) change monthly. Specify cache-Control directives, CDN configuration, and invalidation mechanisms.
- A federated social network server is receiving hate speech reports from other servers. Describe the technical, legal, and ethical considerations in designing a moderation policy that respects federation principles while protecting users.

**Section C: Essay (30%)**
- Choose one of the following:
  1. "The web of 2040 is less open than the web of 2010." Evaluate this claim with reference to platform centralization, government regulation, and technological architecture.
  2. Compare the security models of centralized systems (single trusted operator) and decentralized systems (distributed trust). Under what circumstances is each model superior?
  3. The agentic web — where AI agents act on behalf of users — promises convenience but threatens autonomy. Is this trade-off acceptable? What safeguards should exist?

### Practical Component (Take-home, 1 week)

Optimize the performance of a provided poorly-performing web application. Deliverables:
1. A Lighthouse score report showing improvement from "Poor" to "Good" on all Core Web Vitals.
2. A written analysis (max 5 pages) documenting the optimizations applied, their measured impact, and any trade-offs made.
3. The modified source code, committed to a Git repository with clear commit messages.

### Sample Practice Problems

1. A CDN edge node has a cache hit ratio of 85%. The origin server can handle 1,000 requests per second. What is the maximum sustainable traffic rate to the edge node? If traffic increases to 20,000 requests per second, what happens?
2. Design a URL structure for a local-first note-taking application that supports nested folders, shared documents, and offline creation. The URLs must work when the device is offline and synchronize correctly when connectivity returns.
3. A web application uses a third-party analytics script that adds 1.5 seconds to page load time. The marketing team insists it is essential for conversion tracking. Propose three technical solutions that preserve tracking while minimizing performance impact.

---

*"The web is not a technology. It is an agreement — a set of protocols and practices that allow strangers to collaborate across distance and difference. Our job is to strengthen that agreement, to make it more inclusive, more resilient, and more worthy of the trust that billions of people place in it." — Dr. Freyja Vébjörnsdottir, IT107 Opening Lecture, 2040*
