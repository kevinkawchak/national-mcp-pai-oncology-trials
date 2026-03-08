"""RECIST 1.1 measurement validation and example data structures.

Implements Response Evaluation Criteria In Solid Tumors (RECIST)
version 1.1 validation logic for oncology clinical trials. Provides
validators for target lesion measurements, non-target assessments,
new lesion detection, overall response calculation, and timepoint
comparison.

Reference: Eisenhauer EA, et al. Eur J Cancer. 2009;45(2):228-247.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------

MAX_TARGET_LESIONS = 5
MAX_TARGET_LESIONS_PER_ORGAN = 2
MIN_TARGET_LESION_SIZE_MM = 10.0
MIN_LYMPH_NODE_SHORT_AXIS_MM = 15.0

# Thresholds for response assessment
PR_DECREASE_THRESHOLD = 0.30  # 30% decrease from baseline
PD_INCREASE_THRESHOLD = 0.20  # 20% increase from nadir
PD_ABSOLUTE_INCREASE_MM = 5.0  # 5mm absolute increase


class OverallResponse(str, Enum):
    """RECIST 1.1 overall response categories."""

    CR = "CR"  # Complete Response
    PR = "PR"  # Partial Response
    SD = "SD"  # Stable Disease
    PD = "PD"  # Progressive Disease
    NE = "NE"  # Not Evaluable


class NonTargetAssessment(str, Enum):
    """RECIST 1.1 non-target lesion assessment values."""

    CR = "CR"  # Complete Response
    NON_CR_NON_PD = "non-CR/non-PD"
    PD = "PD"  # Progressive Disease
    NE = "NE"  # Not Evaluable


# -------------------------------------------------------------------
# Example RECIST measurement data structures
# -------------------------------------------------------------------

EXAMPLE_BASELINE_MEASUREMENTS: dict[str, Any] = {
    "timepoint_id": "TP-BASELINE",
    "timepoint_date": "2025-01-15",
    "study_instance_uid": ("1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.79379639"),
    "target_lesions": [
        {
            "lesion_id": "TL-001",
            "organ": "liver",
            "longest_diameter_mm": 32.5,
            "series_instance_uid": (
                "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.10001"
            ),
            "sop_instance_uid": ("1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.50001"),
            "slice_location": -142.5,
            "measurement_method": "axial_longest_diameter",
        },
        {
            "lesion_id": "TL-002",
            "organ": "liver",
            "longest_diameter_mm": 21.0,
            "series_instance_uid": (
                "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.10001"
            ),
            "sop_instance_uid": ("1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.50015"),
            "slice_location": -128.0,
            "measurement_method": "axial_longest_diameter",
        },
        {
            "lesion_id": "TL-003",
            "organ": "lung",
            "longest_diameter_mm": 18.3,
            "series_instance_uid": (
                "1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.10001"
            ),
            "sop_instance_uid": ("1.2.826.0.1.3680043.8.1055.1.20111103111148288.98361414.50042"),
            "slice_location": -45.0,
            "measurement_method": "axial_longest_diameter",
        },
    ],
    "non_target_lesions": [
        {
            "lesion_id": "NTL-001",
            "organ": "bone",
            "description": "T12 vertebral body metastasis",
            "assessment": "non-CR/non-PD",
        },
    ],
    "new_lesions": [],
    "sum_of_diameters_mm": 71.8,  # 32.5 + 21.0 + 18.3
}

EXAMPLE_FOLLOWUP_MEASUREMENTS: dict[str, Any] = {
    "timepoint_id": "TP-WEEK08",
    "timepoint_date": "2025-03-12",
    "study_instance_uid": ("1.2.826.0.1.3680043.8.1055.1.20250312090000000.44444444.55555555"),
    "target_lesions": [
        {
            "lesion_id": "TL-001",
            "organ": "liver",
            "longest_diameter_mm": 22.1,
        },
        {
            "lesion_id": "TL-002",
            "organ": "liver",
            "longest_diameter_mm": 14.5,
        },
        {
            "lesion_id": "TL-003",
            "organ": "lung",
            "longest_diameter_mm": 12.0,
        },
    ],
    "non_target_lesions": [
        {
            "lesion_id": "NTL-001",
            "organ": "bone",
            "description": "T12 vertebral body metastasis",
            "assessment": "non-CR/non-PD",
        },
    ],
    "new_lesions": [],
    "sum_of_diameters_mm": 48.6,  # 22.1 + 14.5 + 12.0
}


# -------------------------------------------------------------------
# Validation functions
# -------------------------------------------------------------------


def validate_target_lesions(
    target_lesions: list[dict[str, Any]],
) -> list[str]:
    """Validate target lesion measurements per RECIST 1.1.

    Checks:
    - Maximum 5 target lesions total.
    - Maximum 2 target lesions per organ.
    - Minimum measurable size (10mm longest diameter,
      15mm short axis for lymph nodes).

    Args:
        target_lesions: List of target lesion measurement
            dictionaries, each containing ``lesion_id``,
            ``organ``, and ``longest_diameter_mm``.

    Returns:
        List of validation error messages. Empty list
        indicates valid measurements.
    """
    errors: list[str] = []

    if len(target_lesions) > MAX_TARGET_LESIONS:
        errors.append(f"Too many target lesions: {len(target_lesions)} (max {MAX_TARGET_LESIONS})")

    # Count lesions per organ
    organ_counts: dict[str, int] = {}
    for lesion in target_lesions:
        organ = lesion.get("organ", "unknown").lower()
        organ_counts[organ] = organ_counts.get(organ, 0) + 1

    for organ, count in organ_counts.items():
        if count > MAX_TARGET_LESIONS_PER_ORGAN:
            errors.append(
                f"Too many target lesions in {organ}: {count} (max {MAX_TARGET_LESIONS_PER_ORGAN})"
            )

    # Validate minimum sizes
    for lesion in target_lesions:
        diameter = lesion.get("longest_diameter_mm", 0)
        lesion_id = lesion.get("lesion_id", "unknown")
        organ = lesion.get("organ", "").lower()

        if organ == "lymph_node":
            if diameter < MIN_LYMPH_NODE_SHORT_AXIS_MM:
                errors.append(
                    f"Lymph node {lesion_id} short axis "
                    f"{diameter}mm < "
                    f"{MIN_LYMPH_NODE_SHORT_AXIS_MM}mm "
                    f"minimum"
                )
        elif diameter < MIN_TARGET_LESION_SIZE_MM:
            errors.append(
                f"Target lesion {lesion_id} diameter "
                f"{diameter}mm < "
                f"{MIN_TARGET_LESION_SIZE_MM}mm minimum"
            )

    return errors


def validate_non_target_assessment(
    assessment: str,
) -> bool:
    """Validate a non-target lesion assessment value.

    Per RECIST 1.1, non-target lesions are assessed as:
    CR, non-CR/non-PD, or PD.

    Args:
        assessment: Assessment string to validate.

    Returns:
        True if the assessment is a valid RECIST 1.1 value.
    """
    try:
        NonTargetAssessment(assessment)
        return True
    except ValueError:
        return False


def validate_new_lesion(
    new_lesion: dict[str, Any],
) -> list[str]:
    """Validate a new lesion detection record.

    New lesions must have identifying information and a
    reference to the imaging study where they were detected.

    Args:
        new_lesion: Dictionary describing the new lesion.

    Returns:
        List of validation error messages.
    """
    errors: list[str] = []
    required_fields = [
        "lesion_id",
        "organ",
        "description",
        "detection_date",
    ]

    for field in required_fields:
        if not new_lesion.get(field):
            errors.append(f"New lesion missing required field: {field!r}")

    return errors


def calculate_sum_of_diameters(
    target_lesions: list[dict[str, Any]],
) -> float:
    """Calculate the sum of longest diameters.

    Args:
        target_lesions: List of target lesion measurements.

    Returns:
        Sum of longest diameters in millimeters.
    """
    return sum(lesion.get("longest_diameter_mm", 0.0) for lesion in target_lesions)


def calculate_overall_response(
    baseline_sum: float,
    nadir_sum: float,
    current_sum: float,
    non_target_assessment: str | None = None,
    has_new_lesions: bool = False,
) -> OverallResponse:
    """Calculate RECIST 1.1 overall response.

    Determines the overall response category based on
    target lesion sum changes, non-target assessments,
    and new lesion status.

    Algorithm per RECIST 1.1:
    1. If new lesions detected -> PD
    2. If target sum increased >= 20% from nadir AND
       >= 5mm absolute increase -> PD
    3. If non-target PD -> PD
    4. If all target lesions disappeared (sum = 0) AND
       non-target CR -> CR
    5. If target sum decreased >= 30% from baseline -> PR
    6. Otherwise -> SD

    Args:
        baseline_sum: Sum of diameters at baseline (mm).
        nadir_sum: Smallest sum of diameters observed (mm).
        current_sum: Sum of diameters at current
            timepoint (mm).
        non_target_assessment: Non-target lesion assessment
            string, if applicable.
        has_new_lesions: Whether new lesions were detected.

    Returns:
        The calculated OverallResponse.
    """
    # New lesions always mean PD
    if has_new_lesions:
        return OverallResponse.PD

    # Check for progression from nadir
    if nadir_sum > 0:
        increase_ratio = (current_sum - nadir_sum) / nadir_sum
        absolute_increase = current_sum - nadir_sum
        if increase_ratio >= PD_INCREASE_THRESHOLD and absolute_increase >= PD_ABSOLUTE_INCREASE_MM:
            return OverallResponse.PD

    # Non-target PD overrides
    if non_target_assessment == NonTargetAssessment.PD.value:
        return OverallResponse.PD

    # Complete response: all targets gone + non-target CR
    if current_sum == 0.0:
        if non_target_assessment is None or non_target_assessment == NonTargetAssessment.CR.value:
            return OverallResponse.CR

    # Partial response: >= 30% decrease from baseline
    if baseline_sum > 0:
        decrease_ratio = (baseline_sum - current_sum) / baseline_sum
        if decrease_ratio >= PR_DECREASE_THRESHOLD:
            return OverallResponse.PR

    return OverallResponse.SD


def compare_timepoints(
    baseline: dict[str, Any],
    followup: dict[str, Any],
    nadir_sum: float | None = None,
) -> dict[str, Any]:
    """Compare two RECIST 1.1 measurement timepoints.

    Computes the overall response by comparing the follow-up
    measurements against the baseline and nadir.

    Args:
        baseline: Baseline measurement timepoint dictionary.
        followup: Follow-up measurement timepoint dictionary.
        nadir_sum: Optional pre-computed nadir sum. If not
            provided, the baseline sum is used as nadir.

    Returns:
        Dictionary containing:
        - ``baseline_sum``: Baseline sum of diameters.
        - ``followup_sum``: Follow-up sum of diameters.
        - ``nadir_sum``: Nadir sum used for comparison.
        - ``percent_change_from_baseline``: Percentage change.
        - ``percent_change_from_nadir``: Percentage change.
        - ``non_target_assessment``: Non-target assessment.
        - ``has_new_lesions``: Whether new lesions found.
        - ``overall_response``: Calculated OverallResponse.
    """
    baseline_sum = baseline.get("sum_of_diameters_mm", 0.0)
    followup_sum = followup.get("sum_of_diameters_mm", 0.0)

    if nadir_sum is None:
        nadir_sum = baseline_sum

    # Update nadir if current is lower
    effective_nadir = min(nadir_sum, followup_sum)

    # Extract non-target assessment
    nt_assessment = None
    non_targets = followup.get("non_target_lesions", [])
    if non_targets:
        assessments = [nt.get("assessment") for nt in non_targets if nt.get("assessment")]
        if assessments:
            # Worst assessment wins
            if any(a == NonTargetAssessment.PD.value for a in assessments):
                nt_assessment = NonTargetAssessment.PD.value
            elif any(a == NonTargetAssessment.NE.value for a in assessments):
                nt_assessment = NonTargetAssessment.NE.value
            elif any(a == NonTargetAssessment.NON_CR_NON_PD.value for a in assessments):
                nt_assessment = NonTargetAssessment.NON_CR_NON_PD.value
            else:
                nt_assessment = NonTargetAssessment.CR.value

    new_lesions = followup.get("new_lesions", [])
    has_new = len(new_lesions) > 0

    overall = calculate_overall_response(
        baseline_sum=baseline_sum,
        nadir_sum=nadir_sum,
        current_sum=followup_sum,
        non_target_assessment=nt_assessment,
        has_new_lesions=has_new,
    )

    pct_from_baseline = (
        ((followup_sum - baseline_sum) / baseline_sum * 100) if baseline_sum > 0 else 0.0
    )
    pct_from_nadir = ((followup_sum - nadir_sum) / nadir_sum * 100) if nadir_sum > 0 else 0.0

    return {
        "baseline_sum": baseline_sum,
        "followup_sum": followup_sum,
        "nadir_sum": effective_nadir,
        "percent_change_from_baseline": round(pct_from_baseline, 1),
        "percent_change_from_nadir": round(pct_from_nadir, 1),
        "non_target_assessment": nt_assessment,
        "has_new_lesions": has_new,
        "overall_response": overall.value,
    }
