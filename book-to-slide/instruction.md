Your Workflow Guide: Building a 50-Slide Deck on Causal Discovery

1. Input Format for Each Slide
The most reliable format to feed me is a structured slide spec block. Use this consistently whether you're doing one slide or ten at a time:

```
--- SLIDE N ---
Layout: [title | two-column | bullets | stat-callout | diagram | section-divider]
Title: <slide title>
Body:
  - Point 1
  - Point 2
  - Point 3
Notes: <optional speaker notes or context for me>
Visual hint: <what kind of visual you want — e.g. "DAG diagram", "comparison table", "icon grid">
```
The key discipline: always include the Layout tag. That's what keeps slides consistent across sessions.

2. Keeping Consistency Across Sessions
At the start of your project, define a Style Contract once and paste it at the top of every new session:

```
STYLE CONTRACT
- Theme: [e.g. "Midnight Executive" — navy #1E2761, ice blue #CADCFC, white]
- Header font: Georgia 40pt bold
- Body font: Calibri 15pt
- Slide size: 13.3" x 7.5" (widescreen 16:9)
- Logo/branding: none
- Motif: DAG-inspired network nodes as decorative accents
- Section divider color: navy full-bleed with white title
```
Paste this at the start of every new conversation and I'll match it exactly.

3. Combining Multiple Small Decks
When you have several .pptx files to merge, just upload them all and say:

```
Merge these in order: part1.pptx, part2.pptx, part3.pptx — keep all formatting intact.
```

I'll use a script to concatenate them cleanly. No reformatting will happen as long as all parts were built with the same Style Contract.

4. Saving Work Across Context Window Limits
The "save state" pattern: at the end of each session, ask me:

```
Generate a session resume block for the next conversation.
```

I'll produce something like:

```
RESUME BLOCK — Causal Discovery Deck
Completed: Slides 1–18 (file: causal_part1.pptx)
Style Contract: [copy of your contract above]
Next slide: 19
Topic queue:
  - Slide 19: PC Algorithm steps
  - Slide 20: FCI vs PC comparison
  - ...
```
You paste this at the start of the next session and we continue seamlessly.

5. Suggested Structure for a 50-Slide Causal Discovery Deck
Here's a battle-tested outline you can adapt:

| Section | Slides | Topics |
|---|---|---|
| **1. Intro** | 1–4 | Title, motivation, "why causality?", correlation vs causation |
| **2. Foundations** | 5–12 | DAGs, d-separation, Markov condition, faithfulness, structural equations |
| **3. Discovery Algorithms** | 13–24 | PC, FCI, GES, LiNGAM, NOTEARS — one or two slides per algorithm |
| **4. Constraint-Based Methods** | 25–30 | CI tests, skeleton learning, orientation rules |
| **5. Score-Based Methods** | 31–35 | BIC, MDL, greedy equivalence search |
| **6. Identifiability** | 36–40 | Markov equivalence classes, CPDAG, when is the true graph recoverable? |
| **7. Applications** | 41–46 | Healthcare, economics, ML fairness, time-series causality |
| **8. Challenges & Frontiers** | 47–49 | Hidden confounders, scalability, LLMs + causal discovery |
| **9. Summary** | 50 | Key takeaways, further reading |