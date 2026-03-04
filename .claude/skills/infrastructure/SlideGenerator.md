# SlideGenerator

## When to Use
- Presentation decks from experiment results.
- Conference talks, team updates, investor presentations.
- Automated slide generation from results.json + figures.

## Packages
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
```
**Install:** `pip install python-pptx`

## Corresponding Script
`/scripts/infrastructure/slide_generator.py`
- `generate_deck(spec) -> Presentation` — build PPTX from SlideSpec
- `SlideSpec` — dataclass: title, subtitle, slides list
- `SlideContent` — dataclass: title, bullet_points, figure_path, layout

## Gotchas
1. **Layouts matter.** python-pptx uses slide layouts from the template. Index 0 = title, 1 = title+content, 5 = blank, 6 = title only. Check your template.
2. **Image sizing.** Specify `Inches()` explicitly. Default stretches to full slide.
3. **Bullet points, not paragraphs.** Slides should have 3–5 bullets max. One idea per bullet.
4. **Font consistency.** Set font in the slide master, not per-text-box.

## Interpretation Guide
N/A — output skill.

## References
- python-pptx: https://python-pptx.readthedocs.io/
