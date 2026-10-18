"""Boundary Tests and Analytical Results Test Runner.

Implements all 10 boundary and edge-case test cases from Section 14:
1. Zero available resources.
2. A process with zero remaining Need.
3. An invalid process identifier.
4. A negative resource request.
5. Allocation exceeding maximum demand.
6. A request exceeding remaining Need.
7. A request exceeding Available.
8. An inconsistent resource total.
9. A safe configuration.
10. An unsafe configuration.

Also implements the dynamic execution runner for the Required Analytical Results Table (TC1 - TC6)
from Section 16.
"""

from __future__ import annotations

from typing import Any, Dict, List
from .bankers import (
    calculate_available,
    calculate_need,
    find_safe_sequence,
    find_unsafe_request_example,
    find_waiting_request_example,
    simulate_resource_request,
)
from .deadlock_detection import build_circular_wait_scenario, detect_deadlock
from .deadlock_prevention import compare_prevention_policies, fixed_order_policy
from .validation import validate_request, validate_resource_configuration, validate_state


def run_boundary_tests() -> List[Dict[str, Any]]:
    """Execute all 10 boundary and edge-case tests with live results and assertions."""
    results: List[Dict[str, Any]] = []

    # 1. Zero available resources (valid state where a process with zero need can finish)
    tot1 = [5, 5]
    alloc1 = [[3, 3], [2, 2]]
    max1 = [[3, 3], [5, 5]]  # P0 has need [0, 0]
    avail1 = calculate_available(tot1, alloc1)  # [0, 0]
    safe1 = find_safe_sequence(tot1, alloc1, max1)
    p1_passed = (avail1 == [0, 0]) and safe1["safe"]
    results.append({
        "id": "BT1",
        "name": "Zero Available Resources",
        "input": f"Total={tot1}, Alloc={alloc1}, Available={avail1}, P0 Need=[0, 0]",
        "expected": "Valid edge case; P0 finishes immediately with zero need, releasing resources",
        "actual": f"Available={avail1}, Safe={safe1['safe']}, Sequence={safe1['safe_sequence']}",
        "pass": p1_passed,
        "explanation": "A zero Available vector is not automatically an error or deadlocked. P0 needs 0 resources, finishes first, releases [3, 3], enabling P1 to finish.",
    })

    # 2. A process with zero remaining Need
    tot2 = [10, 10]
    alloc2 = [[4, 4], [2, 2]]
    max2 = [[4, 4], [5, 5]]
    need2 = calculate_need(max2, alloc2)
    p2_passed = (need2[0] == [0, 0])
    results.append({
        "id": "BT2",
        "name": "Process with Zero Remaining Need",
        "input": f"P0 Allocation={alloc2[0]}, Maximum={max2[0]}",
        "expected": "P0 Need is [0, 0]; process can execute to completion immediately",
        "actual": f"P0 Need = {need2[0]}",
        "pass": p2_passed,
        "explanation": "When Need is zero, a process has already obtained its maximum demand and can terminate without requesting further resources.",
    })

    # 3. An invalid process identifier
    val3 = validate_request(
        process_id=99,
        request=[1, 1],
        need=[[2, 2]],
        available=[5, 5],
        total_instances=[10, 10],
    )
    p3_passed = (val3["status"] == "invalid") and ("invalid" in val3["message"].lower())
    results.append({
        "id": "BT3",
        "name": "Invalid Process Identifier",
        "input": "Process ID = 99 (valid range: 0..0)",
        "expected": "Rejected with status 'invalid' and descriptive error message",
        "actual": f"Status: {val3['status']} — {val3['message']}",
        "pass": p3_passed,
        "explanation": "Process indices outside the configured matrix boundaries are rejected before any resource evaluation.",
    })

    # 4. A negative resource request
    val4 = validate_request(
        process_id=0,
        request=[-1, 2],
        need=[[3, 3]],
        available=[5, 5],
        total_instances=[10, 10],
    )
    p4_passed = (val4["status"] == "invalid") and any("negative" in err.lower() for err in val4["errors"])
    results.append({
        "id": "BT4",
        "name": "Negative Resource Request",
        "input": "Request = [-1, 2]",
        "expected": "Rejected as invalid input; resource counts must be nonnegative integers",
        "actual": f"Status: {val4['status']} — {val4.get('message', val4['errors'])}",
        "pass": p4_passed,
        "explanation": "Resource requests must represent nonnegative counts. Negative values are caught and rejected during input validation.",
    })

    # 5. Allocation exceeding maximum demand
    val5 = validate_resource_configuration(
        total_instances=[10, 10],
        allocation=[[5, 8]],
        maximum=[[5, 4]],  # Resource 1 allocation (8) exceeds Maximum (4)
    )
    p5_passed = (not val5["valid"]) and any("exceeds maximum" in err.lower() for err in val5["errors"])
    results.append({
        "id": "BT5",
        "name": "Allocation Exceeding Maximum Demand",
        "input": "Allocation=[5, 8], Maximum=[5, 4]",
        "expected": "Configuration invalid; Allocation cannot exceed Maximum demand",
        "actual": f"Valid: {val5['valid']} — {val5['errors']}",
        "pass": p5_passed,
        "explanation": "In the Banker's model, no process may hold more resources than its declared maximum demand.",
    })

    # 6. A request exceeding remaining Need
    sim6 = simulate_resource_request(
        total_instances=[10, 10],
        allocation=[[2, 2]],
        maximum=[[5, 5]],
        process_id=0,
        request=[4, 1],  # Need is [3, 3]; 4 > 3
    )
    p6_passed = (sim6["status"] == "invalid") and (not sim6["granted"]) and sim6["state_unchanged"]
    results.append({
        "id": "BT6",
        "name": "Request Exceeding Remaining Need",
        "input": "Need=[3, 3], Request=[4, 1]",
        "expected": "Rejected as invalid/excessive request; original state remains unchanged",
        "actual": f"Status: {sim6['status']} — {sim6['message']}",
        "pass": p6_passed,
        "explanation": "A process cannot request more than its declared remaining Need. Doing so violates its maximum claim contract.",
    })

    # 7. A request exceeding Available
    sim7 = simulate_resource_request(
        total_instances=[10, 10],
        allocation=[[2, 2]],
        maximum=[[8, 8]],
        process_id=0,
        request=[9, 1],  # Need is [6, 6], wait: request 9 > need 6. Let's make Need=[8, 8] and Available=[8, 8]
    )
    # Let's construct clean case where Request <= Need but Request > Available:
    # Total=[5, 5], Alloc=[[3, 3], [1, 1]], Available=[1, 1]. P0 Max=[5, 5], Need=[2, 2]. P0 requests [2, 1] <= Need, but 2 > Available[0](1).
    sim7_clean = simulate_resource_request(
        total_instances=[5, 5],
        allocation=[[3, 3], [1, 1]],
        maximum=[[5, 5], [2, 2]],
        process_id=0,
        request=[2, 1],
    )
    p7_passed = (sim7_clean["status"] == "waiting") and (not sim7_clean["granted"]) and sim7_clean["state_unchanged"]
    results.append({
        "id": "BT7",
        "name": "Request Exceeding Available Resources",
        "input": "Need=[2, 2], Available=[1, 1], Request=[2, 1]",
        "expected": "Classified as 'waiting' (not invalid); state remains completely unchanged",
        "actual": f"Status: {sim7_clean['status']} — {sim7_clean['message']}",
        "pass": p7_passed,
        "explanation": "When Request <= Need but Request > Available, the request is valid but must wait. It is not an invalid request.",
    })

    # 8. An inconsistent resource total
    val8 = validate_resource_configuration(
        total_instances=[5, 5],
        allocation=[[3, 3], [4, 1]],  # sum(Alloc[:, 0]) = 7 > Total 5
        maximum=[[4, 4], [4, 4]],
    )
    p8_passed = (not val8["valid"]) and any("exceeds total capacity" in err.lower() for err in val8["errors"])
    results.append({
        "id": "BT8",
        "name": "Inconsistent Resource Total",
        "input": "Total=[5, 5], Total Allocated=[7, 4]",
        "expected": "Configuration invalid; total allocated cannot exceed system resource capacity",
        "actual": f"Valid: {val8['valid']} — {val8['errors']}",
        "pass": p8_passed,
        "explanation": "If the sum of allocations across processes exceeds the total resource capacity, Available becomes negative, which is physically impossible.",
    })

    # 9. A safe configuration
    tot9 = [10, 5, 7]
    alloc9 = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
    max9 = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
    safe9 = find_safe_sequence(tot9, alloc9, max9)
    p9_passed = safe9["safe"] and (len(safe9["safe_sequence"]) == 5)
    results.append({
        "id": "BT9",
        "name": "Safe Configuration",
        "input": f"Default 5-process, 3-resource state with Available={safe9['available']}",
        "expected": "SAFE state identified; complete safe sequence generated",
        "actual": f"Safe: {safe9['safe']}, Sequence: {safe9['safe_sequence']}",
        "pass": p9_passed,
        "explanation": "All 5 processes can finish sequentially under their declared maximum bounds. System remains completely safe.",
    })

    # 10. An unsafe configuration
    # Structurally valid inputs, but Available is low and all processes have high needs
    tot10 = [3, 3, 2]
    alloc10 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    max10 = [[3, 3, 2], [3, 3, 2], [3, 3, 2]]  # Each needs [2, 3, 2], [3, 2, 2], [3, 3, 1], Available=[2, 2, 1]
    safe10 = find_safe_sequence(tot10, alloc10, max10)
    p10_passed = (not safe10["safe"]) and (len(safe10["unfinished_processes"]) > 0)
    results.append({
        "id": "BT10",
        "name": "Unsafe Configuration",
        "input": f"Available={safe10['available']}, Needs each exceed Available",
        "expected": "UNSAFE state identified; no complete safe sequence exists",
        "actual": f"Safe: {safe10['safe']}, Unfinished: {safe10['unfinished_processes']}",
        "pass": p10_passed,
        "explanation": "No process can be guaranteed to finish under maximum demands. Note: Unsafe means lack of safe execution guarantee, not an immediate deadlock.",
    })

    return results


