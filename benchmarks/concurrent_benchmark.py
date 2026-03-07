"""Concurrent access pattern benchmarks.

Measures performance under concurrent access patterns
and contention scenarios for national-scale deployment readiness.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from conformance.fixtures.audit_records import make_audit_record
from conformance.fixtures.provenance_records import make_provenance_record


@dataclass
class ConcurrentResult:
    """Result of a concurrent benchmark run."""

    operation: str
    threads: int
    total_operations: int
    duration_seconds: float
    operations_per_second: float
    errors: int = 0


def concurrent_audit_records(threads: int = 4, operations: int = 100) -> ConcurrentResult:
    """Benchmark concurrent audit record creation.

    Args:
        threads: Number of concurrent threads.
        operations: Total number of operations to perform.

    Returns:
        ConcurrentResult with performance metrics.
    """
    errors = 0

    def create_record() -> bool:
        try:
            make_audit_record()
            return True
        except Exception:
            return False

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(create_record) for _ in range(operations)]
        for future in as_completed(futures):
            if not future.result():
                errors += 1
    elapsed = time.perf_counter() - start

    return ConcurrentResult(
        operation="audit_record_creation",
        threads=threads,
        total_operations=operations,
        duration_seconds=elapsed,
        operations_per_second=operations / elapsed if elapsed > 0 else 0,
        errors=errors,
    )


def concurrent_provenance_records(threads: int = 4, operations: int = 100) -> ConcurrentResult:
    """Benchmark concurrent provenance record creation.

    Args:
        threads: Number of concurrent threads.
        operations: Total number of operations to perform.

    Returns:
        ConcurrentResult with performance metrics.
    """
    errors = 0

    def create_record() -> bool:
        try:
            make_provenance_record()
            return True
        except Exception:
            return False

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(create_record) for _ in range(operations)]
        for future in as_completed(futures):
            if not future.result():
                errors += 1
    elapsed = time.perf_counter() - start

    return ConcurrentResult(
        operation="provenance_record_creation",
        threads=threads,
        total_operations=operations,
        duration_seconds=elapsed,
        operations_per_second=operations / elapsed if elapsed > 0 else 0,
        errors=errors,
    )


def run_all_benchmarks() -> list[ConcurrentResult]:
    """Run all concurrent benchmarks.

    Returns:
        List of ConcurrentResult for each benchmark.
    """
    results = []
    for threads in [1, 2, 4, 8]:
        results.append(concurrent_audit_records(threads=threads, operations=50))
        results.append(concurrent_provenance_records(threads=threads, operations=50))
    return results
