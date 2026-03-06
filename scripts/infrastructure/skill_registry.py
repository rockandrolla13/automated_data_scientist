"""
Skill Registry — search, discover, and validate AgentDS skills.

Usage:
    from scripts.infrastructure.skill_registry import search, suggest_for_goal

    # Search by keyword
    results = search("volatility forecasting", top_k=5)
    for match in results:
        print(f"[{match.score:.2f}] {match.skill.id}: {match.skill.use_when}")

    # Suggest skills for a goal
    suggestions = suggest_for_goal("Find alpha in IG credit spreads")

    # Validate registry
    errors = validate_registry()
"""

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class SkillEntry:
    """A skill in the registry."""
    id: str
    category: str
    script: str
    tags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    use_when: str = ""
    related: list[str] = field(default_factory=list)
    not_for: list[str] = field(default_factory=list)


@dataclass
class SkillMatch:
    """A search result with score."""
    skill: SkillEntry
    score: float
    match_reasons: list[str] = field(default_factory=list)


def _find_registry_path() -> Path:
    """Find registry.yaml in standard locations."""
    candidates = [
        Path.home() / ".claude" / "skills" / "agentds" / "registry.yaml",
        Path(".claude/skills/registry.yaml"),
        Path(__file__).parent.parent.parent / ".claude" / "skills" / "registry.yaml",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f"registry.yaml not found in: {[str(c) for c in candidates]}")


def load_registry(registry_path: Optional[Path] = None) -> list[SkillEntry]:
    """Load all skills from registry.yaml.

    Args:
        registry_path: Path to registry.yaml. Auto-detected if None.

    Returns:
        List of SkillEntry objects.
    """
    if registry_path is None:
        registry_path = _find_registry_path()

    with open(registry_path) as f:
        data = yaml.safe_load(f)

    entries = []
    for item in data.get("skills", []):
        entries.append(SkillEntry(
            id=item["id"],
            category=item.get("category", ""),
            script=item.get("script", ""),
            tags=item.get("tags", []),
            keywords=item.get("keywords", []),
            use_when=item.get("use_when", ""),
            related=item.get("related", []),
            not_for=item.get("not_for", []),
        ))
    return entries


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    return re.findall(r'\b[a-z0-9]+\b', text.lower())


def _compute_match_score(query_tokens: set[str], skill: SkillEntry) -> tuple[float, list[str]]:
    """Compute relevance score and match reasons for a skill.

    Returns:
        (score, list of reasons why it matched)
    """
    score = 0.0
    reasons = []

    # Tag matches (high weight)
    tag_tokens = set(_tokenize(" ".join(skill.tags)))
    tag_overlap = query_tokens & tag_tokens
    if tag_overlap:
        score += len(tag_overlap) * 0.3
        reasons.append(f"tags: {', '.join(tag_overlap)}")

    # Keyword matches (high weight)
    kw_tokens = set(_tokenize(" ".join(skill.keywords)))
    kw_overlap = query_tokens & kw_tokens
    if kw_overlap:
        score += len(kw_overlap) * 0.25
        reasons.append(f"keywords: {', '.join(kw_overlap)}")

    # use_when matches (medium weight)
    use_tokens = set(_tokenize(skill.use_when))
    use_overlap = query_tokens & use_tokens
    if use_overlap:
        score += len(use_overlap) * 0.15
        reasons.append(f"use_when: {', '.join(list(use_overlap)[:3])}")

    # ID/category match (boost)
    id_tokens = set(_tokenize(skill.id))
    cat_tokens = set(_tokenize(skill.category))
    if query_tokens & id_tokens:
        score += 0.4
        reasons.append(f"id: {skill.id}")
    if query_tokens & cat_tokens:
        score += 0.2
        reasons.append(f"category: {skill.category}")

    # Negative: not_for penalty
    not_for_tokens = set(_tokenize(" ".join(skill.not_for)))
    not_for_overlap = query_tokens & not_for_tokens
    if not_for_overlap:
        score -= len(not_for_overlap) * 0.3

    return max(0.0, score), reasons


def search(
    query: str,
    top_k: int = 5,
    min_score: float = 0.1,
    registry_path: Optional[Path] = None,
) -> list[SkillMatch]:
    """Search skills by keyword, tag, or natural language query.

    Args:
        query: Search query (e.g., "volatility forecasting", "credit spreads")
        top_k: Maximum results to return
        min_score: Minimum score threshold
        registry_path: Path to registry.yaml

    Returns:
        List of SkillMatch sorted by score descending.
    """
    skills = load_registry(registry_path)
    query_tokens = set(_tokenize(query))

    if not query_tokens:
        return []

    matches = []
    for skill in skills:
        score, reasons = _compute_match_score(query_tokens, skill)
        if score >= min_score:
            matches.append(SkillMatch(skill=skill, score=score, match_reasons=reasons))

    matches.sort(key=lambda m: m.score, reverse=True)
    return matches[:top_k]


