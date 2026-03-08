"""KMS/HSM-backed signing key hooks.

Provides an abstract key-management interface for signing
operations, key rotation, audit record signing, and token
signing within the National MCP PAI Oncology Trials platform.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class KeyAlgorithm(Enum):
    """Supported signing key algorithms."""

    RSA_2048 = "RSA_2048"
    RSA_4096 = "RSA_4096"
    EC_P256 = "EC_P256"
    EC_P384 = "EC_P384"
    ED25519 = "ED25519"


class KeyState(Enum):
    """Lifecycle state of a managed key."""

    ACTIVE = "active"
    PENDING_ROTATION = "pending_rotation"
    ROTATED = "rotated"
    DISABLED = "disabled"
    DESTROYED = "destroyed"


@dataclass(frozen=True)
class KeyMetadata:
    """Metadata for a managed signing key."""

    key_id: str
    algorithm: KeyAlgorithm
    state: KeyState
    created_at: float
    rotated_at: float | None = None
    expires_at: float | None = None
    labels: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SigningResult:
    """Result of a signing operation."""

    key_id: str
    algorithm: KeyAlgorithm
    signature: bytes
    signed_at: float


@dataclass(frozen=True)
class AuditSignature:
    """A signed audit record."""

    record_id: str
    record_hash: str
    signature: bytes
    key_id: str
    signed_at: float


class KeyManagementAdapter(ABC):
    """Abstract interface to a KMS or HSM backend.

    Implementations wrap cloud KMS services (AWS KMS, GCP
    Cloud KMS, Azure Key Vault) or on-premises HSMs behind
    a uniform signing interface.
    """

    # -- key lifecycle --------------------------------------

    @abstractmethod
    async def create_key(
        self,
        key_id: str,
        algorithm: KeyAlgorithm,
        *,
        labels: dict[str, str] | None = None,
    ) -> KeyMetadata:
        """Create a new managed signing key.

        Parameters
        ----------
        key_id:
            Unique identifier for the key.
        algorithm:
            The signing algorithm to use.
        labels:
            Optional metadata labels.

        Returns
        -------
        KeyMetadata
            Metadata for the newly created key.
        """

    @abstractmethod
    async def get_key_metadata(self, key_id: str) -> KeyMetadata:
        """Retrieve metadata for an existing key."""

    @abstractmethod
    async def rotate_key(self, key_id: str) -> KeyMetadata:
        """Trigger rotation for a managed key.

        The previous key version remains available for
        verification but will no longer be used for new
        signing operations.

        Returns
        -------
        KeyMetadata
            Updated metadata reflecting the rotation.
        """

    @abstractmethod
    async def disable_key(self, key_id: str) -> KeyMetadata:
        """Disable a key, preventing further use."""

    @abstractmethod
    async def list_keys(
        self,
        *,
        state_filter: KeyState | None = None,
    ) -> list[KeyMetadata]:
        """List managed keys, optionally filtered by state."""

    # -- signing operations ---------------------------------

    @abstractmethod
    async def sign(
        self,
        key_id: str,
        data: bytes,
    ) -> SigningResult:
        """Sign *data* using the specified key.

        Parameters
        ----------
        key_id:
            Identifier of the signing key.
        data:
            The raw bytes to sign.

        Returns
        -------
        SigningResult
            The signature and associated metadata.
        """

    @abstractmethod
    async def verify(
        self,
        key_id: str,
        data: bytes,
        signature: bytes,
    ) -> bool:
        """Verify a signature against *data*.

        Returns
        -------
        bool
            ``True`` when the signature is valid.
        """

    # -- high-level helpers ---------------------------------

    async def sign_audit_record(
        self,
        key_id: str,
        record_id: str,
        record_hash: str,
    ) -> AuditSignature:
        """Produce a signed audit record.

        Parameters
        ----------
        key_id:
            Signing key to use.
        record_id:
            Unique ID of the audit record.
        record_hash:
            Hex-encoded hash of the record contents.

        Returns
        -------
        AuditSignature
            The signed audit artefact.
        """
        result = await self.sign(key_id, record_hash.encode("utf-8"))
        return AuditSignature(
            record_id=record_id,
            record_hash=record_hash,
            signature=result.signature,
            key_id=result.key_id,
            signed_at=result.signed_at,
        )

    async def sign_token_payload(
        self,
        key_id: str,
        payload: bytes,
    ) -> SigningResult:
        """Sign a token payload (e.g. JWT signing input).

        This is a convenience alias for :meth:`sign` with
        intent-revealing semantics for token issuance flows.
        """
        return await self.sign(key_id, payload)
