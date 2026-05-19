# Lecture 04: Self-Sovereign Identity — Identity Without Corporate Intermediaries

**AI-7305: Distributed AI as Community Infrastructure**
**Instructor:** Prof. Runa Gridweaver Freyjasdottir | **Date:** September 24 & 26, 2040

---

## The Identity Problem

Every AI system that serves people needs to know something about them. A health AI needs to know your medical history. A learning AI needs to know your educational background. A legal AI needs to know your jurisdiction. An agricultural AI needs to know your soil conditions and crop plans.

In the centralized AI paradigm, identity was solved by the platforms: you logged in with Google, Facebook, or Apple, and the AI accessed whatever data those platforms had accumulated about you. This was convenient. It was also an existential threat to self-determination. When your identity is mediated by a corporation, you are not a person—you are a data subject. The corporation decides what you can prove about yourself, who you can prove it to, and what it costs.

The Cottage Factory needs a different identity infrastructure. Communities need to authenticate their members, verify credentials, and control access to AI services—without relying on corporate identity providers and without creating a new centralized authority that substitutes one gatekeeper for another.

This is the problem self-sovereign identity (SSI) was designed to solve.

## What Self-Sovereign Identity Means

The term "self-sovereign identity" was coined around 2015 by Christopher Allen, who articulated ten principles of self-sovereign identity: existence, control, access, transparency, persistence, portability, interoperability, consent, minimization, and protection. In the context of the Cottage Factory, we can distill these into three core commitments:

### 1. You Own Your Identity

Your identity is not stored on someone else's server. It lives in a digital wallet that you control—a cryptographic facility that you can back up, transfer, and revoke access to at will. No corporation, government, or community node can revoke your ability to prove who you are.

### 2. You Control What You Share

When a Cottage Factory node needs to verify something about you—say, that you're a resident of the community, or that you have a particular medical condition relevant to a diagnostic model—you share only the minimum necessary information. You don't share your entire identity record. You share a **verifiable credential**: a cryptographically signed assertion that proves the specific claim without revealing any additional information.

### 3. You Choose Your Identifiers

You are not assigned an identifier by a central authority. You generate your own decentralized identifiers (DIDs) using cryptographic key pairs. You can create as many or as few identifiers as you need, for as many or as few contexts as you choose. A doctor and a teacher in the same community might use the same underlying identity infrastructure but never know each other's identifiers unless they choose to link them.

## The Technical Architecture

Let's get specific. The SSI infrastructure in the Cottage Factory model uses three core technologies:

### Decentralized Identifiers (DIDs)

A DID is a globally unique identifier that is created, owned, and controlled by its subject. It takes the form `did:method:specific-id-string`. In the Cottage Factory context, we primarily use two DID methods:

- **`did:web`**: A DID that is anchored to a web domain. This is suitable for community nodes and organizations that already have a web presence. For example, the Luleå node's DID is `did:web:nman-lulea.se:node`. The DID document is hosted on the node's own server and contains the public keys and service endpoints necessary for verification.
- **`did:peer`**: A pairwise DID created for private interactions between two parties. This is suitable for individual community members who don't need a globally resolvable identifier. For example, when a resident of Luleå sends a verifiable credential to the node, they use a `did:peer` that is only meaningful within that relationship.

The key insight is that **not everyone needs a globally resolvable DID**. Most community interactions are pairwise or small-group. Global resolvability adds complexity and exposure without adding proportional value. We use `did:peer` for the vast majority of interactions and `did:web` for institutional identities.

### Verifiable Credentials (VCs)

A Verifiable Credential is a tamper-evident digital assertion about a subject, issued by an authority, and held by the subject. The W3C Verifiable Credentials Data Model (which reached v2.1 in 2038) provides the standard.

In the Cottage Factory context, common VCs include:

- **Residency credentials:** Issued by the municipal government, proving that you live in the community served by the node.
- **Age range credentials:** Proving that you are, for example, "over 18" or "over 65" without revealing your exact date of birth.
- **Medical credentials:** Issued by the local clinic, proving specific health conditions relevant to AI-assisted diagnosis without revealing your full medical history.
- **Role credentials:** Issued by community organizations, proving that you hold a particular role (teacher, elder, council member, etc.) that may give you different access levels.
- **Consent credentials:** Proving that you have consented to specific data uses, with the scope and duration of consent embedded in the credential.

The architecture ensures that the credential issuer does not know when or how the credential is used. The credential holder presents it to a verifier only when they choose to, and the verifier learns only the claim in the credential, not any other information about the holder.

### Zero-Knowledge Proofs (ZKPs)

For enhanced privacy, the Cottage Factory SSI layer supports zero-knowledge proofs that allow a community member to prove properties of their credentials without revealing the credentials themselves. For example:

- A resident can prove they are eligible for a health screening AI (because they are over 50 and a resident) without revealing their exact age or their address.
- A farmer can prove they own land in the watershed without revealing the exact parcel or acreage.
- A student can prove they have completed prerequisite coursework without revealing their grades or their institutional affiliation.

ZKPs are built on top of the VC infrastructure using BBS+ signatures, which allow selective disclosure and predicate proofs. The technical details are in Bodén et al. (2037), which is a core reading for this week.

## Identity in Community Context

SSI was originally designed for individual interactions in a global marketplace—you prove things about yourself to strangers, programmatically, without human intermediaries. The Cottage Factory context is different, and the differences matter.

### Community as Trust Anchor

