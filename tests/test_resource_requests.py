from algorithms import (
    commit_request_if_safe,
    find_unsafe_request_example,
    find_waiting_request_example,
    simulate_request,
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


def test_request_resulting_in_unsafe_state_is_denied():
    scenario = find_unsafe_request_example(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM)
    result = simulate_resource_request(
        DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM,
        scenario["process_id"], scenario["request"],
    )
    assert result["status"] == "denied"
    assert result["granted"] is False
    assert result["state_unchanged"] is True
    assert "tentative_allocation" in result
    assert "tentative_available" in result


def test_successful_request_commit():
    request = [1, 0, 0]
    result = simulate_resource_request(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM, 4, request)
    assert result["status"] == "granted"
    assert result["granted"] is True
    assert result["state_unchanged"] is False
    assert result["after_allocation"][4] == [1, 0, 2]
    assert result["after_available"] == [2, 3, 2]


def test_commit_request_helper():
    committed, result, new_alloc, new_avail = commit_request_if_safe(
        DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM, 4, [1, 0, 0]
    )
    assert committed is True
    assert new_alloc[4] == [1, 0, 2]
    assert new_avail == [2, 3, 2]


def test_denial_leaves_matrices_strictly_identical():
    scenario = find_unsafe_request_example(DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM)
    committed, result, alloc_after, avail_after = commit_request_if_safe(
        DEFAULT_TOTAL, DEFAULT_ALLOCATION, DEFAULT_MAXIMUM, scenario["process_id"], scenario["request"]
    )
    assert committed is False
    assert alloc_after == DEFAULT_ALLOCATION
    assert avail_after == [3, 3, 2]
