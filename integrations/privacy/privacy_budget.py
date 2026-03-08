"""Privacy budget accounting.

Tracks differential-privacy epsilon budgets per query and per
site, detects budget exhaustion, and supports configurable
reset policies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class ResetPolicy(Enum):
    """When the privacy budget may be reset."""

    NEVER = "never"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    PER_EPOCH = "per_epoch"


class BudgetStatus(Enum):
    """Current status of a privacy budget."""

    AVAILABLE = "available"
    LOW = "low"
    EXHAUSTED = "exhausted"


@dataclass
class BudgetAllocation:
    """A single epsilon allocation against a budget."""

    allocation_id: str
    epsilon: float
    query_id: str
    site_id: str
    allocated_at: float = 0.0
    description: str = ""


@dataclass
class SiteBudget:
    """Privacy budget for a single site."""

    site_id: str
    total_epsilon: float
    consumed_epsilon: float = 0.0
    allocations: list[BudgetAllocation] = field(default_factory=list)
    reset_policy: ResetPolicy = ResetPolicy.NEVER
    last_reset_at: float = 0.0
    low_threshold: float = 0.1

    @property
    def remaining_epsilon(self) -> float:
        """Remaining epsilon budget."""
        return max(0.0, self.total_epsilon - self.consumed_epsilon)

    @property
    def status(self) -> BudgetStatus:
        """Current budget status."""
        if self.remaining_epsilon <= 0.0:
            return BudgetStatus.EXHAUSTED
        if self.remaining_epsilon <= self.low_threshold:
            return BudgetStatus.LOW
        return BudgetStatus.AVAILABLE


class PrivacyBudgetManager:
    """Manages differential-privacy epsilon budgets.

    Supports per-site budget tracking, allocation recording,
    exhaustion detection, and configurable reset policies.

    Parameters
    ----------
    default_epsilon:
        Default total epsilon for newly registered sites.
    default_reset_policy:
        Default reset policy for new sites.
    low_threshold:
        Remaining epsilon below which the budget is flagged
        as ``LOW``.
    """

    def __init__(
        self,
        *,
        default_epsilon: float = 1.0,
        default_reset_policy: ResetPolicy = ResetPolicy.NEVER,
        low_threshold: float = 0.1,
    ) -> None:
        self._default_epsilon = default_epsilon
        self._default_reset_policy = default_reset_policy
        self._low_threshold = low_threshold
        self._budgets: dict[str, SiteBudget] = {}
        self._next_alloc_id = 0

    # -- site registration ----------------------------------

    def register_site(
        self,
        site_id: str,
        *,
        total_epsilon: float | None = None,
        reset_policy: ResetPolicy | None = None,
    ) -> SiteBudget:
        """Register a site with an epsilon budget.

        Parameters
        ----------
        site_id:
            Unique site identifier.
        total_epsilon:
            Total epsilon budget; defaults to constructor
            value.
        reset_policy:
            Budget reset policy; defaults to constructor
            value.

        Returns
        -------
        SiteBudget
            The created budget record.
        """
        budget = SiteBudget(
            site_id=site_id,
            total_epsilon=(total_epsilon if total_epsilon is not None else self._default_epsilon),
            reset_policy=(reset_policy if reset_policy is not None else self._default_reset_policy),
            low_threshold=self._low_threshold,
            last_reset_at=time.time(),
        )
        self._budgets[site_id] = budget
        return budget

    def get_budget(self, site_id: str) -> SiteBudget:
        """Retrieve the budget for a site.

        Raises
        ------
        KeyError
            If the site has not been registered.
        """
        budget = self._budgets.get(site_id)
        if budget is None:
            raise KeyError(f"No budget registered for site {site_id!r}")
        return budget

    def list_budgets(self) -> list[SiteBudget]:
        """List all registered site budgets."""
        return list(self._budgets.values())

    # -- allocation -----------------------------------------

    def allocate(
        self,
        site_id: str,
        epsilon: float,
        query_id: str,
        *,
        description: str = "",
    ) -> BudgetAllocation:
        """Allocate epsilon from a site's budget.

        Parameters
        ----------
        site_id:
            Target site.
        epsilon:
            Amount of epsilon to consume.
        query_id:
            Identifier of the query/computation.
        description:
            Human-readable note.

        Returns
        -------
        BudgetAllocation
            The recorded allocation.

        Raises
        ------
        ValueError
            If the allocation would exceed the remaining
            budget.
        """
        budget = self.get_budget(site_id)
        if epsilon <= 0:
            raise ValueError("Epsilon allocation must be positive")
        if epsilon > budget.remaining_epsilon:
            raise ValueError(
                f"Allocation of {epsilon} exceeds remaining "
                f"budget {budget.remaining_epsilon:.6f} for "
                f"site {site_id!r}"
            )

        self._next_alloc_id += 1
        allocation = BudgetAllocation(
            allocation_id=f"alloc-{self._next_alloc_id}",
            epsilon=epsilon,
            query_id=query_id,
            site_id=site_id,
            allocated_at=time.time(),
            description=description,
        )
        budget.consumed_epsilon += epsilon
        budget.allocations.append(allocation)
        return allocation

    # -- exhaustion detection -------------------------------

    def is_exhausted(self, site_id: str) -> bool:
        """Return ``True`` when the site budget is exhausted."""
        return self.get_budget(site_id).status == BudgetStatus.EXHAUSTED

    def can_allocate(self, site_id: str, epsilon: float) -> bool:
        """Check whether *epsilon* can be allocated."""
        budget = self.get_budget(site_id)
        return epsilon <= budget.remaining_epsilon

    # -- reset ----------------------------------------------

    def reset_budget(self, site_id: str) -> SiteBudget:
        """Reset the consumed budget for a site.

        Returns
        -------
        SiteBudget
            The budget after reset.
        """
        budget = self.get_budget(site_id)
        budget.consumed_epsilon = 0.0
        budget.allocations.clear()
        budget.last_reset_at = time.time()
        return budget

    def apply_reset_policies(self) -> list[str]:
        """Apply automatic resets according to each site's
        :class:`ResetPolicy`.

        Returns
        -------
        list[str]
            Site IDs that were reset.
        """
        now = time.time()
        reset_sites: list[str] = []
        intervals: dict[ResetPolicy, float] = {
            ResetPolicy.DAILY: 86_400,
            ResetPolicy.WEEKLY: 604_800,
            ResetPolicy.MONTHLY: 2_592_000,
        }

        for site_id, budget in self._budgets.items():
            interval = intervals.get(budget.reset_policy)
            if interval is None:
                continue
            elapsed = now - budget.last_reset_at
            if elapsed >= interval:
                self.reset_budget(site_id)
                reset_sites.append(site_id)

        return reset_sites