In a global SSI system, trust is established through a "trust registry"—a list of authoritative issuers that verifiers accept. In the Cottage Factory context, the community itself is the trust anchor. The credential issuers that matter are the ones within the community: the municipal government, the clinic, the school, the cooperative grocery. Residents trust these issuers because they know them personally, because they participate in their governance, and because they can hold them accountable directly.

This doesn't mean trust is blind or naive. The community's trust registry is maintained through democratic governance—by the Community AI Council, with input from all residents. If an issuer is compromised or untrustworthy, the community can remove them from the registry through a democratic process. This is very different from trusting Google or the DMV because you have no alternative.

### Identity and Belonging

Here is something the SSI literature rarely addresses: identity is not just about verification. It is also about belonging. When a resident of Luleå uses a residency credential to access the NMAN node, they are not just proving a fact. They are enacting a relationship. They belong to this community. The node serves them because they are a member of the community that owns the node.

This relational aspect of identity is central to the Cottage Factory model. We do not design identity systems to facilitate anonymous transactions between strangers. We design them to support trusted, accountable relationships within communities that know each other.

This has practical implications:

- **Reputation is contextual.** Your reputation in one community does not automatically transfer to another. This is a feature, not a bug. It prevents the consolidation of social capital and protects against the kinds of surveillance that reputation systems enable.
- **Accountability requires identifiability.** Within a community context, members often need to be identifiable to each other—not for surveillance, but for the reciprocal accountability that community life requires. If you use the community's AI services, the community has a legitimate interest in knowing that you are who you say you are.
- **Exit must be possible.** Community identity should be voluntary. If a community's governance becomes oppressive, members must be able to leave and take their credentials with them. This is why self-sovereignty is non-negotiable—even in a community context, identity ultimately belongs to the individual.

## SSI and Federated Learning

The SSI layer is not separate from the federated learning layer—it enables it. Here's how:

- **Authentication for federation rounds.** When nodes participate in a federation round, they authenticate each other using DIDs and VCs. A node can verify that a federation partner is a legitimate community node (not a spoofing attack) without learning anything about that node's internal data or users.
- **Consent management.** Before a community's data is used for a federation round, the SSI layer records consent credentials from the affected community members. This consent is granular (specific model, specific purpose, specific duration) and revocable.
- **Selective disclosure for model governance.** Community AI Councils can use zero-knowledge proofs to verify that a proposed model update meets governance criteria (e.g., "this model was trained on data from at least 5 communities representing at least 3 different linguistic groups") without revealing which communities or which data.
- **Audit trails.** Every federation interaction is logged with verifiable credentials, creating an audit trail that governance bodies can use to verify compliance. This is essential for accountability and for building the trust that makes federation possible.

## Challenges and Open Problems

SSI in the community context faces several challenges that are still being actively researched:

### Key Management

The hardest practical problem in SSI is key management. If you lose your private key, you lose your identity. In a corporate context, this is handled by "social recovery"—a set of trusted contacts who can jointly authorize key rotation. In a community context, this is both easier (community members know each other and can serve as recovery contacts) and harder (the technical literacy required for key management is uneven).

NMAN's solution is the **Community Key Custody Protocol**: each community member's key is divisible into Shamir's Secret Sharing shards, distributed among trusted community members and institutional custodians (the municipal office, the library). Recovery requires a threshold of shards. This isn't perfect—a determined attacker who compromises enough community members could recover the key—but it's far more robust than individual key management and far more sovereign than corporate key escrow.

### Digital Inclusion

Not everyone has a smartphone. Not everyone is comfortable with cryptographic operations. Not everyone reads the language that the SSI interface is written in. These are not edge cases—they represent a significant minority of community members in every Cottage Factory deployment.

The principle here is clear: SSI must not create a digital underclass. If you cannot manage your own identity credentials, the community must provide assisted access—a trusted person who helps you create and manage your wallet, with your informed consent. This is analogous to how communities have always handled literacy: some people read for themselves, some are helped by others, and the community ensures that everyone can participate regardless of their individual skill level.

### Interoperability

Every Cottage Factory deployment needs to interoperate with other deployments (for federation) and with external identity systems (for interactions with national governments, healthcare systems, etc.). The W3C standards for DIDs and VCs provide the technical foundation, but social interoperability—agreeing on what credentials mean, who can issue them, and how disputes are resolved—requires ongoing negotiation between communities.

The Longhouse Protocol's governance layer provides a framework for this negotiation, but it remains one of the hardest practical problems in the space.

---

## Discussion Questions

1. Is there a fundamental tension between self-sovereignty and community belonging? Can you truly own your identity if your access to community AI services depends on community-issued credentials?
2. The Community Key Custody Protocol distributes key shards among trusted community members. What are the privacy implications? How would you feel about your neighbors holding shards of your private key?
3. In a community where everyone knows each other, is privacy even necessary? What are the arguments for and against transparency within a community?
4. How would you design an SSI system for a community that includes both highly technical members and members who have never used a computer?

## Further Reading

- Bodén, M. et al. (2037). "Self-Sovereign Identity in Municipal AI Networks." *IEEE Transactions on Dependable and Secure Computing*.
- Allen, C. (2016). "The Path to Self-Sovereign Identity." *SSIR*.
- W3C Verifiable Credentials Data Model v2.1 (2038). https://www.w3.org/TR/vc-data-model-2.1/
- Nakamura, K. (2039). "Consent as Credential: Managing Data Use Permissions in Community AI." *Proceedings of ACM CCS*.
- CBM Policy Brief #3 (2036). "Identity and Indigenous Sovereignty: Lessons from Cascadia."