def suggest_for_goal(
    goal: str,
    top_k: int = 5,
    registry_path: Optional[Path] = None,
) -> list[SkillMatch]:
    """Suggest skills relevant to a high-level goal.

    Args:
        goal: User's goal (e.g., "Find alpha in IG credit spreads")
        top_k: Maximum suggestions

    Returns:
        List of relevant SkillMatch.
    """
    # Same as search but with goal-oriented framing
    return search(goal, top_k=top_k, min_score=0.05, registry_path=registry_path)


def get_related(skill_id: str, registry_path: Optional[Path] = None) -> list[SkillEntry]:
    """Get related skills for a given skill.

    Args:
        skill_id: ID of the skill (e.g., "GARCH")

    Returns:
        List of related SkillEntry objects.
    """
    skills = load_registry(registry_path)
    skill_map = {s.id: s for s in skills}

    target = skill_map.get(skill_id)
    if not target:
        return []

    related = []
    for rel_id in target.related:
        if rel_id in skill_map:
            related.append(skill_map[rel_id])
    return related


def validate_registry(
    registry_path: Optional[Path] = None,
    skills_dir: Optional[Path] = None,
    scripts_dir: Optional[Path] = None,
) -> list[str]:
    """Validate registry against actual skill files.

    Returns:
        List of error messages. Empty = all valid.
    """
    errors = []

    # Find paths
    if registry_path is None:
        try:
            registry_path = _find_registry_path()
        except FileNotFoundError as e:
            return [str(e)]

    if skills_dir is None:
        skills_dir = registry_path.parent
    if scripts_dir is None:
        scripts_dir = registry_path.parent.parent.parent / "scripts"

    # Load registry
    try:
        skills = load_registry(registry_path)
    except Exception as e:
        return [f"Failed to load registry: {e}"]

    skill_ids = {s.id for s in skills}

    # Check each skill has corresponding .md file
    for skill in skills:
        md_path = skills_dir / skill.category / f"{skill.id}.md"
        if not md_path.exists():
            errors.append(f"Missing .md: {md_path}")

    # Check each skill has corresponding .py file
    for skill in skills:
        # Convert PascalCase to snake_case
        snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', skill.id).lower()
        py_path = scripts_dir / skill.category / f"{snake_name}.py"
        if not py_path.exists():
            errors.append(f"Missing .py: {py_path}")

    # Check related skills reference valid IDs
    for skill in skills:
        for rel in skill.related:
            if rel not in skill_ids:
                errors.append(f"{skill.id}: related skill '{rel}' not found in registry")

    # Check for orphan .md files (skills not in registry)
    for category_dir in skills_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        for md_file in category_dir.glob("*.md"):
            if md_file.name == "registry.yaml":
                continue
            skill_id = md_file.stem
            if skill_id not in skill_ids:
                errors.append(f"Orphan .md not in registry: {md_file}")

    return errors


def format_match(match: SkillMatch) -> str:
    """Format a SkillMatch for display."""
    s = match.skill
    lines = [
        f"{s.id} ({s.category})  score: {match.score:.2f}",
        f"  → {s.use_when[:80]}..." if len(s.use_when) > 80 else f"  → {s.use_when}",
    ]
    if s.related:
        lines.append(f"  Related: {', '.join(s.related[:3])}")
    if match.match_reasons:
        lines.append(f"  Matched: {'; '.join(match.match_reasons[:3])}")
    return "\n".join(lines)


def print_search_results(matches: list[SkillMatch]) -> None:
    """Print search results in a formatted way."""
    if not matches:
        print("No matching skills found.")
        return

    print(f"Found {len(matches)} matching skills:\n")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {format_match(match)}\n")


def main():
    """CLI entry point for validation."""
    import argparse

    parser = argparse.ArgumentParser(description="AgentDS Skill Registry")
    parser.add_argument("--validate", action="store_true", help="Validate registry")
    parser.add_argument("--search", type=str, help="Search for skills")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    args = parser.parse_args()

    if args.validate:
        errors = validate_registry()
        if errors:
            print(f"Found {len(errors)} errors:")
            for e in errors:
                print(f"  - {e}")
            exit(1)
        else:
            print("✓ Registry is valid")
            exit(0)

    if args.search:
        results = search(args.search, top_k=args.top_k)
        print_search_results(results)


if __name__ == "__main__":
    main()
