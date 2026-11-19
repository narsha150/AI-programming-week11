
import pytest

from bug3_logic import count_pass, find_max


@pytest.mark.parametrize(
    "scores, expected",
    [
        pytest.param([70, 85, 60, 95], 95, id="normal"),
        pytest.param([95, 85, 70, 60], 95, id="maximum-at-start"),
        pytest.param([70, 95, 85, 60], 95, id="maximum-in-middle"),
        pytest.param([10, 20, 30], 30, id="maximum-at-end"),
        pytest.param([60], 60, id="single-element"),
        pytest.param([10, 20], 20, id="two-elements-increasing"),
        pytest.param([20, 10], 20, id="two-elements-decreasing"),
        pytest.param([60, 60, 60], 60, id="all-equal"),
        pytest.param([95, 70, 95], 95, id="duplicate-maximum"),
        pytest.param([-30, -20, -10], -10, id="negative-scores"),
        pytest.param([-1, 0], 0, id="zero-maximum"),
        pytest.param([59.5, 60.0, 60.5], 60.5, id="float-scores"),
    ],
)
def test_find_max(scores, expected):
    assert find_max(scores) == expected


def test_find_max_empty_list_raises_index_error():
    with pytest.raises(IndexError):
        find_max([])


@pytest.mark.parametrize(
    "scores",
    [
        pytest.param(None, id="none"),
        pytest.param(60, id="non-subscriptable"),
        pytest.param([60, "invalid", 70], id="incomparable-elements"),
    ],
)
def test_find_max_invalid_input_raises_type_error(scores):
    with pytest.raises(TypeError):
        find_max(scores)


@pytest.mark.parametrize(
    "scores, expected",
    [
        pytest.param([70, 85, 60, 95], 4, id="normal"),
        pytest.param([70, 85, 95], 3, id="all-above-cutoff"),
        pytest.param([0, 40, 59], 0, id="all-below-cutoff"),
        pytest.param([60, 60, 59], 2, id="repeated-cutoff"),
        pytest.param([59, 60, 61], 2, id="around-cutoff"),
        pytest.param([60, 60, 60], 3, id="all-at-cutoff"),
        pytest.param([59], 0, id="single-below-cutoff"),
        pytest.param([60], 1, id="single-at-cutoff"),
        pytest.param([61], 1, id="single-above-cutoff"),
        pytest.param([], 0, id="empty-list"),
        pytest.param([59.9, 60.0, 60.1], 2, id="float-boundary"),
    ],
)
def test_count_pass_default_cutoff(scores, expected):
    assert count_pass(scores) == expected


@pytest.mark.parametrize(
    "scores, cutoff, expected",
    [
        pytest.param([79, 80, 81], 80, 2, id="custom-cutoff"),
        pytest.param([-1, 0, 1], 0, 2, id="zero-cutoff"),
        pytest.param([-11, -10, -9], -10, 2, id="negative-cutoff"),
        pytest.param([59.4, 59.5, 59.6], 59.5, 2, id="float-cutoff"),
        pytest.param([99, 100], 100, 1, id="hundred-cutoff"),
        pytest.param([], 80, 0, id="empty-list-custom-cutoff"),
    ],
)
def test_count_pass_custom_cutoff(scores, cutoff, expected):
    assert count_pass(scores, cutoff=cutoff) == expected


@pytest.mark.parametrize(
    "scores, cutoff",
    [
        pytest.param(None, 60, id="none-scores"),
        pytest.param(60, 60, id="non-iterable-scores"),
        pytest.param([60, "invalid"], 60, id="incomparable-score"),
        pytest.param([60], None, id="none-cutoff"),
        pytest.param([60], "60", id="string-cutoff"),
    ],
)
def test_count_pass_invalid_input_raises_type_error(scores, cutoff):
    with pytest.raises(TypeError):
        count_pass(scores, cutoff=cutoff)
