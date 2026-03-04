"""
Solution Retrieval — load and match proven recipes from solutions/.

Usage:
    from scripts.infrastructure.solution_retrieval import match_solution, load_solution
    match = match_solution("spread momentum in HY bonds")
    if match:
        recipe = load_solution(match)
"""
import os
from pathlib import Path
from typing import Optional

import yaml


def list_solutions(solutions_dir: str = "solutions/") -> list[str]:
    """List all solution recipe names (without .yaml)."""
    sol_path = Path(solutions_dir)
    if not sol_path.exists():
        return []
    return sorted(
        f.stem for f in sol_path.glob("*.yaml")
    )


def load_solution(name: str, solutions_dir: str = "solutions/") -> dict:
    """Load a solution recipe by name.

    Args:
        name: Solution name (without .yaml extension)
        solutions_dir: Path to solutions directory

    Returns:
        dict with keys: name, description, origin, workflow, scripts, params, metrics, learnings
    """
    path = Path(solutions_dir) / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Solution not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def match_solution(
    hypothesis_text: str,
    solutions_dir: str = "solutions/",
) -> Optional[str]:
    """Keyword-match hypothesis text against solution descriptions.

    Returns the name of the best-matching solution, or None if no match.
    """
    solutions = list_solutions(solutions_dir)
    if not solutions:
        return None

    query_words = set(hypothesis_text.lower().split())
    best_name = None
    best_score = 0

    for name in solutions:
        try:
            recipe = load_solution(name, solutions_dir)
        except (FileNotFoundError, yaml.YAMLError):
            continue
        desc = recipe.get("description", "") + " " + recipe.get("learnings", "")
        desc_words = set(desc.lower().split())
        overlap = len(query_words & desc_words)
        if overlap > best_score:
            best_score = overlap
            best_name = name

    return best_name if best_score >= 2 else None


def create_solution(
    name: str,
    description: str,
    origin: str,
    workflow: str,
    scripts: list[str],
    params: dict,
    metrics: dict,
    learnings: str,
    solutions_dir: str = "solutions/",
) -> str:
    """Create a new solution recipe from a confirmed experiment.

    Returns the path to the created file.
    """
    recipe = {
        "name": name,
        "description": description,
        "origin": origin,
        "workflow": workflow,
        "scripts": scripts,
        "params": params,
        "metrics": metrics,
        "learnings": learnings,
    }
    path = Path(solutions_dir) / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(recipe, f, default_flow_style=False, sort_keys=False)
    return str(path)
