from algorithms.deadlock_prevention import (
    compare_prevention_policies,
    fixed_order_policy,
    simulate_fixed_ordering_policy,
    simulate_hold_and_wait_prevention,
)


def test_resource_order_prevention():
    order = ["R0", "R1", "R2"]
    assert fixed_order_policy(order, ["R0", "R1"]) is True
    assert fixed_order_policy(order, ["R0", "R1", "R2"]) is True
    assert fixed_order_policy(order, ["R2", "R1"]) is False
    assert fixed_order_policy(order, ["R1", "R0"]) is False


def test_simulate_fixed_ordering_policy():
    res = simulate_fixed_ordering_policy()
    assert res["compliance"]["P0"] is True
    assert res["compliance"]["P1"] is False  # P1 requests R1 then R0
    assert "P1" in res["violations"]
    assert res["enforced_circular_wait"] is False


def test_simulate_hold_and_wait_prevention():
    res = simulate_hold_and_wait_prevention()
    assert res["incremental_hold_and_wait"]["circular_wait_possible"] is True
    assert res["all_at_once_allocation"]["circular_wait_possible"] is False


def test_prevention_policy_summary():
    result = compare_prevention_policies()
    assert result["circular_wait_possible"] is False
    assert result["wait_longer"] is True
    assert result["utilization_reduction"] > 0
