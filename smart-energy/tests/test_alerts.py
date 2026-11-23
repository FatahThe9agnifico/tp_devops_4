import pytest

from energy_app.alerts import battery_alert, invalid_measurement_alert
from energy_app.sensors import UnknownSensorError


def test_low_battery_alert():
    alert = battery_alert(15)
    assert alert["type"] == "BATTERIE_FAIBLE"


def test_no_alert_above_threshold():
    assert battery_alert(80) is None


def test_alert_rejects_invalid_level():
    with pytest.raises(ValueError):
        battery_alert(120)


def test_invalid_measurement_alert_for_unknown_sensor():
    alert = invalid_measurement_alert(
        UnknownSensorError("Capteur inconnu : S99")
    )
    assert alert["type"] == "MESURE_INVALIDE"