def run_analytical_test_cases() -> List[Dict[str, Any]]:
    """Execute the 6 Required Analytical Test Cases (TC1 - TC6) dynamically."""
    default_total = [10, 5, 7]
    default_allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ]
    default_maximum = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
    ]

    # TC1: Safe state
    safe_result = find_safe_sequence(default_total, default_allocation, default_maximum)
    tc1_pass = safe_result["safe"] and len(safe_result["safe_sequence"]) == len(default_allocation)

    # TC2: Request exceeds Available
    waiting_example = find_waiting_request_example(default_total, default_allocation, default_maximum)
    waiting_result = simulate_resource_request(
        default_total, default_allocation, default_maximum,
        waiting_example["process_id"], waiting_example["request"],
    )
    tc2_pass = (waiting_result["status"] == "waiting") and waiting_result["state_unchanged"]

    # TC3: Request makes state unsafe
    unsafe_example = find_unsafe_request_example(default_total, default_allocation, default_maximum)
    unsafe_result = simulate_resource_request(
        default_total, default_allocation, default_maximum,
        unsafe_example["process_id"], unsafe_example["request"],
    )
    tc3_pass = (unsafe_result["status"] == "denied") and unsafe_result["state_unchanged"]

    # TC4: Deadlocked scenario
    scenario = build_circular_wait_scenario()
    deadlock_result = detect_deadlock(scenario["available"], scenario["allocation"], scenario["request"])
    tc4_pass = deadlock_result["deadlocked"] and set(deadlock_result["deadlocked_processes"]) == {0, 1}

    # TC5: Prevention policy applied
    prevention = compare_prevention_policies()
    tc5_pass = (prevention["circular_wait_possible"] is False) and (prevention["wait_longer"] is True)

    # TC6: Boundary and invalid inputs
    boundary_results = run_boundary_tests()
    all_boundary_passed = all(b["pass"] for b in boundary_results)
    tc6_pass = all_boundary_passed

    rows = [
        {
            "Test Case": "TC1 — Safe state",
            "System Condition": "Safe",
            "Input or Scenario": f"Default 5-process allocation; Available = {safe_result['available']}",
            "Expected Result": "Safe sequence found",
            "Actual Result": f"Safe sequence: {safe_result['safe_sequence']}",
            "Pass/Fail": "PASS" if tc1_pass else "FAIL",
            "Analysis/Conclusion": "All processes can finish sequentially. Work vector increases monotonically to total instances.",
        },
        {
            "Test Case": "TC2 — Request exceeds Available",
            "System Condition": "Waiting",
            "Input or Scenario": f"P{waiting_example['process_id']} requests {waiting_example['request']} (Available={waiting_example['available']})",
            "Expected Result": "Request not granted immediately; classified as waiting",
            "Actual Result": f"Status: {waiting_result['status']} (state_unchanged={waiting_result['state_unchanged']})",
            "Pass/Fail": "PASS" if tc2_pass else "FAIL",
            "Analysis/Conclusion": "Request is valid because Request <= Need, but cannot be satisfied immediately. Correctly placed in waiting state without modifying allocation.",
        },
        {
            "Test Case": "TC3 — Request makes state unsafe",
            "System Condition": "Unsafe",
            "Input or Scenario": f"P{unsafe_example['process_id']} requests {unsafe_example['request']}",
            "Expected Result": "Request denied; original state unchanged",
            "Actual Result": f"Status: {unsafe_result['status']} (state_unchanged={unsafe_result['state_unchanged']})",
            "Pass/Fail": "PASS" if tc3_pass else "FAIL",
            "Analysis/Conclusion": "Tentative allocation leaves no complete safe sequence. The algorithm detects the unsafe outcome, rolls back the tentative state, and denies the request.",
        },
        {
            "Test Case": "TC4 — Deadlocked scenario",
            "System Condition": "Deadlock",
            "Input or Scenario": scenario["cycle"],
            "Expected Result": "Deadlock identified by the selected detection method",
            "Actual Result": f"Deadlocked processes: {[f'P{p}' for p in deadlock_result['deadlocked_processes']]}",
            "Pass/Fail": "PASS" if tc4_pass else "FAIL",
            "Analysis/Conclusion": "Single-instance circular wait condition confirmed by detection algorithm (Work=[0,0], neither process can proceed).",
        },
        {
            "Test Case": "TC5 — Prevention policy applied",
            "System Condition": "Prevention",
            "Input or Scenario": "Fixed global ordering (R0 < R1 < R2) & Hold-and-Wait elimination",
            "Expected Result": "Selected deadlock condition eliminated under enforced policy",
            "Actual Result": f"Circular wait possible: {prevention['circular_wait_possible']} (Enforced)",
            "Pass/Fail": "PASS" if tc5_pass else "FAIL",
            "Analysis/Conclusion": "Strict hierarchical ordering forbids backward requests, making directed cycle formation impossible by topological sorting.",
        },
        {
            "Test Case": "TC6 — Boundary and invalid inputs",
            "System Condition": "Boundary / Invalid",
            "Input or Scenario": f"10 automated edge & invalid cases (negatives, overflows, bounds)",
            "Expected Result": "Correct handling or a useful validation message across all cases",
            "Actual Result": f"{sum(1 for b in boundary_results if b['pass'])}/10 boundary cases passed",
            "Pass/Fail": "PASS" if tc6_pass else "FAIL",
            "Analysis/Conclusion": "All boundary conditions (zero available, negative requests, invalid IDs, over-allocation) handled strictly according to OS theory.",
        },
    ]

    return rows
