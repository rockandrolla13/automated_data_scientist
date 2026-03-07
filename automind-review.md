# Critical Review: AutoMind (2025) vs Our Framework

## What AutoMind Actually Is

AutoMind (Ou et al., 2025, Zhejiang/Ant Group) is a direct successor to DS-Agent that fixes its core weakness — linear iteration — by replacing it with **tree search over the solution space**. Published 14 months after DS-Agent, tested on MLE-Bench (the standard Kaggle competition benchmark for agents).

The architecture has three interlocking components:

### 1. Agentic Knowledgeable Tree Search

The solution space is modeled as a tree T = (N, E). Each node N is a tuple (plan, code, metric). Three actions branch the tree:

```
DRAFT  — generate new solution from scratch (using paper knowledge)
IMPROVE — refine a valid node (using Kaggle tricks)
DEBUG  — fix a buggy node (using error output)
```

The search policy π is stochastic:
- First ensure C_init draft nodes exist (default 5) → creates multiple independent starting points
- Then with probability H_debug, pick a random buggy leaf and debug it
- Then with probability H_greedy, pick the best valid node and improve it
- Otherwise, pick a random valid node and improve it (exploration)

This is essentially a **stochastic beam search** with 3 action types. The key insight: by maintaining 5 independent drafts and probabilistically exploring vs exploiting, it avoids the local-optima trap that kills DS-Agent's linear iteration.

### 2. Expert Knowledge Base (3,237 tricks + papers)

Two retrieval channels:
- **Tricks** (from 455 Kaggle competitions, forum posts) → fed to IMPROVE action
- **Papers** (from KDD/ICLR/NeurIPS/ICML, last 3 years) → fed to DRAFT action

Retrieval uses a **hierarchical labeling system** (11 top-level categories with subcategories), not raw embedding similarity. This is better than DS-Agent's flat cosine similarity because it separates "what domain is this" from "what technique applies."

### 3. Self-Adaptive Coding Strategy

A complexity scorer (1-5 scale) decides per-plan:
- Score ≤ threshold → one-pass code generation (fast, efficient)
- Score > threshold → stepwise decomposition with AST checks and execution feedback per substep

Ablation shows this is critical: without it, valid submission rate drops 27.6% and win rate drops 13.2%. The bottleneck for LLM-generated code is long scripts with error accumulation — stepwise generation catches errors early.

---

## Key Results

| Metric | AIDE (prior SOTA) | AutoMind | Delta |
|--------|-------------------|----------|-------|
| Win rate (avg@3, MLE-Bench) | 0.36 | 0.41 | +5.2% |
| Win rate (best@3, MLE-Bench) | 0.48 | 0.58 | +10.6% |
| Time to match SOTA | 24h | 15h | -37.5% |
| Token cost (to match) | 2.49M | 2.25M | -9.6% |

The efficiency gain is notable: same performance in 60% of the time.

---

## Honest Comparison: What They Have That We Don't

### 1. TREE SEARCH — The Most Important Gap

**AutoMind:** 5 independent drafts, each improvable. Stochastic policy balances explore/exploit. Best node across all branches wins.

**Our framework (after DS-Agent prompts):** Linear iteration on ONE approach. Max 3 revision cycles. If the first approach is wrong, we're stuck.

**Why this matters:** Their best@3 is 20% higher than avg@3. This means the variance across drafts is huge — some drafts find solutions that others miss entirely. By maintaining 5 independent starting points, they capture solutions that linear iteration would never reach.

**Adaptation for us:** We can't run 5 parallel Claude Code sessions. But we CAN generate 3 independent plan.md files before executing any of them, evaluate them conceptually, then execute the most promising 2-3. This is what AUTOMIND PROMPT 1 adds.

### 2. TWO-CHANNEL KNOWLEDGE RETRIEVAL

**AutoMind:** Papers feed DRAFT (initial solution design). Tricks feed IMPROVE (optimization tips).

**Our framework:** No external knowledge retrieval at all. The agent uses whatever's in its training data + our skill .md files.

**Why this matters:** Their ablation shows 11.8% win rate drop without knowledge. The knowledge base acts as a "shortcut" to proven techniques, preventing the agent from wasting iterations rediscovering known methods.

**Adaptation for us:** Our skill .md files ARE the tricks channel (domain-specific, curated). What we're missing is the papers channel — checking if there's a better method in the literature before committing to the first one that comes to mind. AUTOMIND PROMPT 2 adds this.

### 3. STRUCTURED IMPROVE vs DEBUG ACTIONS

**AutoMind:** Improve gets the valid parent + tricks + task description. Debug gets the buggy parent + error output only. Different prompts, different information.

