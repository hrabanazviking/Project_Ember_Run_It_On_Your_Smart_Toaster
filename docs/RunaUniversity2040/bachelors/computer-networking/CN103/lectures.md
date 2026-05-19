# CN103: Data Communications & Signal Processing
## Bachelor of Science in Computer Networking — University of Yggdrasil, 2040

### Course Overview

Every bit that traverses a network—from a transatlantic submarine cable carrying 400 Tbps of traffic to the Wi-Fi signal that delivers this lecture to your tablet—is ultimately an analogue physical phenomenon. Before networking became software-defined, before SDN controllers abstracted the forwarding plane, before BGP and OSPF and TCP—there was the physical layer: voltage levels, electromagnetic waveforms, and the information theory that transforms those waveforms into reliable digital communication. This course grounds the networking student in the physics of connectivity, because the network engineer who does not understand the physical layer is like a navigator who does not understand the sea: they can follow the chart, but they cannot survive the storm.

We begin with the mathematical foundations—Fourier analysis, Nyquist sampling, Shannon's channel capacity theorem—and progress through modulation techniques, line coding, multiplexing, error detection and correction, and the practical realities of guided and unguided transmission media. By course end, you will be able to read an eye diagram, calculate the Shannon capacity of a noisy channel, and explain why 5G millimetre-wave signals cannot penetrate a concrete wall but can deliver 10 Gbps to a device in direct line-of-sight. The Norns weave our fate from threads of light through glass; understanding those threads is the work of this course.

**Prerequisites:** CN101 Introduction to Computer Networking  
**Credits:** 4  
**Term:** Year 1, Semester 2  
**Instructor:** Dr. Sigurd Wave-Breaker, Ph.D.  
**Office Hours:** Týsdagr 10:00–12:00, Sigil Hall B-12

---

## Lecture 1: Signals, Spectra, and the Fourier Revolution
### Required Reading: Lathi, B.P. & Ding, Z. (2038). *Modern Digital and Analog Communication Systems* (6th ed.). Oxford University Press. Chapters 2–3.

The central insight of data communications is that any signal—no matter how complex—can be decomposed into a sum of pure sine waves of different frequencies, amplitudes, and phases. This is the Fourier transform, and it is arguably the most important mathematical tool in all of communications engineering. When Jean-Baptiste Joseph Fourier presented his 1807 memoir on heat conduction to the French Academy, he could not have imagined that his decomposition would become the foundation of global telecommunications—but here we are, two centuries later, with every LTE symbol, every Wi-Fi OFDM subcarrier, and every fibre-optic wavelength-division channel owing its existence to Fourier's insight.

A signal's frequency-domain representation reveals information that the time-domain view conceals. A square wave—the fundamental digital signal—appears simple in the time domain: it alternates between high and low voltage at regular intervals. But in the frequency domain, it reveals itself as an infinite series of odd harmonics: the fundamental frequency f, plus 3f at one-third amplitude, 5f at one-fifth amplitude, and so on to infinity. A digital system that switches at 1 GHz generates not just a 1 GHz tone but radiation at 3 GHz, 5 GHz, 7 GHz—harmonics that cause electromagnetic interference (EMI) and must be managed through careful PCB layout, shielding, and filtering. The 2040 ITU-R SM.329 standard on spurious emissions mandates that harmonics above the 5th must be suppressed by at least 60 dB relative to the fundamental—a requirement that drives much of modern hardware design.

Bandwidth—the range of frequencies a signal occupies—is the fundamental currency of communications. A pure sine wave at 100 MHz has zero bandwidth (it occupies a single point in the frequency domain) but carries zero information because it never changes. Information requires change, and change requires bandwidth. The relationship between data rate and bandwidth is formalised in the Nyquist formula (Lecture 2), but the intuitive principle is: faster data rates require more bandwidth because the signal must change state more rapidly, and rapid state changes contain higher-frequency components. Every communications system is fundamentally a trade between data rate, bandwidth, signal power, and noise—the four variables of the Shannon-Hartley equation that governs the entire field.

The practical skill this lecture imparts is spectrum analysis. In the lab, you will use a spectrum analyser (Keysight N9042B UXA or similar) to observe the frequency-domain representation of: a pure sine wave, a square wave at 10 MHz, an AM-modulated carrier, and a Wi-Fi 6 OFDM signal. You will measure the 3 dB bandwidth, identify the harmonic structure, and correlate time-domain jitter with frequency-domain phase noise—skills that form the diagnostic toolkit of every network hardware engineer.

**Discussion Questions:**
1. Why does a pure sine wave carry zero information despite being the fundamental building block of all communications?
2. If a 100 MHz square wave's 5th harmonic violates FCC Part 15 radiated emission limits, what three design changes could suppress it?
3. Explain why the Fourier transform is equally applicable to acoustic signals (sonar), optical signals (fibre), and radio signals (Wi-Fi).

---

## Lecture 2: The Nyquist-Shannon Trinity — Sampling, Capacity, and the Information Ceiling
### Required Reading: Cover, T.M. & Thomas, J.A. (2040). *Elements of Information Theory* (3rd ed.). Wiley. Chapters 7–9.

Three theorems form the theoretical ceiling of all digital communication. The Nyquist Sampling Theorem (1928) defines the minimum rate at which an analogue signal must be sampled to enable perfect digital reconstruction. The Nyquist Bit-Rate Formula defines the maximum symbol rate for a noiseless channel of given bandwidth. And the Shannon-Hartley Theorem (1948) defines the maximum error-free data rate for a noisy channel—the absolute Shannon limit that no modulation scheme, no coding technique, and no quantum trickery can exceed. Together, these three results constrain every network you will ever design.

The Sampling Theorem states: to perfectly reconstruct a bandlimited signal of bandwidth B Hz, you must sample it at a rate of at least 2B samples per second. This is the Nyquist rate. Sample at less than 2B, and you suffer aliasing—high-frequency components impersonating low-frequency components in the sampled representation, producing irrecoverable distortion. Every ADC (analogue-to-digital converter) in every network interface card is designed around this theorem: a 100 Gigabit Ethernet receiver sampling a 25.78125 Gbaud PAM4 signal must sample at a minimum of 51.5625 Gsamples/second, and in practice samples at 64–80 Gsps to provide margin for non-ideal anti-aliasing filters.

