# Migration Plan: Local Development → Global Access via Symlinks

**Date:** 2026-03-06
**Objective:** Develop AgentDS locally with git sync, make skills globally available via symlinks.

---

## 1. The Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR WORKFLOW                            │
│                                                                 │
│   1. Edit skills/scripts in this repo                          │
│   2. Git commit + push to remote                                │
│   3. Symlinks point ~/.claude/ → this repo                      │
│   4. Any project sees your changes immediately                  │
│                                                                 │
│   No copying. No manual sync. Edit once, use everywhere.        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. One-Time Setup

Run these commands once to set up global access:

### Step 1: Create global directories (if they don't exist)

```bash
mkdir -p ~/.claude/skills
mkdir -p ~/.claude/commands
mkdir -p ~/.claude/agents
```

### Step 2: Create symlinks

```bash
# From your home directory, link to this repo

# Skills
ln -s /media/ak/10E1026C4FA6006E/GitRepos/automated_data_scientist/.claude/skills \
      ~/.claude/skills/agentds

# Commands
ln -s /media/ak/10E1026C4FA6006E/GitRepos/automated_data_scientist/.claude/commands \
      ~/.claude/commands/agentds

# Agents
ln -s /media/ak/10E1026C4FA6006E/GitRepos/automated_data_scientist/.claude/agents \
      ~/.claude/agents/agentds
```

### Step 3: Install Python scripts as editable package

```bash
cd /media/ak/10E1026C4FA6006E/GitRepos/automated_data_scientist

# Create setup.py if it doesn't exist (see Section 4)
pip install -e ./scripts
```

### Step 4: Verify

```bash
# Check symlinks exist
ls -la ~/.claude/skills/
ls -la ~/.claude/commands/
ls -la ~/.claude/agents/

# Check Python package
python -c "from agentds.ml_stats.garch import fit_garch; print('OK')"
```

---

## 3. Daily Workflow

### Developing Skills

```bash
# 1. Edit in this repo
cd /media/ak/10E1026C4FA6006E/GitRepos/automated_data_scientist
vim .claude/skills/ml_stats/GARCH.md

# 2. Changes are IMMEDIATELY available globally (symlink)
# No copy needed. Any project using ~/.claude/skills/agentds sees the change.

# 3. Commit and push
git add -A
git commit -m "Update GARCH skill with new gotcha"
git push
```

### Using in Another Project

```bash
cd ~/projects/my_crypto_analysis

# Create minimal CLAUDE.md
cat > CLAUDE.md << 'EOF'
# My Crypto Analysis

## Uses
- agentds (global skill pack via ~/.claude/skills/agentds/)

## Project-Specific
- Data: ./data/
- Experiments: ./experiments/
EOF

# Start Claude Code — it finds agentds skills automatically
claude
```

---

## 4. Setup.py for Scripts Package

Create this file at `scripts/setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="agentds",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "arch",
        "pymc",
        "scipy",
        # ... other deps from requirements.txt
    ],
    python_requires=">=3.10",
)
```

Then:

```bash
pip install -e ./scripts
```

**Editable install (`-e`)** means changes to scripts are immediately available without reinstalling.

---

## 5. Handling Multiple Machines

If you work on multiple computers:

### Machine A (primary development)

```bash
# Normal workflow
cd ~/automated_data_scientist
git pull
# Edit, commit, push
```

### Machine B (secondary)

```bash
# Clone repo
git clone https://github.com/you/automated_data_scientist ~/automated_data_scientist

# Set up symlinks (same as Section 2)
ln -s ~/automated_data_scientist/.claude/skills ~/.claude/skills/agentds
ln -s ~/automated_data_scientist/.claude/commands ~/.claude/commands/agentds
ln -s ~/automated_data_scientist/.claude/agents ~/.claude/agents/agentds

# Install scripts
pip install -e ~/automated_data_scientist/scripts

# To get updates
cd ~/automated_data_scientist && git pull
```

---

## 6. Registry Migration

### Phase 1: Bootstrap registry from existing skills

```bash
# Run after creating scripts/infrastructure/bootstrap_registry.py
python scripts/infrastructure/bootstrap_registry.py --auto

# Output: .claude/skills/registry.yaml with 72 entries
```

### Phase 2: Enrich with tags

```bash
python scripts/infrastructure/bootstrap_registry.py --infer-tags
# Review and edit registry.yaml manually
```

### Phase 3: Validate

```bash
python scripts/infrastructure/skill_registry.py --validate

# Expected output:
# ✓ 72 skills have registry entries
# ✓ 72 scripts exist for all skills
# ✓ All related skills reference valid IDs
```

---

## 7. File Changes Summary

| Action | Files |
|--------|-------|
| Create | `scripts/setup.py` |
| Create | `.claude/skills/registry.yaml` |
| Create | `scripts/infrastructure/skill_registry.py` |
| Create | `scripts/infrastructure/bootstrap_registry.py` |
| Create | `.claude/commands/find.md` |
| Update | All agent .md files (add Step 0: Discover) |
| Update | CLAUDE.md §3, §4, §6 |

---

## 8. Quick Reference: Commands

```bash
# === ONE-TIME SETUP ===
mkdir -p ~/.claude/{skills,commands,agents}
ln -s /path/to/repo/.claude/skills ~/.claude/skills/agentds
ln -s /path/to/repo/.claude/commands ~/.claude/commands/agentds
ln -s /path/to/repo/.claude/agents ~/.claude/agents/agentds
pip install -e /path/to/repo/scripts

# === VERIFY ===
ls ~/.claude/skills/agentds/       # Should list: credit_fi, ml_stats, etc.
python -c "import agentds"         # Should not error

# === UPDATE (after git pull) ===
# Nothing needed! Symlinks point to repo, editable install uses repo.
# Changes appear instantly.

# === VALIDATE REGISTRY ===
python scripts/infrastructure/skill_registry.py --validate
```

---

## 9. Rollback Plan

If something breaks:

```bash
# Remove symlinks (doesn't delete source files)
rm ~/.claude/skills/agentds
rm ~/.claude/commands/agentds
rm ~/.claude/agents/agentds

# Uninstall package
pip uninstall agentds

# Back to project-scoped mode (skills only work in this repo)
```

---

## 10. Checklist

- [ ] Create `~/.claude/` directories
- [ ] Create symlinks for skills, commands, agents
- [ ] Create `scripts/setup.py`
- [ ] Run `pip install -e ./scripts`
- [ ] Create `registry.yaml` (bootstrap from existing skills)
- [ ] Create `skill_registry.py`
- [ ] Create `/find` command
- [ ] Update agent instructions (add Discover step)
- [ ] Validate everything works
- [ ] Test in a new project folder
