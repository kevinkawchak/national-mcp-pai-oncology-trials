"""FHIR Clinical Data MCP server entrypoint.

Provides the FHIRServer class that wires together the FHIR adapter,
de-identification pipeline, transport, routing, and middleware.
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
from servers.trialmcp_fhir.deid_pipeline import DeidentificationPipeline
from servers.trialmcp_fhir.fhir_adapter import FHIRAdapter, MockFHIRAdapter

logger = logging.getLogger(__name__)


class FHIRServer:
    """MCP FHIR Clinical Data Server — trialmcp-fhir.

    Implements FHIR R4 read/search with mandatory HIPAA Safe Harbor
    de-identification, HMAC-SHA256 pseudonymization, and audit emission.
    """

    SERVER_NAME = "trialmcp-fhir"

    def __init__(
        self,
        config: ServerConfig | None = None,
        adapter: FHIRAdapter | None = None,
    ) -> None:
        self.config = config or load_config(server_name=self.SERVER_NAME)
        self.adapter = adapter or MockFHIRAdapter()
        self.deid = DeidentificationPipeline(
            hmac_key=self.config.extra.get("hmac_key", "trialmcp-default-key")
        )
        self.validator = SchemaValidator()
        self.health = HealthChecker(self.SERVER_NAME)
        self.audit = AuditMiddleware()
        self.router = RequestRouter(self.SERVER_NAME)
        self.transport = MCPTransport()

        self._register_tools()

    def _register_tools(self) -> None:
        self.router.register("fhir_read", self.handle_read)
        self.router.register("fhir_search", self.handle_search)
        self.router.register("fhir_patient_lookup", self.handle_patient_lookup)
        self.router.register("fhir_study_status", self.handle_study_status)

    def handle_read(
        self,
        resource_type: str = "",
        resource_id: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle fhir_read tool call."""
        if not SchemaValidator.validate_fhir_id(resource_id):
            raise ValidationError(f"Invalid FHIR resource ID: {resource_id}")

        resource = self.adapter.read(resource_type, resource_id)
        if resource is None:
            raise NotFoundError(f"{resource_type}/{resource_id} not found")

        deidentified = self.deid.deidentify_resource(resource)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="fhir_read",
            caller=kwargs.get("caller", "unknown"),
            result_summary="OK",
            parameters={"resource_type": resource_type, "resource_id": resource_id},
        )
        return deidentified

    def handle_search(
        self,
        resource_type: str = "",
        params: dict[str, str] | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle fhir_search tool call."""
        if limit > 100:
            limit = 100

        bundle = self.adapter.search(resource_type, params, limit)
        deidentified = self.deid.deidentify_bundle(bundle)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="fhir_search",
            caller=kwargs.get("caller", "unknown"),
            result_summary=f"OK ({deidentified.get('total', 0)} results)",
            parameters={"resource_type": resource_type},
        )
        return deidentified

    def handle_patient_lookup(self, pseudonym: str = "", **kwargs: Any) -> dict[str, Any]:
        """Handle fhir_patient_lookup tool call."""
        patient = self.adapter.patient_lookup(pseudonym)
        if patient is None:
            raise NotFoundError(f"Patient {pseudonym} not found")

        deidentified = self.deid.deidentify_resource(patient)
        self.audit.emit(
            server=self.SERVER_NAME,
            tool="fhir_patient_lookup",
            caller=kwargs.get("caller", "unknown"),
            result_summary="OK",
        )
        return deidentified

    def handle_study_status(self, study_id: str = "", **kwargs: Any) -> dict[str, Any]:
        """Handle fhir_study_status tool call."""
        study = self.adapter.study_status(study_id)
        if study is None:
            raise NotFoundError(f"Study {study_id} not found")

        self.audit.emit(
            server=self.SERVER_NAME,
            tool="fhir_study_status",
            caller=kwargs.get("caller", "unknown"),
            result_summary="OK",
            parameters={"study_id": study_id},
        )
        return study

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
    """CLI entrypoint for trialmcp-fhir server."""
    from servers.common.logging import setup_logging

    setup_logging(level="INFO", server_name="trialmcp-fhir")
    server = FHIRServer()
    server.run()


if __name__ == "__main__":
    main()
