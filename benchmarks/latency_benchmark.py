"""Latency benchmarks for each MCP server tool.

Measures request-response latency for all tool operations
across the 5 MCP servers.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class LatencyResult:
    """Result of a latency benchmark run."""

    server: str
    tool: str
    samples: int
    min_ms: float = 0.0
    max_ms: float = 0.0
    mean_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0


def measure_latency(func: Any, iterations: int = 100) -> list[float]:
    """Measure function execution latency.

    Args:
        func: Callable to benchmark.
        iterations: Number of iterations to run.

    Returns:
        List of latency measurements in milliseconds.
    """
    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        latencies.append((end - start) * 1000)
    return latencies


def compute_stats(latencies: list[float]) -> dict[str, float]:
    """Compute latency statistics.

    Args:
        latencies: List of latency measurements in milliseconds.

    Returns:
        Dictionary with min, max, mean, p50, p95, p99 statistics.
    """
    if not latencies:
        return {"min": 0, "max": 0, "mean": 0, "p50": 0, "p95": 0, "p99": 0}

    sorted_lat = sorted(latencies)
    n = len(sorted_lat)

    return {
        "min": sorted_lat[0],
        "max": sorted_lat[-1],
        "mean": sum(sorted_lat) / n,
        "p50": sorted_lat[n // 2],
        "p95": sorted_lat[int(n * 0.95)],
        "p99": sorted_lat[int(n * 0.99)],
    }


def benchmark_audit_hash() -> LatencyResult:
    """Benchmark audit hash computation latency."""
    from conformance.fixtures.audit_records import compute_audit_hash, make_audit_record

    record = make_audit_record()
    latencies = measure_latency(lambda: compute_audit_hash(record), iterations=1000)
    stats = compute_stats(latencies)

    return LatencyResult(
        server="trialmcp-ledger",
        tool="compute_audit_hash",
        samples=1000,
        min_ms=stats["min"],
        max_ms=stats["max"],
        mean_ms=stats["mean"],
        p50_ms=stats["p50"],
        p95_ms=stats["p95"],
        p99_ms=stats["p99"],
    )


def benchmark_chain_construction() -> LatencyResult:
    """Benchmark audit chain construction latency."""
    from conformance.fixtures.audit_records import make_audit_chain

    latencies = measure_latency(lambda: make_audit_chain(length=10), iterations=100)
    stats = compute_stats(latencies)

    return LatencyResult(
        server="trialmcp-ledger",
        tool="make_audit_chain",
        samples=100,
        min_ms=stats["min"],
        max_ms=stats["max"],
        mean_ms=stats["mean"],
        p50_ms=stats["p50"],
        p95_ms=stats["p95"],
        p99_ms=stats["p99"],
    )


def run_all_benchmarks() -> list[LatencyResult]:
    """Run all latency benchmarks.

    Returns:
        List of LatencyResult for each benchmark.
    """
    return [
        benchmark_audit_hash(),
        benchmark_chain_construction(),
    ]
