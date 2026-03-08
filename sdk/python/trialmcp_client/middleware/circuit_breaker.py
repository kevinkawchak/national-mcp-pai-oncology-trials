"""Circuit breaker for clinical dependency resilience.

Implements the three-state circuit breaker pattern (CLOSED -> OPEN ->
HALF-OPEN -> CLOSED) to prevent cascading failures when an MCP server
becomes unresponsive.  Each of the five servers has an independent breaker.
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any

from ..config import CircuitBreakerPolicy, ServerName
from ..exceptions import UnavailableError

logger = logging.getLogger("trialmcp.middleware.circuit_breaker")


class CircuitState(str, Enum):
    """The three states of a circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Per-server circuit breaker.

    State transitions:

    * **CLOSED** (healthy): requests pass through normally.  Consecutive
      failures are counted.
    * **OPEN** (tripped): all requests are rejected immediately with
      :class:`UnavailableError`.  After ``recovery_timeout_seconds`` the
      breaker transitions to HALF-OPEN.
    * **HALF-OPEN** (probing): a limited number of requests are allowed
      through.  If they succeed the breaker returns to CLOSED; if they
      fail it re-opens.

    Parameters
    ----------
    server_name:
        Human-readable server identifier for logging.
    policy:
        The :class:`CircuitBreakerPolicy` governing thresholds and timeouts.
    """

    def __init__(
        self,
        server_name: str,
        policy: CircuitBreakerPolicy | None = None,
    ) -> None:
        self._server = server_name
        self._policy = policy or CircuitBreakerPolicy()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0
        self._half_open_calls = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> CircuitState:
        """Current state of the circuit breaker, accounting for recovery."""
        if self._state == CircuitState.OPEN:
            if self._recovery_elapsed():
                self._transition(CircuitState.HALF_OPEN)
        return self._state

    @property
    def failure_count(self) -> int:
        """Number of consecutive failures recorded."""
        return self._failure_count

    def check(self) -> None:
        """Gate a request through the circuit breaker.

        Raises
        ------
        UnavailableError:
            If the circuit is OPEN and the recovery timeout has not elapsed.
        """
        current = self.state  # triggers OPEN -> HALF_OPEN transition if ready

        if current == CircuitState.OPEN:
            logger.warning("Circuit breaker OPEN for %s — rejecting request", self._server)
            raise UnavailableError(
                f"Circuit breaker open for {self._server}; server is temporarily unavailable",
                server=self._server,
            )

        if current == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self._policy.half_open_max_calls:
                logger.warning(
                    "Circuit breaker HALF-OPEN call limit reached for %s",
                    self._server,
                )
                raise UnavailableError(
                    f"Circuit breaker half-open probe limit reached for {self._server}",
                    server=self._server,
                )
            self._half_open_calls += 1

    def record_success(self) -> None:
        """Record a successful request."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            logger.info(
                "Circuit breaker probe success for %s (%d/%d)",
                self._server,
                self._success_count,
                self._policy.half_open_max_calls,
            )
            if self._success_count >= self._policy.half_open_max_calls:
                self._transition(CircuitState.CLOSED)
        elif self._state == CircuitState.CLOSED:
            # Reset failure counter on success
            if self._failure_count > 0:
                logger.debug("Resetting failure count for %s after success", self._server)
                self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed request."""
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker probe failed for %s — re-opening", self._server)
            self._transition(CircuitState.OPEN)

        elif self._state == CircuitState.CLOSED:
            if self._failure_count >= self._policy.failure_threshold:
                logger.error(
                    "Circuit breaker tripping for %s after %d failures",
                    self._server,
                    self._failure_count,
                )
                self._transition(CircuitState.OPEN)

    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED."""
        self._transition(CircuitState.CLOSED)

    def to_dict(self) -> dict[str, Any]:
        """Serialise the breaker state for diagnostics."""
        return {
            "server": self._server,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "last_failure_time": self._last_failure_time,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _recovery_elapsed(self) -> bool:
        """True if enough time has passed since the last failure."""
        elapsed = time.monotonic() - self._last_failure_time
        return elapsed >= self._policy.recovery_timeout_seconds

    def _transition(self, new_state: CircuitState) -> None:
        """Perform a state transition with appropriate resets."""
        old = self._state
        self._state = new_state
        logger.info("Circuit breaker %s: %s -> %s", self._server, old.value, new_state.value)

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
            self._success_count = 0
        elif new_state == CircuitState.OPEN:
            self._half_open_calls = 0
            self._success_count = 0


class CircuitBreakerRegistry:
    """Manages per-server circuit breakers.

    Parameters
    ----------
    policy:
        Default :class:`CircuitBreakerPolicy` applied to all breakers.
    """

    def __init__(self, policy: CircuitBreakerPolicy | None = None) -> None:
        self._policy = policy or CircuitBreakerPolicy()
        self._breakers: dict[str, CircuitBreaker] = {}

    def get(self, server: ServerName | str) -> CircuitBreaker:
        """Return (or create) the circuit breaker for *server*.

        Parameters
        ----------
        server:
            A :class:`ServerName` enum member or a plain string.
        """
        key = server.value if isinstance(server, ServerName) else server
        if key not in self._breakers:
            self._breakers[key] = CircuitBreaker(key, self._policy)
        return self._breakers[key]

    def status(self) -> dict[str, dict[str, Any]]:
        """Return the current state of all tracked circuit breakers."""
        return {name: cb.to_dict() for name, cb in self._breakers.items()}

    def reset_all(self) -> None:
        """Reset all circuit breakers to CLOSED."""
        for cb in self._breakers.values():
            cb.reset()
