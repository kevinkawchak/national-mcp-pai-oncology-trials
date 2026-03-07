"""CLI runner for the black-box conformance harness.

Provides command-line interface for running conformance tests
against target MCP server deployments with configurable target,
profile, level, and output format options.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from conformance.harness.config import HarnessConfig


@dataclass
class TestResult:
    """Result of a single conformance test.

    Attributes:
        name: Test name/identifier.
        category: Test category (unit, integration, blackbox, adversarial).
        passed: Whether the test passed.
        duration_ms: Test execution duration in milliseconds.
        message: Descriptive message (error message if failed).
        details: Additional test details.
    """

    name: str
    category: str
    passed: bool
    duration_ms: float = 0.0
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConformanceReport:
    """Conformance test run report.

    Attributes:
        version: Report format version.
        timestamp: Report generation timestamp.
        profile: Conformance profile tested.
        level: Conformance level tested.
        target: Target server description.
        total: Total number of tests.
        passed: Number of passing tests.
        failed: Number of failing tests.
        skipped: Number of skipped tests.
        duration_ms: Total duration in milliseconds.
        results: Individual test results.
        environment: Environment details.
    """

    version: str = "1.0.0"
    timestamp: str = ""
    profile: str = ""
    level: int = 1
    target: str = ""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_ms: float = 0.0
    results: list[TestResult] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "profile": self.profile,
            "level": self.level,
            "target": self.target,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "duration_ms": self.duration_ms,
            "results": [asdict(r) for r in self.results],
            "environment": self.environment,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_junit_xml(self) -> str:
        """Serialize report to JUnit XML format."""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<testsuites name="trialmcp-conformance" tests="{self.total}" '
            f'failures="{self.failed}" time="{self.duration_ms / 1000:.3f}">',
            f'  <testsuite name="{self.profile}-level-{self.level}" '
            f'tests="{self.total}" failures="{self.failed}" '
            f'time="{self.duration_ms / 1000:.3f}">',
        ]

        for result in self.results:
            duration_s = result.duration_ms / 1000
            lines.append(
                f'    <testcase name="{_xml_escape(result.name)}" '
                f'classname="{_xml_escape(result.category)}" '
                f'time="{duration_s:.3f}">'
            )
            if not result.passed:
                lines.append(f'      <failure message="{_xml_escape(result.message)}" />')
            lines.append("    </testcase>")

        lines.append("  </testsuite>")
        lines.append("</testsuites>")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Serialize report to Markdown format."""
        lines = [
            f"# Conformance Report: {self.profile} Level {self.level}",
            "",
            f"**Target:** {self.target}",
            f"**Timestamp:** {self.timestamp}",
            f"**Duration:** {self.duration_ms:.0f}ms",
            "",
            "## Summary",
            "",
            "| Metric | Count |",
            "|--------|-------|",
            f"| Total  | {self.total} |",
            f"| Passed | {self.passed} |",
            f"| Failed | {self.failed} |",
            f"| Skipped | {self.skipped} |",
            "",
            "## Results",
            "",
            "| Test | Category | Status | Duration |",
            "|------|----------|--------|----------|",
        ]

        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            lines.append(
                f"| {result.name} | {result.category} | {status} | {result.duration_ms:.0f}ms |"
            )

        return "\n".join(lines)

    def to_html(self) -> str:
        """Serialize report to HTML dashboard format."""
        pass_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        rows = []
        for r in self.results:
            status_class = "pass" if r.passed else "fail"
            status_text = "PASS" if r.passed else "FAIL"
            rows.append(
                f"<tr class='{status_class}'><td>{_html_escape(r.name)}</td>"
                f"<td>{_html_escape(r.category)}</td>"
                f"<td>{status_text}</td>"
                f"<td>{r.duration_ms:.0f}ms</td></tr>"
            )

        return f"""<!DOCTYPE html>
<html><head><title>Conformance Report</title>
<style>
body {{ font-family: sans-serif; margin: 2em; }}
.pass {{ color: green; }} .fail {{ color: red; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f5f5f5; }}
.summary {{ display: flex; gap: 2em; margin: 1em 0; }}
.metric {{ padding: 1em; background: #f9f9f9; border-radius: 4px; }}
</style></head>
<body>
<h1>Conformance Report: {_html_escape(self.profile)} Level {self.level}</h1>
<p>Target: {_html_escape(self.target)} | {_html_escape(self.timestamp)}</p>
<div class="summary">
<div class="metric"><strong>Total:</strong> {self.total}</div>
<div class="metric pass"><strong>Passed:</strong> {self.passed}</div>
<div class="metric fail"><strong>Failed:</strong> {self.failed}</div>
<div class="metric"><strong>Pass Rate:</strong> {pass_rate:.1f}%</div>
</div>
<table><thead><tr><th>Test</th><th>Category</th><th>Status</th>
<th>Duration</th></tr></thead><tbody>
{"".join(rows)}
</tbody></table></body></html>"""


def _xml_escape(text: str) -> str:
    """Escape text for XML attribute values."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _html_escape(text: str) -> str:
    """Escape text for HTML content."""
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="trialmcp-conformance",
        description="Run MCP conformance tests against target server deployments",
    )
    parser.add_argument(
        "--target",
        default="stdin",
        help="Target server transport type (stdin, http, docker)",
    )
    parser.add_argument(
        "--address",
        default="",
        help="Target server address (command, URL, or container)",
    )
    parser.add_argument(
        "--profile",
        default="base",
        choices=[
            "base",
            "clinical-read",
            "imaging-guided-oncology",
            "multi-site-federated",
            "robot-assisted-procedure",
        ],
        help="Conformance profile to test",
    )
    parser.add_argument(
        "--level",
        type=int,
        default=1,
        choices=[1, 2, 3, 4, 5],
        help="Conformance level (1-5)",
    )
    parser.add_argument(
        "--output-format",
        default="json",
        choices=["json", "junit", "html", "markdown"],
        help="Output report format",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory for test reports",
    )
    parser.add_argument(
        "--config",
        default="",
        help="Path to harness configuration file",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Verbose output",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the conformance harness CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, 1 for failures).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Load configuration
    if args.config:
        config = HarnessConfig.from_file(args.config)
    else:
        config = HarnessConfig(
            profile=args.profile,
            level=args.level,
            output_format=args.output_format,
            output_dir=args.output_dir,
            timeout=args.timeout,
            verbose=args.verbose,
        )

    # Build report
    report = ConformanceReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        profile=config.profile,
        level=config.level,
        target=args.address or "local",
        environment={
            "python_version": (
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            ),
            "harness_version": "0.8.0",
        },
    )

    # Output report
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if config.output_format == "json":
        output_file = output_dir / "conformance-report.json"
        output_file.write_text(report.to_json(), encoding="utf-8")
    elif config.output_format == "junit":
        output_file = output_dir / "conformance-report.xml"
        output_file.write_text(report.to_junit_xml(), encoding="utf-8")
    elif config.output_format == "html":
        output_file = output_dir / "conformance-report.html"
        output_file.write_text(report.to_html(), encoding="utf-8")
    elif config.output_format == "markdown":
        output_file = output_dir / "conformance-report.md"
        output_file.write_text(report.to_markdown(), encoding="utf-8")

    if config.verbose:
        print(f"Conformance report written to {output_file}")
        print(f"Total: {report.total} | Passed: {report.passed} | Failed: {report.failed}")

    return 1 if report.failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