**Our framework:** Revision step (6b) doesn't distinguish between "the method is suboptimal" and "the code crashed." Both trigger the same "diagnose and fix" protocol.

**Why this matters:** Debugging is about fixing errors. Improving is about trying new ideas. Conflating them means the agent might try to "improve" broken code instead of fixing the actual error, or conversely, might just patch an error when a fundamentally different approach is needed.

**Adaptation for us:** Less critical because our scripts are pre-written and tested. The "buggy code" failure mode doesn't apply when you're calling `backtest_engine.backtest()` rather than generating the backtest code from scratch. Our revision failures are almost always metric-based, not error-based.

### 4. EXPLORATION PROBABILITY (H_greedy = 0.8)

**AutoMind:** 80% of the time, improve the best node. 20% of the time, improve a random valid node.

**Our framework:** 100% greedy — always fix the worst metric on the current approach.

**Why this matters:** The 20% exploration finds paths that greedy would miss. In their BELKA case study, the winning solution came from a non-obvious retrieval of MolTrans and DeepDTA papers, not from iterating on the initial gradient boosting approach.

---

## What They DON'T Have (That We Do)

Same structural advantages as in the DS-Agent review:

| Our Advantage | Why It Still Matters |
|---------------|---------------------|
| Hypothesis discipline (H₀/H₁) | They optimize metrics with no scientific question |
| Bias/leakage checklist | 5-item mandatory check before evaluation |
| Temporal split enforcement | Their benchmarks use random splits |
| 54 typed scripts | Their code is generated per-task, ~60% buggy |
| Domain specialization (credit/FI) | They cover generic Kaggle tasks |
| Audit trail (LOG.md + results.json + plan.md) | They track tree nodes but no experiment genealogy |
| Single-touch test protocol | They use validation to select, but no explicit test discipline |
| Transaction cost modeling | Not applicable to image classification benchmarks |

Their 41% win rate against Kaggle humans sounds impressive until you realize that means 59% of humans still beat them. And that's on benchmarks where the evaluation metric is known and unambiguous. In finance, where the metric IS the question (is Sharpe the right metric? Over what horizon? Net of what costs?), their framework would be lost.

---

## The Three Improvements We Should Steal

### 1. Multi-Draft Branching (from tree search)
Not full tree search — that requires running code in parallel containers. But generating 3 independent plans before executing any, then pursuing the most promising 2-3. This is AUTOMIND PROMPT 1.

### 2. Literature Retrieval Before Planning (from knowledge base)
An arXiv search before writing plan.md. Surfaces methods the agent wouldn't think of on its own. This is AUTOMIND PROMPT 2.

### 3. Pre-Planning Retrieval Pipeline (from the overall architecture)
Before any new experiment: case bank → solutions → literature → then plan. This is AUTOMIND PROMPT 3. It institutionalizes the "check before you build" principle.

---

## What NOT to Steal

- **Self-adaptive coding** — we don't generate code, we call scripts
- **AST checking** — irrelevant when scripts are pre-tested
- **24-hour batch execution** — we're interactive
- **3,237 Kaggle tricks** — wrong domain; we'd need credit/FI-specific tricks
- **Hierarchical labeling system** — over-engineering for 54 skills; YAML frontmatter is sufficient
- **Stochastic search policy** — premature; we'd need 20+ experiments logged before the branching probability matters

---

## Summary: Total Changes After Both Papers

| Source | Change | Files | Lines |
|--------|--------|-------|-------|
| DS-Agent | Iteration loop (§4 step 6b) | CLAUDE.md edit | ~10 |
| DS-Agent | plan.md template (§9) | CLAUDE.md edit | ~15 |
| DS-Agent | Extended results.json (§9) | CLAUDE.md edit | ~20 |
| DS-Agent | CaseBank skill + script | 2 new files | ~200 |
| DS-Agent | SolutionRetrieval + solutions/ | 3 new files | ~180 |
| AutoMind | Multi-draft branching (§4 step 6c) | CLAUDE.md edit | ~10 |
| AutoMind | KnowledgeRetrieval skill + script | 2 new files | ~180 |
| AutoMind | Pre-planning retrieval (§4 step 2b) | CLAUDE.md edit | ~5 |
| AutoMind | §6 reference update | CLAUDE.md edit | ~6 |
| **Total** | | **7 new files, 1 new dir, CLAUDE.md edits** | **~625** |

The fundamental lesson from both papers, stated plainly: **iteration beats single-shot, diversity beats iteration, and memory beats amnesia.** DS-Agent proved iteration. AutoMind proved diversity. We already have the scientific rigor they both lack. Adding their search and retrieval mechanisms to our hypothesis discipline would be the strongest combination in this space.
