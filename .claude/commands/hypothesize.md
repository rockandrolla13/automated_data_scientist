---
name: hypothesize
description: Generate 5 testable hypotheses with H₀/H₁, named scripts, and workflow tags. Waits for user selection.
---

Generate hypotheses for: $ARGUMENTS

## Steps
1. Check /data/ for available cleaned datasets. If none: suggest running /eda first.
2. Run pre-planning retrieval silently:
   - Case bank: any prior experiments on this topic?
   - Solutions: any matching recipes?
   - Literature: any relevant papers?
3. Generate exactly 5 hypotheses. For each:
   - Number (1-5), with ⭐ prefix
   - H₀ (null) and H₁ (alternative), clearly stated
   - Scripts: name the exact .py files from /scripts/ that would be called
   - Skills: name the exact .md files from /.claude/skills/ to read first
   - Workflow tag: (Workflow A), (Workflow B), or (Workflow C) per §10
4. Print all 5.
5. **STOP.** Print: "Star the numbers you want me to execute."
6. Do NOT execute anything. Wait for user selection.

$ARGUMENTS is a research question or topic.
Example: /hypothesize alpha in IG credit spreads