The Nyquist Bit-Rate Formula extends this to noiseless channels: maximum symbol rate = 2B symbols/second for a channel of bandwidth B Hz. If each symbol carries M bits (M = log₂(V), where V is the number of discrete voltage levels), then the maximum data rate is 2B × log₂(V) bits per second. This explains the progression of Ethernet standards: 10GBASE-T uses PAM16 encoding (16 levels, 4 bits per symbol) over 500 MHz of bandwidth, yielding 2 × 500 MHz × 4 = 4 Gbps theoretical per twisted pair, with four pairs giving 16 Gbps—the extra overhead goes to forward error correction (FEC) that brings the net data rate to 10 Gbps.

But the Shannon-Hartley Theorem is the real hammer: C = B × log₂(1 + S/N), where C is channel capacity in bits per second, B is bandwidth in Hz, and S/N is the signal-to-noise ratio (linear, not dB). This equation tells us that capacity grows linearly with bandwidth but only logarithmically with signal-to-noise ratio. Doubling bandwidth doubles capacity. Doubling signal power (which doubles S/N) increases capacity by only B bits per second—a linear gain from a logarithmic argument. This is why network engineers obsess over bandwidth allocation (spectrum licencing, fibre counts, WDM channel spacing) and why 6G research focuses on opening new spectrum bands (7–24 GHz, sub-THz) rather than simply increasing transmission power.

A practical consequence: for a typical Wi-Fi 7 channel with 320 MHz bandwidth and 30 dB SNR (S/N = 1000), Shannon capacity is C = 320 × 10⁶ × log₂(1001) ≈ 3.19 Gbps. Wi-Fi 7's claimed maximum data rate of 46 Gbps (with 16 spatial streams, 4096-QAM, and MLO) approaches this theoretical limit through spatial multiplexing—essentially creating multiple parallel Shannon channels through MIMO beamforming. But the per-stream limit remains: no single spatial stream can exceed the Shannon bound for its bandwidth and SNR.

**Discussion Questions:**
1. Why does aliasing produce irrecoverable distortion, whereas quantisation noise can be reduced by increasing bit depth?
2. A 5G NR channel has 100 MHz bandwidth and 20 dB SNR. Calculate its Shannon capacity. Now double the bandwidth; what is the new capacity? Now double the SNR instead; which has greater effect, and why?
3. Why does Shannon capacity grow only logarithmically with SNR? Provide an intuitive explanation.

---

## Lecture 3: Modulation — Encoding Bits into Waves
### Required Reading: Proakis, J.G. & Salehi, M. (2039). *Digital Communications* (6th ed.). McGraw-Hill. Chapters 4–5.

Modulation is the art of imprinting digital information onto an analogue carrier wave. The carrier—a sinusoidal electromagnetic oscillation at a specific frequency—is modified in one or more of its three fundamental properties: amplitude, frequency, or phase. These three dimensions give rise to the three canonical modulation families: Amplitude Shift Keying (ASK), Frequency Shift Keying (FSK), and Phase Shift Keying (PSK). Modern high-speed networks use Quadrature Amplitude Modulation (QAM), which modulates both amplitude and phase simultaneously, packing more bits into each symbol at the cost of greater susceptibility to noise.

ASK is the simplest scheme: the carrier amplitude is switched between discrete levels to represent bits. On-Off Keying (OOK), where the carrier is either present (1) or absent (0), was used in early radio telegraphy and survives today in fibre-optic communications—a laser pulsing on and off at 100 Gbps is fundamentally an OOK signal. The limitation of ASK is its vulnerability to amplitude noise: a thunderstorm's electrical interference or a loose connector that attenuates the signal can flip a 1 to a 0 with no warning.

FSK encodes bits as frequency shifts: a lower frequency represents 0, a higher frequency represents 1. Bluetooth Basic Rate uses Gaussian Frequency Shift Keying (GFSK) with a modulation index of 0.28–0.35, trading spectral efficiency for robustness against interference. FSK's key advantage is constant envelope—the signal amplitude never changes, so power amplifiers can operate in their most efficient saturation region. This makes FSK ideal for battery-constrained IoT devices, which is why LoRa (Long Range) uses a variant called Chirp Spread Spectrum (CSS) that sweeps the carrier frequency linearly across the channel bandwidth.

PSK shifts the carrier phase to encode bits. Binary PSK (BPSK) uses two phases (0° and 180°) to encode one bit per symbol—the most robust digital modulation scheme, used by GPS satellites broadcasting at -130 dBm received power (below the thermal noise floor). Quadrature PSK (QPSK) uses four phases (45°, 135°, 225°, 315°) for two bits per symbol. 8-PSK uses eight phases for three bits per symbol, but as the constellation points crowd closer together, the receiver must distinguish smaller phase differences, making the system more vulnerable to phase noise.

QAM combines ASK and PSK: each symbol is defined by both an amplitude and a phase, represented as a point on the complex plane (I/Q diagram). 16-QAM uses a 4×4 grid of constellation points for four bits per symbol. 64-QAM uses an 8×8 grid for six bits. 256-QAM uses 16×16 for eight bits. Wi-Fi 7's 4096-QAM packs 12 bits per symbol—but requires a minimum SNR of approximately 39 dB, achievable only in near-ideal conditions (a device within 2 metres of the access point with minimal multipath). The trade-off between spectral efficiency (bits/Hz) and required SNR is the central design decision in any modulation scheme, and it is captured in the waterfall curves of bit-error-rate (BER) vs. Eb/N0 (energy per bit to noise power spectral density ratio) that you will generate in the laboratory.

**Discussion Questions:**
1. Why is BPSK more robust than QPSK even though both encode bits in phase alone?
2. Calculate the spectral efficiency (bits/s/Hz) of 256-QAM with a symbol rate of 1 Msymbol/s and a channel bandwidth of 200 kHz. Is this feasible under Shannon's theorem?
3. Why does 4096-QAM require approximately 39 dB SNR? Derive the relationship between QAM order and minimum SNR.

---

## Lecture 4: Line Coding and Baseband Transmission
### Required Reading: Stallings, W. (2039). *Data and Computer Communications* (11th ed.). Pearson. Chapters 5–6.

Line coding bridges the gap between abstract bits and physical voltage waveforms on a wire. The simplest approach—map 1 to +V and 0 to 0V—is called Non-Return-to-Zero (NRZ) encoding and seems perfectly adequate until you encounter its fatal flaw: a long run of consecutive 1s or 0s produces a constant voltage with no transitions, causing the receiver's clock recovery circuit to drift. Without synchronisation, the receiver cannot determine where one bit ends and the next begins. Every practical line code must provide sufficient transition density to maintain clock synchronisation.

