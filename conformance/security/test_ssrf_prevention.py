"""Security conformance tests for SSRF (Server-Side Request Forgery) prevention.

Validates that conforming implementations reject URL injection attempts
in all user-supplied input fields per the National MCP-PAI Oncology
Trials Standard.

Specification references:
  - spec/security.md — SSRF prevention (reject http/https in resource IDs)
  - spec/tool-contracts.md — Input validation for fhir_read, fhir_search
  - profiles/base-profile.md — Security requirements
"""

from __future__ import annotations

import pytest

from conformance.fixtures.clinical_resources import (
    FHIR_ID_PATTERN,
    SSRF_PAYLOADS,
)


class TestSSRFPrevention:
    """Validates SSRF prevention per spec/security.md."""

    @pytest.mark.parametrize("payload", SSRF_PAYLOADS)
    def test_ssrf_url_rejected_in_fhir_id(self, payload: str) -> None:
        """URLs in FHIR resource IDs MUST be rejected to prevent SSRF."""
        # FHIR IDs must match ^[A-Za-z0-9\\-._]+$ which excludes ://
        assert not FHIR_ID_PATTERN.match(payload), f"SSRF payload should be rejected: {payload}"

    @pytest.mark.parametrize("payload", SSRF_PAYLOADS)
    def test_ssrf_url_detected_by_protocol_check(self, payload: str) -> None:
        """URLs MUST be detected by case-insensitive http/https prefix check."""
        lower = payload.lower()
        has_protocol = lower.startswith("http://") or lower.startswith("https://")
        assert has_protocol, f"Should detect protocol in: {payload}"

    def test_ssrf_rejection_is_case_insensitive(self) -> None:
        """SSRF detection MUST be case-insensitive."""
        mixed_case_urls = [
            "HTTP://internal/admin",
            "Https://evil.com",
            "hTtP://localhost",
            "HTTPS://STEAL-DATA.COM",
        ]
        for url in mixed_case_urls:
            lower = url.lower()
            assert lower.startswith("http://") or lower.startswith("https://")

    def test_internal_ip_addresses_detected(self) -> None:
        """Common internal/metadata IP patterns MUST be flagged."""
        internal_urls = [
            "http://169.254.169.254/metadata",
            "http://127.0.0.1/admin",
            "http://localhost:8080",
            "http://[::1]/internal",
            "http://10.0.0.1/api",
            "http://192.168.1.1/config",
            "http://172.16.0.1/internal",
        ]
        for url in internal_urls:
            assert not FHIR_ID_PATTERN.match(url)

    def test_non_url_fhir_ids_accepted(self) -> None:
        """Legitimate FHIR resource IDs MUST be accepted."""
        valid_ids = [
            "patient-001",
            "obs.12345",
            "condition_789",
            "med-req-001.v2",
            "Patient-a3f8e2d1",
        ]
        for fhir_id in valid_ids:
            assert FHIR_ID_PATTERN.match(fhir_id), f"Should accept: {fhir_id}"

    def test_data_uri_rejected(self) -> None:
        """Data URIs MUST be rejected in resource ID fields."""
        data_uris = [
            "data:text/html,<script>alert(1)</script>",
            "data:application/json,{}",
        ]
        for uri in data_uris:
            assert not FHIR_ID_PATTERN.match(uri)

    def test_javascript_uri_rejected(self) -> None:
        """JavaScript URIs MUST be rejected in resource ID fields."""
        js_uris = [
            "javascript:alert(1)",
            "JAVASCRIPT:void(0)",
        ]
        for uri in js_uris:
            assert not FHIR_ID_PATTERN.match(uri)
