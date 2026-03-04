"""
CaseBank — index and retrieve similar past experiments.

Usage:
    from scripts.infrastructure.case_bank import retrieve_similar, format_case
    matches = retrieve_similar("spread momentum in IG bonds")
    for case, score in matches:
        print(f"[{score:.2f}] {format_case(case)}")
"""
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ExperimentCase:
    """Represents a past experiment indexed from results.json."""
    hypothesis_id: str
    hypothesis: str
    scripts: list[str]
    result: str  # CONFIRMED, PARTIAL, FAILED
    metrics: dict
    learnings: str
    folder: str


def index_experiments(experiments_dir: str = "experiments/") -> list[ExperimentCase]:
    """Scan all experiment folders and build index from results.json files.

    Args:
        experiments_dir: Path to experiments directory

    Returns:
        List of ExperimentCase dataclasses
    """
    exp_path = Path(experiments_dir)
    if not exp_path.exists():
        return []

    cases = []
    for folder in exp_path.iterdir():
        if not folder.is_dir():
            continue
        results_file = folder / "results.json"
        if not results_file.exists():
            continue

        try:
            with open(results_file) as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        # Extract metrics from either top-level or test_metrics
        metrics = data.get("test_metrics", data.get("metrics", {}))

        cases.append(ExperimentCase(
            hypothesis_id=data.get("hypothesis_id", folder.name),
            hypothesis=data.get("hypothesis", ""),
            scripts=data.get("scripts_called", []),
            result=data.get("result", "UNKNOWN"),
            metrics=metrics,
            learnings=data.get("learnings", ""),
            folder=folder.name,
        ))

    return cases


def _tokenize(text: str) -> list[str]:
    """Simple tokenization: lowercase, split on non-alphanumeric."""
    import re
    return re.findall(r'\b[a-z0-9]+\b', text.lower())


def _tfidf_similarity(query: str, documents: list[str]) -> list[float]:
    """Compute TF-IDF cosine similarity between query and documents.

    Args:
        query: Query text
        documents: List of document texts

    Returns:
        List of similarity scores (0-1) for each document
    """
    if not documents:
        return []

    # Tokenize
    query_tokens = _tokenize(query)
    doc_tokens_list = [_tokenize(doc) for doc in documents]

    # Build vocabulary
    vocab = set(query_tokens)
    for tokens in doc_tokens_list:
        vocab.update(tokens)
    vocab = sorted(vocab)
    word_to_idx = {w: i for i, w in enumerate(vocab)}

    # Compute document frequencies
    doc_freq = Counter()
    for tokens in doc_tokens_list:
        doc_freq.update(set(tokens))

    n_docs = len(documents)

    def to_tfidf_vector(tokens: list[str]) -> list[float]:
        tf = Counter(tokens)
        vec = [0.0] * len(vocab)
        for word, count in tf.items():
            if word in word_to_idx:
                idx = word_to_idx[word]
                # TF-IDF with log normalization
                idf = math.log((n_docs + 1) / (doc_freq.get(word, 0) + 1)) + 1
                vec[idx] = count * idf
        return vec

    def cosine_sim(v1: list[float], v2: list[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    query_vec = to_tfidf_vector(query_tokens)
    similarities = []
    for tokens in doc_tokens_list:
        doc_vec = to_tfidf_vector(tokens)
        similarities.append(cosine_sim(query_vec, doc_vec))

    return similarities


def retrieve_similar(
    hypothesis_text: str,
    experiments_dir: str = "experiments/",
    top_k: int = 3,
    min_score: float = 0.3,
) -> list[tuple[ExperimentCase, float]]:
    """Find the top-k most similar past experiments.

    Args:
        hypothesis_text: The hypothesis to match against
        experiments_dir: Path to experiments directory
        top_k: Maximum number of results
        min_score: Minimum similarity score to include

    Returns:
        List of (ExperimentCase, similarity_score) tuples, sorted by score descending
    """
    cases = index_experiments(experiments_dir)
    if not cases:
        return []

    # Build document strings: hypothesis + learnings + scripts
    documents = [
        f"{c.hypothesis} {c.learnings} {' '.join(c.scripts)}"
        for c in cases
    ]

    scores = _tfidf_similarity(hypothesis_text, documents)

    # Pair cases with scores, filter, sort
    results = [
        (case, score)
        for case, score in zip(cases, scores)
        if score >= min_score
    ]
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:top_k]


def format_case(case: ExperimentCase) -> str:
    """Format an ExperimentCase for display.

    Args:
        case: The experiment case to format

    Returns:
        Formatted string with key information
    """
    metrics_str = ", ".join(
        f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}"
        for k, v in case.metrics.items()
        if k != "task_specific"
    )
    return (
        f"{case.hypothesis_id} [{case.result}]\n"
        f"  Hypothesis: {case.hypothesis}\n"
        f"  Metrics: {metrics_str}\n"
        f"  Learnings: {case.learnings}\n"
        f"  Folder: {case.folder}"
    )
