"""Suivi du niveau de batterie (module partiellement implémenté)."""

LOW_THRESHOLD = 20       # en %, en dessous : batterie faible
CAPACITY_WH = 5000       # capacité de la batterie en Wh


def validate_level(level):
    """Le niveau de batterie doit être compris entre 0 et 100 %."""
    if isinstance(level, bool) or not isinstance(level, (int, float)):
        raise ValueError(f"Niveau invalide : {level!r}")
    if level < 0 or level > 100:
        raise ValueError(f"Niveau hors limites (0-100) : {level}")
    return level


def is_low(level, threshold=LOW_THRESHOLD):
    """Vrai si la batterie est faible (strictement sous le seuil)."""
    validate_level(level)
    return level < threshold


def update_level(level, balance_w, duration_h=1.0, capacity_wh=CAPACITY_WH):
    """Retourne le nouveau niveau (%) après `duration_h` heures,
    sachant que le bilan énergétique vaut `balance_w` watts.
    Un surplus (bilan > 0) charge la batterie, un déficit la décharge.
    """
    validate_level(level)
    if isinstance(balance_w, bool) or not isinstance(balance_w, (int, float)):
        raise ValueError(f"Bilan invalide : {balance_w!r}")
    if isinstance(duration_h, bool) or not isinstance(duration_h, (int, float)):
        raise ValueError(f"Durée invalide : {duration_h!r}")
    if duration_h < 0:
        raise ValueError("La durée ne peut pas être négative")
    if isinstance(capacity_wh, bool) or not isinstance(capacity_wh, (int, float)):
        raise ValueError(f"Capacité invalide : {capacity_wh!r}")
    if capacity_wh <= 0:
        raise ValueError("La capacité doit être strictement positive")
    delta_wh = balance_w * duration_h
    delta_percent = delta_wh / capacity_wh * 100
    new_level = level + delta_percent
    return max(0, min(100, new_level))
