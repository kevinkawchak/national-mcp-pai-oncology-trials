"""mTLS support utilities.

Provides helpers for client-certificate extraction, certificate
chain verification interfaces, and distinguished-name parsing
used by the mutual-TLS identity flow in the National MCP PAI
Oncology Trials platform.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class CertificateStatus(Enum):
    """Validation status of a presented certificate."""

    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNTRUSTED = "untrusted"
    INVALID = "invalid"


@dataclass(frozen=True)
class DistinguishedName:
    """Parsed X.509 distinguished-name components."""

    common_name: str | None = None
    organization: str | None = None
    organizational_unit: str | None = None
    country: str | None = None
    state: str | None = None
    locality: str | None = None
    serial_number: str | None = None
    raw: str = ""


@dataclass(frozen=True)
class CertificateInfo:
    """Metadata extracted from a client certificate."""

    subject: DistinguishedName
    issuer: DistinguishedName
    serial: str
    not_before: str
    not_after: str
    fingerprint_sha256: str
    san_dns: list[str] = field(default_factory=list)
    san_uri: list[str] = field(default_factory=list)
    raw_pem: str = ""


@dataclass(frozen=True)
class ChainVerificationResult:
    """Outcome of a certificate-chain verification."""

    status: CertificateStatus
    chain_depth: int
    details: str = ""
    certificate: CertificateInfo | None = None


# -- Distinguished-name parsing ----------------------------

_RDN_MAP: dict[str, str] = {
    "CN": "common_name",
    "O": "organization",
    "OU": "organizational_unit",
    "C": "country",
    "ST": "state",
    "L": "locality",
    "SERIALNUMBER": "serial_number",
}

_RDN_PATTERN = re.compile(
    r"(?:^|,)\s*([A-Z]+)\s*=\s*"
    r"(?:\"([^\"]*)\"|([^,]*))"
)


def parse_distinguished_name(dn_string: str) -> DistinguishedName:
    """Parse an RFC 2253-style DN string into components.

    Parameters
    ----------
    dn_string:
        A distinguished-name string such as
        ``CN=alice,O=Acme,C=US``.

    Returns
    -------
    DistinguishedName
        Parsed components.
    """
    parts: dict[str, str] = {}
    for match in _RDN_PATTERN.finditer(dn_string):
        key = match.group(1).upper()
        value = match.group(2) or match.group(3)
        attr = _RDN_MAP.get(key)
        if attr:
            parts[attr] = value.strip()
    return DistinguishedName(raw=dn_string, **parts)


# -- Certificate extraction --------------------------------


def extract_client_certificate_pem(
    headers: dict[str, str],
    *,
    header_name: str = "X-Client-Cert",
) -> str | None:
    """Extract a PEM-encoded client certificate from headers.

    Many reverse-proxies forward the validated client
    certificate in a configurable HTTP header.

    Parameters
    ----------
    headers:
        HTTP request headers (case-insensitive lookup
        recommended by caller).
    header_name:
        The header carrying the URL-encoded PEM certificate.

    Returns
    -------
    str | None
        Decoded PEM string, or ``None`` when the header is
        absent.
    """
    raw = headers.get(header_name)
    if raw is None:
        return None
    # Reverse-proxies often URL-encode the PEM.
    from urllib.parse import unquote

    return unquote(raw)


# -- Abstract chain verifier --------------------------------


class CertificateChainVerifier(ABC):
    """Abstract interface for certificate-chain verification.

    Implementations may delegate to OpenSSL, a cloud KMS
    trust-store, or an internal PKI validation service.
    """

    @abstractmethod
    async def verify_chain(
        self,
        leaf_pem: str,
        intermediates: list[str] | None = None,
    ) -> ChainVerificationResult:
        """Verify the presented certificate chain.

        Parameters
        ----------
        leaf_pem:
            PEM-encoded leaf (client) certificate.
        intermediates:
            Optional list of PEM-encoded intermediate
            certificates.

        Returns
        -------
        ChainVerificationResult
            Verification outcome with chain details.
        """

    @abstractmethod
    async def extract_info(self, pem: str) -> CertificateInfo:
        """Parse a PEM certificate and return metadata.

        Parameters
        ----------
        pem:
            PEM-encoded certificate.

        Returns
        -------
        CertificateInfo
            Extracted certificate metadata.
        """


class MTLSIdentityExtractor:
    """Extracts and validates identity from mTLS connections.

    Combines certificate extraction, chain verification, and
    DN parsing into a single reusable helper.

    Parameters
    ----------
    chain_verifier:
        The concrete chain verifier to use.
    cert_header:
        HTTP header containing the forwarded client cert.
    """

    def __init__(
        self,
        chain_verifier: CertificateChainVerifier,
        *,
        cert_header: str = "X-Client-Cert",
    ) -> None:
        self._verifier = chain_verifier
        self._cert_header = cert_header

    async def extract_identity(
        self,
        headers: dict[str, str],
    ) -> tuple[CertificateInfo, ChainVerificationResult]:
        """Extract and verify client identity from headers.

        Returns
        -------
        tuple[CertificateInfo, ChainVerificationResult]
            Certificate metadata and chain verification
            outcome.

        Raises
        ------
        ValueError
            If no client certificate is present.
        """
        pem = extract_client_certificate_pem(headers, header_name=self._cert_header)
        if pem is None:
            raise ValueError(f"No client certificate in header {self._cert_header!r}")
        info = await self._verifier.extract_info(pem)
        result = await self._verifier.verify_chain(pem)
        return info, result