Manchester encoding solves the synchronisation problem by guaranteeing at least one transition per bit: 1 is encoded as a low-to-high transition at mid-bit, 0 as high-to-low. The cost is that Manchester encoding requires twice the bandwidth of NRZ for the same data rate—the maximum frequency component is double that of the bit rate. Ethernet's original 10BASE-T standard used Manchester encoding at 10 Mbps; 100BASE-TX abandoned it for the more efficient 4B5B + MLT-3 scheme, which achieves 100 Mbps over the same Category 5 cable by using multi-level signalling and block coding.

Modern high-speed serial links use 8B/10B, 64B/66B, or 128B/130B block codes that provide DC balance (equal numbers of 1s and 0s over time) and guaranteed transition density while limiting the encoding overhead. 8B/10B encoding, developed by IBM in 1983 for ESCON and now used in PCI Express 1.x/2.x, SATA, and HDMI, maps each 8-bit data byte to a 10-bit symbol, adding 25% overhead. The encoding ensures a maximum run length of 5 identical bits and maintains running disparity (the cumulative difference between 1s and 0s) within ±1 of zero. 64B/66B encoding, used in 10 Gigabit Ethernet and PCI Express 3.0+, reduces overhead to 3.125% by scrambling the 64-bit payload with a self-synchronising scrambler, adding only a 2-bit sync header.

DC balance matters because most transmission paths are AC-coupled—they use series capacitors (or transformers for Ethernet) to block DC voltage, which would otherwise bias receiver thresholds and cause bit errors. An AC-coupled link cannot transmit a DC signal; the average voltage over any reasonable time window must be zero. Line codes achieve DC balance by ensuring roughly equal numbers of 1s and 0s over time, which also minimises baseline wander—the slow drift of the receiver's decision threshold caused by accumulated DC imbalance.

Eye diagrams are the diagnostic tool for line-coded signals. An oscilloscope triggered on the recovered clock and overlaid with many-bit periods produces an "eye" pattern: a clean, wide-open eye indicates low jitter, low noise, and good signal integrity; a closed eye indicates that the receiver cannot reliably distinguish 1 from 0. In the lab, you will generate eye diagrams for NRZ, Manchester, and 8B/10B signals at 1 Gbps over varying cable lengths, measuring eye height (voltage margin), eye width (timing margin), and jitter RMS—the three parameters that determine whether a link meets its BER specification of 10⁻¹² (one error per trillion bits) or better.

**Discussion Questions:**
1. Why does Manchester encoding require twice the bandwidth of NRZ? Prove your answer with a Fourier analysis.
2. Explain why an AC-coupled link requires DC-balanced line coding, and what happens to the eye diagram when DC balance is lost.
3. Compare 8B/10B and 64B/66B encoding. Under what circumstances would you choose each?

---

## Lecture 5: Multiplexing — Many Signals, One Medium
### Required Reading: Keiser, G. (2040). *Optical Fiber Communications* (6th ed.). McGraw-Hill. Chapters 8–9.

Multiplexing is the strategy that makes global communications economically viable: rather than running a dedicated physical medium for every conversation, we combine many signals onto a shared medium and separate them at the destination. The four canonical multiplexing dimensions—frequency, time, code, and space—correspond to four fundamental physical properties, and modern networks use all four simultaneously.

Frequency Division Multiplexing (FDM) assigns each signal a distinct frequency band within the shared medium. The entire broadcast radio and television industry is FDM: each station occupies a 200 kHz band (FM radio) or 6 MHz band (ATSC 3.0 television) at a different centre frequency, and your receiver's tuner selects one band while rejecting the others. In fibre optics, Wavelength Division Multiplexing (WDM) is simply FDM at optical frequencies: each "colour" of laser light—C-band wavelengths from 1530 nm to 1565 nm, spaced at 50 GHz (0.4 nm) intervals in Dense WDM—carries an independent 400 Gbps data stream, enabling a single fibre pair to carry 30+ Tbps over thousands of kilometres.

Time Division Multiplexing (TDM) allocates the entire channel bandwidth to each signal in rotating time slots. The modern Public Switched Telephone Network's core uses Synchronous Optical Networking (SONET/SDH) with 125-microsecond frames divided into time slots; a DS0 channel (64 kbps) occupies one slot per frame. At the opposite extreme, Time Division Multiple Access (TDMA) in cellular networks (GSM, 5G NR) dynamically allocates time slots to users based on demand, with slot assignments changing every transmission time interval (TTI)—as fast as 0.125 ms in 5G's ultra-reliable low-latency communication (URLLC) mode.

Code Division Multiplexing (CDM) is the mathematical outlier: instead of separating signals in frequency or time, it assigns each signal a unique pseudo-random code sequence. All signals transmit simultaneously across the entire available bandwidth. The receiver correlates the received composite signal against the desired code, which causes the desired signal to coherently combine while the interfering signals appear as noise (processing gain). CDMA, commercialised by Qualcomm for 3G cellular (IS-95, CDMA2000, WCDMA), is no longer the dominant cellular technology (OFDMA displaced it in 4G/5G) but lives on in GPS—all 31 GPS satellites transmit on the same 1575.42 MHz L1 frequency, distinguished only by their unique C/A codes.

Space Division Multiplexing (SDM) is the newest and most promising dimension. MIMO (Multiple-Input Multiple-Output) antenna arrays exploit the fact that radio waves take slightly different paths between each transmit-receive antenna pair, creating independent spatial channels that can carry independent data streams. A 4×4 MIMO system can theoretically quadruple throughput over the same bandwidth and time slots, though in practice channel correlation limits the gain to 2–3×. In fibre optics, multi-core fibre (MCF)—containing 7, 19, or even 37 separate light-guiding cores within a single 125μm cladding—promises to multiply single-fibre capacity by the core count, potentially enabling petabit-per-second links by 2040.

The multiplexing hierarchy is cumulative: a modern 5G base station uses SDM (MIMO antenna arrays) × FDM (OFDM subcarriers at 30 kHz spacing) × TDM (slot allocation per TTI) simultaneously. Understanding how these dimensions compose—and where they interfere with each other—is the art of physical-layer system design.

**Discussion Questions:**
1. Why does CDMA require tight power control, whereas OFDMA does not?
2. Calculate the total capacity of a C-band DWDM system with 96 channels at 50 GHz spacing, each carrying 400 Gbps using 16-QAM modulation.
3. How does spatial multiplexing in MIMO differ fundamentally from frequency multiplexing? Can they be used together without interference?

---

## Lecture 6: Error Detection — The Shield of the Lower Layers
### Required Reading: Peterson, W.W. & Weldon, E.J. (2038). *Error-Correcting Codes* (3rd ed.). MIT Press. Chapters 1–4.

