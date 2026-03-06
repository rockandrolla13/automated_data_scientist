"""
Bootstrap Registry — generate registry.yaml from existing skill files.

Usage:
    python scripts/infrastructure/bootstrap_registry.py --auto
    python scripts/infrastructure/bootstrap_registry.py --infer-tags
    python scripts/infrastructure/bootstrap_registry.py --validate
"""

import re
from pathlib import Path
from typing import Optional

import yaml


# Tag inference rules: pattern -> tags
TAG_INFERENCE_RULES = {
    # Method type
    r'\bregression\b': ['regression'],
    r'\bclassification\b': ['classification'],
    r'\bcluster': ['clustering'],
    r'\bforecast': ['forecasting'],
    r'\bsimulat': ['simulation'],
    r'\boptimiz': ['optimization'],
    r'\bcausal': ['causal'],
    r'\bbayesian\b': ['bayesian', 'uncertainty'],
    r'\bmcmc\b': ['bayesian', 'sampling'],
    r'\bbootstrap': ['resampling'],

    # Asset/domain
    r'\bcredit\b': ['credit'],
    r'\bbond\b': ['credit', 'fixed-income'],
    r'\bspread\b': ['credit', 'spreads'],
    r'\bequity|stock': ['equity'],
    r'\brate\b|yield': ['rates', 'fixed-income'],
    r'\bcrypto|bitcoin|btc': ['crypto'],

    # Data type
    r'\btime.?series\b': ['time-series'],
    r'\bcross.?section': ['cross-sectional'],
    r'\bpanel\b': ['panel'],
    r'\bgraph\b|network': ['graph'],

    # Task
    r'\brisk\b': ['risk'],
    r'\balpha\b|signal': ['alpha', 'signal'],
    r'\bhedg': ['hedging'],
    r'\bpric': ['pricing'],
    r'\bvaluat': ['valuation'],
    r'\bclean': ['cleaning', 'preprocessing'],
    r'\beda\b|explor': ['eda', 'exploration'],

    # Specific methods
    r'\bgarch\b': ['volatility', 'time-series', 'heteroskedasticity'],
    r'\barima\b': ['time-series', 'forecasting'],
    r'\bpca\b|principal.?component': ['dimensionality-reduction'],
    r'\bshap\b|explain': ['explainability'],
    r'\bconformal\b': ['uncertainty', 'prediction-intervals'],
    r'\bneural|deep.?learning|lstm|transformer': ['deep-learning'],
    r'\breinforcement': ['reinforcement-learning'],
    r'\bmarkov|regime': ['regime', 'state-space'],
    r'\bmerton|default': ['credit-risk', 'default'],
    r'\bbacktest': ['backtesting', 'alpha'],
    r'\bportfolio': ['portfolio', 'allocation'],
}


def extract_frontmatter(skill_path: Path) -> dict:
    """Extract YAML frontmatter from a skill .md file."""
    content = skill_path.read_text()

    # Match YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def extract_content(skill_path: Path) -> str:
    """Extract content after frontmatter."""
    content = skill_path.read_text()
    # Remove frontmatter
    content = re.sub(r'^---\s*\n.*?\n---\s*\n?', '', content, flags=re.DOTALL)
    return content


def infer_tags(content: str, existing_tags: list[str] = None) -> list[str]:
    """Infer tags from skill content."""
    existing_tags = existing_tags or []
    tags = set(existing_tags)

    content_lower = content.lower()

    for pattern, inferred in TAG_INFERENCE_RULES.items():
        if re.search(pattern, content_lower):
            tags.update(inferred)

    return sorted(tags)


