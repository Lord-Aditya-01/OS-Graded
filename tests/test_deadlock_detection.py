from algorithms.deadlock_detection import (
    build_circular_wait_scenario,
    detect_deadlock,
    get_rag_edges,
    recover_and_detect,
    recover_process,
)


def test_deadlock_detection_for_circular_wait_example():
    scenario = build_circular_wait_scenario()
    result = detect_deadlock(scenario["available"], scenario["allocation"], scenario["request"])
    assert result["deadlocked"] is True
    assert set(result["deadlocked_processes"]) == {0, 1}
    assert len(result["steps"]) == 0  # Neither process can proceed initially


def test_recovery_after_terminating_a_process():
    scenario = build_circular_wait_scenario()
    recovered = recover_process(scenario["available"], scenario["allocation"], scenario["request"], 0)
    assert recovered["allocation"][0] == [0, 0]
    assert recovered["available"] == [1, 0]
    assert recovered["released"] == [1, 0]


def test_recover_and_detect_clears_deadlock():
    scenario = build_circular_wait_scenario()
    result = recover_and_detect(scenario["available"], scenario["allocation"], scenario["request"], 0)
    assert result["deadlock_cleared"] is True
    assert result["detection_after"]["deadlocked"] is False
    assert len(result["detection_after"]["finished"]) == 2


def test_rag_edge_generation():
    scenario = build_circular_wait_scenario()
    edges = get_rag_edges(scenario["allocation"], scenario["request"], ["R0", "R1"])
    # P0 holds R0 -> edge ('R0', 'P0', ...)
    # P0 requests R1 -> edge ('P0', 'R1', ...)
    # P1 holds R1 -> edge ('R1', 'P1', ...)
    # P1 requests R0 -> edge ('P1', 'R0', ...)
    assert len(edges) == 4
    edge_pairs = [(e[0], e[1]) for e in edges]
    assert ("R0", "P0") in edge_pairs
    assert ("P0", "R1") in edge_pairs
    assert ("R1", "P1") in edge_pairs
    assert ("P1", "R0") in edge_pairs


def test_no_deadlock_when_work_is_sufficient():
    # If available is sufficient to satisfy all requests
    available = [2, 2]
    allocation = [[1, 0], [0, 1]]
    request = [[1, 0], [0, 1]]
    result = detect_deadlock(available, allocation, request)
    assert result["deadlocked"] is False
    assert len(result["finished"]) == 2
