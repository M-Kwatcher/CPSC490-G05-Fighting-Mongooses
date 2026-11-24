"""Checks for the direction requirement (#17). Lives in prototype/tests/. Run from prototype/ with:
    python -m pytest tests/test_scenarios.py -q
"""

from locator.scenarios import (REQUIRED_PASS_RATE, REQUIRED_SCENARIOS, SCENARIOS,
                               Scenario, meetsRequirement, passRate, runAll, runScenario)


def test_at_least_twenty_scenarios():
    assert len(SCENARIOS) >= REQUIRED_SCENARIOS


def test_scenarios_are_distinct():
    keys = {(s.trueAngleDeg, s.noiseLevel, s.spacingM) for s in SCENARIOS}
    assert len(keys) == len(SCENARIOS)


def test_pass_rate_meets_requirement():
    results = runAll()
    assert passRate(results) >= REQUIRED_PASS_RATE
    assert meetsRequirement(results)


def test_runs_are_repeatable():
    first = [(r[1], r[2]) for r in runAll()]
    second = [(r[1], r[2]) for r in runAll()]
    assert first == second


def test_noise_free_case_is_accurate():
    estimate, error, passed = runScenario(Scenario("clean", 30, 0.0, 10.0, seed=1))
    assert passed and abs(error) < 1.0


def test_left_and_right_have_opposite_signs():
    left = runScenario(Scenario("left", -40, 0.0))[0]
    right = runScenario(Scenario("right", 40, 0.0))[0]
    assert left < 0 < right
