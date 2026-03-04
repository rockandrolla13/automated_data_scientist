# PyZotero

## When to Use
- Managing bibliography references for reports/wikis.
- Searching your Zotero library for papers related to a hypothesis.
- Auto-generating citation lists for experiment READMEs.

## Packages
```python
from pyzotero import zotero
```
**Install:** `pip install pyzotero`

## Corresponding Script
`/scripts/infrastructure/pyzotero.py`
- `search_library(query, library_id, api_key) -> list[dict]` — search Zotero
- `format_citation(item, style) -> str` — format as APA/Chicago
- `get_bibtex(items) -> str` — export BibTeX block

## Gotchas
1. **API key required.** Set `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID` env vars.
2. **Rate limited.** Don't loop search inside a tight loop.
3. **Group vs user libraries.** `library_type="user"` or `"group"` — get this right.

## Interpretation Guide
N/A — utility. Success = correct citations retrieved and formatted.

## References
- PyZotero: https://pyzotero.readthedocs.io/
- Zotero API: https://www.zotero.org/support/dev/web_api/v3/start
