"""NON-NORMATIVE Reference Implementation — Conformance Runner.

CLI tool for executing the National MCP-PAI Oncology Trials conformance
test suite against a local or remote MCP server deployment.  Wraps
``pytest`` with sensible defaults and reports a conformance summary.

Usage
-----
::

    python -m reference.python.conformance_runner            # all tests
    python -m reference.python.conformance_runner --level 1  # Core only
    python -m reference.python.conformance_runner --level 3  # up to Imaging
    python -m reference.python.conformance_runner --security # security only

See Also
--------
- conformance/README.md : Test harness documentation
- profiles/             : Conformance profiles per level
- spec/conformance.md   : Normative conformance requirements

References
----------
1. Kawchak, K. (2026). *TrialMCP: MCP Servers for Physical AI
   Oncology Clinical Trial Systems*.
   DOI: 10.5281/zenodo.18869776
2. Kawchak, K. (2026). *Physical AI Oncology Trials: End-to-End
   Framework for Robotic Systems in Clinical Trials*.
   DOI: 10.5281/zenodo.18445179
3. Kawchak, K. (2026). *PAI Oncology Trial FL: Federated Learning
   for Physical AI Oncology Trials*.
   DOI: 10.5281/zenodo.18840880
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Repository root (two levels up from this file)
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFORMANCE_DIR = _REPO_ROOT / "conformance"

# Test directory mapping per conformance level
LEVEL_DIRS: dict[int, list[str]] = {
    1: ["positive/test_core_conformance.py"],
    2: ["positive/test_clinical_read_conformance.py"],
    3: ["positive/test_imaging_conformance.py"],
    4: ["interoperability/"],
    5: [],  # all tests
}


def build_pytest_args(
    level: int | None = None,
    security_only: bool = False,
    verbose: bool = True,
) -> list[str]:
    """Build the ``pytest`` argument list for the requested scope.

    Parameters
    ----------
    level : int or None
        Maximum conformance level to test (1–5).  ``None`` runs all.
    security_only : bool
        If ``True``, run only the security test category.
    verbose : bool
        Enable verbose output (``-v``).

    Returns
    -------
    list[str]
        Arguments suitable for ``pytest.main()``.
    """
    args: list[str] = []

    if verbose:
        args.append("-v")

    if security_only:
        args.append(str(_CONFORMANCE_DIR / "security"))
        return args

    if level is None or level >= 5:
        args.append(str(_CONFORMANCE_DIR))
        return args

    # Accumulate test paths for levels 1..level
    paths: list[str] = []
    for lvl in range(1, level + 1):
        for entry in LEVEL_DIRS.get(lvl, []):
            target = _CONFORMANCE_DIR / entry
            paths.append(str(target))

    # Always include negative tests
    paths.append(str(_CONFORMANCE_DIR / "negative"))

    args.extend(paths)
    return args


def main(argv: list[str] | None = None) -> int:
    """Entry point for the conformance runner.

    Returns
    -------
    int
        Exit code (0 = all tests passed).
    """
    parser = argparse.ArgumentParser(
        description="National MCP-PAI Oncology Trials — Conformance Runner",
    )
    parser.add_argument(
        "--level",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Maximum conformance level to validate (default: all)",
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run only security conformance tests",
    )
    parser.add_argument(
        "--no-verbose",
        action="store_true",
        help="Suppress verbose output",
    )
    args = parser.parse_args(argv)

    try:
        import pytest
    except ImportError:
        print(
            "ERROR: pytest is required. Install with: "
            "pip install 'national-mcp-pai-oncology-trials[test]'",
            file=sys.stderr,
        )
        return 1

    pytest_args = build_pytest_args(
        level=args.level,
        security_only=args.security,
        verbose=not args.no_verbose,
    )
    return pytest.main(pytest_args)


if __name__ == "__main__":
    sys.exit(main())
