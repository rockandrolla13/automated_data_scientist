---
name: report
description: Generate stakeholder deliverables from a completed experiment — figures, PDF, slides, notebook.
---

Generate report for: $ARGUMENTS

$ARGUMENTS is a hypothesis ID (e.g., HYP-001) or experiment folder name.

## Steps
1. **Load** — Read experiments/<folder>/results.json and README.md.
   - If experiment not found or no results.json: STOP with error.

2. **Figures** — Read skill: .claude/skills/infrastructure/PublicationFigures.md
   - Generate key figures via scripts/infrastructure/publication_figures.py
   - Save to /artifacts/figures/

3. **Report** — Read skill: .claude/skills/infrastructure/PDFReportGenerator.md
   - Generate markdown or PDF report via scripts/infrastructure/pdf_report_generator.py
   - Structure: Conclusion first → Evidence → Method → Appendix
   - Save to /artifacts/reports/

4. **Optional** — If user asks, also generate:
   - Slides via /scripts/infrastructure/slide_generator.py
   - Dashboard via /scripts/infrastructure/dashboard_generator.py
   - Polished notebook → /notebooks/

5. **Summary** — Print: deliverables created, paths, what each contains.

Write for a PM audience: lead with conclusion, support with 4 canonical metrics, include 1-2 key figures. No metric soup.
