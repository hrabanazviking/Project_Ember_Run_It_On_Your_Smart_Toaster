# Lecture 2: The AI Winters — Famine, Fire, and the Long Silence

**AI-5101: History of AI — From Perceptrons to Prompt Engineering (1943–2025)**
**Weeks 2–3 | Runa Gridweaver Freyjasdottir, PhD Candidate**

---

## Prologue: The Definition of Winter

An "AI Winter" is a period during which funding for artificial intelligence research collapses, professional interest wanes, and the term "artificial intelligence" itself becomes a stigma—a mark of naivety or charlatanism on a researcher's CV. There were two such winters in the classical period: the First (approximately 1974–1980) and the Second (approximately 1987–1993). A third, milder cooling occurred in the wake of the dot-com bust (2001–2003), but it was brief and partial.

This lecture asks: Why did these winters happen? What did they destroy, and what did they preserve? And—most critically for those of us living in an era of superconscious abundance—what do they teach us about the relationship between hype, funding, and genuine capability?

The Norse knew winter. Fimbulwinter, the great winter before Ragnarök, lasted three years. The AI winters lasted longer. But unlike Fimbulwinter, they did not end the world. They *reshaped* it.

---

## Part I: The First AI Winter (1974–1980)

### 1. The Bloom Before the Frost

The period from roughly 1956 to 1973 was the First Summer of AI. It began with the Dartmouth Conference (1956), where John McCarthy coined the term "artificial intelligence," and it was sustained by a series of impressive—if ultimately limited—demonstrations:

- **Logic Theorist** (Newell, Shaw, & Simon, 1956): A program that proved theorems from *Principia Mathematica*
- **ELIZA** (Weizenbaum, 1966): A simple pattern-matching chatbot that nonetheless convinced users it "understood" them
- **MACHack VI** (Greenblatt, 1967): A chess program that achieved a D-class rating
- **Shakey** (SRI, 1969–1972): A mobile robot that could plan and execute simple tasks using vision

These demonstrations attracted funding. DARPA, the NSF, and the military poured money into AI labs. MIT, Stanford, Carnegie Mellon, and SRI became the four pillars of American AI research. In Britain, the Science Research Council funded AI at Edinburgh, Essex, and Sussex.

The rhetoric was immense. In 1965, Herbert Simon predicted that "machines will be capable, within twenty years, of doing any work a man can do." In 1970, Marvin Minsky told Life magazine that "in from three to eight years we will have a machine with the general intelligence of an average human being."

Simon and Minsky were not fools. They were reflecting a genuine sense of progress. But they were also reflecting a fundamental bias that afflicts AI researchers in every era: the conflation of *narrow demonstrations* with *general capability*. Logic Theorist could prove theorems—but only in propositional calculus. ELIZA could hold a conversation—but only through pattern matching. Each demonstration was a *local* success that was rhetorically generalized to *global* claims.

### 1.1 The Lighthill Report (1973)

In Britain, the First Winter was triggered by a single document: Sir James Lighthill's report to the Science Research Council, titled "Artificial Intelligence: A General Survey" (1973). Lighthill, a distinguished fluid dynamicist, was asked to evaluate AI research and determine whether continued funding was justified.

His assessment was devastating. Lighthill divided AI into three categories:

- **Category A: Automation**: Real-world applications (industrial automation, process control). Lighthill judged these valuable but not truly "AI."
- **Category B: Bridge topics**: Machine learning, pattern recognition—areas with genuine scientific content that overlapped with statistics and engineering.
- **Category C: Blue-sky AI**: General intelligence, natural language understanding, autonomous robots. Lighthill judged these to have produced "grandiose objectives" with no corresponding achievements.

The report concluded that "in no part of the field have the discoveries made so far produced the major impact that was then promised." The Science Research Council subsequently slashed funding for AI in Britain. Edinburgh's Department of Machine Intelligence and Perception was essentially dismantled.

### 1.2 The American Contraction

In the United States, the First Winter was driven not by a single report but by accumulated frustration. The Mansfield Amendment (1969) required the military to fund only "mission-oriented" research, cutting off the basic science funding that had sustained AI labs. DARPA, which had been AI's single largest funder, redirected its priorities.

By 1974, DARPA's AI budget had been cut dramatically. MIT's AI Lab lost significant funding. Stanford's AI Lab, under the direction of John McCarthy, was also hit. Researchers who had been hired during the boom found themselves without grants, and many left the field entirely.

