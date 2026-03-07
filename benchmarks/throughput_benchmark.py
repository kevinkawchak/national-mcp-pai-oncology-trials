"""Throughput benchmarks for MCP servers.

Measures requests-per-second capacity for each server type.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ThroughputResult:
    """Result of a throughput benchmark run."""

    server: str
    tool: str
    total_requests: int
    duration_seconds: float
    requests_per_second: float


def measure_throughput(func: Any, duration_seconds: float = 1.0) -> ThroughputResult:
    """Measure operation throughput.

    Args:
        func: Callable to benchmark. Must accept no arguments.
        duration_seconds: Duration to run the benchmark.

    Returns:
        ThroughputResult with requests per second.
    """
    count = 0
    start = time.perf_counter()
    deadline = start + duration_seconds

    while time.perf_counter() < deadline:
        func()
        count += 1

    elapsed = time.perf_counter() - start
    return ThroughputResult(
        server="",
        tool="",
        total_requests=count,
        duration_seconds=elapsed,
        requests_per_second=count / elapsed if elapsed > 0 else 0,
    )


def benchmark_authz_evaluate_throughput() -> ThroughputResult:
    """Benchmark AuthZ evaluate throughput."""
    from conformance.fixtures.authz_decisions import make_allow_decision

    result = measure_throughput(make_allow_decision, duration_seconds=1.0)
    result.server = "trialmcp-authz"
    result.tool = "authz_evaluate"
    return result


def benchmark_audit_record_throughput() -> ThroughputResult:
    """Benchmark audit record creation throughput."""
    from conformance.fixtures.audit_records import make_audit_record

    result = measure_throughput(make_audit_record, duration_seconds=1.0)
    result.server = "trialmcp-ledger"
    result.tool = "ledger_append"
    return result


def benchmark_provenance_record_throughput() -> ThroughputResult:
    """Benchmark provenance record creation throughput."""
    from conformance.fixtures.provenance_records import make_provenance_record

    result = measure_throughput(make_provenance_record, duration_seconds=1.0)
    result.server = "trialmcp-provenance"
    result.tool = "provenance_record_access"
    return result


def run_all_benchmarks() -> list[ThroughputResult]:
    """Run all throughput benchmarks.

    Returns:
        List of ThroughputResult for each benchmark.
    """
    return [
        benchmark_authz_evaluate_throughput(),
        benchmark_audit_record_throughput(),
        benchmark_provenance_record_throughput(),
    ]
