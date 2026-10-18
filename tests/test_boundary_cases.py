"""Tests for Boundary Edge Cases (Section 14) and Analytical Results (Section 16)."""

from algorithms.boundary_tests import run_analytical_test_cases, run_boundary_tests


def test_all_10_boundary_cases_pass():
    """Verify that every one of the 10 boundary cases from Section 14 passes with correct logic."""
    results = run_boundary_tests()
    assert len(results) == 10
    for test in results:
        assert test["pass"] is True, f"Boundary test {test['id']} failed: {test['actual']}"


def test_all_6_analytical_test_cases_pass():
    """Verify that all 6 required analytical test cases (TC1-TC6) pass dynamically."""
    table = run_analytical_test_cases()
    assert len(table) == 6
    for row in table:
        assert row["Pass/Fail"] == "PASS", f"Analytical test {row['Test Case']} failed: {row['Actual Result']}"
