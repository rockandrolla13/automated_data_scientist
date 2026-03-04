"""image_generation — Programmatic scientific diagrams and AI image prompts."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path


def generate_workflow_diagram(
    steps: list[str],
    title: str = "Workflow",
    path: str | None = None,
    colors: list[str] | None = None,
) -> plt.Figure:
    """Horizontal step-by-step workflow diagram."""
    n = len(steps)
    colors = colors or plt.cm.Set3(np.linspace(0, 1, n))

    fig, ax = plt.subplots(figsize=(max(n * 2.5, 8), 3))
    ax.set_xlim(-0.5, n * 2.5)
    ax.set_ylim(-1, 2)
    ax.axis("off")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

    for i, (step, color) in enumerate(zip(steps, colors)):
        x = i * 2.5
        box = FancyBboxPatch((x, 0), 2, 1.2, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor="gray", linewidth=1.5)
        ax.add_patch(box)
        ax.text(x + 1, 0.6, f"{i+1}. {step}", ha="center", va="center",
                fontsize=9, fontweight="bold", wrap=True)

        if i < n - 1:
            ax.annotate("", xy=(x + 2.3, 0.6), xytext=(x + 2.0, 0.6),
                        arrowprops=dict(arrowstyle="->", color="gray", lw=2))

    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    return fig


def generate_schematic(
    boxes: list[dict],  # [{"label": "A", "x": 0, "y": 0}, ...]
    arrows: list[tuple],  # [("A", "B"), ...]
    title: str = "",
    path: str | None = None,
) -> plt.Figure:
    """Box-and-arrow schematic from spec."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")
    ax.set_title(title, fontsize=14, fontweight="bold")

    box_positions = {}
    for b in boxes:
        box = FancyBboxPatch((b["x"], b["y"]), 2, 0.8, boxstyle="round,pad=0.1",
                              facecolor="lightblue", edgecolor="navy", linewidth=1.5)
        ax.add_patch(box)
        ax.text(b["x"] + 1, b["y"] + 0.4, b["label"], ha="center", va="center", fontsize=10)
        box_positions[b["label"]] = (b["x"] + 1, b["y"] + 0.4)

    for src, dst in arrows:
        if src in box_positions and dst in box_positions:
            ax.annotate("", xy=box_positions[dst], xytext=box_positions[src],
                        arrowprops=dict(arrowstyle="->", color="gray", lw=1.5))

    ax.autoscale()
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
        plt.close(fig)
    return fig


def generate_image_prompt(description: str, style: str = "scientific") -> str:
    """Format a structured prompt for AI image generation."""
    return (
        f"Scientific illustration: {description}. "
        f"Style: clean, professional {style} diagram. "
        f"White background, high contrast, publication quality. "
        f"No text labels (those will be added in post-processing)."
    )


if __name__ == "__main__":
    steps = ["Data Audit", "EDA", "Hypothesis", "Model", "Evaluate", "Report"]
    generate_workflow_diagram(steps, title="Research Pipeline", path="figures/workflow.png")
    print("Workflow diagram saved.")
