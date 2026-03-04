"""pdf_report_generator — Generate PDF reports from experiment results."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ReportSection:
    title: str
    content: str  # Markdown-ish text
    figures: list[str] = field(default_factory=list)  # paths to PNGs


@dataclass
class ReportSpec:
    title: str
    author: str
    date: str
    hypothesis_id: str
    abstract: str
    sections: list[ReportSection]
    metrics: dict | None = None


def generate_report(spec: ReportSpec, output_path: str = "report.pdf") -> str:
    """Generate PDF from ReportSpec using fpdf2."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)

    # Title page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 40, spec.title, ln=True, align="C")
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, f"Author: {spec.author}", ln=True, align="C")
    pdf.cell(0, 10, f"Date: {spec.date}", ln=True, align="C")
    pdf.cell(0, 10, f"Hypothesis: {spec.hypothesis_id}", ln=True, align="C")

    # Abstract
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Abstract", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, spec.abstract)

    # Metrics summary
    if spec.metrics:
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Key Metrics", ln=True)
        pdf.set_font("Courier", "", 11)
        for k, v in spec.metrics.items():
            pdf.cell(0, 7, f"  {k}: {v}", ln=True)

    # Sections
    for section in spec.sections:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, section.title, ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, section.content)

        for fig_path in section.figures:
            if Path(fig_path).exists():
                pdf.ln(5)
                pdf.image(fig_path, w=170)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(output_path)
    return output_path


if __name__ == "__main__":
    spec = ReportSpec(
        title="IG Spread Momentum Analysis",
        author="AgentDS",
        date="2025-03-03",
        hypothesis_id="HYP-001",
        abstract="We test whether 5-day IG spread momentum predicts excess returns.",
        sections=[
            ReportSection(title="Methodology", content="GARCH(1,1) fitted to spread changes..."),
            ReportSection(title="Results", content="OOS Sharpe = 0.82, t = 1.91..."),
        ],
        metrics={"oos_sharpe": 0.82, "t_stat": 1.91, "max_drawdown": -0.043, "ir": 0.61},
    )
    path = generate_report(spec, "../../artifacts/reports/hyp_001_report.pdf")
    print(f"Report: {path}")