Every physical channel introduces errors. Thermal noise in the receiver's amplifier (proportional to kTB, where k is Boltzmann's constant, T is temperature in Kelvin, and B is bandwidth), shot noise in semiconductor junctions, impulse noise from electrical switching, inter-symbol interference from multipath propagation, and cosmic-ray-induced bit flips in DRAM cells all conspire to corrupt transmitted data. Error detection transforms an unreliable channel into a reliable one by adding redundancy—extra bits that allow the receiver to determine, with high probability, whether the received data matches what was sent.

Parity is the simplest scheme: an extra bit is appended to each byte (or word) such that the total number of 1s is even (even parity) or odd (odd parity). A single-bit error flips the parity, which the receiver detects. But a double-bit error in the same byte flips parity twice, restoring the original parity value and producing an undetectable error. Parity's limitation—it can detect an odd number of errors but not an even number—motivates more sophisticated codes.

Cyclic Redundancy Check (CRC) is the workhorse of modern networking. A CRC treats the data as a binary polynomial and divides it by a generator polynomial, appending the remainder as the checksum. The receiver performs the same division; if the remainder doesn't match, an error has occurred. The strength of a CRC is measured by its Hamming distance—the minimum number of bit errors that can transform one valid codeword into another. CRC-32 (used in Ethernet, SATA, PNG, GZIP) with polynomial 0x04C11DB7 has a Hamming distance of 4 for messages up to 9,123 bits, meaning it can detect any 1-, 2-, or 3-bit error and any odd number of errors, plus all burst errors of length ≤32 bits, for messages within that length. CRC-32C (Castagnoli), used in iSCSI and SCTP, improves on CRC-32 with better burst-error detection for certain patterns, using polynomial 0x1EDC6F41.

Checksums provide a lighter-weight alternative for protocols where CRC's computational cost is prohibitive. The Internet Checksum (RFC 1071), used in IP, TCP, and UDP headers, is simply the one's complement sum of 16-bit words. It is computationally trivial—implementable in a few dozen CPU instructions—but weak: it cannot detect reordering of 16-bit words, it fails to detect certain common error patterns, and its Hamming distance is only 2. TCP's checksum has been the subject of research demonstrating that, for certain data patterns, the probability of an undetected error is as high as 1 in 2¹⁶ (one in 65,536)—unacceptably high for terabyte-scale data transfers. This is why protocols like SCTP and QUIC use CRC-32c instead.

Fletcher's checksum and the Adler-32 checksum (used in zlib) offer intermediate properties: stronger than the Internet Checksum, faster than CRC for software implementation on CPUs without CRC hardware acceleration, but still inferior to CRC in mathematical guarantees. The introduction of CRC32 instruction (Intel SSE4.2, 2008) and ARMv8 CRC instructions eliminated the performance advantage of checksums for most modern processors, making CRC the default choice for new protocol designs.

For networking students, the practical skill is choosing the right error-detection code for the expected error characteristics of the channel. Ethernet's 10⁻¹² BER target, combined with CRC-32's undetected-error probability of approximately 10⁻¹⁴ for 1500-byte frames, has proven sufficient for four decades. But for 100+ Gbps links carrying 9000-byte jumbo frames, the undetected-error probability rises, and modern standards like 400GBASE-R use an inner FEC (Reed-Solomon RS(544,514)) plus CRC to maintain the target undetected-error rate.

**Discussion Questions:**
1. Why is the Internet Checksum still used in TCP/IP four decades after its weaknesses were documented?
2. Prove that CRC-32 can detect all burst errors of length ≤32 bits.
3. Calculate the undetected-error probability for a 9000-byte jumbo frame with CRC-32, assuming a random bit-error rate of 10⁻¹².

---

## Lecture 7: Forward Error Correction — Healing the Signal in Flight
### Required Reading: Ryan, W.E. & Lin, S. (2039). *Channel Codes: Classical and Modern* (2nd ed.). Cambridge University Press. Chapters 3–6, 10.

Error detection (Lecture 6) tells us that an error occurred. Forward Error Correction (FEC) goes further: it corrects errors at the receiver without requiring retransmission. This is important because retransmission adds latency (at least one round-trip time, which is 50ms for geostationary satellite links, 240ms for Earth-Mars communication in 2040, and simply unacceptable for real-time applications) and because some channels are simplex—the receiver cannot send anything back. Deep-space probes, broadcast television, and submarine fibre-optic repeaters all rely on FEC to function at all.

Reed-Solomon codes are the most widely deployed block FEC. An RS(n,k) code takes k data symbols and adds n−k parity symbols, producing an n-symbol codeword that can correct up to (n−k)/2 symbol errors. The 1982 Compact Disc standard used RS(32,28) cross-interleaved coding to correct burst errors up to 4,000 consecutive bits—enough to bridge a 2.5mm scratch on the disc surface. DVB (Digital Video Broadcasting) uses RS(204,188) to protect MPEG transport streams against atmospheric and impulse interference. 400GBASE-R Ethernet uses RS(544,514) operating on 10-bit symbols to achieve a post-FEC BER of 10⁻¹⁵ from a pre-FEC BER of approximately 2×10⁻⁴—an improvement of eleven orders of magnitude.

Low-Density Parity-Check (LDPC) codes, invented by Robert Gallager in 1960 but considered computationally impractical until the 1990s, have become the dominant FEC for high-speed links. LDPC codes approach the Shannon limit to within 0.0045 dB—essentially the theoretical maximum efficiency—because their sparse parity-check matrices enable iterative belief-propagation decoding that converges toward the maximum-likelihood solution. Wi-Fi 6 (802.11ax) uses LDPC as its mandatory FEC. 5G NR uses LDPC for the data channel and Polar codes for the control channel. The DVB-S2X satellite broadcasting standard uses LDPC with code rates from 1/4 (extremely robust, 75% overhead) to 9/10 (spectrally efficient, 11% overhead), selecting the rate dynamically based on link conditions.

Turbo codes, invented by Berrou, Glavieux, and Thitimajshima in 1993, stunned the communications world by demonstrating performance within 0.7 dB of the Shannon limit using two parallel convolutional encoders separated by an interleaver plus iterative decoding. 3G and 4G cellular networks used Turbo codes extensively. Their decline in favour of LDPC (for 5G data channels) reflects LDPC's better performance at very high code rates and its lower decoding latency for hardware-accelerated implementations—critical for the sub-1ms latency targets of 5G URLLC.

