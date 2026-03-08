"""Comprehensive tests for safety modules.

Covers the safety gate service, robot registry, task validator,
approval checkpoint, e-stop controller, procedure state machine,
and site verifier.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from safety.approval_checkpoint import (
    ApprovalCheckpoint,
    ApprovalStatus,
)
from safety.estop import EStopController
from safety.gate_service import (
    GateStatus,
    SafetyGateService,
)
from safety.procedure_state import (
    ProcedureMode,
    ProcedureState,
    ProcedureStatus,
)
from safety.robot_registry import (
    CertificationStatus,
    RobotEntry,
    RobotRegistry,
)
from safety.site_verifier import (
    SiteStatus,
    SiteVerifier,
)
from safety.task_validator import (
    TaskValidator,
    ValidationStatus,
)

# ===================================================================
# Helper: valid capability dict for robot registry
# ===================================================================


def _valid_capabilities(**overrides: Any) -> dict[str, Any]:
    """Return a minimal valid capability descriptor."""
    base: dict[str, Any] = {
        "manipulator": {"type": "articulated", "dof": 6},
        "sensors": {"force_torque": True},
        "safety_systems": {"estop": True},
        "communication": {"protocol": "ros2"},
        "supported_procedures": [
            "lobectomy",
            "prostatectomy",
        ],
    }
    base.update(overrides)
    return base


def _valid_site_profile(**overrides: Any) -> dict[str, Any]:
    """Return a minimal valid site capability profile."""
    base: dict[str, Any] = {
        "site_id": "site-001",
        "site_name": "National Oncology Center",
        "infrastructure": {
            "servers": {"count": 4},
            "storage": {"encrypted": True},
            "network": {"latency_ms": 5},
            "regulatory_overlay": {"version": "1.0"},
        },
        "supported_procedures": [
            "lobectomy",
            "prostatectomy",
        ],
        "regulatory_status": {
            "irb_approved": True,
            "fda_cleared": True,
            "data_governance_compliant": True,
            "certification_expiry": (
                (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
            ),
        },
    }
    base.update(overrides)
    return base


# ===================================================================
# 1. Safety Gate Service
# ===================================================================


class TestSafetyGateService:
    """Tests for pre-procedure safety matrix evaluation."""

    def setup_method(self) -> None:
        self.service = SafetyGateService()

    def _all_pass_inputs(self) -> dict[str, dict[str, Any]]:
        return {
            "patient_consent": {
                "consent_given": True,
                "consent_date": "2025-01-15",
            },
            "site_capability": {
                "verified": True,
                "site_id": "site-001",
            },
            "robot_capability": {
                "eligible": True,
                "robot_id": "robot-001",
            },
            "trial_protocol": {
                "compliant": True,
                "protocol_id": "PROT-001",
            },
            "human_approval": {
                "approved": True,
                "approver": "Dr. Smith",
            },
        }

    def test_all_gates_pass(self) -> None:
        inputs = self._all_pass_inputs()
        decision = self.service.evaluate_gates("proc-001", **inputs)
        assert decision.overall_pass is True
        assert len(decision.conditions) == 5
        assert all(c.status == GateStatus.PASS for c in decision.conditions)

    def test_consent_fails(self) -> None:
        inputs = self._all_pass_inputs()
        inputs["patient_consent"] = {"consent_given": False}
        decision = self.service.evaluate_gates("proc-001", **inputs)
        assert decision.overall_pass is False
        consent_gate = decision.conditions[0]
        assert consent_gate.status == GateStatus.FAIL

    def test_site_capability_fails(self) -> None:
        inputs = self._all_pass_inputs()
        inputs["site_capability"] = {"verified": False}
        decision = self.service.evaluate_gates("proc-001", **inputs)
        assert decision.overall_pass is False

    def test_robot_capability_fails(self) -> None:
        inputs = self._all_pass_inputs()
        inputs["robot_capability"] = {"eligible": False}
        decision = self.service.evaluate_gates("proc-001", **inputs)
        assert decision.overall_pass is False

    def test_trial_protocol_fails(self) -> None:
        inputs = self._all_pass_inputs()
        inputs["trial_protocol"] = {"compliant": False}
        decision = self.service.evaluate_gates("proc-001", **inputs)
        assert decision.overall_pass is False

    def test_human_approval_pending(self) -> None:
        inputs = self._all_pass_inputs()
        inputs["human_approval"] = {"pending": True}
        decision = self.service.evaluate_gates("proc-001", **inputs)
        assert decision.overall_pass is False
        approval_gate = decision.conditions[4]
        assert approval_gate.status == GateStatus.PENDING

    def test_human_approval_denied(self) -> None:
        inputs = self._all_pass_inputs()
        inputs["human_approval"] = {
            "approved": False,
            "pending": False,
        }
        decision = self.service.evaluate_gates("proc-001", **inputs)
        assert decision.overall_pass is False
        approval_gate = decision.conditions[4]
        assert approval_gate.status == GateStatus.FAIL

    def test_audit_trail_records(self) -> None:
        inputs = self._all_pass_inputs()
        self.service.evaluate_gates("proc-001", **inputs)
        self.service.evaluate_gates("proc-002", **inputs)
        trail = self.service.get_audit_trail()
        assert len(trail) == 2

    def test_audit_trail_filter_by_procedure(self) -> None:
        inputs = self._all_pass_inputs()
        self.service.evaluate_gates("proc-001", **inputs)
        self.service.evaluate_gates("proc-002", **inputs)
        trail = self.service.get_audit_trail("proc-001")
        assert len(trail) == 1
        assert trail[0].procedure_id == "proc-001"

    def test_decision_has_unique_id(self) -> None:
        inputs = self._all_pass_inputs()
        d1 = self.service.evaluate_gates("proc-001", **inputs)
        d2 = self.service.evaluate_gates("proc-001", **inputs)
        assert d1.decision_id != d2.decision_id

    def test_multiple_failures(self) -> None:
        decision = self.service.evaluate_gates(
            "proc-fail",
            patient_consent={},
            site_capability={},
            robot_capability={},
            trial_protocol={},
            human_approval={},
        )
        assert decision.overall_pass is False
        fail_count = sum(1 for c in decision.conditions if c.status == GateStatus.FAIL)
        assert fail_count == 5


# ===================================================================
# 2. Robot Registry
# ===================================================================


class TestRobotRegistry:
    """Tests for robot registration and eligibility matching."""

    def setup_method(self) -> None:
        self.registry = RobotRegistry()

    def _make_entry(
        self,
        robot_id: str = "robot-001",
        usl_score: float = 85.0,
        certification: CertificationStatus = (CertificationStatus.CLINICAL),
        **cap_overrides: Any,
    ) -> RobotEntry:
        return RobotEntry(
            robot_id=robot_id,
            platform_name="TestBot",
            usl_score=usl_score,
            capabilities=_valid_capabilities(**cap_overrides),
            certification=certification,
        )

    def test_register_robot(self) -> None:
        entry = self._make_entry()
        result = self.registry.register(entry)
        assert result.robot_id == "robot-001"

    def test_register_invalid_capabilities_raises(self) -> None:
        entry = RobotEntry(
            robot_id="robot-bad",
            platform_name="BadBot",
            usl_score=50.0,
            capabilities={},
        )
        with pytest.raises(ValueError, match="Invalid"):
            self.registry.register(entry)

    def test_register_invalid_usl_score(self) -> None:
        entry = RobotEntry(
            robot_id="robot-bad",
            platform_name="BadBot",
            usl_score=150.0,
            capabilities=_valid_capabilities(),
        )
        with pytest.raises(ValueError, match="USL score"):
            self.registry.register(entry)

    def test_lookup_found(self) -> None:
        self.registry.register(self._make_entry())
        result = self.registry.lookup("robot-001")
        assert result is not None
        assert result.robot_id == "robot-001"

    def test_lookup_not_found(self) -> None:
        assert self.registry.lookup("nonexistent") is None

    def test_match_for_procedure_by_type(self) -> None:
        self.registry.register(self._make_entry())
        matches = self.registry.match_for_procedure(
            "lobectomy",
            required_capabilities=[],
        )
        assert len(matches) == 1

    def test_match_for_procedure_wrong_type(self) -> None:
        self.registry.register(self._make_entry())
        matches = self.registry.match_for_procedure(
            "unsupported_procedure",
            required_capabilities=[],
        )
        assert len(matches) == 0

    def test_match_for_procedure_min_usl(self) -> None:
        self.registry.register(self._make_entry(usl_score=40.0))
        matches = self.registry.match_for_procedure(
            "lobectomy",
            required_capabilities=[],
            min_usl_score=50.0,
        )
        assert len(matches) == 0

    def test_match_clinical_required(self) -> None:
        self.registry.register(
            self._make_entry(
                robot_id="sim-only",
                certification=(CertificationStatus.SIMULATION_ONLY),
            )
        )
        self.registry.register(
            self._make_entry(
                robot_id="clinical",
                certification=CertificationStatus.CLINICAL,
            )
        )
        matches = self.registry.match_for_procedure(
            "lobectomy",
            required_capabilities=[],
            clinical_required=True,
        )
        assert len(matches) == 1
        assert matches[0].robot_id == "clinical"

    def test_match_excludes_suspended(self) -> None:
        self.registry.register(
            self._make_entry(
                certification=CertificationStatus.SUSPENDED,
            )
        )
        matches = self.registry.match_for_procedure("lobectomy", required_capabilities=[])
        assert len(matches) == 0

    def test_match_sorted_by_usl_desc(self) -> None:
        self.registry.register(self._make_entry(robot_id="low", usl_score=60.0))
        self.registry.register(self._make_entry(robot_id="high", usl_score=95.0))
        matches = self.registry.match_for_procedure("lobectomy", required_capabilities=[])
        assert matches[0].robot_id == "high"

    def test_match_required_capabilities(self) -> None:
        self.registry.register(self._make_entry())
        matches = self.registry.match_for_procedure(
            "lobectomy",
            required_capabilities=["sensors"],
        )
        assert len(matches) == 1

    def test_match_missing_required_capability(self) -> None:
        self.registry.register(self._make_entry())
        matches = self.registry.match_for_procedure(
            "lobectomy",
            required_capabilities=["lidar"],
        )
        assert len(matches) == 0

    def test_validate_capability_missing_keys(self) -> None:
        errors = RobotRegistry.validate_capability({})
        assert len(errors) == 4  # 4 required keys


# ===================================================================
# 3. Task Validator
# ===================================================================


class TestTaskValidator:
    """Tests for task order validation."""

    def setup_method(self) -> None:
        self.validator = TaskValidator()

    def _valid_task_order(self, **overrides: Any) -> dict[str, Any]:
        base: dict[str, Any] = {
            "task_order_id": "TO-001",
            "procedure_type": "lobectomy",
            "patient_id": "p1",
            "site_id": "site-001",
            "robot_id": "robot-001",
            "protocol_id": "PROT-001",
        }
        base.update(overrides)
        return base

    def _valid_preconditions(self) -> dict[str, Any]:
        return {
            "patient_identity_confirmed": True,
            "consent_valid": True,
            "site_cleared": True,
            "robot_calibrated": True,
        }

    def _valid_postconditions(self) -> dict[str, Any]:
        return {
            "completion_status": "completed",
            "measurements": {"duration_minutes": 120},
            "adverse_events": [],
        }

    def test_valid_task_order(self) -> None:
        result = self.validator.validate(
            self._valid_task_order(),
            self._valid_preconditions(),
            self._valid_postconditions(),
        )
        assert result.is_valid is True

    def test_missing_schema_fields(self) -> None:
        result = self.validator.validate({})
        assert result.status == ValidationStatus.INVALID
        assert len(result.schema_errors) == 6

    def test_missing_single_field(self) -> None:
        order = self._valid_task_order()
        del order["robot_id"]
        result = self.validator.validate(order)
        assert any("robot_id" in e for e in result.schema_errors)

    def test_precondition_failures(self) -> None:
        result = self.validator.validate(
            self._valid_task_order(),
            preconditions={},
        )
        assert len(result.precondition_errors) == 4

    def test_partial_precondition_failure(self) -> None:
        pre = self._valid_preconditions()
        pre["consent_valid"] = False
        result = self.validator.validate(
            self._valid_task_order(),
            preconditions=pre,
        )
        assert any("consent" in e.lower() for e in result.precondition_errors)

    def test_postcondition_failures(self) -> None:
        result = self.validator.validate(
            self._valid_task_order(),
            self._valid_preconditions(),
            postconditions={},
        )
        assert len(result.postcondition_errors) == 3

    def test_protocol_disallowed_procedure(self) -> None:
        constraints = {"allowed_procedures": ["prostatectomy"]}
        result = self.validator.validate(
            self._valid_task_order(),
            self._valid_preconditions(),
            self._valid_postconditions(),
            protocol_constraints=constraints,
        )
        assert any("not allowed" in e for e in result.protocol_errors)

    def test_protocol_duration_exceeded(self) -> None:
        order = self._valid_task_order(duration_minutes=300)
        constraints = {"max_duration_minutes": 240}
        result = self.validator.validate(
            order,
            self._valid_preconditions(),
            self._valid_postconditions(),
            protocol_constraints=constraints,
        )
        assert any("Duration" in e for e in result.protocol_errors)

    def test_protocol_excluded_site(self) -> None:
        constraints = {"excluded_sites": ["site-001"]}
        result = self.validator.validate(
            self._valid_task_order(),
            self._valid_preconditions(),
            self._valid_postconditions(),
            protocol_constraints=constraints,
        )
        assert any("excluded" in e for e in result.protocol_errors)

    def test_validate_preconditions_standalone(self) -> None:
        errors = self.validator.validate_preconditions({})
        assert len(errors) == 4

    def test_validate_postconditions_standalone(self) -> None:
        errors = self.validator.validate_postconditions({})
        assert len(errors) == 3


# ===================================================================
# 4. Approval Checkpoint
# ===================================================================


class TestApprovalCheckpoint:
    """Tests for human-in-the-loop approval gates."""

    def setup_method(self) -> None:
        self.checkpoint = ApprovalCheckpoint(default_timeout=300)

    def test_request_approval(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Pre-procedure check",
        )
        assert req.procedure_id == "proc-1"
        assert req.timeout_seconds == 300

    def test_approve(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Check",
        )
        resp = self.checkpoint.respond(
            req.request_id,
            approved=True,
            approver="Dr. Smith",
        )
        assert resp.status == ApprovalStatus.APPROVED

    def test_deny(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Check",
        )
        resp = self.checkpoint.respond(
            req.request_id,
            approved=False,
            approver="Dr. Smith",
            comments="Patient not ready",
        )
        assert resp.status == ApprovalStatus.DENIED

    def test_timeout(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Check",
            timeout_seconds=1,
        )
        future = datetime.now(timezone.utc) + timedelta(seconds=10)
        resp = self.checkpoint.check_status(req.request_id, current_time=future)
        assert resp.status == ApprovalStatus.TIMED_OUT

    def test_check_status_pending(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Check",
        )
        resp = self.checkpoint.check_status(req.request_id)
        assert resp.status == ApprovalStatus.PENDING

    def test_check_status_after_response(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Check",
        )
        self.checkpoint.respond(
            req.request_id,
            approved=True,
            approver="Dr. X",
        )
        resp = self.checkpoint.check_status(req.request_id)
        assert resp.status == ApprovalStatus.APPROVED

    def test_escalate_denied(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Check",
        )
        self.checkpoint.respond(
            req.request_id,
            approved=False,
            approver="Dr. X",
        )
        resp = self.checkpoint.escalate(
            req.request_id,
            escalation_target="department_head",
            reason="Override needed",
        )
        assert resp.status == ApprovalStatus.ESCALATED
        assert resp.escalation_target == "department_head"

    def test_escalate_timed_out(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Check",
            timeout_seconds=1,
        )
        future = datetime.now(timezone.utc) + timedelta(seconds=10)
        self.checkpoint.check_status(req.request_id, current_time=future)
        resp = self.checkpoint.escalate(
            req.request_id,
            escalation_target="on_call",
        )
        assert resp.status == ApprovalStatus.ESCALATED

    def test_escalate_pending_raises(self) -> None:
        req = self.checkpoint.request_approval(
            procedure_id="proc-1",
            procedure_type="lobectomy",
            requester="system",
            reason="Check",
        )
        with pytest.raises(ValueError, match="denied"):
            self.checkpoint.escalate(
                req.request_id,
                escalation_target="someone",
            )

    def test_unknown_request_raises(self) -> None:
        with pytest.raises(KeyError):
            self.checkpoint.check_status("nonexistent")

    def test_respond_unknown_raises(self) -> None:
        with pytest.raises(KeyError):
            self.checkpoint.respond("nonexistent", approved=True, approver="X")

    def test_requires_approval_all_types(self) -> None:
        cp = ApprovalCheckpoint()
        assert cp.requires_approval("anything") is True

    def test_requires_approval_specific_types(self) -> None:
        cp = ApprovalCheckpoint(mandatory_types=["lobectomy"])
        assert cp.requires_approval("lobectomy") is True
        assert cp.requires_approval("biopsy") is False


# ===================================================================
# 5. E-Stop Controller
# ===================================================================


class TestEStopController:
    """Tests for emergency stop lifecycle."""

    def setup_method(self) -> None:
        self.controller = EStopController()
        self.controller.register_server("server-1")
        self.controller.register_server("server-2")

    def test_initial_status_idle(self) -> None:
        status = self.controller.get_status()
        assert status["status"] == "IDLE"

    def test_trigger_estop(self) -> None:
        signal = self.controller.trigger_estop(
            procedure_id="proc-1",
            reason="Patient distress",
            triggered_by="nurse",
            current_state={"step": "incision"},
        )
        assert signal.procedure_id == "proc-1"
        assert signal.reason == "Patient distress"
        assert len(signal.affected_servers) == 2
        status = self.controller.get_status()
        assert status["status"] == "TRIGGERED"

    def test_trigger_estop_preserves_state(self) -> None:
        state = {"step": "resection", "progress": 0.5}
        signal = self.controller.trigger_estop(
            "proc-1",
            "Emergency",
            "operator",
            current_state=state,
        )
        assert signal.preserved_state == state

    def test_double_trigger_raises(self) -> None:
        self.controller.trigger_estop("proc-1", "First", "nurse")
        with pytest.raises(RuntimeError, match="already"):
            self.controller.trigger_estop("proc-2", "Second", "nurse")

    def test_acknowledge(self) -> None:
        self.controller.trigger_estop("proc-1", "Emergency", "nurse")
        signal = self.controller.acknowledge(
            acknowledged_by="surgeon",
            post_abort_evidence={"images": ["img1.dcm"]},
        )
        assert signal.post_abort_evidence["images"] == ["img1.dcm"]
        status = self.controller.get_status()
        assert status["status"] == "ACKNOWLEDGED"

    def test_acknowledge_no_estop_raises(self) -> None:
        with pytest.raises(RuntimeError, match="No active"):
            self.controller.acknowledge("surgeon")

    def test_recover(self) -> None:
        self.controller.trigger_estop("proc-1", "Emergency", "nurse")
        self.controller.acknowledge("surgeon")
        signal = self.controller.recover(
            authorised_by="chief_surgeon",
            recovery_notes="All clear",
        )
        assert signal.post_abort_evidence["recovery_authorised_by"] == "chief_surgeon"
        status = self.controller.get_status()
        assert status["status"] == "IDLE"

    def test_recover_before_acknowledge_raises(self) -> None:
        self.controller.trigger_estop("proc-1", "Emergency", "nurse")
        with pytest.raises(RuntimeError, match="acknowledged"):
            self.controller.recover("surgeon")

    def test_history(self) -> None:
        self.controller.trigger_estop("proc-1", "First", "nurse")
        self.controller.acknowledge("surgeon")
        self.controller.recover("chief")
        history = self.controller.get_history()
        assert len(history) == 1
        assert history[0].procedure_id == "proc-1"

    def test_register_unregister_server(self) -> None:
        self.controller.unregister_server("server-2")
        signal = self.controller.trigger_estop("proc-1", "Test", "operator")
        assert "server-2" not in signal.affected_servers
        assert "server-1" in signal.affected_servers

    def test_full_lifecycle(self) -> None:
        self.controller.trigger_estop("proc-1", "Test", "operator")
        self.controller.acknowledge("surgeon")
        self.controller.recover("chief")
        # Can trigger again after recovery
        signal = self.controller.trigger_estop("proc-2", "New incident", "nurse")
        assert signal.procedure_id == "proc-2"


# ===================================================================
# 6. Procedure State Machine
# ===================================================================


class TestProcedureState:
    """Tests for procedure lifecycle state machine."""

    def test_initial_state_is_scheduled(self) -> None:
        ps = ProcedureState("proc-1")
        assert ps.status == ProcedureStatus.SCHEDULED

    def test_valid_transition_scheduled_to_precheck(
        self,
    ) -> None:
        ps = ProcedureState("proc-1")
        record = ps.transition(ProcedureStatus.PRE_CHECK)
        assert ps.status == ProcedureStatus.PRE_CHECK
        assert record.from_state == ProcedureStatus.SCHEDULED

    def test_valid_full_happy_path(self) -> None:
        ps = ProcedureState("proc-1", mode=ProcedureMode.CLINICAL)
        ps.transition(ProcedureStatus.PRE_CHECK)
        ps.transition(ProcedureStatus.APPROVED)
        ps.transition(ProcedureStatus.IN_PROGRESS)
        ps.transition(ProcedureStatus.POST_CHECK)
        ps.transition(ProcedureStatus.COMPLETED)
        assert ps.status == ProcedureStatus.COMPLETED
        assert ps.is_terminal is True

    def test_invalid_transition_raises(self) -> None:
        ps = ProcedureState("proc-1")
        with pytest.raises(ValueError, match="Invalid"):
            ps.transition(ProcedureStatus.COMPLETED)

    def test_abort_from_scheduled(self) -> None:
        ps = ProcedureState("proc-1")
        ps.transition(ProcedureStatus.ABORTED)
        assert ps.status == ProcedureStatus.ABORTED
        assert ps.is_terminal is True

    def test_abort_from_in_progress(self) -> None:
        ps = ProcedureState("proc-1", mode=ProcedureMode.CLINICAL)
        ps.transition(ProcedureStatus.PRE_CHECK)
        ps.transition(ProcedureStatus.APPROVED)
        ps.transition(ProcedureStatus.IN_PROGRESS)
        ps.transition(ProcedureStatus.ABORTED)
        assert ps.status == ProcedureStatus.ABORTED

    def test_fail_from_precheck(self) -> None:
        ps = ProcedureState("proc-1")
        ps.transition(ProcedureStatus.PRE_CHECK)
        ps.transition(ProcedureStatus.FAILED)
        assert ps.status == ProcedureStatus.FAILED
        assert ps.is_terminal is True

    def test_cannot_transition_from_terminal(self) -> None:
        ps = ProcedureState("proc-1")
        ps.transition(ProcedureStatus.ABORTED)
        with pytest.raises(ValueError):
            ps.transition(ProcedureStatus.SCHEDULED)

    def test_can_transition_check(self) -> None:
        ps = ProcedureState("proc-1")
        assert ps.can_transition(ProcedureStatus.PRE_CHECK)
        assert not ps.can_transition(ProcedureStatus.COMPLETED)

    def test_history(self) -> None:
        ps = ProcedureState("proc-1")
        ps.transition(ProcedureStatus.PRE_CHECK)
        ps.transition(ProcedureStatus.APPROVED)
        history = ps.get_history()
        assert len(history) == 2
        assert history[0].to_state == ProcedureStatus.PRE_CHECK

    def test_simulation_mode(self) -> None:
        ps = ProcedureState("proc-1", mode=ProcedureMode.SIMULATION)
        assert ps.is_clinical is False
        ps.transition(ProcedureStatus.PRE_CHECK)
        ps.transition(ProcedureStatus.APPROVED)
        record = ps.transition(ProcedureStatus.IN_PROGRESS)
        assert "SIMULATION" in record.reason

    def test_clinical_mode(self) -> None:
        ps = ProcedureState("proc-1", mode=ProcedureMode.CLINICAL)
        assert ps.is_clinical is True

    def test_serialize_deserialize(self) -> None:
        ps = ProcedureState("proc-1", mode=ProcedureMode.CLINICAL)
        ps.transition(ProcedureStatus.PRE_CHECK)
        ps.transition(ProcedureStatus.APPROVED)

        data = ps.serialize()
        restored = ProcedureState.deserialize(data)
        assert restored.procedure_id == "proc-1"
        assert restored.status == ProcedureStatus.APPROVED
        assert restored.mode == ProcedureMode.CLINICAL
        assert len(restored.get_history()) == 2

    def test_to_json_from_json(self) -> None:
        ps = ProcedureState("proc-1")
        ps.transition(ProcedureStatus.PRE_CHECK)
        json_str = ps.to_json()
        restored = ProcedureState.from_json(json_str)
        assert restored.status == ProcedureStatus.PRE_CHECK

    def test_serialize_is_valid_json(self) -> None:
        ps = ProcedureState("proc-1")
        ps.transition(ProcedureStatus.PRE_CHECK)
        json_str = ps.to_json()
        parsed = json.loads(json_str)
        assert parsed["procedure_id"] == "proc-1"


# ===================================================================
# 7. Site Verifier
# ===================================================================


class TestSiteVerifier:
    """Tests for site capability verification."""

    def setup_method(self) -> None:
        self.verifier = SiteVerifier()

    def test_verify_valid_site(self) -> None:
        profile = _valid_site_profile()
        result = self.verifier.verify_site(profile)
        assert result.is_verified is True
        assert result.status == SiteStatus.VERIFIED
        assert "lobectomy" in result.eligible_procedures

    def test_verify_missing_schema_fields(self) -> None:
        result = self.verifier.verify_site({})
        assert result.status == SiteStatus.NOT_VERIFIED
        assert len(result.details["schema_errors"]) >= 4

    def test_verify_missing_infrastructure(self) -> None:
        profile = _valid_site_profile()
        profile["infrastructure"] = {}
        result = self.verifier.verify_site(profile)
        assert result.status != SiteStatus.VERIFIED
        assert len(result.infrastructure_errors) == 4

    def test_verify_missing_irb(self) -> None:
        profile = _valid_site_profile()
        profile["regulatory_status"]["irb_approved"] = False
        result = self.verifier.verify_site(profile)
        assert result.status == SiteStatus.NOT_VERIFIED
        assert any("IRB" in e for e in result.regulatory_errors)

    def test_verify_missing_fda(self) -> None:
        profile = _valid_site_profile()
        profile["regulatory_status"]["fda_cleared"] = False
        result = self.verifier.verify_site(profile)
        assert any("FDA" in e for e in result.regulatory_errors)

    def test_verify_expired_certification(self) -> None:
        profile = _valid_site_profile()
        profile["regulatory_status"]["certification_expiry"] = "2020-01-01T00:00:00+00:00"
        result = self.verifier.verify_site(profile)
        assert any("expired" in e for e in result.regulatory_errors)

    def test_verify_invalid_expiry_date(self) -> None:
        profile = _valid_site_profile()
        profile["regulatory_status"]["certification_expiry"] = "not-a-date"
        result = self.verifier.verify_site(profile)
        assert any("Invalid" in e for e in result.regulatory_errors)

    def test_check_procedure_eligibility_true(self) -> None:
        profile = _valid_site_profile()
        assert self.verifier.check_procedure_eligibility(profile, "lobectomy")

    def test_check_procedure_eligibility_false(self) -> None:
        profile = _valid_site_profile()
        assert not self.verifier.check_procedure_eligibility(profile, "unsupported_procedure")

    def test_check_procedure_not_verified_site(self) -> None:
        profile = _valid_site_profile()
        profile["regulatory_status"]["irb_approved"] = False
        assert not self.verifier.check_procedure_eligibility(profile, "lobectomy")

    def test_conditionally_verified(self) -> None:
        profile = _valid_site_profile()
        del profile["infrastructure"]["network"]
        result = self.verifier.verify_site(profile)
        assert result.status == SiteStatus.CONDITIONALLY_VERIFIED

    def test_validate_regulatory_compliance_full(
        self,
    ) -> None:
        reg = {
            "irb_approved": True,
            "fda_cleared": True,
            "data_governance_compliant": True,
        }
        errors = SiteVerifier.validate_regulatory_compliance(reg)
        assert errors == []

    def test_validate_regulatory_compliance_all_missing(
        self,
    ) -> None:
        errors = SiteVerifier.validate_regulatory_compliance({})
        assert len(errors) == 3
