# TP - Les tests continus dans DevOps

Application Python simplifiee de gestion intelligente de l'energie solaire.
Ce depot montre comment tester des modules IoT, automatiser les tests avec Pytest
et executer ces tests avec GitHub Actions.

## Depot

- Depot GitHub : https://github.com/FatahThe9agnifico/tp_devops_4
- Projet principal : [`smart-energy/`](./smart-energy)
- Rapport detaille : [`RAPPORT_TP.md`](./RAPPORT_TP.md)
- Architecture reseau et InerCoin : [`SYSTEM_DESIGN.html`](./SYSTEM_DESIGN.html)
- Sujet officiel : [`tp_tests_continus_energie.pdf`](./tp_tests_continus_energie.pdf)

## Fonctionnement

Un capteur envoie un message contenant un identifiant, un horodatage et une
mesure. L'application verifie ensuite le message avant de calculer le bilan
energetique, le niveau de batterie et les alertes.

```text
Message IoT
  -> energy_app/sensors.py
  -> bilan par energy_app/energy.py
  -> niveau de batterie par energy_app/battery.py
  -> alerte par energy_app/alerts.py
```

| Module | Role |
|---|---|
| `sensors.py` | Verifie les identifiants, les mesures autorisees, les valeurs et les rejeux |
| `energy.py` | Calcule production - consommation |
| `battery.py` | Valide le niveau de batterie et calcule sa charge ou decharge |
| `alerts.py` | Produit les alertes batterie faible ou mesure invalide |

## Installation et tests

Depuis Windows PowerShell :

```powershell
cd C:\Users\utilisateur\Desktop\tp-devops-4\smart-energy
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -v
```

Resultat local attendu : **33 tests collectes et 33 tests reussis**.

## Structure

```text
smart-energy/
  energy_app/
    sensors.py
    energy.py
    battery.py
    alerts.py
    data/sensors.json
  tests/
  scripts/generate_registry.py
  .github/workflows/tests.yml
```

## Securite

Le registre ne contient pas `S1`, `S2` ou `S3` en clair. Il stocke leurs
empreintes SHA-256 calculees avec un sel. L'application compare ensuite
l'empreinte de l'identifiant recu aux entrees autorisees.

Les controles principaux sont :

- rejet d'un identifiant inconnu ;
- rejet d'une mesure envoyee par le mauvais capteur ;
- rejet d'un niveau de batterie hors limites ;
- rejet d'un horodatage rejoue ou plus ancien ;
- absence des identifiants en clair dans le fichier JSON.

## Integrations continues

Le workflow [`.github/workflows/tests.yml`](./.github/workflows/tests.yml)
s'execute pour les pushs et les pull requests vers `main`. Il utilise Python
3.12, installe `requirements.txt` puis lance `pytest -v`.

Les executions sont visibles dans l'onglet
[Actions](https://github.com/FatahThe9agnifico/tp_devops_4/actions).
