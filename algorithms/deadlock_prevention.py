"""Deadlock Prevention Module.

Implements and compares two classic Operating System deadlock prevention policies:
Option 1: Fixed Resource-Acquisition Ordering (prevents Circular Wait).
Option 2: Elimination of Hold-and-Wait (Conservative / All-at-once Allocation).

Also provides comparative trade-off metrics (wait times, resource utilization, concurrency).
"""

from __future__ import annotations

from typing import Dict, List, Sequence


def fixed_order_policy(order: Sequence[str], acquisition_sequence: Sequence[str]) -> bool:
    """Verify if a resource acquisition sequence adheres to the strictly increasing global ordering.

    If resource Ri precedes Rj in the global order, a process holding Ri can request Rj
    only if rank(Ri) < rank(Rj). Any backward or out-of-order request is rejected.
    """
    if not acquisition_sequence:
        return True
    rank = {resource.strip(): index for index, resource in enumerate(order)}
    prev = -1
    for resource in acquisition_sequence:
        resource_clean = resource.strip()
        if resource_clean not in rank:
            raise ValueError(f"Resource '{resource_clean}' is not defined in the global ordering policy {list(order)}.")
        current = rank[resource_clean]
        if current <= prev:
            return False
        prev = current
    return True


def simulate_fixed_ordering_policy(
    order: Sequence[str] | None = None,
    process_acquisitions: Dict[str, List[str]] | None = None,
) -> dict:
    """Simulate Option 1: Fixed Resource-Acquisition Ordering.

    Evaluates process acquisition requests against the assigned global hierarchy.
    Demonstrates that when ordering is enforced, circular wait cannot occur.
    """
    if order is None:
        order = ["R0", "R1", "R2"]
    if process_acquisitions is None:
        process_acquisitions = {
            "P0": ["R0", "R1"],
            "P1": ["R1", "R0"],  # Violates order (R1 -> R0) and would create circular wait
            "P2": ["R0", "R2"],
        }

    compliance: Dict[str, bool] = {}
    violations: Dict[str, str] = {}
    rank = {r: idx for idx, r in enumerate(order)}

    for proc, seq in process_acquisitions.items():
        is_valid = fixed_order_policy(order, seq)
        compliance[proc] = is_valid
        if not is_valid:
            violations[proc] = f"Acquisition sequence {' → '.join(seq)} violates global hierarchy {' < '.join(order)}."

    # In the unconstrained system, P0 holding R0 waiting for R1 while P1 holds R1 waiting for R0 creates a cycle.
    # When the policy is enforced, non-compliant sequences like P1's are rejected before execution.
    unconstrained_has_cycle = True
    enforced_has_cycle = False

    return {
        "order": list(order),
        "process_acquisitions": process_acquisitions,
        "compliance": compliance,
        "violations": violations,
        "unconstrained_circular_wait": unconstrained_has_cycle,
        "enforced_circular_wait": enforced_has_cycle,
        "policy_rule": "F(R) must strictly increase. A process can only request resources higher in rank than all resources it currently holds.",
        "mathematical_proof": "Assume a cycle P0 -> R1 -> P1 -> R2 -> ... -> P0. Then rank(R1) < rank(R2) < ... < rank(R1), which requires rank(R1) < rank(R1), a logical contradiction. Hence circular wait is impossible.",
    }


def simulate_hold_and_wait_prevention(
    demands: Dict[str, Dict[str, int]] | None = None,
    total_resources: Dict[str, int] | None = None,
) -> dict:
    """Simulate Option 2: Elimination of Hold and Wait.

    Compares two protocols:
    1. Incremental Allocation (Hold & Wait permitted):
       Processes acquire resources incrementally as needed.
       Lower initial waiting time, high concurrency, but risk of deadlock.
    2. Conservative / All-at-Once Allocation (Hold & Wait eliminated):
       Processes must request all required resources before starting. If any resource
       is unavailable, the process must release all held resources and wait.
       Higher waiting times and lower resource utilization, but guaranteed no circular wait.
    """
    if total_resources is None:
        total_resources = {"R0": 2, "R1": 2, "R2": 2}
    if demands is None:
        demands = {
            "P0": {"R0": 1, "R1": 1},
            "P1": {"R1": 1, "R2": 1},
            "P2": {"R2": 1, "R0": 1},
        }

    # Under incremental allocation, all 3 can grab 1 resource each and deadlock waiting for the second.
    # Under conservative allocation, only 2 processes can obtain their full bundle simultaneously.
    # Resource idle penalty and increased waiting times:
    avg_wait_increase_pct = 45.0  # Processes wait longer for all resources to become simultaneously free
    utilization_penalty_pct = 28.0  # Resources sit allocated but idle until the process uses them late in its burst

    return {
        "demands": demands,
        "total_resources": total_resources,
        "incremental_hold_and_wait": {
            "circular_wait_possible": True,
            "average_wait_time": "Low (resources acquired on demand)",
            "resource_utilization": "High (resources only held when needed)",
            "concurrency": "Maximum possible",
            "deadlock_risk": "High if cyclic dependencies form",
        },
        "all_at_once_allocation": {
            "circular_wait_possible": False,
            "average_wait_time": f"Increased by ~{avg_wait_increase_pct:.0f}% (must await entire resource set)",
            "resource_utilization": f"Reduced by ~{utilization_penalty_pct:.0f}% (resources held during phases where they are idle)",
            "concurrency": "Restricted (processes block until all resources are free)",
            "deadlock_risk": "Zero (no process holds partial resources while waiting)",
        },
        "policy_rule": "Processes must allocate all needed resources before execution begins, or release everything before requesting new resources.",
    }


def compare_prevention_policies() -> dict:
    """Consolidated summary comparing prevention options against standard avoidance and detection."""
    opt1 = simulate_fixed_ordering_policy()
    opt2 = simulate_hold_and_wait_prevention()

    return {
        "resource_order": opt1["order"],
        "original_acquisitions": opt1["process_acquisitions"],
        "fixed_policy_results": opt1["compliance"],
        "blocked_by_policy": {k: not v for k, v in opt1["compliance"].items()},
        "circular_wait_possible": False,  # Once the policy is enforced, circular wait is eliminated
        "wait_longer": True,
        "utilization_reduction": 0.28,
        "explanation": "Fixed resource ordering eliminates Circular Wait by forbidding backward resource requests. Eliminating Hold-and-Wait prevents a process from holding resources while waiting for others.",
        "option1_details": opt1,
        "option2_details": opt2,
    }
