"""Secure aggregation hooks.

Provides an aggregation protocol interface with privacy-
preserving result combination via additive masking, share
generation, and result reconstruction.
"""

from __future__ import annotations

import hashlib
import os
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AggregationProtocol(Enum):
    """Supported secure aggregation protocols."""

    PLAIN = "plain"
    ADDITIVE_MASKING = "additive_masking"
    SECURE_SUM = "secure_sum"


class ShareStatus(Enum):
    """Status of a contribution share."""

    PENDING = "pending"
    RECEIVED = "received"
    VERIFIED = "verified"
    INVALID = "invalid"


@dataclass(frozen=True)
class AggregationConfig:
    """Configuration for a secure aggregation round."""

    protocol: AggregationProtocol = AggregationProtocol.ADDITIVE_MASKING
    min_participants: int = 2
    vector_length: int = 0
    modulus: int = 2**32
    require_verification: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Share:
    """A single participant's masked share."""

    site_id: str
    round_id: str
    values: list[int]
    mask_commitment: str = ""
    status: ShareStatus = ShareStatus.PENDING
    submitted_at: float = 0.0


@dataclass
class AggregationRound:
    """State for one secure aggregation round."""

    round_id: str
    config: AggregationConfig
    shares: list[Share] = field(default_factory=list)
    result: list[int] | None = None
    is_complete: bool = False


# -- additive masking helpers --------------------------------


def generate_mask(length: int, modulus: int = 2**32) -> list[int]:
    """Generate a random additive mask vector.

    Parameters
    ----------
    length:
        Number of elements in the mask vector.
    modulus:
        Modular arithmetic modulus.

    Returns
    -------
    list[int]
        Random mask values in ``[0, modulus)``.
    """
    masks: list[int] = []
    for _ in range(length):
        raw = struct.unpack(">I", os.urandom(4))[0]
        masks.append(raw % modulus)
    return masks


def apply_mask(
    values: list[int],
    mask: list[int],
    modulus: int = 2**32,
) -> list[int]:
    """Apply an additive mask to a value vector.

    Parameters
    ----------
    values:
        Original values.
    mask:
        Mask vector (same length as *values*).
    modulus:
        Modular arithmetic modulus.

    Returns
    -------
    list[int]
        Masked values ``(v + m) mod modulus``.
    """
    if len(values) != len(mask):
        raise ValueError("Values and mask must have the same length")
    return [(v + m) % modulus for v, m in zip(values, mask)]


def remove_mask(
    masked: list[int],
    mask: list[int],
    modulus: int = 2**32,
) -> list[int]:
    """Remove an additive mask from a masked vector.

    Returns
    -------
    list[int]
        Original values ``(masked - m) mod modulus``.
    """
    if len(masked) != len(mask):
        raise ValueError("Masked values and mask must have the same length")
    return [(v - m) % modulus for v, m in zip(masked, mask)]


def compute_commitment(mask: list[int]) -> str:
    """Compute a SHA-256 commitment for a mask vector.

    The commitment allows later verification that the
    correct mask was used without revealing the mask
    itself.
    """
    blob = ",".join(str(v) for v in mask)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# -- aggregation logic --------------------------------------


def aggregate_shares(
    shares: list[Share],
    modulus: int = 2**32,
) -> list[int]:
    """Sum masked shares element-wise modulo *modulus*.

    Parameters
    ----------
    shares:
        All participant shares for a round.
    modulus:
        Modular arithmetic modulus.

    Returns
    -------
    list[int]
        Aggregated sum vector.

    Raises
    ------
    ValueError
        If shares have inconsistent vector lengths.
    """
    if not shares:
        raise ValueError("No shares to aggregate")
    length = len(shares[0].values)
    for s in shares[1:]:
        if len(s.values) != length:
            raise ValueError("All shares must have the same vector length")
    result = [0] * length
    for share in shares:
        for i, v in enumerate(share.values):
            result[i] = (result[i] + v) % modulus
    return result


class SecureAggregationAdapter(ABC):
    """Abstract adapter for secure aggregation protocols.

    Implementations integrate with secure computation
    frameworks or provide built-in additive-masking
    aggregation.
    """

    @abstractmethod
    async def create_round(
        self,
        round_id: str,
        config: AggregationConfig,
    ) -> AggregationRound:
        """Initialize a new aggregation round."""

    @abstractmethod
    async def submit_share(
        self,
        round_id: str,
        share: Share,
    ) -> AggregationRound:
        """Submit a participant's share for a round."""

    @abstractmethod
    async def finalize(self, round_id: str) -> list[int]:
        """Finalize the round and produce aggregated result.

        Raises
        ------
        ValueError
            If the minimum participant count has not been
            reached.
        """

    @abstractmethod
    async def get_round(self, round_id: str) -> AggregationRound:
        """Retrieve the current state of a round."""

    @abstractmethod
    async def generate_shares(
        self,
        site_id: str,
        round_id: str,
        values: list[int],
    ) -> tuple[Share, list[int]]:
        """Generate a masked share and return the mask.

        Returns
        -------
        tuple[Share, list[int]]
            The masked share and the mask used (kept by the
            participant for later verification).
        """

    @abstractmethod
    async def reconstruct(
        self,
        round_id: str,
        aggregated: list[int],
        masks: list[list[int]],
    ) -> list[int]:
        """Reconstruct the true aggregate by removing masks.

        Parameters
        ----------
        round_id:
            The round being reconstructed.
        aggregated:
            Element-wise sum of masked shares.
        masks:
            All participant masks.

        Returns
        -------
        list[int]
            The unmasked aggregate result.
        """
