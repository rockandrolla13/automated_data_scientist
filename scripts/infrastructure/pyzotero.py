"""pyzotero — Zotero library search and citation formatting."""

import os


def search_library(
    query: str,
    library_id: str | None = None,
    api_key: str | None = None,
    library_type: str = "user",
    limit: int = 10,
) -> list[dict]:
    """Search Zotero library. Returns list of item dicts."""
    from pyzotero import zotero

    lid = library_id or os.environ.get("ZOTERO_LIBRARY_ID")
    key = api_key or os.environ.get("ZOTERO_API_KEY")
    if not lid or not key:
        raise ValueError("Set ZOTERO_LIBRARY_ID and ZOTERO_API_KEY env vars")

    zot = zotero.Zotero(lid, library_type, key)
    items = zot.items(q=query, limit=limit, sort="relevance")

    results = []
    for item in items:
        data = item.get("data", {})
        results.append({
            "key": data.get("key", ""),
            "title": data.get("title", ""),
            "authors": [
                f"{c.get('lastName', '')}, {c.get('firstName', '')}"
                for c in data.get("creators", [])
            ],
            "date": data.get("date", ""),
            "abstract": data.get("abstractNote", "")[:200],
            "item_type": data.get("itemType", ""),
        })
    return results


def format_citation(item: dict, style: str = "apa") -> str:
    """Format item dict as citation string."""
    authors = "; ".join(item.get("authors", [])[:3])
    if len(item.get("authors", [])) > 3:
        authors += " et al."
    title = item.get("title", "Untitled")
    year = item.get("date", "n.d.")[:4]

    if style == "apa":
        return f"{authors} ({year}). {title}."
    return f"{authors}, \"{title},\" {year}."


def get_bibtex(items: list[dict]) -> str:
    """Generate BibTeX block from item list."""
    entries = []
    for item in items:
        key = item.get("key", "unknown")
        first_author = item["authors"][0].split(",")[0] if item.get("authors") else "Unknown"
        year = item.get("date", "")[:4]
        entry = (
            f"@article{{{first_author}{year}_{key},\n"
            f'  title = {{{item.get("title", "")}}},\n'
            f'  author = {{{" and ".join(item.get("authors", []))}}},\n'
            f'  year = {{{year}}},\n'
            f"}}"
        )
        entries.append(entry)
    return "\n\n".join(entries)


if __name__ == "__main__":
    results = search_library("credit risk structural model")
    for r in results:
        print(format_citation(r))
