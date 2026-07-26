"""Checks for the one-forward/one-reverse retained query compiler."""

import pytest

pytest.importorskip("numpy")

from benchmarks.coupled_nd_retained_compiler import (
    compile_retained,
    default_problem,
)
from benchmarks.retained_reverse_compiler import (
    compile_retained_reverse,
    plan_reverse_work,
)


@pytest.mark.parametrize("dimension", (4, 11))
def test_reverse_compiler_returns_same_all_axis_readouts_with_less_work(dimension):
    problem = default_problem(dimension)
    reverse = compile_retained_reverse(problem, order=4)
    repeated = compile_retained(problem, order=4)
    assert abs(reverse.value - repeated.value) <= 1e-12
    assert max(
        abs(left - right)
        for left, right in zip(
            reverse.axis_first_moments,
            repeated.axis_first_moments,
        )
    ) <= 1e-12
    assert len(reverse.axis_first_moments) == dimension
    assert reverse.total_work_tokens < repeated.total_work_tokens


def test_reverse_work_is_fully_predictable_before_execution():
    problem = default_problem(11)
    plan = plan_reverse_work(problem, order=4)
    result = compile_retained_reverse(problem, order=4)
    assert plan.total_work_tokens == result.total_work_tokens == 9000
    assert plan.peak_retained_elements == result.peak_retained_elements == 16
