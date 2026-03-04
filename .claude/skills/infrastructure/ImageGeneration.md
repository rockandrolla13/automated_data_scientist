# ImageGeneration

## When to Use
- Scientific diagrams, schematics, conceptual illustrations.
- Workflow diagrams that are hard to draw programmatically.
- Graphical abstracts for papers or presentations.

## Packages
```python
# Uses LLM image generation APIs or local tools
# matplotlib for programmatic diagrams
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
```

## Corresponding Script
`/scripts/infrastructure/image_generation.py`
- `generate_workflow_diagram(steps, path)` — matplotlib-based step diagram
- `generate_schematic(spec, path)` — box-and-arrow diagram from spec
- `generate_image_prompt(description) -> str` — format prompt for AI image generation

## Gotchas
1. **AI-generated images need review.** Always inspect for accuracy before publication.
2. **Matplotlib diagrams are reproducible.** Prefer them for anything that must be version-controlled.
3. **Resolution matters.** Generate at 300dpi for print, 150dpi for screen.
4. **Style consistency.** Use the same color palette across all figures in a report.

## Interpretation Guide
N/A — creative output. Success = clear, accurate, publication-appropriate visual.

## References
- Matplotlib patches: https://matplotlib.org/stable/gallery/shapes_and_collections/
