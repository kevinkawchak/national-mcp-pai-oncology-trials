"""Benchmark report generator with historical comparison.

Generates benchmark reports from latency, throughput, chain,
and concurrent benchmark results with optional historical comparison.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def generate_benchmark_report(
    latency_results: list[Any] | None = None,
    throughput_results: list[Any] | None = None,
    chain_results: list[Any] | None = None,
    concurrent_results: list[Any] | None = None,
) -> dict[str, Any]:
    """Generate a comprehensive benchmark report.

    Args:
        latency_results: Latency benchmark results.
        throughput_results: Throughput benchmark results.
        chain_results: Chain benchmark results.
        concurrent_results: Concurrent benchmark results.

    Returns:
        Complete benchmark report dictionary.
    """
    report = {
        "version": "0.8.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmarks": {},
    }

    if latency_results:
        report["benchmarks"]["latency"] = [asdict(r) for r in latency_results]

    if throughput_results:
        report["benchmarks"]["throughput"] = [asdict(r) for r in throughput_results]

    if chain_results:
        report["benchmarks"]["chain"] = [asdict(r) for r in chain_results]

    if concurrent_results:
        report["benchmarks"]["concurrent"] = [asdict(r) for r in concurrent_results]

    return report


def compare_with_baseline(
    current: dict[str, Any],
    baseline: dict[str, Any],
    threshold_pct: float = 20.0,
) -> dict[str, Any]:
    """Compare current results against a baseline.

    Args:
        current: Current benchmark results.
        baseline: Baseline benchmark results.
        threshold_pct: Percentage threshold for regression detection.

    Returns:
        Comparison report with regression flags.
    """
    regressions = []

    for category in current.get("benchmarks", {}):
        if category not in baseline.get("benchmarks", {}):
            continue

        current_items = current["benchmarks"][category]
        baseline_items = baseline["benchmarks"][category]

        for c_item, b_item in zip(current_items, baseline_items):
            # Check for latency regressions (higher is worse)
            if "mean_ms" in c_item and "mean_ms" in b_item:
                if b_item["mean_ms"] > 0:
                    pct_change = (c_item["mean_ms"] - b_item["mean_ms"]) / b_item["mean_ms"] * 100
                    if pct_change > threshold_pct:
                        regressions.append(
                            {
                                "category": category,
                                "metric": "mean_ms",
                                "baseline": b_item["mean_ms"],
                                "current": c_item["mean_ms"],
                                "change_pct": pct_change,
                            }
                        )

            # Check for throughput regressions (lower is worse)
            if "requests_per_second" in c_item and "requests_per_second" in b_item:
                if b_item["requests_per_second"] > 0:
                    pct_change = (
                        (b_item["requests_per_second"] - c_item["requests_per_second"])
                        / b_item["requests_per_second"]
                        * 100
                    )
                    if pct_change > threshold_pct:
                        regressions.append(
                            {
                                "category": category,
                                "metric": "requests_per_second",
                                "baseline": b_item["requests_per_second"],
                                "current": c_item["requests_per_second"],
                                "change_pct": pct_change,
                            }
                        )

    return {
        "regressions_found": len(regressions) > 0,
        "regression_count": len(regressions),
        "threshold_pct": threshold_pct,
        "regressions": regressions,
    }


def save_report(report: dict[str, Any], output_dir: str | Path) -> Path:
    """Save benchmark report to a JSON file.

    Args:
        report: Benchmark report dictionary.
        output_dir: Output directory.

    Returns:
        Path to the saved report file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "benchmark-report.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