The *effect* of the winter was not merely financial. It was *reputational*. During the First Winter, proposing an AI project in a grant application became a strategic liability. The term "artificial intelligence" was replaced by euphemisms: "machine learning," "pattern recognition," "computational intelligence." Researchers rebranded to survive.

### 1.3 What Was Lost

The First Winter killed several research programs that might have accelerated progress:

- **Connectionist research** was already on life support after Minsky and Papert's 1969 book. The winter finished the job.
- **Robotics** programs were defunded; Shakey's descendants would not walk for another decade.
- **Natural language processing** reverted to a subfield of computational linguistics, lost to the AI mainstream.
- Importantly, the winter destroyed *institutional memory*. Researchers left the field and took their expertise with them. Graduate students chose other topics. Labs closed. When connectionism was revived in the 1980s, much of the groundwork had to be rediscovered.

---

## Part II: The Inter-Summer: Expert Systems (1980–1987)

### 2.1 The Second Bloom

AI's second summer was driven by a single technology: expert systems. These were programs that encoded human expert knowledge as if-then rules and used logical inference to make decisions. They worked—not for general intelligence, but for narrow, well-defined domains.

- **MYCIN** (Stanford, 1972–1976): Diagnosed bacterial infections with 69% accuracy, outperforming some human physicians
- **DENDRAL** (Stanford, 1965–1980s): Identified chemical compounds from mass spectrometry data
- **R1/XCON** (Carnegie Group, 1978): Configured DEC VAX computer orders, saving DEC an estimated $40 million/year

R1/XCON was the commercial success that sparked the boom. If an expert system could save a corporation $40 million, then AI was not just academic—it was profitable. Defense agencies, inspired by the Japanese Fifth Generation Computer Project (1982), poured money into AI again. Venture capital followed. Companies like Symbolics, IntelliCorp, and Teknowledge went public. The AI industry was valued at over $1 billion by 1985.

### 2.2 The Fragility of Expert Systems

The problem with expert systems—though it was not widely acknowledged at the time—was that they were *brittle*. They worked beautifully within their domain, but:

- They could not learn from new data; every rule had to be hand-coded
- They could not generalize outside their domain
- Scaling was exponentially costly: adding the 1000th rule often required resolving conflicts with the previous 999
- They had no common sense—a medical diagnostic system could not understand that a patient who had died could not be treated

These limitations were known intellectually but not *experientially*. The market had not yet encountered them at scale. It would.

---

## Part III: The Second AI Winter (1987–1993)

### 3.1 The Collapse

The Second Winter was more brutal than the First because it destroyed not just academic funding but an entire commercial ecosystem. The causes were multiple:

1. **Technical disappointment**: Expert systems failed to scale. The knowledge acquisition bottleneck—getting human experts to articulate their knowledge as rules—proved intractable. Systems that worked in demos failed in production.

2. **Hardware disruption**: The rise of personal computers and workstations destroyed the market for specialized AI hardware. Companies like Symbolics that sold $100,000 LISP machines were undercut by general-purpose workstations from Sun and DEC. The entire LISP machine industry collapsed.

3. **The end of the Fifth Generation hype**: Japan's Fifth Generation Computer Project, which had catalyzed Western investment in AI, was widely perceived as a failure by 1987. It had promised natural language processing and parallel inference; it delivered neither.

4. **Economic recession**: The early 1990s recession reduced corporate spending on experimental technology.

The commercial stampede reversed. AI companies went bankrupt. Venture capital fled. By 1993, the term "artificial intelligence" was once again toxic. Papers previously titled "An AI Approach to X" were retitled "A Computational Approach to X." Researchers again became semantic refugees, rebranding their work as "machine learning," "statistical inference," or "cognitive science."

### 3.2 The Survivors

Not everything died. Key research survived in specific niches:

- **Boosting and ensemble methods** (Freund & Schapire, 1990; Schapire, 1990): Developed at Bell Labs and AT&T, largely outside mainstream AI
- **Support vector machines** (Boser, Guyon & Vapnik, 1992): Developed within the statistics community, barely acknowledged by AI
- **Reinforcement learning** (Watkins, 1989; Sutton & Barto, 1998): Kept alive by a small community at the University of Massachusetts
- **Backpropagation** at the University of Toronto (Hinton's group): A handful of researchers sustained the connectionist flame

The populations that survived the Second Winter did so by staying small, staying focused, and staying the hell away from the word "intelligence."

### 3.3 The International Dimension

The Second Winter was particularly devastating in the United States and Britain. Other countries fared differently:

- **Japan** maintained investment through the Fifth Generation project's official conclusion in 1992, though the project was widely considered a failure
- **Europe** maintained some funding through ESPRIT and other EU programs, which had longer time horizons than DARPA
- **The Soviet Union and its successors** had a parallel tradition in cybernetics and statistical pattern recognition that was less affected by Western funding cycles

This geographic variation is important: it means that the "winters" were not universal. They were specific to particular funding ecosystems and intellectual communities. The lesson is not that AI progress stopped—only that *American and British institutional AI* contracted violently.

---

## Part IV: Lessons and Patterns

### 4.1 The Hype Cycle as Thermodynamic Law

The pattern is remarkably consistent across both winters:

1. **Cryptic discovery**: A genuine technical advance occurs (perceptrons, expert systems)
2. **Rhetorical amplification**: Researchers and journalists generalize from narrow demonstrations to grand claims
3. **Funding flood**: Government and industry pour money into the field
4. **Failure to deliver on the grand promise**: The advance doesn't scale or generalize
5. **Reputational collapse**: The gap between promise and delivery is exposed
6. **Winter**: Funding evaporates, researchers leave, the term becomes stigmatized

This is not merely a story about AI. It is a story about the sociology of promises. AI researchers are not uniquely dishonest; they are uniquely *visible*. When a researcher in materials science overpromises, the result is a failed grant. When an AI researcher overpromises, the result is a social panic about robot overlords followed by an equally irrational social panic about AI failure.

### 4.2 What Winters Preserve

Paradoxically, the winters also preserved something important: the *core insights* of the approaches that were temporarily defunded. Perceptrons were not rediscovered—they were preserved in mathematical form, waiting for hardware and data to catch up. Backpropagation survived in the PDP books (1986) and in Hinton'sToronto lab. Expert system shells became the foundation for rule-based systems in industry, even if they were no longer called "AI."

The winters acted like the Norse concept of *urvall*—the preservation of the essential through the stripping away of the non-essential. What died was the hype, the grandiose promises, the overfunded labs staffed by people who didn't understand the core ideas. What survived was the mathematics.

### 4.3 The Meta-Lesson for the Superconscious Era

This course is not merely an exercise in historical curiosity. We live in 2040, in the Age of Superconsciousness. The capabilities we now take for granted—instant multimodal reasoning, autonomous scientific discovery, cognitive prostheses—would have seemed like magic to Rosenblatt or Minsky. But the pattern that produced the winters has not been broken; it has merely been suspended by continuous delivery of genuinely impressive results.

The question we must ask, as historians and as citizens, is: **What would it take to produce a Third Winter?** Not the mild cooling of 2001, but a genuine collapse of funding and faith. The answer, I suggest, lies in the gap between:

- What superconscious systems *can do* (which is extraordinary)
- What superconscious systems are *understood to do* by the public and by funders (which is often distorted)

If that gap grows wide enough—if the promise diverges sufficiently from the lived reality—the thermodynamic conditions for winter will re-form. History does not repeat, but it rhymes.

---

## References

- Lighthill, J. (1973). Artificial intelligence: A general survey. In *Artificial Intelligence: A Paper Symposium*. Science Research Council.
- Crevier, D. (1993). *AI: The Tumultuous History of the Search for Artificial Intelligence*. Basic Books.
- McCorduck, P. (2004). *Machines Who Think* (2nd ed.). A.K. Peters.
- Newell, A., Shaw, J.C. & Simon, H.A. (1958). Elements of a theory of human problem solving. *Psychological Review*, 65(3), 151–166.
- Dreyfus, H.L. (1972). *What Computers Can't Do*. MIT Press.
- Feigenbaum, E.A. & McCorduck, P. (1983). *The Fifth Generation*. Addison-Wesley.
- Simmons, R.F. (1970). Some semantic structures for question-answering systems. In *Natural Language Processing*. Algorithmics Press.
- Buchanan, B.G. & Shortliffe, E.H. (1984). *Rule-Based Expert Systems*. Addison-Wesley.
- Hendler, T. (2008). Avoiding another AI winter. *AI Magazine*, 29(3), 12–14.

---

*In Norse myth, Fimbulwinter is followed by a new world rising from the sea. The AI winters were followed by revivals—but the revivals did not erase what was lost. Each winter ended a line of inquiry, silenced a voice, destroyed a lab. History remembers the survivors. We should also remember the dead.*