def build_registry_entry(skill_path: Path, infer: bool = False) -> dict:
    """Build a registry entry from a skill file."""
    frontmatter = extract_frontmatter(skill_path)
    content = extract_content(skill_path)

    skill_id = skill_path.stem
    category = skill_path.parent.name

    # Convert PascalCase to snake_case for script name
    snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', skill_id).lower()

    # Extract use_when from description or content
    use_when = frontmatter.get('description', '')
    if not use_when:
        # Try to extract from ## When to Use section
        match = re.search(r'##\s*When to Use\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            use_when = match.group(1).strip()[:200]

    # Build entry
    entry = {
        'id': skill_id,
        'category': category,
        'script': f"agentds.{category}.{snake_name}",
        'tags': [],
        'keywords': [],
        'use_when': use_when.replace('\n', ' ').strip(),
        'related': [],
        'not_for': [],
    }

    # Infer tags if requested
    if infer:
        entry['tags'] = infer_tags(content + ' ' + use_when)

    return entry


def scan_skills(skills_dir: Path) -> list[Path]:
    """Find all skill .md files."""
    skills = []
    for category_dir in skills_dir.iterdir():
        if not category_dir.is_dir():
            continue
        if category_dir.name.startswith('.'):
            continue
        for md_file in category_dir.glob('*.md'):
            # Skip non-skill files
            if md_file.name.lower() in ('readme.md', 'registry.yaml'):
                continue
            skills.append(md_file)
    return sorted(skills)


def build_registry(
    skills_dir: Path,
    infer_tags: bool = False,
) -> dict:
    """Build complete registry from skill files."""
    skills = scan_skills(skills_dir)

    entries = []
    for skill_path in skills:
        entry = build_registry_entry(skill_path, infer=infer_tags)
        entries.append(entry)

    return {
        'pack': 'agentds',
        'version': '1.0',
        'global': True,
        'skills': entries,
    }


def write_registry(registry: dict, output_path: Path) -> None:
    """Write registry to YAML file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Custom YAML formatting for readability
    class FlowList(list):
        pass

    def represent_flow_list(dumper, data):
        return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

    yaml.add_representer(FlowList, represent_flow_list)

    # Convert lists to flow style for compact output
    for skill in registry['skills']:
        skill['tags'] = FlowList(skill['tags'])
        skill['keywords'] = FlowList(skill['keywords'])
        skill['related'] = FlowList(skill['related'])
        skill['not_for'] = FlowList(skill['not_for'])

    with open(output_path, 'w') as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"Wrote {len(registry['skills'])} skills to {output_path}")


def merge_with_existing(new_registry: dict, existing_path: Path) -> dict:
    """Merge new registry with existing, preserving manual edits."""
    if not existing_path.exists():
        return new_registry

    with open(existing_path) as f:
        existing = yaml.safe_load(f)

    existing_map = {s['id']: s for s in existing.get('skills', [])}

    # Merge: new entries take base info, existing entries preserve manual fields
    merged_skills = []
    for new_skill in new_registry['skills']:
        if new_skill['id'] in existing_map:
            old = existing_map[new_skill['id']]
            # Preserve manually edited fields
            new_skill['tags'] = old.get('tags') or new_skill['tags']
            new_skill['keywords'] = old.get('keywords') or new_skill['keywords']
            new_skill['related'] = old.get('related') or new_skill['related']
            new_skill['not_for'] = old.get('not_for') or new_skill['not_for']
        merged_skills.append(new_skill)

    new_registry['skills'] = merged_skills
    return new_registry


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Bootstrap AgentDS skill registry")
    parser.add_argument('--auto', action='store_true',
                        help='Auto-generate registry from skill files')
    parser.add_argument('--infer-tags', action='store_true',
                        help='Infer tags from skill content')
    parser.add_argument('--skills-dir', type=Path,
                        default=Path('.claude/skills'),
                        help='Path to skills directory')
    parser.add_argument('--output', type=Path,
                        default=Path('.claude/skills/registry.yaml'),
                        help='Output path for registry.yaml')
    parser.add_argument('--merge', action='store_true',
                        help='Merge with existing registry, preserving manual edits')
    args = parser.parse_args()

    if args.auto or args.infer_tags:
        print(f"Scanning skills in {args.skills_dir}...")
        registry = build_registry(args.skills_dir, infer_tags=args.infer_tags)

        if args.merge and args.output.exists():
            print(f"Merging with existing {args.output}...")
            registry = merge_with_existing(registry, args.output)

        write_registry(registry, args.output)
        print("Done!")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
