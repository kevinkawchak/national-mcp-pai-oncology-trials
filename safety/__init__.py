"""Physical AI safety enforcement for national MCP oncology trials.

This package implements robot safety and execution boundaries
for the national MCP standard governing Physical AI oncology
clinical trials. It provides:

- Safety gate evaluation and policy enforcement
- Robot capability registration and eligibility matching
- Task-order validation with pre/post-condition contracts
- Mandatory human-in-the-loop approval checkpoints
- Emergency stop signal propagation and recovery
- Procedure state machine with transition validation
- Site capability verification and regulatory compliance

All modules enforce simulation-only vs clinical-mode
boundaries and maintain full audit trails for regulatory
compliance.
"""

from __future__ import annotations

from safety.approval_checkpoint import (
    ApprovalCheckpoint,
    ApprovalRequest,
    ApprovalResponse,
)
from safety.estop import EStopController, EStopSignal
from safety.gate_service import GateCondition, SafetyGateService
from safety.procedure_state import ProcedureMode, ProcedureState
from safety.robot_registry import RobotEntry, RobotRegistry
from safety.site_verifier import (
    SiteVerificationResult,
    SiteVerifier,
)
from safety.task_validator import TaskValidationResult, TaskValidator

__all__ = [
    "ApprovalCheckpoint",
    "ApprovalRequest",
    "ApprovalResponse",
    "EStopController",
    "EStopSignal",
    "GateCondition",
    "ProcedureMode",
    "ProcedureState",
    "RobotEntry",
    "RobotRegistry",
    "SafetyGateService",
    "SiteVerificationResult",
    "SiteVerifier",
    "TaskValidationResult",
    "TaskValidator",
]
