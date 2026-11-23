import pytest

from energy_app.battery import is_low, update_level, validate_level


def test_battery_15_is_low():
    assert is_low(15) is True


def test_battery_limits_are_not_low():
    assert is_low(50) is False
    assert is_low(20) is False


@pytest.mark.parametrize("level", [120, -5])
def test_invalid_battery_level(level):
    with pytest.raises(ValueError):
        validate_level(level)


def test_update_level_increases_to_60():
    assert update_level(50, 500, 1) == 60


def test_update_level_is_capped_at_100():
    assert update_level(99, 5000, 1) == 100


def test_update_level_is_capped_at_zero():
    assert update_level(5, -2000, 1) == 0