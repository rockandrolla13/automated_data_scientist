"""Setup script for AgentDS - installable as 'agentds' package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements (core only for base install)
CORE_DEPS = [
    "numpy>=1.24",
    "pandas>=2.0",
    "scipy>=1.11",
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "scikit-learn>=1.3",
]

setup(
    name="agentds",
    version="1.0.0",
    description="Agentic Data Scientist - hypothesis-driven research framework",
    author="AgentDS",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=CORE_DEPS,
    extras_require={
        "full": [
            # See requirements.txt for full list
            "arch>=6.0",
            "statsmodels>=0.14",
            "pymc>=5.10",
            "torch>=2.1",
            "plotly>=5.18",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentds-validate=infrastructure.skill_registry:main",
        ],
    },
)
