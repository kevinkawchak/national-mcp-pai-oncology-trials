"""Configurable retry middleware with exponential backoff.

Implements a retry strategy suitable for clinical-trial workloads where
transient failures (rate-limiting, temporary unavailability) are expected
but data-integrity errors must never be silently retried.
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any, Awaitable, Callable

from ..config import RetryPolicy
from ..exceptions import RateLimitedError, TrialMCPError

logger = logging.getLogger("trialmcp.middleware.retry")

# Error codes that are *never* retried regardless of policy
_NON_RETRYABLE_CODES = frozenset(
    {
        "AUTHZ_DENIED",
        "PERMISSION_DENIED",
        "INVALID_INPUT",
        "VALIDATION_FAILED",
        "NOT_FOUND",
        "CHAIN_BROKEN",
        "PHI_LEAK",
    }
)


class RetryMiddleware:
    """Middleware that retries failed tool calls with exponential backoff.

    Only errors whose ``code`` appears in :pyattr:`RetryPolicy.retryable_codes`
    are retried.  Safety-critical error codes (e.g. ``CHAIN_BROKEN``,
    ``PHI_LEAK``) are never retried.

    Parameters
    ----------
    policy:
        The :class:`RetryPolicy` governing retry behaviour.
    """

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self._policy = policy or RetryPolicy()

    async def execute(
        self,
        operation: Callable[[], Awaitable[dict[str, Any]]],
        *,
        server_name: str = "",
    ) -> dict[str, Any]:
        """Execute *operation* with automatic retries on transient failures.

        Parameters
        ----------
        operation:
            An async callable that performs the actual MCP tool call.
        server_name:
            Server name for logging purposes.

        Returns
        -------
        dict:
            The successful response from *operation*.

        Raises
        ------
        TrialMCPError:
            The last error if all retry attempts are exhausted, or a
            non-retryable error on the first occurrence.
        """
        last_error: TrialMCPError | None = None

        for attempt in range(1 + self._policy.max_retries):
            try:
                return await operation()

            except TrialMCPError as exc:
                last_error = exc

                # Never retry safety-critical or deterministic errors
                if exc.code in _NON_RETRYABLE_CODES:
                    logger.warning(
                        "Non-retryable error %s from %s (attempt %d): %s",
                        exc.code,
                        server_name,
                        attempt + 1,
                        exc.message,
                    )
                    raise

                # Check if this error code is in the retryable set
                if exc.code not in self._policy.retryable_codes:
                    logger.warning(
                        "Error %s not in retryable set for %s: %s",
                        exc.code,
                        server_name,
                        exc.message,
                    )
                    raise

                if attempt >= self._policy.max_retries:
                    logger.error(
                        "All %d retries exhausted for %s: %s",
                        self._policy.max_retries,
                        server_name,
                        exc.message,
                    )
                    raise

                delay = self._compute_delay(attempt, exc)
                logger.info(
                    "Retryable error %s from %s (attempt %d/%d), backing off %.2fs: %s",
                    exc.code,
                    server_name,
                    attempt + 1,
                    self._policy.max_retries,
                    delay,
                    exc.message,
                )
                await asyncio.sleep(delay)

        # Should not be reached, but satisfy type checker
        if last_error:
            raise last_error
        return {}  # pragma: no cover

    def _compute_delay(self, attempt: int, error: TrialMCPError) -> float:
        """Calculate the backoff delay for the given attempt.

        For ``RATE_LIMITED`` errors the server-specified ``retry_after``
        value takes precedence over the computed exponential delay.

        Parameters
        ----------
        attempt:
            Zero-based attempt index.
        error:
            The error that triggered the retry.

        Returns
        -------
        float:
            Delay in seconds.
        """
        # Honour server-specified retry-after for rate limiting
        if isinstance(error, RateLimitedError) and error.retry_after is not None:
            return float(error.retry_after)

        # Exponential backoff with jitter
        base = self._policy.base_delay_seconds
        exp = self._policy.exponential_base**attempt
        delay = base * exp

        # Add up to 25% jitter
        jitter = delay * 0.25 * random.random()  # noqa: S311
        delay += jitter

        return min(delay, self._policy.max_delay_seconds)

    @property
    def policy(self) -> RetryPolicy:
        """Return the active retry policy."""
        return self._policy
