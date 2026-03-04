"""workflows — Workflow definitions, retrieval, and experiment validation."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WorkflowSpec:
    name: str
    label: str
    steps: list[str]
    required_scripts: list[str]
    required_outputs: list[str]


WORKFLOWS: dict[str, WorkflowSpec] = {
    "A": WorkflowSpec(
        name="A", label="Signal Research",
        steps=["EDA", "Feature Engineering", "Signal Construction", "Backtest", "Evaluate", "Log"],
        required_scripts=["eda.py", "signal_construction.py", "backtest_engine.py"],
        required_outputs=["results.json", "README.md", "figures/"],
    ),
    "B": WorkflowSpec(
        name="B", label="Model Comparison",
        steps=["EDA", "Fit N Models", "Cross-Validate on Val", "Select Best", "Test-Set Evaluation", "Log"],
        required_scripts=["hypothesis_testing.py"],
        required_outputs=["results.json", "README.md"],
    ),
    "C": WorkflowSpec(
        name="C", label="Causal Investigation",
        steps=["EDA", "DAG Specification", "Estimate Effect", "Refutation Tests", "Sensitivity Analysis", "Log"],
        required_scripts=["causal_effect.py"],
        required_outputs=["results.json", "README.md"],
    ),
    "D": WorkflowSpec(
        name="D", label="Stakeholder Deliverable",
        steps=["Load Results", "Generate Figures", "Build Report/Slides/Notebook", "Promote to /artifacts"],
        required_scripts=["publication_figures.py"],
        required_outputs=[],  # Output goes to /artifacts/, not experiment folder
    ),
    "E": WorkflowSpec(
        name="E", label="Full Pipeline",
        steps=["EDA", "Clean", "Features", "Model", "Diagnostics", "Visualization", "Report"],
        required_scripts=["eda.py", "data_loading.py", "publication_figures.py"],
        required_outputs=["results.json", "README.md", "figures/"],
    ),
}


def get_workflow(name: str) -> WorkflowSpec:
    """Retrieve workflow by letter name."""
    name = name.upper().strip()
    if name not in WORKFLOWS:
        raise ValueError(f"Unknown workflow '{name}'. Available: {list(WORKFLOWS.keys())}")
    return WORKFLOWS[name]


def list_workflows() -> list[dict]:
    """Return summary of all workflows."""
    return [
        {"name": w.name, "label": w.label, "steps": len(w.steps)}
        for w in WORKFLOWS.values()
    ]


def validate_workflow(experiment_dir: str, workflow_name: str) -> list[str]:
    """Check experiment folder has all required outputs. Returns list of missing items."""
    spec = get_workflow(workflow_name)
    exp = Path(experiment_dir)
    missing = []

    for output in spec.required_outputs:
        target = exp / output
        if output.endswith("/"):
            if not target.is_dir() or not any(target.iterdir()):
                missing.append(f"Missing or empty directory: {output}")
        else:
            if not target.exists():
                missing.append(f"Missing file: {output}")

    # Check results.json has required fields
    results_path = exp / "results.json"
    if results_path.exists():
        import json
        with open(results_path) as f:
            results = json.load(f)
        required_fields = ["hypothesis_id", "metrics", "result"]
        for rf in required_fields:
            if rf not in results:
                missing.append(f"results.json missing field: {rf}")

    return missing


if __name__ == "__main__":
    print("Available workflows:")
    for w in list_workflows():
        print(f"  {w['name']}: {w['label']} ({w['steps']} steps)")

    # Example validation
    import sys
    if len(sys.argv) > 2:
        exp_dir, wf = sys.argv[1], sys.argv[2]
        issues = validate_workflow(exp_dir, wf)
        if issues:
            print(f"\nValidation issues for {exp_dir}:")
            for i in issues:
                print(f"  ⚠ {i}")
        else:
            print(f"\n✓ {exp_dir} passes Workflow {wf} validation.")
