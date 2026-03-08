"""Federated coordinator abstractions.

Manages site enrollment, federated learning rounds, aggregation
coordination, and status tracking for the National MCP PAI
Oncology Trials platform.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SiteStatus(Enum):
    """Enrollment status of a participating site."""

    PENDING = "pending"
    ENROLLED = "enrolled"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"


class RoundPhase(Enum):
    """Phases within a single federated learning round."""

    INITIALIZE = "initialize"
    COLLECT = "collect"
    AGGREGATE = "aggregate"
    DISTRIBUTE = "distribute"
    COMPLETED = "completed"
    FAILED = "failed"


class FederationStatus(Enum):
    """Overall status of a federation session."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SiteEnrollment:
    """Enrollment record for a participating site."""

    site_id: str
    site_name: str
    status: SiteStatus = SiteStatus.PENDING
    enrolled_at: float | None = None
    capabilities: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RoundState:
    """State of a single federated learning round."""

    round_id: str
    round_number: int
    phase: RoundPhase = RoundPhase.INITIALIZE
    started_at: float = 0.0
    completed_at: float | None = None
    participating_sites: list[str] = field(default_factory=list)
    contributions_received: list[str] = field(default_factory=list)
    aggregation_result: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FederationSession:
    """A federated learning session across sites."""

    session_id: str
    trial_id: str
    status: FederationStatus = FederationStatus.CREATED
    enrolled_sites: list[SiteEnrollment] = field(default_factory=list)
    rounds: list[RoundState] = field(default_factory=list)
    current_round: int = 0
    total_rounds: int = 0
    created_at: float = 0.0
    config: dict[str, Any] = field(default_factory=dict)


class FederationCoordinator(ABC):
    """Abstract coordinator for federated learning.

    Implementations manage the full lifecycle of a federation
    session: site enrollment, round orchestration, aggregation
    coordination, and result distribution.
    """

    # -- session management ---------------------------------

    @abstractmethod
    async def create_session(
        self,
        trial_id: str,
        *,
        total_rounds: int = 1,
        config: dict[str, Any] | None = None,
    ) -> FederationSession:
        """Create a new federation session.

        Parameters
        ----------
        trial_id:
            Associated clinical trial identifier.
        total_rounds:
            Number of planned federated rounds.
        config:
            Session-level configuration.

        Returns
        -------
        FederationSession
            The newly created session.
        """

    @abstractmethod
    async def get_session(self, session_id: str) -> FederationSession:
        """Retrieve a federation session by ID."""

    @abstractmethod
    async def update_session_status(
        self,
        session_id: str,
        status: FederationStatus,
    ) -> FederationSession:
        """Transition the session to a new status."""

    # -- site enrollment ------------------------------------

    @abstractmethod
    async def enroll_site(
        self,
        session_id: str,
        site_id: str,
        site_name: str,
        *,
        capabilities: dict[str, Any] | None = None,
    ) -> SiteEnrollment:
        """Enroll a site in a federation session.

        Returns
        -------
        SiteEnrollment
            The enrollment record.
        """

    @abstractmethod
    async def update_site_status(
        self,
        session_id: str,
        site_id: str,
        status: SiteStatus,
    ) -> SiteEnrollment:
        """Update enrollment status for a site."""

    @abstractmethod
    async def list_enrolled_sites(
        self,
        session_id: str,
        *,
        status: SiteStatus | None = None,
    ) -> list[SiteEnrollment]:
        """List sites enrolled in a session."""

    # -- round management -----------------------------------

    @abstractmethod
    async def initialize_round(
        self,
        session_id: str,
    ) -> RoundState:
        """Initialize the next federated round.

        Returns
        -------
        RoundState
            The new round in ``INITIALIZE`` phase.
        """

    @abstractmethod
    async def record_contribution(
        self,
        session_id: str,
        round_id: str,
        site_id: str,
        contribution: dict[str, Any],
    ) -> RoundState:
        """Record a site's contribution for the current round."""

    @abstractmethod
    async def advance_phase(
        self,
        session_id: str,
        round_id: str,
        phase: RoundPhase,
    ) -> RoundState:
        """Move a round to the next phase."""

    # -- aggregation ----------------------------------------

    @abstractmethod
    async def aggregate(
        self,
        session_id: str,
        round_id: str,
    ) -> dict[str, Any]:
        """Trigger aggregation for a completed round.

        Returns
        -------
        dict[str, Any]
            Aggregated result payload.
        """

    @abstractmethod
    async def distribute_result(
        self,
        session_id: str,
        round_id: str,
    ) -> RoundState:
        """Distribute aggregated results back to sites."""

    # -- status / tracking ----------------------------------

    @abstractmethod
    async def get_round_status(
        self,
        session_id: str,
        round_id: str,
    ) -> RoundState:
        """Get the current state of a round."""

    @abstractmethod
    async def list_rounds(self, session_id: str) -> list[RoundState]:
        """List all rounds in a session."""
