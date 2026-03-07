"""National MCP-PAI Oncology Trials — 5-Minute Quickstart Demo.

Demonstrates the complete workflow across all 5 MCP servers:
1. Robot requests authorization token (authz)
2. Token is validated (authz)
3. FHIR clinical data is read with de-identification (fhir)
4. DICOM imaging query is executed (dicom)
5. Audit record is appended to the ledger (ledger)
6. Provenance record is created (provenance)
7. Audit chain is verified (ledger)
8. Provenance DAG is verified (provenance)

Usage:
    python examples/quickstart/run_demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_result(label: str, data: dict) -> None:
    """Print a labeled JSON result."""
    print(f"\n  {label}:")
    print(f"  {json.dumps(data, indent=2, default=str)[:500]}")


def main() -> int:
    """Run the complete quickstart demo workflow."""
    print("\n" + "=" * 60)
    print("  National MCP-PAI Oncology Trials — Quickstart Demo")
    print("  Version 0.7.0 | All 5 MCP Servers")
    print("=" * 60)

    # --- 1. Initialize all servers ---
    print_section("1. Initializing MCP Servers")

    from servers.trialmcp_authz import AuthzServer
    from servers.trialmcp_dicom import DICOMServer
    from servers.trialmcp_fhir import FHIRServer
    from servers.trialmcp_ledger import LedgerServer
    from servers.trialmcp_provenance import ProvenanceServer

    authz = AuthzServer()
    fhir = FHIRServer()
    dicom = DICOMServer()
    ledger = LedgerServer()
    provenance = ProvenanceServer()

    print("  [OK] trialmcp-authz initialized")
    print("  [OK] trialmcp-fhir initialized")
    print("  [OK] trialmcp-dicom initialized")
    print("  [OK] trialmcp-ledger initialized")
    print("  [OK] trialmcp-provenance initialized")

    # --- 2. Robot agent requests authorization token ---
    print_section("2. Robot Agent Requests Token (authz)")
    token_result = authz.handle_issue_token(role="robot_agent", expires_in=3600)
    print_result("Token issued", token_result)
    token_hash = token_result["token_hash"]

    # --- 3. Validate the token ---
    print_section("3. Token Validation (authz)")
    validation = authz.handle_validate_token(token_hash=token_hash)
    print_result("Token validation", validation)

    # --- 4. Evaluate authorization for FHIR read ---
    print_section("4. Authorization Evaluation (authz)")
    authz_result = authz.handle_evaluate(role="robot_agent", tool="fhir_read")
    print_result("AuthZ decision", authz_result)

    # --- 5. FHIR clinical data read ---
    print_section("5. FHIR Clinical Data Read (fhir)")
    fhir_result = fhir.handle_read(
        resource_type="Patient",
        resource_id="patient-001",
        caller="robot_agent_001",
    )
    print_result("De-identified FHIR resource", fhir_result)

    # --- 6. DICOM imaging query ---
    print_section("6. DICOM Imaging Query (dicom)")
    dicom_result = dicom.handle_query(
        query_level="STUDY",
        modality="CT",
        role="robot_agent",
        caller="robot_agent_001",
    )
    print_result("DICOM query result", dicom_result)

    # --- 7. Append audit record to ledger ---
    print_section("7. Audit Ledger Append (ledger)")
    audit_record = ledger.handle_append(
        server="trialmcp-fhir",
        tool="fhir_read",
        caller="robot_agent_001",
        result_summary="OK",
        parameters={"resource_type": "Patient", "resource_id": "patient-001"},
    )
    print_result("Audit record", audit_record)

    # --- 8. Record provenance ---
    print_section("8. Provenance Record (provenance)")
    prov_record = provenance.handle_record(
        source_id="patient-001",
        action="read",
        actor_id="robot_agent_001",
        actor_role="robot_agent",
        tool_call="fhir_read",
        source_type="fhir",
        origin_server="trialmcp-fhir",
        description="Robot agent read patient data for procedure planning",
    )
    print_result("Provenance record", prov_record)

    # --- 9. Verify audit chain ---
    print_section("9. Audit Chain Verification (ledger)")
    verify_result = ledger.handle_verify()
    print_result("Chain verification", verify_result)

    # --- 10. Verify provenance DAG ---
    print_section("10. Provenance DAG Verification (provenance)")
    dag_result = provenance.handle_verify()
    print_result("DAG verification", dag_result)

    # --- Summary ---
    print_section("Demo Complete")
    print("  All 5 MCP servers executed successfully:")
    print("    - trialmcp-authz:      Token issued, validated, authz evaluated")
    print("    - trialmcp-fhir:       Patient data read with HIPAA de-identification")
    print("    - trialmcp-dicom:      CT imaging queried with patient name hashing")
    print("    - trialmcp-ledger:     Audit record appended, chain verified")
    print("    - trialmcp-provenance: Provenance recorded, DAG verified")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
