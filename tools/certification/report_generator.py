"""Machine-readable conformance report generator.

Generates conformance reports in JSON, JUnit XML, HTML dashboard,
and Markdown formats from test results.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class TestEntry:
    """A single test result entry."""

    name: str
    category: str
    passed: bool
    duration_ms: float = 0.0
    message: str = ""
    server: str = ""
    profile: str = ""


@dataclass
class ConformanceReport:
    """Complete conformance report.

    Attributes:
        title: Report title.
        version: Report version.
        timestamp: Generation timestamp.
        profile: Conformance profile tested.
        level: Conformance level.
        target: Target server description.
        environment: Environment metadata.
        results: List of test entries.
    """

    title: str = "TrialMCP Conformance Report"
    version: str = "0.8.0"
    timestamp: str = ""
    profile: str = "base"
    level: int = 1
    target: str = ""
    environment: dict[str, str] = field(default_factory=dict)
    results: list[TestEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def pass_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0.0


def generate_json_report(report: ConformanceReport) -> str:
    """Generate a JSON conformance report.

    Args:
        report: ConformanceReport to serialize.

    Returns:
        JSON string representation.
    """
    data = {
        "title": report.title,
        "version": report.version,
        "timestamp": report.timestamp,
        "profile": report.profile,
        "level": report.level,
        "target": report.target,
        "environment": report.environment,
        "summary": {
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "pass_rate": report.pass_rate,
        },
        "results": [asdict(r) for r in report.results],
    }
    return json.dumps(data, indent=2)


def generate_junit_xml(report: ConformanceReport) -> str:
    """Generate a JUnit XML conformance report for CI integration.

    Args:
        report: ConformanceReport to serialize.

    Returns:
        JUnit XML string representation.
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<testsuites name="{_xml_esc(report.title)}" '
        f'tests="{report.total}" failures="{report.failed}">',
        f'  <testsuite name="{_xml_esc(report.profile)}-level-{report.level}" '
        f'tests="{report.total}" failures="{report.failed}">',
    ]
    for entry in report.results:
        lines.append(
            f'    <testcase name="{_xml_esc(entry.name)}" '
            f'classname="{_xml_esc(entry.category)}" '
            f'time="{entry.duration_ms / 1000:.3f}">'
        )
        if not entry.passed:
            lines.append(f'      <failure message="{_xml_esc(entry.message)}" />')
        lines.append("    </testcase>")
    lines.append("  </testsuite>")
    lines.append("</testsuites>")
    return "\n".join(lines)


def generate_html_report(report: ConformanceReport) -> str:
    """Generate an HTML dashboard conformance report.

    Args:
        report: ConformanceReport to serialize.

    Returns:
        HTML string representation.
    """
    rows = []
    for r in report.results:
        cls = "pass" if r.passed else "fail"
        status = "PASS" if r.passed else "FAIL"
        rows.append(
            f"<tr class='{cls}'><td>{_html_esc(r.name)}</td>"
            f"<td>{_html_esc(r.category)}</td>"
            f"<td>{status}</td><td>{r.duration_ms:.0f}ms</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html><head><title>{_html_esc(report.title)}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2em; color: #333; }}
h1 {{ color: #1a1a2e; }}
.pass {{ color: #2e7d32; }} .fail {{ color: #c62828; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 1em; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f5f5f5; }}
.summary {{ display: flex; gap: 2em; margin: 1em 0; }}
.metric {{ padding: 1em; background: #f9f9f9; border-radius: 8px;
           border: 1px solid #eee; min-width: 120px; text-align: center; }}
</style></head>
<body>
<h1>{_html_esc(report.title)}</h1>
<p><strong>Profile:</strong> {_html_esc(report.profile)} Level {report.level}
| <strong>Target:</strong> {_html_esc(report.target)}
| <strong>Generated:</strong> {_html_esc(report.timestamp)}</p>
<div class="summary">
<div class="metric"><strong>Total</strong><br>{report.total}</div>
<div class="metric pass"><strong>Passed</strong><br>{report.passed}</div>
<div class="metric fail"><strong>Failed</strong><br>{report.failed}</div>
<div class="metric"><strong>Pass Rate</strong><br>{report.pass_rate:.1f}%</div>
</div>
<table><thead><tr><th>Test</th><th>Category</th><th>Status</th>
<th>Duration</th></tr></thead><tbody>
{"".join(rows)}
</tbody></table></body></html>"""


def generate_markdown_report(report: ConformanceReport) -> str:
    """Generate a Markdown conformance report for PR comments.

    Args:
        report: ConformanceReport to serialize.

    Returns:
        Markdown string representation.
    """
    lines = [
        f"# {report.title}",
        "",
        f"**Profile:** {report.profile} Level {report.level}  ",
        f"**Target:** {report.target}  ",
        f"**Generated:** {report.timestamp}  ",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total | {report.total} |",
        f"| Passed | {report.passed} |",
        f"| Failed | {report.failed} |",
        f"| Pass Rate | {report.pass_rate:.1f}% |",
        "",
        "## Results",
        "",
        "| Test | Category | Status | Duration |",
        "|------|----------|--------|----------|",
    ]
    for r in report.results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"| {r.name} | {r.category} | {status} | {r.duration_ms:.0f}ms |")
    return "\n".join(lines)


def save_report(
    report: ConformanceReport,
    output_dir: str | Path,
    formats: list[str] | None = None,
) -> list[Path]:
    """Save conformance report to files in specified formats.

    Args:
        report: ConformanceReport to save.
        output_dir: Directory for output files.
        formats: List of formats ('json', 'junit', 'html', 'markdown').

    Returns:
        List of paths to saved report files.
    """
    if formats is None:
        formats = ["json"]

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    generators = {
        "json": (generate_json_report, "conformance-report.json"),
        "junit": (generate_junit_xml, "conformance-report.xml"),
        "html": (generate_html_report, "conformance-report.html"),
        "markdown": (generate_markdown_report, "conformance-report.md"),
    }

    for fmt in formats:
        if fmt in generators:
            gen_func, filename = generators[fmt]
            path = out / filename
            path.write_text(gen_func(report), encoding="utf-8")
            saved.append(path)

    return saved


def _xml_esc(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def _html_esc(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )
