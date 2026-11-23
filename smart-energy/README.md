# smart-energy : TP « Les tests continus dans DevOps »

Application Python de gestion simplifiée de l'énergie solaire.
Le projet contient les modules applicatifs, les tests unitaires, d'intégration
et de sécurité, ainsi que le workflow GitHub Actions.

Le rapport complet se trouve à la racine du dépôt : [`RAPPORT_TP.md`](../RAPPORT_TP.md).

## Installation et exécution

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

## Ce qui est fourni / à faire

| Fichier | État | À faire |
|---|---|---|
| `energy_app/energy.py` | complet | rien (sert d'exemple) |
| `energy_app/data/sensors.json` | fourni | registre des capteurs : identifiants **hachés** (SHA-256 + sel), jamais en clair |
| `energy_app/sensors.py` | partiel | vérification d'usurpation, `ReplayGuard.check` |
| `energy_app/battery.py` | partiel | `update_level` |
| `energy_app/alerts.py` | partiel | `battery_alert` |
| `tests/test_*.py` | **vides** | écrire les tests (voir `TESTS_A_ECRIRE.md`) |
| `tests/test_security.py` | **vide** | au moins 3 tests de sécurité |
| `.github/workflows/tests.yml` | partiel | 4 `TODO` |

## Méthode conseillée

1. Lisez `TESTS_A_ECRIRE.md` et le code de `energy_app/`.
2. Écrivez un test, lancez `pytest -v`.
3. S'il échoue (par exemple usurpation, rejeu), corrigez le code correspondant.
4. Poussez sur GitHub et vérifiez le résultat du workflow dans l'onglet *Actions*.

## Rôles des modules

- `sensors.py` reçoit les messages IoT, vérifie l'identifiant et la cohérence mesure/capteur, puis transmet une mesure normalisée.
- `energy.py` calcule le bilan électrique à partir de la production et de la consommation.
- `battery.py` valide le niveau de batterie et applique l'évolution de charge ou de décharge.
- `alerts.py` transforme une batterie faible ou une erreur de mesure en alerte.

Les données passent ainsi : `sensors.py` produit une mesure normalisée ; `energy.py` produit un bilan en watts ; `battery.py` transforme ce bilan en nouveau niveau ; `alerts.py` reçoit le niveau ou l'erreur et produit l'alerte finale.

## Tableau de sécurité

| Menace | Entrée malveillante et résultat attendu | Règle suffisante ? |
|---|---|---|
| Identifiant falsifié | `S99` est rejeté par `UnknownSensorError`. | Oui pour les identifiants absents du registre ; le registre reste nécessairement tenu à jour. |
| Usurpation | S1 envoie `battery` : `SensorMismatchError`. | Oui pour empêcher un capteur connu d'envoyer une autre mesure. |
| Mesure manipulée | `battery = 120` ou `-5` : `ValueError`. | Oui pour les limites locales, mais une authentification du réseau reste nécessaire contre une substitution complète. |
| Rejeu | Même timestamp ou timestamp plus ancien : `ReplayError`. | Oui pour cet ordre temporel par capteur, avec horodatage fiable et synchronisation des garde-fous. |
| Fichier JSON lu | Le fichier contient des empreintes, pas les identifiants en clair. | Non à lui seul contre l'attaque par dictionnaire : des identifiants courts peuvent être devinés en calculant les empreintes. |

Un lecteur du registre ne connaît pas directement `S1`, `S2` et `S3`, mais peut tester des identifiants courants si le sel est public. Il faut utiliser des identifiants longs et aléatoires et idéalement une clé secrète dans une primitive d'authentification adaptée (HMAC).

## Tests d'intégration

- I1 utilise une méthode ascendante : les deux parseurs IoT sont testés séparément puis leur résultat est combiné avec `compute_balance`.
- I2 utilise une méthode ascendante : le calcul du bilan est relié à `update_level`.
- I3 utilise une méthode descendante : on part du message complet S3 et on descend vers son parsing puis la génération d'alerte.
- I4 utilise une méthode descendante : un message S99 et son erreur sont transformés directement en alerte `MESURE_INVALIDE`.

## Question finale

Il faut vérifier l'identifiant et la cohérence des mesures pour éviter qu'un capteur inconnu ou usurpé puisse provoquer une charge, une décharge ou une alerte erronée : des données invalides pourraient endommager la batterie ou conduire à des décisions énergétiques dangereuses.
