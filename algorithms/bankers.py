from __future__ import annotations

from itertools import product
from typing import List, Sequence

from .validation import validate_request, validate_state


def calculate_available(total_instances: Sequence[int], allocation: Sequence[Sequence[int]]) -> List[int]:
    total = list(total_instances)
    return [total[j] - sum(row[j] for row in allocation) for j in range(len(total))]


def calculate_need(maximum: Sequence[Sequence[int]], allocation: Sequence[Sequence[int]]) -> List[List[int]]:
    return [
        [maximum[i][j] - allocation[i][j] for j in range(len(maximum[i]))]
        for i in range(len(maximum))
    ]


def find_safe_sequence(total_instances: Sequence[int], allocation: Sequence[Sequence[int]], maximum: Sequence[Sequence[int]]) -> dict:
    state = validate_state(total_instances, allocation, maximum)
    if not state["valid"]:
        raise ValueError("; ".join(state["errors"]))

    available = state["available"]
    need = state["need"]
    work = available[:]
    finish = [False for _ in allocation]
    safe_sequence: List[int] = []
    steps: List[dict] = []

    iteration = 0
    while True:
        progress = False
        for process_index in range(len(allocation)):
            if finish[process_index]:
                continue
            if all(need[process_index][j] <= work[j] for j in range(len(work))):
                iteration += 1
                work_before = work[:]
                released = list(allocation[process_index])
                work = [work[j] + released[j] for j in range(len(work))]
                finish[process_index] = True
                safe_sequence.append(process_index)
                steps.append(
                    {
                        "iteration": iteration,
                        "selected_process": process_index,
                        "need": list(need[process_index]),
                        "work_before": work_before,
                        "work_after": work[:],
                        "released": released,
                        "explanation": f"Process P{process_index} Need {need[process_index]} <= Work {work_before}. Process finishes, releases {released}, updating Work to {work[:]}."
                    }
                )
                progress = True
                break
        if not progress:
            break

    safe = len(safe_sequence) == len(allocation)
    unfinished_processes = [i for i in range(len(allocation)) if not finish[i]]
    result = {
        "safe": safe,
        "safe_sequence": safe_sequence,
        "unfinished_processes": unfinished_processes,
        "available": available,
        "need": need,
        "steps": steps,
        "reason": (
            "All processes can finish in the computed sequence."
            if safe
            else f"No complete safe sequence exists. Unfinished processes: {[f'P{i}' for i in unfinished_processes]} cannot satisfy their Need with remaining Work {work}."
        ),
    }
    return result


def find_waiting_request_example(total_instances: Sequence[int] | None = None, allocation: Sequence[Sequence[int]] | None = None, maximum: Sequence[Sequence[int]] | None = None) -> dict:
    if total_instances is None:
        total_instances = [10, 5, 7]
    if allocation is None:
        allocation = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ]
    if maximum is None:
        maximum = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ]

    available = calculate_available(total_instances, allocation)
    need = calculate_need(maximum, allocation)

    for process_id in range(len(allocation)):
        max_need = [max(need[process_id]), max(need[process_id]), max(need[process_id])]
        for request in product(range(0, max_need[0] + 1), repeat=len(total_instances)):
            request_vec = list(request)
            if any(request_vec[i] > need[process_id][i] for i in range(len(total_instances))):
                continue
            if any(request_vec[i] > available[i] for i in range(len(total_instances))):
                return {
                    "process_id": process_id,
                    "request": request_vec,
                    "need": need[process_id],
                    "available": available,
                    "is_waiting_example": True,
                }
    raise RuntimeError("No waiting-request scenario could be found for the supplied state.")


