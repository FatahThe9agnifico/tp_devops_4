import pytest

from energy_app.sensors import (
    InvalidMeasurement,
    UnknownSensorError,
    hash_sensor_id,
    load_registry,
    parse_measurement,
)


def test_s1_parses_valid_battery_message():
    result = parse_measurement(
        {"sensor_id": "S3", "timestamp": 1718000000, "battery": 15}
    )
    assert result["sensor_id"] == "S3"
    assert result["metric"] == "battery"
    assert result["value"] == 15


def test_s1_production_sensor():
    result = parse_measurement(
        {"sensor_id": "S1", "timestamp": 1718000001, "production": 1200}
    )
    assert result["metric"] == "production"
    assert result["value"] == 1200


def test_unknown_sensor():
    with pytest.raises(UnknownSensorError):
        parse_measurement({"sensor_id": "S99", "timestamp": 1, "battery": 15})


def test_missing_timestamp():
    with pytest.raises(InvalidMeasurement):
        parse_measurement({"sensor_id": "S3", "battery": 15})


def test_non_numeric_value():
    with pytest.raises(InvalidMeasurement):
        parse_measurement({"sensor_id": "S3", "timestamp": 1, "battery": "abc"})


def test_two_measures_are_rejected():
    with pytest.raises(InvalidMeasurement):
        parse_measurement(
            {"sensor_id": "S3", "timestamp": 1, "battery": 15, "production": 100}
        )


def test_hash_sensor_id_is_stable_and_distinct():
    registry = load_registry()
    salt = registry["salt"]
    hash_s1a = hash_sensor_id("S1", salt)
    hash_s1b = hash_sensor_id("S1", salt)
    hash_s2 = hash_sensor_id("S2", salt)
    assert len(hash_s1a) == 64
    assert hash_s1a != "S1"
    assert hash_s1a == hash_s1b
    assert hash_s1a != hash_s2