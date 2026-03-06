# Architecture Review: Global Discoverability for AgentDS

**Date:** 2026-03-06
**Objective:** Make AgentDS skills globally discoverable and accessible across all projects.

---

## 1. Problem Statement

### Current Pain Points

1. **Unknown unknowns** — Skills exist but users don't know they exist. Work gets reinvented.
2. **Project-scoped** — Skills live in one repo. New projects can't access them.
3. **No search** — 72 skills across 4 categories with no way to query "what helps with X?"
4. **Manual sync** — Adding a skill requires editing CLAUDE.md §6 by hand.

### Success Criteria

- [ ] Any project can access AgentDS skills
- [ ] `/find <query>` returns relevant skills
- [ ] Agents surface relevant skills before starting work
- [ ] Single source of truth (develop once, use everywhere)

---

## 2. Solution: Global Skill Registry

### Architecture Overview

```
Development (this repo)              Global (symlinked)
───────────────────────              ──────────────────
automated_data_scientist/            ~/.claude/
├── .claude/                         ├── skills/agentds/ ──→ symlink
│   ├── skills/         ←──────────────┘
│   ├── commands/       ←────────────┬── commands/agentds/
│   └── agents/         ←────────────┴── agents/agentds/
├── scripts/            ←──────────── pip install -e ./scripts
└── registry.yaml
```

**Key insight:** Develop locally, symlink globally. Git tracks source, symlinks provide access.

---

## 3. Registry Schema

**Location:** `.claude/skills/registry.yaml`

```yaml
pack: agentds
version: "1.0"
global: true

skills:
  - id: GARCH
    category: ml_stats
    script: agentds.ml_stats.garch

    tags:
      - volatility
      - time-series
      - forecasting
      - risk
      - conditional-variance

    keywords:
      - heteroskedasticity
      - vol clustering
      - ARCH
      - variance targeting

    use_when: >
      Modeling time-varying volatility, testing for volatility
      clustering, or when returns show fat tails.

    related:
      - RegimeDetection
      - ARIMA
      - ConformalPrediction

    not_for:
      - static volatility
      - implied vol from options
```

### Tag Taxonomy

| Domain | Tags |
|--------|------|
| Method | regression, classification, clustering, forecasting, simulation, optimization, causal |
| Asset | credit, equity, rates, fx, crypto |
| Data | time-series, cross-sectional, panel, graph |
| Task | risk, alpha, hedging, pricing, valuation, cleaning |

---

## 4. Discovery Triggers

### Trigger 1: Proactive (Task Start)

Agent extracts goal → queries registry → surfaces skills before planning.

```
User: "Find alpha in IG credit spreads"

Agent:
┌─────────────────────────────────────────────────────┐
│ Relevant skills for this task:                      │
│ • CreditSignals — spread momentum, carry signals    │
│ • SpreadDecomposition — isolate credit vs rate      │
│ • GARCH — vol clustering in spreads                 │
│ • RegimeDetection — condition on market state       │
└─────────────────────────────────────────────────────┘
```

### Trigger 2: On-Demand (`/find`)

```
/find volatility forecasting

Results:
1. GARCH (ml_stats)                    score: 0.89
   → Modeling time-varying volatility
   Related: RegimeDetection, ARIMA

2. ConformalPrediction (ml_stats)      score: 0.71
   → Prediction intervals that adapt
```

### Trigger 3: Interception (When Coding)

| Code pattern | Suggest |
|--------------|---------|
| `arch_model(` | GARCH.md |
| `KMeans(` | Clustering.md |
| `DoWhy` | CausalEffect.md |

Advisory only — instruction in agent prompts.

---

## 5. Global Directory Structure

```
~/.claude/
├── skills/
│   └── agentds/ ─────────→ symlink to repo/.claude/skills/
├── commands/
│   └── agentds/ ─────────→ symlink to repo/.claude/commands/
└── agents/
    └── agentds/ ─────────→ symlink to repo/.claude/agents/

~/path/to/automated_data_scientist/    (this repo)
├── .claude/
│   ├── skills/
│   │   ├── registry.yaml
│   │   ├── credit_fi/
│   │   ├── ml_stats/
│   │   ├── quant_finance/
│   │   └── infrastructure/
│   ├── commands/
│   └── agents/
├── scripts/                           (pip package)
│   ├── setup.py
│   ├── credit_fi/
│   ├── ml_stats/
│   ├── quant_finance/
│   └── infrastructure/
└── CLAUDE.md
```

---

## 6. Integration Points

### 6.1 Agent Instructions

Add Step 0 to all agents:

```markdown
## Protocol
0. **Discover** — Query registry for relevant skills before any work.
1. Every experiment starts with H₀/H₁...
```

### 6.2 CLAUDE.md Updates

**§3 Mode B:** Add skill discovery step
**§4 Workflow:** Query registry during hypothesize step
**§6:** Auto-generate from registry (or reference registry)

### 6.3 New Script

`scripts/infrastructure/skill_registry.py`:

```python
@dataclass
class SkillEntry:
    id: str
    category: str
    script: str
    tags: list[str]
    keywords: list[str]
    use_when: str
    related: list[str]
    not_for: list[str]

def load_registry() -> list[SkillEntry]
def search(query: str, top_k: int = 5) -> list[SkillMatch]
def get_related(skill_id: str) -> list[str]
def suggest_for_goal(goal: str) -> list[SkillMatch]
def validate_registry() -> list[str]
```

### 6.4 New Command

`.claude/commands/find.md`:

```markdown
---
name: find
description: Search skills by keyword, tag, or natural language query.
---

Search for: $ARGUMENTS

1. Load registry from ~/.claude/skills/agentds/registry.yaml
2. Match query against tags, keywords, use_when
3. Return top 5 matches with scores and related skills
```

---

## 7. Extension Patterns

### 7.1 Adding New Skills

1. Create `.claude/skills/<category>/<Name>.md`
2. Create `scripts/<category>/<name>.py`
3. Add entry to `registry.yaml`
4. Run `skill_registry.py --validate`

### 7.2 Path to Semantic Search

Registry enables future upgrade:

```python
# Future: compute embeddings from registry text
embeddings = encode([f"{s.use_when} {s.tags}" for s in skills])
# Hybrid: keyword match + embedding similarity
```

### 7.3 Skill Composition

```yaml
- id: SignalResearch
  type: workflow
  composes: [EDA, SignalConstruction, BacktestEngine]
```

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Skills with registry entry | 100% (72/72) |
| `/find` returns relevant result | >80% of queries |
| Unknown-unknown incidents | Reduced (qualitative) |
| New project setup time | <5 min (symlink + pip) |

---

## 9. References

- CLAUDE.md §1-11 (current architecture)
- Von Luxburg (2007) — spectral clustering (for future semantic similarity)
- Internal: CaseBank, SolutionRetrieval patterns
