"""
Knowledge Retrieval — search arXiv for relevant methods before experiment planning.

Usage:
    from scripts.infrastructure.knowledge_retrieval import recommend_methods
    methods = recommend_methods("volatility clustering in credit spreads")
    for m in methods:
        print(f"{m['title']} — {m['method_summary']}")
"""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional


@dataclass
class PaperResult:
    title: str
    authors: list[str]
    abstract: str
    published: str
    url: str
    method_summary: str = ""


def search_papers(query: str, max_results: int = 5) -> list[PaperResult]:
    """Search arXiv for papers matching query.

    Args:
        query: Search string (e.g., "GARCH credit spread volatility")
        max_results: Max papers to return

    Returns:
        List of PaperResult dataclasses
    """
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = response.read()
    except Exception as e:
        print(f"[KnowledgeRetrieval] arXiv search failed: {e}")
        return []

    root = ET.fromstring(data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results = []

    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)

        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None and name.text:
                authors.append(name.text.strip())

        links = entry.findall("atom:link", ns)
        pdf_url = ""
        for link in links:
            if link.get("title") == "pdf":
                pdf_url = link.get("href", "")
                break
        if not pdf_url:
            id_elem = entry.find("atom:id", ns)
            pdf_url = id_elem.text.strip() if id_elem is not None else ""

        results.append(PaperResult(
            title=title.text.strip() if title is not None and title.text else "",
            authors=authors[:5],
            abstract=summary.text.strip() if summary is not None and summary.text else "",
            published=published.text[:10] if published is not None and published.text else "",
            url=pdf_url,
        ))

    return results


def extract_method_summary(abstract: str) -> str:
    """Extract key method/technique from abstract (first 2 sentences of method description)."""
    sentences = [s.strip() for s in abstract.replace("\n", " ").split(".") if len(s.strip()) > 20]
    # Heuristic: look for sentences with method keywords
    method_keywords = [
        "we propose", "we introduce", "we present", "our method", "our approach",
        "we develop", "this paper", "we design", "framework", "algorithm",
    ]
    method_sentences = [
        s for s in sentences
        if any(kw in s.lower() for kw in method_keywords)
    ]
    if method_sentences:
        return ". ".join(method_sentences[:2]) + "."
    # Fallback: first two substantive sentences
    return ". ".join(sentences[:2]) + "." if sentences else ""


def recommend_methods(
    hypothesis_text: str,
    max_results: int = 3,
) -> list[dict]:
    """Search papers and extract method summaries relevant to hypothesis.

    Returns list of dicts with: title, authors, published, url, method_summary.
    """
    papers = search_papers(hypothesis_text, max_results=max_results * 2)
    results = []
    for p in papers:
        p.method_summary = extract_method_summary(p.abstract)
        if p.method_summary:
            results.append({
                "title": p.title,
                "authors": ", ".join(p.authors[:3]),
                "published": p.published,
                "url": p.url,
                "method_summary": p.method_summary,
            })
        if len(results) >= max_results:
            break
    return results
