"""DICOM Imaging MCP server entrypoint.

Provides the DICOMServer class that wires together the DICOM adapter,
role-based modality restrictions, transport, routing, and middleware.
"""

from __future__ import annotations

import logging
from typing import Any

from servers.common.config import ServerConfig, load_config
from servers.common.errors import NotFoundError, ValidationError, error_response
from servers.common.health import HealthChecker
from servers.common.middleware import AuditMiddleware
from servers.common.routing import RequestRouter
from servers.common.transport import MCPTransport
from servers.common.validation import SchemaValidator
from servers.trialmcp_dicom.dicom_adapter import (
    ALL_SUPPORTED_MODALITIES,
    ROLE_QUERY_LEVELS,
    DICOMAdapter,
    MockDICOMAdapter,
)

logger = logging.getLogger(__name__)


class DICOMServer:
    """MCP DICOM Imaging Server — trialmcp-dicom.

    Implements DICOM query/retrieve with role-based modality restrictions,
    UID validation, patient name hashing, and audit emission.
    """

    SERVER_NAME = "trialmcp-dicom"

    def __init__(
        self,
        config: ServerConfig | None = None,
        adapter: DICOMAdapter | None = None,
    ) -> None:
        self.config = config or load_config(server_name=self.SERVER_NAME)
        self.adapter = adapter or MockDICOMAdapter()
        self.health = HealthChecker(self.SERVER_NAME)
        self.audit = AuditMiddleware()
        self.router = RequestRouter(self.SERVER_NAME)
        self.transport = MCPTransport()

        self._register_tools()

    def _register_tools(self) -> None:
        self.router.register("dicom_query", self.handle_query)
        self.router.register("dicom_retrieve", self.handle_retrieve)

    def handle_query(
        self,
        query_level: str = "STUDY",
        modality: str | None = None,
        patient_id: str | None = None,
        study_uid: str | None = None,
        role: str = "robot_agent",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle dicom_query tool call."""
        # Validate role has permission for query level
        allowed_levels = ROLE_QUERY_LEVELS.get(role, [])
        if query_level not in allowed_levels:
            raise ValidationError(f"Role '{role}' cannot query at level '{query_level}'")

        # Validate modality if specified
        if modality and modality not in ALL_SUPPORTED_MODALITIES:
            raise ValidationError(f"Unsupported modality: {modality}")

        # Validate DICOM UID if specified
        if study_uid and not SchemaValidator.validate_dicom_uid(study_uid):
            raise ValidationError(f"Invalid DICOM UID: {study_uid}")

        results = self.adapter.query(
            query_level=query_level,
            modality=modality,
            patient_id=patient_id,
            study_uid=study_uid,
        )

        self.audit.emit(
            server=self.SERVER_NAME,
            tool="dicom_query",
            caller=kwargs.get("caller", role),
            result_summary=f"OK ({len(results)} results)",
            parameters={
                "query_level": query_level,
                "modality": modality or "",
                "role": role,
            },
        )

        return {
            "query_level": query_level,
            "results": results,
            "total": len(results),
        }

    def handle_retrieve(
        self,
        study_uid: str = "",
        role: str = "robot_agent",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle dicom_retrieve tool call."""
        if not SchemaValidator.validate_dicom_uid(study_uid):
            raise ValidationError(f"Invalid DICOM UID: {study_uid}")

        metadata = self.adapter.retrieve(study_uid)
        if metadata is None:
            raise NotFoundError(f"Study {study_uid} not found")

        self.audit.emit(
            server=self.SERVER_NAME,
            tool="dicom_retrieve",
            caller=kwargs.get("caller", role),
            result_summary="OK",
            parameters={"study_uid": study_uid, "role": role},
        )

        return metadata

    def run(self) -> None:
        """Start the server transport loop."""
        logger.info("Starting %s", self.SERVER_NAME)
        self.transport.start()
        while self.transport.is_running:
            request = self.transport.read_request()
            if request is None:
                break
            try:
                request_id = request.get("id")
                result = self.router.route_request(request)
                self.transport.write_result(request_id, result)
            except (ValidationError, NotFoundError) as exc:
                resp = error_response(exc.code, exc.message, server=self.SERVER_NAME)
                self.transport.write_result(request.get("id"), resp)
            except KeyError as exc:
                self.transport.write_error(request.get("id"), -32601, str(exc))
            except Exception as exc:
                logger.exception("Error processing request")
                self.transport.write_error(request.get("id"), -32603, str(exc))


def main() -> None:
    """CLI entrypoint for trialmcp-dicom server."""
    from servers.common.logging import setup_logging

    setup_logging(level="INFO", server_name="trialmcp-dicom")
    server = DICOMServer()
    server.run()


if __name__ == "__main__":
    main()