Polar codes, invented by Erdal Arıkan in 2008, are the first codes proven to achieve Shannon capacity for all binary-input symmetric memoryless channels as the code length approaches infinity. 5G NR uses Polar codes for control channels (DCI, UCI) because of their excellent performance at short block lengths (20–100 bits) where LDPC's iterative decoder struggles to converge. The underlying principle—channel polarisation, where independent copies of a channel are transformed into "good" channels (near-perfect) and "bad" channels (near-useless)—is a mathematical construction so elegant that it has spawned an entire subfield of polar-coded modulation for next-generation optical and wireless systems.

From a network engineer's perspective, FEC is not free. It adds latency (encoding/decoding time), reduces throughput (the code rate = k/n is the fraction of capacity available for data), and increases silicon area and power consumption. The code rate selection for a given link is an optimisation problem: lower code rate = more error correction but less net throughput; higher code rate = more throughput but less error resilience. 5G NR's adaptive modulation and coding (AMC) selects from 28 MCS (Modulation and Coding Scheme) combinations, ranging from QPSK + code rate 120/1024 (extremely robust, 0.23 bits/s/Hz spectral efficiency) to 256QAM + code rate 948/1024 (maximum throughput, 7.4 bits/s/Hz), with the selection updated every millisecond based on the UE's reported Channel Quality Indicator (CQI).

**Discussion Questions:**
1. Why does LDPC decoding latency make it less suitable than Polar codes for 5G control channels?
2. Calculate the net data rate of a 400GBASE-R Ethernet link using RS(544,514) FEC with 10-bit symbols and a raw symbol rate of 53.125 Gbaud.
3. Explain why Turbo codes were revolutionary in 1993 but have been displaced by LDPC and Polar codes in 5G.

---

## Lecture 8: Guided Transmission Media — Copper, Coax, and the Persistence of Wire
### Required Reading: Barnes, J. (2039). *Electronic System Design: Interference and Noise Control Techniques* (3rd ed.). Chapters 2–4.

Unshielded Twisted Pair (UTP) copper cabling remains the dominant access-layer transmission medium in 2040 because it solves a problem that fibre cannot: power delivery. Power over Ethernet (PoE++ IEEE 802.3bt, up to 90W per port) powers Wi-Fi access points, IP cameras, LED lighting, building sensors, and IoT gateways through the same cable that carries data. A single Category 8.2 cable delivers 40 Gbps of data and 90W of DC power over 30 metres—an integration of communication and energy that fibre, for all its bandwidth advantages, simply cannot match.

The twisted-pair cable's genius is its use of differential signalling: each signal is transmitted as the voltage difference between two wires twisted together, rather than between one wire and ground. External electromagnetic interference (EMI) couples roughly equally into both wires (common-mode noise), and the differential receiver subtracts the two voltages, cancelling the common-mode noise while preserving the differential signal. This common-mode rejection ratio (CMRR) is typically 40–60 dB for well-manufactured twisted pair, meaning the receiver suppresses common-mode noise by a factor of 100 to 1,000. The twist rate further improves performance: tighter twists (shorter pitch) increase coupling between the two conductors, reducing the loop area that acts as an antenna for both emission and susceptibility. Category 8 cables use individually shielded pairs with varying twist rates to minimise crosstalk between adjacent pairs within the same jacket.

Coaxial cable solves a different problem: carrying high-frequency signals over long distances with minimal loss. The coaxial geometry—a central conductor surrounded by a cylindrical dielectric insulator, then a cylindrical outer conductor (shield)—creates a perfectly contained electromagnetic field that does not radiate outward and does not admit external interference. This waveguide-below-cutoff property makes coaxial cable the medium of choice for RF signals from DC to 50+ GHz: cable television distribution, cellular base station antenna feeds, laboratory test equipment interconnects, and quantum computing control lines all use coaxial cable. The characteristic impedance of 50Ω (RF) and 75Ω (video/CATV) is determined by the ratio of inner conductor diameter to outer conductor inner diameter, independent of length.

Attenuation—signal loss per unit distance—is the limiting factor for all metallic transmission media. Skin effect causes high-frequency current to concentrate near the conductor surface, reducing the effective cross-sectional area and increasing resistance proportional to the square root of frequency. Dielectric loss in the insulator material increases linearly with frequency. The combined effect limits Category 8.2 cable to 30 metres at 40GBASE-T, and RG-6 coaxial cable to approximately 100 metres at 3 GHz (typical satellite IF frequency). For longer distances or higher frequencies, we turn to fibre—or to free space.

Twinax (twin-axial) cable, using two inner conductors surrounded by a common shield, has become dominant in data centres for short-reach high-speed links. SFP28 Direct Attach Copper (DAC) cables carry 25 Gbps over 5 metres using twinax at a fraction of the cost and power of optical transceivers. The 800G MSA's active electrical cable (AEC) standard pushes this to 112 Gbps per lane using PAM4 signalling over twinax, with integrated re-timers in the connector shells compensating for channel loss. The copper-vs-fibre boundary has shifted dramatically: what required fibre at 10 metres in 2020 can be done with copper in 2040, thanks to advances in equalisation (CTLE, DFE) and modulation (PAM4 with FEC).

**Discussion Questions:**
1. Why does differential signalling suppress common-mode noise? Derive the CMRR formula for an ideal differential receiver.
2. Calculate the maximum cable length for a 40GBASE-T link given a channel insertion loss budget of 35 dB at 2 GHz and a Category 8 cable loss of 1.2 dB/m at 2 GHz.
3. Under what circumstances would you choose twinax DAC over active optical cable (AOC) for a 100G data centre link?

---

## Lecture 9: Fibre Optics — Light in the Glass Thread
### Required Reading: Agrawal, G.P. (2039). *Fiber-Optic Communication Systems* (5th ed.). Wiley. Chapters 1–4.

Optical fibre is the closest thing to pure Shannon capacity that physics allows: a single strand of glass thinner than a human hair can carry 400 Gbps per wavelength, and 96 wavelengths per fibre, for a total of 38.4 Tbps per fibre pair—each fibre strand carrying more data than the entire internet did in the year 2000. The secret is total internal reflection: when light travelling in a medium of higher refractive index (the fibre core) strikes the boundary with a lower-index medium (the cladding) at an angle shallower than the critical angle, it reflects perfectly, with zero loss. This traps light inside the core waveguide for tens of kilometres.

