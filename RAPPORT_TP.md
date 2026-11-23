# Rapport du TP - Les tests continus dans DevOps

## 1. Objectif

Le TP vise a mettre en pratique les tests logiciels dans une application
Python simple de gestion de l'energie solaire. L'application simule des
messages envoyes par trois capteurs IoT. La verification de ces messages,
le calcul du bilan et les alertes doivent ensuite etre automatises avec
Pytest puis GitHub Actions.

## 2. Architecture et circulation des donnees

### `sensors.py`

Ce module recoit les messages et les transforme en dictionnaire normalise :

```text
sensor_id -> identifiant du capteur
timestamp -> horodatage du message
metric -> production, consumption ou battery
value -> valeur numerique de la mesure
```

Il verifie notamment :

- que le message est un dictionnaire ;
- que l'identifiant existe dans le registre ;
- que le timestamp est present ;
- qu'une seule mesure est presente ;
- que la mesure est numerique ;
- que la mesure correspond au droit du capteur ;
- que les niveaux batterie respectent les limites.

### `energy.py`

Ce module calcule le bilan :

```text
bilan = production - consommation
```

Un resultat positif signifie un surplus. Un resultat negatif signifie un
deficit. Les valeurs negatives sont interdites.

### `battery.py`

Ce module valide le niveau de batterie entre 0 et 100 %. Il utilise ensuite
le bilan en watts pour calculer l'energie ajoutee ou retiree pendant une
duree. Le nouveau niveau est borne entre 0 % et 100 %.

Exemple :

```text
niveau initial = 50 %
bilan = +500 W
duree = 1 h
capacite = 5000 Wh
ajout = 500 Wh / 5000 Wh * 100 = 10 %
niveau final = 60 %
```

### `alerts.py`

Ce module renvoie une alerte lorsque la batterie est strictement sous 20 %.
Il renvoie aussi une alerte standardisee lorsqu'une mesure ou un identifiant
est invalide.

## 3. Corrections realisees

### Usurpation

Dans `parse_measurement()`, le module compare maintenant la mesure envoyee
a la mesure autorisee dans `sensors.json`. Par exemple, S1 peut envoyer
`production`, mais pas `battery`. Sinon, `SensorMismatchError` est leve.

### Mise a jour de la batterie

`update_level()` calcule :

```text
nouveau niveau = niveau + bilan * duree / capacite * 100
```

Le resultat est borne avec les limites 0 % et 100 %. Le module valide aussi
le bilan, la duree et la capacite.

### Alertes

`battery_alert()` renvoie maintenant :

```json
{"type": "BATTERIE_FAIBLE", "message": "Batterie faible : 15 %"}
```

sous 20 %, et `None` sinon.

### Rejeu

`ReplayGuard.check()` memorise le dernier timestamp accepte pour chaque
capteur. Il refuse un timestamp egal ou plus ancien avec `ReplayError`.

## 4. Strategie de tests

### Tests unitaires

Les tests unitaires verifient une fonction et un seul comportement a la fois.

Exemples :

- S3 envoie une batterie valide ;
- S99 est inconnu ;
- une production negative leve `ValueError` ;
- le niveau 15 % est faible ;
- 120 % est refuse ;
- une charge de 500 W pendant une heure passe de 50 % a 60 % ;
- une alerte est generee sous 20 %.

### Tests d'integration

I1 est ascendant : on assemble les mesures S1 et S2 puis on calcule leur
bilan.

I2 est ascendant : on relie le bilan calcule a la mise a jour de la batterie.

I3 est descendant : on part du message S3 complet, puis on descend vers le
parsing et la generation d'alerte.

I4 est descendant : on traite un message S99 puis sa conversion en alerte
`MESURE_INVALIDE`.

### Tests de securite

Les tests couvrent les menaces principales :

| Menace | Entree | Resultat |
|---|---|---|
| Identifiant falsifie | S99 | `UnknownSensorError` |
| Usurpation | S1 envoie battery | `SensorMismatchError` |
| Mesure manipulee | battery 120 ou -5 | `ValueError` |
| Rejeu | timestamp egal ou ancien | `ReplayError` |
| Hash comme identifiant | empreinte utilisee comme sensor_id | `UnknownSensorError` |
| Registre public | lecture du fichier JSON | aucun identifiant en clair |

## 5. Evaluation du registre hache

Le fichier `sensors.json` contient des empreintes SHA-256 avec un sel public.
Un attaquant peut donc lire les empreintes, mais ne voit pas directement
S1, S2 ou S3.

Cependant, avec des identifiants courts et faciles a deviner, il peut calculer
leurs empreintes possibles avec le sel connu. Cette protection est donc sensible
a une attaque par dictionnaire.

Les ameliorations recommandees seraient :

- des identifiants longs et aleatoires ;
- un sel propre par capteur ;
- une cle secrete avec HMAC ;
- une authentification du canal reseau ;
- une rotation des identifiants et des secrets.

## 6. GitHub Actions

Le fichier `.github/workflows/tests.yml` declenche le workflow lorsqu'un
push ou une pull request vise `main`.

Les actions automatiques sont :

1. recuperer le depot avec `actions/checkout` ;
2. installer Python 3.12 ;
3. installer `pytest` depuis `requirements.txt` ;
4. executer tous les tests avec `pytest -v`.

Cela garantit que chaque changement est teste avant ou apres son integration,
selon le declencheur utilise.

## 7. Execution locale

Depuis le dossier `smart-energy` :

```powershell
python -m pytest -v
```

Le projet contient actuellement 53 cas de test verifies localement, dont les
nouveaux cas X7-X10 de robustesse des entrees :

```text
53 passed
```

## 8. Tableau de synthese de securite

| Menace | Mesure suffisante ? | Explication |
|---|---|---|
| Identifiant falsifie | Oui pour rejeter S99 | Le hash n'est pas present dans le registre |
| Usurpation | Oui pour les mesures incoherentes | Un capteur ne peut pas changer de type de mesure |
| Batterie 120 / -5 | Oui | Les bornes sont appliquees avant utilisation |
| Rejeu | Oui pour les timestamps repetes | Le garde est compare au dernier timestamp |
| Lecture du JSON | Non contre tous les cas | Des identifiants courts peuvent etre devines |

## 9. Question finale

Il faut verifier l'identifiant d'un capteur avant d'utiliser sa mesure.
Cette verification empeche un appareil inconnu ou usurpe d'injecter des
donnees. Il faut aussi verifier la coherence des mesures afin d'interdire
les valeurs impossibles ou les fonctions envoyees par le mauvais capteur.

Sans ces controles, la batterie ou les alertes pourraient prendre une
decision incorrecte, induire une charge ou une decharge erronee et fausser
la gestion globale de l'installation.

## 10. Conclusion

La solution est decouplee en modules independants. Chaque module dispose de
tests unitaires ou d'integration, les menaces principales disposent de tests
de securite, et le workflow GitHub Actions automatise l'execution complete.
