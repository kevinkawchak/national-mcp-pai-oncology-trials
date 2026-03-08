"""Scheduling/task-order adapter.

Manages procedure scheduling, robot assignment, time-window
management, conflict detection, and schedule validation for
Physical AI oncology clinical trial procedures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProcedureStatus(Enum):
    """Lifecycle status of a scheduled procedure."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ConflictType(Enum):
    """Types of scheduling conflicts."""

    TIME_OVERLAP = "time_overlap"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    ROBOT_ALREADY_ASSIGNED = "robot_already_assigned"
    PARTICIPANT_CONFLICT = "participant_conflict"
    FACILITY_CAPACITY = "facility_capacity"


@dataclass(frozen=True)
class TimeWindow:
    """A time window defined by ISO-8601 timestamps."""

    start: str
    end: str
    timezone: str = "UTC"


@dataclass(frozen=True)
class RobotAssignment:
    """Assignment of a robotic system to a procedure."""

    robot_id: str
    robot_type: str
    capability: str
    assigned_at: str
    notes: str = ""


@dataclass
class ScheduledProcedure:
    """A scheduled clinical trial procedure."""

    procedure_id: str
    trial_id: str
    participant_id: str
    procedure_type: str
    status: ProcedureStatus
    time_window: TimeWindow
    site_id: str
    robot_assignments: list[RobotAssignment] = field(default_factory=list)
    task_order_ref: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScheduleConflict:
    """A detected scheduling conflict."""

    conflict_type: ConflictType
    procedure_id: str
    conflicting_procedure_id: str | None = None
    description: str = ""
    resolution_hint: str = ""


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of schedule validation against task-order
    schema.
    """

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SchedulingAdapter(ABC):
    """Abstract adapter for clinical procedure scheduling.

    Provides a uniform interface for scheduling systems that
    manage Physical AI oncology trial procedures including
    robotic interventions.
    """

    # -- procedure scheduling -------------------------------

    @abstractmethod
    async def create_procedure(
        self,
        trial_id: str,
        participant_id: str,
        procedure_type: str,
        time_window: TimeWindow,
        site_id: str,
        *,
        task_order_ref: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ScheduledProcedure:
        """Create a new scheduled procedure.

        Returns
        -------
        ScheduledProcedure
            The created procedure record.
        """

    @abstractmethod
    async def get_procedure(self, procedure_id: str) -> ScheduledProcedure:
        """Retrieve a procedure by ID."""

    @abstractmethod
    async def update_procedure_status(
        self,
        procedure_id: str,
        status: ProcedureStatus,
    ) -> ScheduledProcedure:
        """Transition a procedure to a new status."""

    @abstractmethod
    async def list_procedures(
        self,
        trial_id: str,
        *,
        site_id: str | None = None,
        participant_id: str | None = None,
        status: ProcedureStatus | None = None,
    ) -> list[ScheduledProcedure]:
        """List procedures with optional filters."""

    # -- robot assignment -----------------------------------

    @abstractmethod
    async def assign_robot(
        self,
        procedure_id: str,
        robot_id: str,
        robot_type: str,
        capability: str,
        *,
        notes: str = "",
    ) -> RobotAssignment:
        """Assign a robotic system to a procedure.

        Raises
        ------
        ValueError
            If the robot is unavailable during the procedure's
            time window.
        """

    @abstractmethod
    async def unassign_robot(
        self,
        procedure_id: str,
        robot_id: str,
    ) -> None:
        """Remove a robot assignment from a procedure."""

    # -- time-window management -----------------------------

    @abstractmethod
    async def reschedule(
        self,
        procedure_id: str,
        new_window: TimeWindow,
    ) -> ScheduledProcedure:
        """Move a procedure to a new time window.

        Raises
        ------
        ValueError
            If the new window causes conflicts.
        """

    # -- conflict detection ---------------------------------

    @abstractmethod
    async def detect_conflicts(
        self,
        procedure_id: str,
    ) -> list[ScheduleConflict]:
        """Detect scheduling conflicts for a procedure.

        Returns
        -------
        list[ScheduleConflict]
            All detected conflicts, empty if none.
        """

    @abstractmethod
    async def detect_conflicts_for_window(
        self,
        site_id: str,
        time_window: TimeWindow,
        *,
        exclude_procedure_id: str | None = None,
    ) -> list[ScheduleConflict]:
        """Detect conflicts within a time window at a site."""

    # -- validation -----------------------------------------

    @abstractmethod
    async def validate_schedule(
        self,
        trial_id: str,
        site_id: str,
    ) -> ValidationResult:
        """Validate the full schedule for a site against the
        task-order schema.

        Returns
        -------
        ValidationResult
            Validation outcome with errors and warnings.
        """
