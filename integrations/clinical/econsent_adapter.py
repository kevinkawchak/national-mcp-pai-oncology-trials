"""eConsent/IRB metadata adapter.

Tracks informed-consent status across Physical AI oncology
trials, verifies IRB approval, and manages consent document
references with support for granular consent categories.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConsentStatus(Enum):
    """Lifecycle status of an informed-consent record."""

    PENDING = "pending"
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class ConsentCategory(Enum):
    """Granular consent categories for PAI oncology trials."""

    GENERAL_TRIAL = "general_trial"
    PHYSICAL_AI = "physical_ai"
    IMAGING = "imaging"
    BIOSPECIMEN = "biospecimen"
    DATA_SHARING = "data_sharing"
    FUTURE_RESEARCH = "future_research"


@dataclass(frozen=True)
class ConsentDocumentRef:
    """Reference to a versioned consent document."""

    document_id: str
    version: str
    title: str
    url: str
    language: str = "en"
    hash_sha256: str = ""


@dataclass
class ConsentRecord:
    """A single participant consent record."""

    consent_id: str
    participant_id: str
    trial_id: str
    status: ConsentStatus
    categories: list[ConsentCategory] = field(default_factory=list)
    document_ref: ConsentDocumentRef | None = None
    granted_at: float | None = None
    expires_at: float | None = None
    withdrawn_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Return ``True`` when consent is currently active."""
        if self.status != ConsentStatus.ACTIVE:
            return False
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        return True


@dataclass(frozen=True)
class IRBApproval:
    """Institutional Review Board approval metadata."""

    irb_id: str
    protocol_id: str
    approval_number: str
    approved_at: float
    expires_at: float
    institution: str
    status: str = "approved"
    conditions: list[str] = field(default_factory=list)


class EConsentAdapter(ABC):
    """Abstract adapter for eConsent and IRB integration.

    Implementations connect to institutional eConsent
    platforms and IRB tracking systems.
    """

    # -- consent management ---------------------------------

    @abstractmethod
    async def get_consent(
        self,
        consent_id: str,
    ) -> ConsentRecord:
        """Retrieve a consent record by ID.

        Raises
        ------
        KeyError
            If the consent record does not exist.
        """

    @abstractmethod
    async def get_participant_consents(
        self,
        participant_id: str,
        trial_id: str,
    ) -> list[ConsentRecord]:
        """List all consent records for a participant in a
        trial.
        """

    @abstractmethod
    async def record_consent(
        self,
        participant_id: str,
        trial_id: str,
        categories: list[ConsentCategory],
        document_ref: ConsentDocumentRef,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ConsentRecord:
        """Record a new consent grant.

        Parameters
        ----------
        participant_id:
            Unique participant identifier.
        trial_id:
            Clinical trial identifier.
        categories:
            Consent categories the participant agreed to.
        document_ref:
            Reference to the signed consent document.
        metadata:
            Optional additional metadata.

        Returns
        -------
        ConsentRecord
            The newly created consent record.
        """

    @abstractmethod
    async def withdraw_consent(
        self,
        consent_id: str,
        *,
        reason: str | None = None,
    ) -> ConsentRecord:
        """Withdraw a previously granted consent.

        Returns
        -------
        ConsentRecord
            Updated record with ``WITHDRAWN`` status.
        """

    @abstractmethod
    async def check_consent(
        self,
        participant_id: str,
        trial_id: str,
        required_categories: list[ConsentCategory],
    ) -> bool:
        """Verify active consent covers all required
        categories.

        Returns
        -------
        bool
            ``True`` when all *required_categories* are
            covered by active, non-expired consent.
        """

    # -- consent categories ---------------------------------

    @abstractmethod
    async def list_categories(self, trial_id: str) -> list[ConsentCategory]:
        """List consent categories configured for a trial."""

    # -- IRB integration ------------------------------------

    @abstractmethod
    async def verify_irb_approval(
        self,
        protocol_id: str,
        institution: str,
    ) -> IRBApproval:
        """Verify current IRB approval for a protocol.

        Raises
        ------
        ValueError
            If no valid approval exists.
        """

    @abstractmethod
    async def get_irb_approval(
        self,
        irb_id: str,
    ) -> IRBApproval:
        """Retrieve IRB approval metadata by ID."""

    # -- document references --------------------------------

    @abstractmethod
    async def get_consent_document(
        self,
        document_id: str,
        version: str | None = None,
    ) -> ConsentDocumentRef:
        """Retrieve a consent document reference.

        Parameters
        ----------
        document_id:
            Document identifier.
        version:
            Specific version; latest if ``None``.
        """