def find_unsafe_request_example(total_instances: Sequence[int] | None = None, allocation: Sequence[Sequence[int]] | None = None, maximum: Sequence[Sequence[int]] | None = None) -> dict:
    if total_instances is None:
        total_instances = [10, 5, 7]
    if allocation is None:
        allocation = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ]
    if maximum is None:
        maximum = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ]

    available = calculate_available(total_instances, allocation)
    need = calculate_need(maximum, allocation)

    for process_id in range(len(allocation)):
        upper_bound = [max(need[process_id][i], 0) for i in range(len(total_instances))]
        for request in product(range(0, max(upper_bound) + 1), repeat=len(total_instances)):
            request_vec = list(request)
            if any(request_vec[i] > need[process_id][i] for i in range(len(total_instances))):
                continue
            if any(request_vec[i] > available[i] for i in range(len(total_instances))):
                continue
            temp_available = [available[i] - request_vec[i] for i in range(len(total_instances))]
            temp_allocation = [list(row) for row in allocation]
            temp_allocation[process_id] = [temp_allocation[process_id][i] + request_vec[i] for i in range(len(total_instances))]
            temp_need = [list(row) for row in need]
            temp_need[process_id] = [temp_need[process_id][i] - request_vec[i] for i in range(len(total_instances))]
            safety = find_safe_sequence(total_instances, temp_allocation, maximum)
            if not safety["safe"]:
                return {
                    "process_id": process_id,
                    "request": request_vec,
                    "original_need": need[process_id],
                    "original_available": available,
                    "tentative_allocation": temp_allocation,
                    "tentative_need": temp_need,
                    "status": "unsafe",
                    "safe_sequence": safety["safe_sequence"],
                }
    raise RuntimeError("No unsafe-request scenario could be found for the supplied state.")


def simulate_resource_request(total_instances: Sequence[int], allocation: Sequence[Sequence[int]], maximum: Sequence[Sequence[int]], process_id: int, request: Sequence[int]) -> dict:
    state = validate_state(total_instances, allocation, maximum)
    if not state["valid"]:
        return {"status": "invalid", "message": "; ".join(state["errors"]), "granted": False, "state_unchanged": True}

    available = state["available"]
    need = state["need"]
    process_validation = validate_request(process_id, request, need, available, total_instances)

    if not process_validation["valid"]:
        return {
            "status": process_validation["status"],
            "message": process_validation["message"],
            "granted": False,
            "state_unchanged": True,
            "request": process_validation.get("request", list(request)),
        }

    request_vec = process_validation["request"]
    temp_available = [available[i] - request_vec[i] for i in range(len(available))]
    temp_allocation = [list(row) for row in allocation]
    temp_allocation[process_id] = [temp_allocation[process_id][i] + request_vec[i] for i in range(len(request_vec))]
    temp_need = [list(row) for row in need]
    temp_need[process_id] = [temp_need[process_id][i] - request_vec[i] for i in range(len(request_vec))]

    safety = find_safe_sequence(total_instances, temp_allocation, maximum)
    if safety["safe"]:
        return {
            "status": "granted",
            "message": "Request granted after a safe-state check.",
            "granted": True,
            "state_unchanged": False,
            "request": request_vec,
            "before_allocation": [list(row) for row in allocation],
            "after_allocation": temp_allocation,
            "before_need": [list(row) for row in need],
            "after_need": temp_need,
            "before_available": available,
            "after_available": temp_available,
            "safe_sequence": safety["safe_sequence"],
        }

    return {
        "status": "denied",
        "message": "Request rejected because it leads to an unsafe state. Original state is restored.",
        "granted": False,
        "state_unchanged": True,
        "request": request_vec,
        "before_allocation": [list(row) for row in allocation],
        "after_allocation": [list(row) for row in allocation],
        "before_need": [list(row) for row in need],
        "after_need": [list(row) for row in need],
        "before_available": available,
        "after_available": available,
        "tentative_allocation": temp_allocation,
        "tentative_need": temp_need,
        "tentative_available": temp_available,
        "unsafe_reason": safety["reason"],
        "unfinished_processes": safety.get("unfinished_processes", []),
    }