Single-mode fibre (SMF), standardised as ITU-T G.652 with a core diameter of 8–10 μm, supports only one propagation mode, eliminating modal dispersion—the spreading of a pulse due to different modes taking different paths. The absence of modal dispersion allows SMF to support bandwidth-distance products exceeding 100 GHz·km, limited primarily by chromatic dispersion (different wavelengths travel at slightly different speeds in glass) and polarisation mode dispersion (PMD, caused by slight asymmetry in the fibre's circular cross-section). Modern SMF achieves attenuation as low as 0.17 dB/km at 1550 nm, the C-band sweet spot where both loss and dispersion are minimised—a triumph of materials science that required reducing hydroxyl (OH⁻) ion contamination to parts per billion.

Multi-mode fibre (MMF), with a 50 μm or 62.5 μm core, supports hundreds of propagation modes. Modal dispersion limits MMF's bandwidth-distance product, making it suitable only for short-reach applications (typically <100 metres for 100G). However, MMF's larger core diameter makes connector alignment vastly easier: a single-mode connector must align two 9 μm cores to within sub-micron precision, while a multi-mode connector can tolerate alignment errors of several microns. This manufacturing tolerance advantage keeps MMF dominant in data-centre server-to-top-of-rack connections where link distances are short and connector density (LC duplex, MPO-12, MPO-16) drives cost.

Dense Wavelength Division Multiplexing (DWDM) multiplies fibre capacity by placing multiple optical carriers at slightly different wavelengths onto the same fibre. The ITU-T G.694.1 DWDM grid defines channels on 100 GHz, 50 GHz, 25 GHz, or 12.5 GHz spacing in the C-band (1530–1565 nm). Flexible-grid (flex-grid) DWDM, standardised in 2035, abandons the fixed grid for variable-width channels that accommodate different baud rates: a 64 Gbaud signal needs ~75 GHz of spectrum, while a 128 Gbaud signal needs ~150 GHz. Modern coherent transceivers (400ZR, 800ZR) pack 400–800 Gbps into a single wavelength using dual-polarisation 16QAM with probabilistic constellation shaping—an optimisation technique where constellation points are transmitted with non-uniform probability to better match the channel's SNR distribution, achieving gains of 0.5–1.0 dB over uniform QAM.

Optical amplification—specifically, the Erbium-Doped Fiber Amplifier (EDFA)—enabled the modern long-haul optical network. An EDFA is a section of optical fibre doped with erbium ions (Er³⁺) that, when pumped with a 980 nm or 1480 nm laser, provides gain across the entire C-band through stimulated emission. Unlike electronic regenerators, which must demultiplex, detect, retime, reshape, and remodulate each individual wavelength (O-E-O conversion), an EDFA amplifies all wavelengths simultaneously in the optical domain (all-optical amplification). A single EDFA can provide 20–25 dB of gain across 40 nm of spectrum, replacing racks of regenerator equipment and enabling transoceanic submarine cables with amplifier spacing of 50–80 km. The 2040 transatlantic Dunant cable (Google) uses 12 fibre pairs with space-division multiplexing, EDFA-amplified repeatered spans, and 400 Gbps per wavelength to achieve 250 Tbps total capacity—enough to transmit the entire contents of the Library of Congress in under 2 seconds.

**Discussion Questions:**
1. Why is chromatic dispersion more problematic for high-baud-rate signals than for low-baud-rate signals?
2. Explain why multimode fibre cannot support DWDM over long distances even if dispersion-compensating techniques are applied.
3. Calculate the total C-band capacity of a 96-channel DWDM system using 800ZR coherent transceivers with flex-grid 75 GHz channel spacing.

---

## Lecture 10: Wireless Transmission — The Unguided Medium
### Required Reading: Rappaport, T.S. (2040). *Wireless Communications: Principles and Practice* (4th ed.). Prentice Hall. Chapters 4–6.

Wireless communication is a paradox: it offers mobility and deployment flexibility that wired media cannot match, yet it is fundamentally less reliable, less secure, and more spectrally constrained. Every wireless link designer battles the four horsemen of the RF apocalypse: path loss (signal weakening with distance), shadowing (obstruction by buildings and terrain), multipath fading (destructive interference from reflected signals arriving out of phase), and interference (other transmitters competing for the same spectrum). Understanding these phenomena—and the techniques that mitigate them—is essential for any network engineer, even if your primary expertise is in wired infrastructure, because the boundary between wired and wireless has dissolved: 5G backhaul runs over fibre; Wi-Fi access points are powered by Ethernet; satellite internet constellations (Starlink, Kuiper, Guowang) compete directly with terrestrial broadband.

Free-space path loss follows the Friis transmission equation: received power = transmitted power × (transmit antenna gain) × (receive antenna gain) × (λ/(4πd))², where λ is wavelength and d is distance. The (λ/4πd)² term means that for every doubling of distance, received power drops by a factor of 4 (6 dB)—and for every doubling of frequency, received power drops by a factor of 4 as well, because shorter wavelengths mean smaller antenna effective aperture for a given physical antenna size. This is why 2.4 GHz Wi-Fi reaches further than 5 GHz Wi-Fi through walls, and why sub-1 GHz bands (LoRa at 868/915 MHz, NB-IoT at 700–900 MHz) are prized for long-range IoT applications: a 900 MHz signal experiences 16 dB less path loss than a 5.8 GHz signal over the same distance.

Multipath fading is the most insidious wireless impairment. A transmitted signal reaches the receiver via multiple paths—direct line-of-sight, reflection from a building, diffraction over a rooftop, scattering from foliage—each with a different delay, amplitude, and phase. When these copies combine at the receiver, they can add constructively (in phase, boosting signal strength) or destructively (180° out of phase, creating a deep fade that drops the signal below the receiver's noise floor). The coherence bandwidth of the channel—the frequency range over which fading is correlated—determines whether the fading is "flat" (all frequency components fade together) or "frequency-selective" (different parts of the signal spectrum experience independent fading). OFDM (Orthogonal Frequency Division Multiplexing), used in Wi-Fi since 802.11a and in 4G/5G, combats frequency-selective fading by dividing the channel into hundreds or thousands of narrow subcarriers, each narrow enough to experience flat fading, and applying adaptive modulation per subcarrier.

Massive MIMO represents the frontier of wireless physical-layer technology. A 5G massive MIMO base station might have 64 or 128 antenna elements, each independently controlled in phase and amplitude, enabling the formation of narrow beams directed at individual user devices. This beamforming concentrates transmitted energy where it is needed, increasing SNR and reducing interference to other users in other directions. The signal processing is formidable—a 64×64 MIMO system requires inverting a 64×64 complex-valued channel matrix every transmission time interval—but dedicated baseband processors (Qualcomm X85, Huawei Balong 6000) handle this in real time. Massive MIMO achieves what is called "favourable propagation": as the number of base station antennas grows large relative to the number of users, the channel vectors between different users become nearly orthogonal, and simple linear processing (matched filtering, zero-forcing) approaches the capacity of optimal non-linear processing.

The wireless spectrum is a finite, regulated resource, and its allocation is the single most political aspect of networking. The ITU's World Radiocommunication Conference (WRC), held every 3–4 years, assigns frequency bands to services (mobile, broadcasting, satellite, aeronautical, radio astronomy, etc.) through international treaty. National regulators (FCC in the US, Ofcom in the UK, PTS in Sweden) implement these allocations through spectrum licencing and auctions. The 2040 WRC-31 allocated the 7–24 GHz band for 6G mobile services, the 71–76 GHz and 81–86 GHz bands for terrestrial wireless backhaul, and reserved 217–230 GHz for experimental sub-terahertz communications—frequencies so high that atmospheric oxygen absorption (a sharp 60 GHz absorption peak) and water vapour absorption limit range to hundreds of metres, but where available bandwidths of 10+ GHz enable data rates unimaginable at lower frequencies.

**Discussion Questions:**
1. Why does a 2.4 GHz signal penetrate walls better than a 5 GHz signal? Explain in terms of the Friis equation and material attenuation.
2. How does OFDM convert a frequency-selective fading channel into multiple flat-fading channels, and why is this beneficial?
3. What physical phenomenon limits the range of 60 GHz and sub-THz communications, and how might this actually be an advantage in dense urban deployments?

---

## Lecture 11: Software-Defined Radio and the Physical Layer in Code
### Required Reading: Tuttlebee, W. (2039). *Software Defined Radio: Enabling Technologies for 6G and Beyond*. Wiley. Chapters 1–5.

For most of communications history, the physical layer was hardware: a modem was a purpose-built integrated circuit with fixed modulation schemes, hardwired error correction, and immutable bandwidth filters. Software-Defined Radio (SDR) changes this by moving modulation, coding, filtering, and even frequency selection into software running on general-purpose processors, FPGAs, or custom DSPs. The implications are profound: a single SDR platform can be a 4G base station in the morning, a Wi-Fi 7 access point in the afternoon, and a spectrum analyser in the evening—all through configuration changes rather than hardware swaps.

The SDR architecture follows a canonical pipeline: antenna → RF front-end (LNA, mixer, filter) → ADC → digital down-converter (DDC) → baseband processor (FPGA/GPU/CPU) → application. The key enabler is the ADC moving ever closer to the antenna. In a traditional superheterodyne receiver, the signal is down-converted through multiple intermediate frequency (IF) stages before digitisation at a relatively low sample rate. A direct-sampling SDR digitises the RF signal directly at the antenna, eliminating analogue down-conversion stages and their associated noise, non-linearity, and component variation. This requires ADCs with sample rates in the tens of gigasamples per second—a capability that became commercially viable around 2025 with the introduction of 64 Gsps, 12-bit ADCs in 28 nm CMOS.

GNU Radio is the dominant open-source SDR framework, providing a graphical signal-processing development environment where blocks (filters, modulators, synchronisers, FEC decoders) are connected into flowgraphs. A complete OFDM receiver can be assembled from GNU Radio blocks in an afternoon; the same receiver can be reconfigured to a different centre frequency, bandwidth, or modulation scheme by changing parameters rather than code. RFNoC (RF Network-on-Chip), an extension to GNU Radio for FPGA-accelerated SDR platforms like the Ettus USRP X440, offloads computationally intensive blocks (FFT, FIR filtering, LDPC decoding) to the FPGA fabric while keeping higher-level protocol processing on the host CPU.

SDR has transformed spectrum monitoring and enforcement. Traditional spectrum analysers are expensive, single-purpose instruments. An SDR-based monitoring network—dozens of $500 RTL-SDR or HackRF receivers distributed across a city, connected to a central spectrum management database—can detect unauthorised transmissions, identify interference sources through time-difference-of-arrival (TDOA) geolocation, and provide real-time spectrum occupancy maps. The FCC's Spectrum Observatory and Ofcom's Spectrum Monitoring Network both rely on SDR infrastructure.

Perhaps the most exciting SDR frontier is its intersection with AI/ML. A neural network trained on millions of labelled RF samples can classify modulation schemes (BPSK, QPSK, 16QAM, 64QAM), estimate SNR, and even demodulate signals without explicit knowledge of the transmitter's parameters—a capability called "blind signal classification" that has applications in spectrum enforcement, cognitive radio (where secondary users dynamically access underutilised spectrum), and electronic warfare. The 2040 DARPA RFMLS (Radio Frequency Machine Learning System) programme demonstrated 99.7% modulation classification accuracy across 24 modulation types at SNR as low as 0 dB—performance that rivals expert human analysts and far exceeds traditional cyclostationary feature-detection methods.

**Discussion Questions:**
1. What are the fundamental trade-offs between implementing a modulation scheme in FPGA fabric versus on a general-purpose CPU in an SDR platform?
2. How does direct RF sampling eliminate the image-rejection problem inherent in superheterodyne receivers?
3. What regulatory challenges does SDR-based cognitive radio pose for traditional static spectrum licencing?

---

## Lecture 12: The Physical Layer of the Future — Quantum, Terahertz, and the Closing of the Spectrum Frontier
### Required Reading: Winzer, P.J., Neilson, D.T., & Chraplyvy, A.R. (2039). "Fiber-optic transmission and networking: the previous 20 years and the next 20 years." *IEEE/OPTICA Journal of Lightwave Technology*, 37(1), 235–268.

We close this course at the frontier where physics imposes hard limits. Shannon's theorem is a law of nature—no more violable than conservation of energy. Every communication channel has a finite capacity, and we are approaching those limits across multiple dimensions. Single-mode fibre capacity is asymptotically approaching the non-linear Shannon limit of approximately 100 Tbps per fibre, constrained by the Kerr non-linearity—the intensity-dependent refractive index of glass that causes cross-phase modulation and four-wave mixing between WDM channels. Multi-core and few-mode fibre (space-division multiplexing) can multiply this by the core/mode count, but each additional spatial channel adds crosstalk that must be managed through MIMO digital signal processing, and the complexity scales quadratically with the number of spatial channels.

At the other end of the spectrum, terahertz communications (100 GHz to 10 THz) represent the last major unexploited spectral frontier. The available bandwidth is staggering—a single 10 GHz channel at 300 GHz could support 100 Gbps with modest modulation—but atmospheric attenuation is severe (100+ dB/km at sea level due to water vapour absorption lines), restricting range to indoor or short outdoor links. The IEEE 802.15.3d standard (2017) defined the first THz wireless standard for point-to-point links at 252–325 GHz, targeting data rates up to 100 Gbps over <100 metres. By 2040, THz transceivers based on InP HBT and CMOS technologies are commercially available for data-centre inter-rack links and wireless virtual-reality headset connections, where the bandwidth demand (8K per eye, 120 Hz, uncompressed = ~120 Gbps for a dual-display VR headset) exceeds what millimetre-wave can provide.

Quantum communication offers a fundamentally different paradigm: instead of encoding information in classical electromagnetic waves, quantum key distribution (QKD) encodes it in single photons whose quantum state cannot be measured without disturbance. The BB84 protocol (Bennett and Brassard, 1984) allows two parties to establish a shared secret key with information-theoretic security—security guaranteed by the laws of quantum mechanics, not by computational hardness assumptions. Practical QKD networks now span hundreds of kilometres over fibre (the Beijing-Shanghai QKD backbone, 2,000 km, operational since 2017) and thousands of kilometres via satellite (Micius satellite, 2016, demonstrated intercontinental QKD). For the network engineer, QKD is not a replacement for conventional encryption but a complementary technology for key distribution in ultra-high-security applications: government communications, financial settlement networks, and critical infrastructure control systems.

The physical layer of 2040 is not defined by a single breakthrough technology but by the intelligent integration of all available media and techniques: fibre for capacity, wireless for mobility, copper for power and legacy access, satellite for global coverage, quantum for security. The network engineer who understands the physics of each—who can calculate the Shannon capacity of a noisy satellite link, read the eye diagram of a 100G PAM4 signal, specify the WDM channel plan for a metro fibre ring, and explain why 4096-QAM works in a Wi-Fi 7 access point but not in a 5G mmWave base station—is the engineer who designs networks that work in the real world, not just in simulation. The Norns weave the threads; our task is to understand the loom.

**Discussion Questions:**
1. Why does the Kerr non-linearity impose a fundamental capacity limit on single-mode fibre that no improvement in modulation or coding can surpass?
2. Compare the security guarantees of QKD with those of post-quantum cryptography (PQC). Under what circumstances would you deploy each?
3. What physical phenomena will ultimately limit data rates in terahertz communications, and how do they differ from the limitations at microwave frequencies?

---

## Final Examination Preparation

The final examination for CN103 consists of two components:

**Part I: Written Examination (60%)** — Choose 4 of the following 8 questions. Each response should be 750–1,200 words, demonstrating both mathematical rigour and practical engineering judgment.

1. A submarine cable system designer must choose between increasing the number of fibre pairs (space-division multiplexing) and increasing the per-wavelength data rate (higher-order QAM with probabilistic shaping). Compare these two approaches in terms of Shannon capacity, cost per bit, power consumption, and failure-mode behaviour. Which would you recommend for a transatlantic cable with a 25-year design life?

2. Derive the Shannon-Hartley capacity for a channel with 320 MHz bandwidth and 30 dB SNR. Now introduce a non-linear amplifier that clips the signal at 3 dB above the average power—how does this affect the effective SNR and the achievable capacity? Propose a modulation scheme and PAPR-reduction technique that mitigates the clipping loss.

3. Compare CRC-32, Reed-Solomon RS(255,239), and LDPC(1944,972) for a link with the following characteristics: BER = 10⁻⁴, latency budget = 100 μs, overhead budget = 10%. For each code, calculate: (a) the probability that a 1500-byte frame contains an undetected error after decoding, (b) the encoding/decoding latency in hardware, and (c) the throughput overhead. Recommend one for a data-centre Ethernet link and justify your choice.

4. A network engineer measures a Category 6A cable at 100 metres and observes an insertion loss of 45 dB at 500 MHz. The 10GBASE-T standard specifies a maximum insertion loss of 35 dB. Explain the discrepancy, propose three possible root causes, and describe the measurement setup that would distinguish between them.

5. Analyse the impact of chromatic dispersion on a 100 Gbps NRZ signal transmitted over 80 km of standard single-mode fibre (G.652, dispersion parameter D = 17 ps/nm·km at 1550 nm). Calculate the pulse broadening and determine whether dispersion compensation is required. If the system is upgraded to 400 Gbps using 56 Gbaud PAM4, how does the dispersion tolerance change?

6. Design a wireless link budget for a 5G mmWave small cell operating at 28 GHz with 800 MHz bandwidth, targeting 4 Gbps peak throughput to a user at 200 metres distance. Account for free-space path loss, atmospheric attenuation (oxygen + water vapour), building penetration loss (15 dB for modern low-E glass), foliage loss (0.4 dB/m for dense urban trees), and rain fade (ITU-R P.838 model for 20 mm/hr rain). Specify the required EIRP and receiver sensitivity.

7. OFDM divides a wideband channel into N narrowband subcarriers. Prove that if N is chosen such that each subcarrier experiences flat fading (subcarrier bandwidth < coherence bandwidth), then a simple one-tap equaliser per subcarrier is sufficient to recover the transmitted symbols. What happens to the peak-to-average power ratio (PAPR) as N increases, and how does this affect the transmitter's power amplifier efficiency?

8. GNU Radio is used to implement a BPSK receiver that operates at 2.4 GHz with 1 MHz bandwidth. The ADC samples at 10 Msps. Trace the signal through the SDR pipeline: antenna → LNA → mixer (LO = 2.3 GHz) → IF filter (1 MHz bandwidth at 100 MHz) → ADC (10 Msps, 12-bit) → digital down-converter → matched filter → symbol timing recovery → decision device. At each stage, identify the signal's centre frequency, bandwidth, and the dominant noise source. Where in this pipeline would you insert a neural network for blind modulation classification, and what additional information would the neural network require?

**Part II: Laboratory Project (40%)** — Using GNU Radio and a USRP B210 SDR platform, implement a complete QPSK transmitter and receiver operating at 915 MHz with 2 MHz bandwidth. Your project must include: (a) a flowgraph with documented signal processing blocks, (b) BER vs. SNR measurements for AWGN channel conditions from 0 dB to 20 dB, compared against the theoretical QPSK BER curve, (c) a demonstration of the receiver's tolerance to carrier frequency offset (±5 kHz) and sample clock offset (±100 ppm), and (d) a 2,000-word report analysing your implementation's performance against theoretical limits and identifying the dominant sources of implementation loss. The project is completed in teams of two and due on the last day of term.

---

*May the Norns weave your signals true, and may your constellations shine bright against the noise.*
