"""Audit chain verification performance benchmarks.

Measures chain construction and verification performance
at increasing scale to ensure national deployment readiness.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from conformance.fixtures.audit_records import (
    compute_audit_hash,
    make_audit_chain,
)


@dataclass
class ChainBenchmarkResult:
    """Result of a chain benchmark run."""

    chain_length: int
    construction_ms: float
    verification_ms: float
    records_per_second: float


def benchmark_chain_construction(length: int) -> float:
    """Benchmark chain construction at a given length.

    Args:
        length: Number of records in the chain.

    Returns:
        Construction time in milliseconds.
    """
    start = time.perf_counter()
    make_audit_chain(length=length)
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed


def benchmark_chain_verification(chain: list[dict]) -> float:
    """Benchmark chain verification.

    Args:
        chain: Audit chain to verify.

    Returns:
        Verification time in milliseconds.
    """
    start = time.perf_counter()
    for i, record in enumerate(chain):
        computed = compute_audit_hash(record)
        if computed != record["hash"]:
            break
        if i > 0 and record["previous_hash"] != chain[i - 1]["hash"]:
            break
    elapsed = (time.perf_counter() - start) * 1000
    return elapsed


def run_all_benchmarks() -> list[ChainBenchmarkResult]:
    """Run chain benchmarks at multiple scales.

    Returns:
        List of ChainBenchmarkResult at different chain lengths.
    """
    results = []
    for length in [10, 50, 100, 500]:
        construction_ms = benchmark_chain_construction(length)
        chain = make_audit_chain(length=length)
        verification_ms = benchmark_chain_verification(chain)

        rps = (length / (construction_ms / 1000)) if construction_ms > 0 else 0

        results.append(
            ChainBenchmarkResult(
                chain_length=length,
                construction_ms=construction_ms,
                verification_ms=verification_ms,
                records_per_second=rps,
            )
        )

    return results
