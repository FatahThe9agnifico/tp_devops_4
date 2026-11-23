from energy_app.alerts import battery_alert, invalid_measurement_alert
from energy_app.battery import update_level
from energy_app.energy import compute_balance
from energy_app.sensors import UnknownSensorError, parse_measurement


def test_s1_and_s2_messages_produce_balance():
    production = parse_measurement(
        {"sensor_id": "S1", "timestamp": 1, "production": 1200}
    )
    consumption = parse_measurement(
        {"sensor_id": "S2", "timestamp": 2, "consumption": 800}
    )
    assert compute_balance(production["value"], consumption["value"]) == 400


def test_balance_updates_battery():
    assert update_level(50, 500, 1) == 60


def test_s3_message_generates_low_battery_alert():
    measurement = parse_measurement(
        {"sensor_id": "S3", "timestamp": 3, "battery": 15}
    )
    alert = battery_alert(measurement["value"])
    assert alert["type"] == "BATTERIE_FAIBLE"


def test_unknown_message_generates_invalid_alert():
    try:
        parse_measurement({"sensor_id": "S99", "timestamp": 4, "battery": 15})
    except UnknownSensorError as error:
        alert = invalid_measurement_alert(error)
    assert alert["type"] == "MESURE_INVALIDE"