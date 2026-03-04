# GraphicalAbstracts

## When to Use
- Single-image summary of an experiment or paper.
- Combining key figure + results + workflow into one visual.
- Conference posters, social media, executive summaries.

## Packages
```python
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
```

## Corresponding Script
`/scripts/infrastructure/graphical_abstracts.py`
- `compose_abstract(title, figures, metrics, path)` — arrange sub-figures + text into one image
- `add_text_panel(fig, ax, text, style)` — formatted text block

## Gotchas
1. **Keep it simple.** Max 4 panels. Too many = unreadable.
2. **High resolution.** Always 300dpi for graphical abstracts.
3. **Consistent fonts.** Use `plt.rcParams["font.family"]` project-wide.
4. **Aspect ratio.** Most journals want 16:9 or square. Check submission guidelines.

## Interpretation Guide
N/A — visual output.

## References
- Nature guidelines: https://www.nature.com/documents/graphical-abstract-guide.pdf
