"""Version metadata for OpenAgentSec (PRD v4.0.2 Phase 1A).

Separates the *product PRD version* (``product_prd_version``) from the
*software release version* (``software_version``).  The two are intentionally
independent: ``software_version`` tracks the packaged release baseline (e.g.
``6.0.0``) and MUST NOT be rewritten to match the PRD version.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

PRODUCT_PRD_VERSION = "4.0.2"


def software_version() -> str:
    """Return the packaged software version (never lowered to the PRD version)."""
    from src.openagentsec import __version__

    return __version__


def get_git_commit(repo_root: Optional[Path] = None) -> Optional[str]:
    """Return the current git HEAD hash without any network access."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root) if repo_root else None,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    return value or None


def version_metadata(repo_root: Optional[Path] = None) -> dict:
    """Return a compact version-metadata mapping for manifests/results."""
    return {
        "product_prd_version": PRODUCT_PRD_VERSION,
        "software_version": software_version(),
        "git_commit": get_git_commit(repo_root),
    }
