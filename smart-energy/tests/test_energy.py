import pytest

from energy_app.energy import compute_balance, has_surplus


def test_surplus_balance():
    assert compute_balance(1200, 800) == 400
    assert has_surplus(1200, 800) is True


def test_deficit_balance():
    assert compute_balance(300, 900) == -600
    assert has_surplus(300, 900) is False


def test_negative_production():
    with pytest.raises(ValueError):
        compute_balance(-100, 800)


def test_negative_consumption():
    with pytest.raises(ValueError):
        compute_balance(1200, -1)