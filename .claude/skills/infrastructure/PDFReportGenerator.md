# PDFReportGenerator

## When to Use
- Final deliverable reports from experiments.
- Structured documents: title, abstract, methodology, results, appendix.
- LaTeX quality without writing LaTeX (uses Jinja2 templates + weasyprint or fpdf2).

## Packages
```python
from jinja2 import Template
from fpdf import FPDF  # fpdf2
```
Alternative: `weasyprint` for HTML→PDF, or raw LaTeX via `subprocess`.

## Corresponding Script
`/scripts/infrastructure/pdf_report_generator.py`
- `generate_report(spec) -> str` — generates PDF at given path
- `ReportSpec` — dataclass: title, author, date, sections, figures, metrics

## Gotchas
1. **fpdf2 is lightweight** but limited on complex layouts. Use weasyprint for CSS-styled reports.
2. **Figures must be pre-generated.** Generate with PublicationFigures first, then embed paths.
3. **LaTeX requires a TeX installation.** Only use if the environment has `pdflatex`.
4. **Unicode in fpdf2** needs `add_font()` with a TTF. Default fonts are Latin-1 only.

## Interpretation Guide
N/A — output skill. Success = well-formatted PDF with all sections, figures, metrics.

## References
- fpdf2: https://pyfpdf.github.io/fpdf2/
- WeasyPrint: https://weasyprint.org/
- Jinja2: https://jinja.palletsprojects.com/
