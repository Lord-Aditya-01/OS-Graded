"""Resource Request Procedure for Banker's Algorithm.

This module implements the complete 7-step resource-request procedure:
Step 1: Validate process ID exists.
Step 2: If Request[i] > Need[i], reject as invalid / excessive request.
Step 3: If Request[i] > Available, report request cannot be granted immediately
        (REQUEST WAITING / NOT CURRENTLY AVAILABLE).
Step 4: Temporarily simulate allocation:
        Available = Available - Request[i]
        Allocation[i] = Allocation[i] + Request[i]
        Need[i] = Need[i] - Request[i]
Step 5: Run the safety algorithm.
Step 6: If safe, commit allocation and report granted.
Step 7: If unsafe, reject request and restore exact original state.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple
from .bankers import calculate_available, calculate_need, find_safe_sequence, simulate_resource_request
from .validation import validate_request, validate_state


def validate_request_parameters(
    process_id: int,
    request: Sequence[int],
    need: Sequence[Sequence[int]],
    available: Sequence[int],
    total_instances: Sequence[int],
) -> dict:
    """Validate a resource request against remaining Need and Available resources."""
    return validate_request(process_id, request, need, available, total_instances)


def simulate_request(
    total_instances: Sequence[int],
    allocation: Sequence[Sequence[int]],
    maximum: Sequence[Sequence[int]],
    process_id: int,
    request: Sequence[int],
) -> dict:
    """Execute the full 7-step Banker's resource-request procedure."""
    return simulate_resource_request(total_instances, allocation, maximum, process_id, request)


def commit_request_if_safe(
    total_instances: Sequence[int],
    allocation: Sequence[Sequence[int]],
    maximum: Sequence[Sequence[int]],
    process_id: int,
    request: Sequence[int],
) -> Tuple[bool, dict, List[List[int]], List[int]]:
    """Simulate request and, if safe, return (True, result, new_allocation, new_available).

    If unsafe or invalid, returns (False, result, original_allocation, original_available).
    Guarantees that state is never mutated unless safety is rigorously proven.
    """
    result = simulate_resource_request(total_instances, allocation, maximum, process_id, request)
    if result["granted"]:
        return True, result, result["after_allocation"], result["after_available"]
    return False, result, [list(r) for r in allocation], calculate_available(total_instances, allocation)


def request_with_validation(
    total_instances: Sequence[int],
    allocation: Sequence[Sequence[int]],
    maximum: Sequence[Sequence[int]],
    process_id: int,
    request: Sequence[int],
) -> dict:
    """Backward-compatible entry point for resource request validation and simulation."""
    return simulate_resource_request(total_instances, allocation, maximum, process_id, request)
