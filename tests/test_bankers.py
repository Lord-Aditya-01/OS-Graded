from algorithms import (
    calculate_available,
    calculate_need,
    find_safe_sequence,
    find_unsafe_request_example,
    find_waiting_request_example,
    simulate_resource_request,
)

DEFAULT_TOTAL = [10, 5, 7]
DEFAULT_ALLOCATION = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2],
]
DEFAULT_MAXIMUM = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3],
]


def test_need_matrix_calculation():
    expected = [
        [7, 4, 3],
        [1, 2, 2],
        [6, 0, 0],
        [0, 1, 1],
        [4, 3, 1],
    ]
    assert calculate_need(DEFAULT_MAXIMUM, DEFAULT_ALLOCATION) == expected


def test_available_vector_calculation():
    available = calculate_available(DEFAULT_TOTAL, DEFAULT_ALLOCATION)
    assert available == [3, 3, 2]


def test_safe_sequence_generation():
    result = find_safe_sequence(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM)
    assert result["safe"] is True
    assert len(result["safe_sequence"]) == len(DEFAULT_ALLOCATION)
    assert len(result["unfinished_processes"]) == 0
    assert len(result["steps"]) == len(DEFAULT_ALLOCATION)


def test_unsafe_state_detection():
    # If total instances are reduced so that no process can finish:
    total = [3, 3, 2]
    alloc = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    max_d = [[3, 3, 2], [3, 3, 2], [3, 3, 2]]
    result = find_safe_sequence(total, alloc, max_d)
    assert result["safe"] is False
    assert len(result["unfinished_processes"]) > 0


def test_step_trace_details():
    result = find_safe_sequence(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM)
    for step in result["steps"]:
        assert "iteration" in step
        assert "selected_process" in step
        assert "work_before" in step
        assert "work_after" in step
        assert "released" in step
        assert "explanation" in step


def test_request_exceeding_need_is_invalid():
    result = simulate_resource_request(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM, 0, [10, 0, 0])
    assert result["status"] == "invalid"
    assert result["granted"] is False
    assert result["state_unchanged"] is True


def test_waiting_request_is_not_invalid():
    scenario = find_waiting_request_example(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM)
    result = simulate_resource_request(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM, scenario["process_id"], scenario["request"])
    assert result["status"] == "waiting"
    assert result["granted"] is False
    assert result["state_unchanged"] is True


def test_unsafe_request_denial_restores_state():
    scenario = find_unsafe_request_example(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM)
    original_alloc = [row[:] for row in DEFAULT_ALLOCATION]
    result = simulate_resource_request(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM, scenario["process_id"], scenario["request"])
    assert result["status"] == "denied"
    assert result["granted"] is False
    assert result["state_unchanged"] is True
    assert DEFAULT_ALLOCATION == original_alloc
