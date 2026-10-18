from algorithms.validation import (
    validate_request,
    validate_resource_configuration,
    validate_state,
)


def test_negative_input_validation():
    validation = validate_request(0, [-1, 0], [[1, 1], [0, 0]], [1, 1], [2, 2])
    assert validation["valid"] is False
    assert validation["status"] == "invalid"


def test_invalid_process_identifier():
    validation = validate_request(99, [0, 0], [[0, 0]], [1, 1], [2, 2])
    assert validation["valid"] is False
    assert "invalid" in validation["message"].lower()


def test_inconsistent_matrix_is_rejected():
    config = validate_resource_configuration([10, 5], [[5, 0]], [[7, 5, 0]])
    assert config["valid"] is False


def test_allocation_exceeding_total_capacity_rejected():
    # Resource 0 has 5 instances, but P0 + P1 = 3 + 4 = 7 allocated
    config = validate_resource_configuration([5, 5], [[3, 2], [4, 1]], [[5, 5], [5, 5]])
    assert config["valid"] is False
    assert any("exceeds total capacity" in e.lower() for e in config["errors"])


def test_allocation_exceeding_maximum_demand_rejected():
    config = validate_resource_configuration([10, 10], [[5, 5]], [[4, 5]])
    assert config["valid"] is False
    assert any("exceeds maximum" in e.lower() for e in config["errors"])


def test_maximum_exceeding_total_instances_rejected():
    config = validate_resource_configuration([5, 5], [[2, 2]], [[6, 4]])
    assert config["valid"] is False
    assert any("exceeds total resource" in e.lower() for e in config["errors"])


def test_valid_state_is_accepted():
    config = validate_state([10, 5, 7], [[0, 1, 0], [2, 0, 0]], [[7, 5, 3], [3, 2, 2]])
    assert config["valid"] is True
    assert config["available"] == [8, 4, 7]
