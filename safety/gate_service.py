"""Safety gate service and policy layer.

Implements pre-procedure safety matrix evaluation with
multi-condition gate checking. Every gate decision is recorded
in an audit trail for regulatory traceability.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class GateStatus(Enum):
    """Evaluation status of an individual safety gate."""

    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


@dataclass
class GateCondition:
    """A single condition within the safety gate matrix.

    Attributes:
        name: Human-readable gate name.
        status: Current evaluation status.
        details: Free-text explanation or evidence reference.
        evaluated_at: Timestamp of evaluation.
    """

    name: str
    status: GateStatus
    details: str = ""
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class GateDecision:
    """Aggregate result of a full safety-gate evaluation.

    Attributes:
        decision_id: Unique identifier for this decision.
        procedure_id: Procedure being evaluated.
        overall_pass: True only when every condition is PASS.
        conditions: Ordered list of evaluated conditions.
        decided_at: Timestamp of the aggregate decision.
    """

    decision_id: str
    procedure_id: str
    overall_pass: bool
    conditions: list[GateCondition]
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SafetyGateService:
    """Evaluates the pre-procedure safety matrix.

    The service checks five mandatory gates before a procedure
    may proceed:

    1. Patient consent verification
    2. Site capability confirmation
    3. Robot capability confirmation
    4. Trial protocol compliance
    5. Human approval on file

    All decisions are persisted in an internal audit trail.
    """

    def __init__(self) -> None:
        self._audit_trail: list[GateDecision] = []

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def evaluate_gates(
        self,
        procedure_id: str,
        patient_consent: dict[str, Any],
        site_capability: dict[str, Any],
        robot_capability: dict[str, Any],
        trial_protocol: dict[str, Any],
        human_approval: dict[str, Any],
    ) -> GateDecision:
        """Run the full safety-gate matrix for a procedure.

        Args:
            procedure_id: Unique procedure identifier.
            patient_consent: Evidence of valid patient consent.
            site_capability: Site capability profile payload.
            robot_capability: Robot capability profile payload.
            trial_protocol: Trial protocol descriptor.
            human_approval: Human-in-the-loop approval record.

        Returns:
            A ``GateDecision`` with per-condition results and
            an overall pass/fail determination.
        """
        conditions: list[GateCondition] = [
            self._check_patient_consent(patient_consent),
            self._check_site_capability(site_capability),
            self._check_robot_capability(robot_capability),
            self._check_trial_protocol(trial_protocol),
            self._check_human_approval(human_approval),
        ]
        overall = all(c.status == GateStatus.PASS for c in conditions)
        decision = GateDecision(
            decision_id=str(uuid.uuid4()),
            procedure_id=procedure_id,
            overall_pass=overall,
            conditions=conditions,
        )
        self._audit_trail.append(decision)
        return decision

    def get_audit_trail(
        self,
        procedure_id: str | None = None,
    ) -> list[GateDecision]:
        """Return recorded gate decisions.

        Args:
            procedure_id: If provided, filter to this procedure.

        Returns:
            List of ``GateDecision`` records.
        """
        if procedure_id is None:
            return list(self._audit_trail)
        return [d for d in self._audit_trail if d.procedure_id == procedure_id]

    # ----------------------------------------------------------
    # Individual gate checks
    # ----------------------------------------------------------

    @staticmethod
    def _check_patient_consent(
        data: dict[str, Any],
    ) -> GateCondition:
        """Verify patient consent is recorded and valid."""
        consent_given = data.get("consent_given", False)
        consent_date = data.get("consent_date")
        if consent_given and consent_date:
            return GateCondition(
                name="patient_consent",
                status=GateStatus.PASS,
                details=(f"Consent recorded on {consent_date}"),
            )
        return GateCondition(
            name="patient_consent",
            status=GateStatus.FAIL,
            details="Missing or invalid patient consent",
        )

    @staticmethod
    def _check_site_capability(
        data: dict[str, Any],
    ) -> GateCondition:
        """Verify that the site meets capability requirements."""
        verified = data.get("verified", False)
        site_id = data.get("site_id", "unknown")
        if verified:
            return GateCondition(
                name="site_capability",
                status=GateStatus.PASS,
                details=f"Site {site_id} verified",
            )
        return GateCondition(
            name="site_capability",
            status=GateStatus.FAIL,
            details=f"Site {site_id} not verified",
        )

    @staticmethod
    def _check_robot_capability(
        data: dict[str, Any],
    ) -> GateCondition:
        """Verify robot capability matches the procedure."""
        eligible = data.get("eligible", False)
        robot_id = data.get("robot_id", "unknown")
        if eligible:
            return GateCondition(
                name="robot_capability",
                status=GateStatus.PASS,
                details=f"Robot {robot_id} eligible",
            )
        return GateCondition(
            name="robot_capability",
            status=GateStatus.FAIL,
            details=f"Robot {robot_id} not eligible",
        )

    @staticmethod
    def _check_trial_protocol(
        data: dict[str, Any],
    ) -> GateCondition:
        """Verify compliance with trial protocol constraints."""
        compliant = data.get("compliant", False)
        protocol_id = data.get("protocol_id", "unknown")
        if compliant:
            return GateCondition(
                name="trial_protocol",
                status=GateStatus.PASS,
                details=(f"Protocol {protocol_id} compliant"),
            )
        return GateCondition(
            name="trial_protocol",
            status=GateStatus.FAIL,
            details=(f"Protocol {protocol_id} non-compliant"),
        )

    @staticmethod
    def _check_human_approval(
        data: dict[str, Any],
    ) -> GateCondition:
        """Verify human-in-the-loop approval is on file."""
        approved = data.get("approved", False)
        approver = data.get("approver", "unknown")
        if approved:
            return GateCondition(
                name="human_approval",
                status=GateStatus.PASS,
                details=f"Approved by {approver}",
            )
        if data.get("pending", False):
            return GateCondition(
                name="human_approval",
                status=GateStatus.PENDING,
                details="Awaiting human approval",
            )
        return GateCondition(
            name="human_approval",
            status=GateStatus.FAIL,
            details="Human approval denied or missing",
        )
