"""Deadlock Detection and Recovery Module.

Implements the standard multi-instance deadlock detection algorithm
(Silberschatz et al., Chapter 8) and circular wait RAG modeling with recovery.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple


def detect_deadlock(
    available: Sequence[int],
    allocation: Sequence[Sequence[int]],
    request: Sequence[Sequence[int]],
) -> dict:
    """Execute the standard deadlock-detection algorithm for multiple resource instances.

    Algorithm:
    1. Work = Available
    2. Finish[i] = (Allocation[i] == 0) for each process i.
       (Processes holding no resources cannot be part of a deadlock).
    3. Find an index i such that:
       a) Finish[i] == False
       b) Request[i] <= Work (component-wise)
    4. If found:
       Work = Work + Allocation[i]
       Finish[i] = True
       Repeat from step 3.
    5. If Finish[i] == False for any i, process i is deadlocked.
    """
    if len(allocation) != len(request):
        raise ValueError("Allocation and request matrices must have matching process counts.")
    if allocation and len(available) != len(allocation[0]):
        raise ValueError("Available vector length must match resource count.")

    work = list(available)
    num_processes = len(allocation)
    # Processes holding no resources can finish immediately
    finish = [sum(allocation[i]) == 0 for i in range(num_processes)]
    steps: List[dict] = []
    iteration = 0

    while True:
        progress = False
        for process_id in range(num_processes):
            if finish[process_id]:
                continue
            if all(request[process_id][r] <= work[r] for r in range(len(work))):
                iteration += 1
                work_before = work[:]
                released = list(allocation[process_id])
                work = [work[r] + released[r] for r in range(len(work))]
                finish[process_id] = True
                steps.append(
                    {
                        "iteration": iteration,
                        "process": process_id,
                        "work_before": work_before,
                        "work_after": work[:],
                        "request": list(request[process_id]),
                        "allocation": released,
                        "explanation": f"Process P{process_id} Request {request[process_id]} <= Work {work_before}. Process completes and releases {released}. Work updated to {work[:]}."
                    }
                )
                progress = True
                break
        if not progress:
            break

    deadlocked = [i for i in range(num_processes) if not finish[i]]
    return {
        "deadlocked": bool(deadlocked),
        "deadlocked_processes": deadlocked,
        "finished": [i for i in range(num_processes) if finish[i]],
        "steps": steps,
        "final_work": work,
        "message": (
            f"Deadlock detected! Processes {[f'P{i}' for i in deadlocked]} are involved in a deadlock."
            if deadlocked
            else "No deadlock detected by the selected detection model. All processes can proceed to completion."
        ),
    }


def build_circular_wait_scenario() -> dict:
    """Construct the textbook 2-process, 2-resource circular wait scenario.

    P0 holds R0 and requests R1.
    P1 holds R1 and requests R0.
    Cycle: P0 -> R1 -> P1 -> R0 -> P0.
    """
    total = [1, 1]
    allocation = [
        [1, 0],
        [0, 1],
    ]
    request = [
        [0, 1],
        [1, 0],
    ]
    available = [0, 0]
    return {
        "total": total,
        "allocation": allocation,
        "request": request,
        "available": available,
        "cycle": "P0 → R1 → P1 → R0 → P0",
        "description": "P0 holds R0 and waits for R1. P1 holds R1 and waits for R0.",
    }


def recover_process(
    available: Sequence[int],
    allocation: Sequence[Sequence[int]],
    request: Sequence[Sequence[int]],
    process_id: int,
) -> dict:
    """Perform deadlock recovery via process termination.

    Terminates the specified process, releases all of its allocated resources
    back into the Available pool, and resets its request vector.
    """
    if process_id < 0 or process_id >= len(allocation):
        raise ValueError(f"Invalid process identifier: {process_id}")

    released = list(allocation[process_id])
    updated_available = [available[r] + released[r] for r in range(len(available))]
    updated_allocation = [list(row) for row in allocation]
    updated_allocation[process_id] = [0 for _ in range(len(available))]
    updated_request = [list(row) for row in request]
    updated_request[process_id] = [0 for _ in range(len(available))]

    return {
        "available": updated_available,
        "allocation": updated_allocation,
        "request": updated_request,
        "released": released,
        "terminated_process": process_id,
    }


def recover_and_detect(
    available: Sequence[int],
    allocation: Sequence[Sequence[int]],
    request: Sequence[Sequence[int]],
    process_id: int,
) -> dict:
    """Terminate a process and immediately re-run deadlock detection on the resulting state."""
    rec = recover_process(available, allocation, request, process_id)
    detection_after = detect_deadlock(rec["available"], rec["allocation"], rec["request"])
    return {
        **rec,
        "detection_after": detection_after,
        "deadlock_cleared": not detection_after["deadlocked"],
    }


def get_rag_edges(
    allocation: Sequence[Sequence[int]],
    request: Sequence[Sequence[int]],
    resource_names: Sequence[str] | None = None,
) -> List[Tuple[str, str, str]]:
    """Generate edges for a Resource Allocation Graph (RAG).

    Returns a list of (source_node, target_node, edge_type):
    - ('R_j', 'P_i', 'assignment') if Allocation[i][j] > 0
    - ('P_i', 'R_j', 'request') if Request[i][j] > 0
    """
    num_p = len(allocation)
    num_r = len(allocation[0]) if num_p > 0 else 0
    if resource_names is None:
        r_names = [f"R{j}" for j in range(num_r)]
    else:
        r_names = list(resource_names)

    edges: List[Tuple[str, str, str]] = []
    for i in range(num_p):
        p_name = f"P{i}"
        for j in range(num_r):
            r_name = r_names[j]
            if allocation[i][j] > 0:
                edges.append((r_name, p_name, f"allocates ({allocation[i][j]})"))
            if request[i][j] > 0:
                edges.append((p_name, r_name, f"requests ({request[i][j]})"))
    return edges
