import pytest

from energy_app.battery import validate_level
from energy_app.sensors import (
    ReplayGuard,
    ReplayError,
    SensorMismatchError,
    UnknownSensorError,
    hash_sensor_id,
    load_registry,
    parse_measurement,
)


def test_x1_forged_sensor_id_is_rejected():
    """Situation : S99 est envoyé. Comportement : l'identifiant est rejeté.
    Résultat : UnknownSensorError confirme l'identifiant falsifié."""
    with pytest.raises(UnknownSensorError):
        parse_measurement({"sensor_id": "S99", "timestamp": 1, "battery": 15})


def test_x2_sensor_cannot_send_another_metric():
    """Situation : S1 envoie battery. Comportement : la règle de cohérence échoue.
    Résultat : SensorMismatchError confirme le blocage de l'usurpation."""
    with pytest.raises(SensorMismatchError):
        parse_measurement({"sensor_id": "S1", "timestamp": 2, "battery": 50})


@pytest.mark.parametrize("battery_level", [120, -5])
def test_x3_manipulated_battery_is_rejected(battery_level):
    """Situation : une valeur battery est hors limites. Comportement : la valeur est rejetée.
    Résultat : ValueError confirme l'intégrité de la mesure."""
    with pytest.raises(ValueError):
        parse_measurement(
            {"sensor_id": "S3", "timestamp": 3, "battery": battery_level}
        )


def test_x4_replay_and_old_timestamp_are_rejected():
    """Situation : deux messages utilisent le même timestamp puis un timestamp ancien.
    Comportement : les deux messages doivent être refusés.
    Résultat : ReplayError confirme la détection du rejeu."""
    guard = ReplayGuard()
    guard.check("S3", 100)
    guard.check("S3", 101)
    with pytest.raises(ReplayError):
        guard.check("S3", 101)
    with pytest.raises(ReplayError):
        guard.check("S3", 99)


def test_x5_hash_as_sensor_id_is_rejected():
    """Situation : l'empreinte de S3 est utilisée comme identifiant.
    Comportement : l'application ne doit pas reconnaître cette valeur.
    Résultat : UnknownSensorError confirme que seul l'identifiant en clair est accepté."""
    registry = load_registry()
    digest = hash_sensor_id("S3", registry["salt"])
    with pytest.raises(UnknownSensorError):
        parse_measurement({"sensor_id": digest, "timestamp": 1, "battery": 15})


def test_x6_registry_does_not_contain_plain_sensor_ids():
    """Situation : le fichier JSON du registre est lu.
    Comportement : les identifiants S1, S2 et S3 ne doivent pas apparaître.
    Résultat : aucune chaîne en clair ne valide l'absence d'identifiants."""
    registry = load_registry()
    import json
    encoded = json.dumps(registry)
    assert "S1" not in encoded
    assert "S2" not in encoded
    assert "S3" not in encoded