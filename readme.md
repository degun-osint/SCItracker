```
███████╗ ██████╗██╗████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔════╝██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████╗██║     ██║   ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
╚════██║██║     ██║   ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
███████║╚██████╗██║   ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚══════╝ ╚═════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ v2.0
            ### Trouvez les parcelles et locaux via SIREN ###  
```
Ce script vous permet de rechercher des parcelles appartenant à des personnes morales via le numéro SIREN.
Ce guide fournit des instructions détaillées sur la manière de configurer et d'utiliser l'application de gestion des données cadastrales pour les parcelles et les locaux des personnes morales.

## Prérequis

Avant de commencer l'installation, assurez-vous que Python et SQLite sont installés sur votre système. Vous aurez également besoin d'accéder à Internet pour télécharger les fichiers de données.

## Installation

1. **Cloner le dépôt** :
   Clonez ce dépôt sur votre machine locale en utilisant la commande suivante : `git clone <url_du_dépôt>`
   Ou télécharger le zip ici : https://github.com/degun-osint/SCItracker/archive/refs/heads/main.zip
2. **Installer les dépendances** :
Installez toutes les dépendances requises pour le projet en exécutant `pip install -r requirements.txt`


## Configuration des Données

Les données pour les locaux et les parcelles doivent être téléchargées et préparées comme suit :

### Téléchargement des Données

1. **Accéder à la source de données** :
Rendez-vous sur le site [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/) pour télécharger les fichiers zip des locaux et des parcelles pour chaque année.

2. **Téléchargement des fichiers** :
Téléchargez les fichiers zip correspondants aux années souhaitées.

### Préparation des Données

1. **Dézipper les fichiers** :
Créez deux dossiers à la racine du projet : `DATA_LOCAUX` pour les locaux et `DATA_PARCELLES` pour les parcelles. Dézippez les fichiers dans les dossiers appropriés, en respectant l'organisation par année.

Par exemple, l'arborescence des fichiers pourrait ressembler à cela :
```
/scitracker
├── DATA_LOCAUX
│ ├── 2020
│ ├── 2021
│ └── 2022
├── DATA_PARCELLES
│ ├── 2020
│ ├── 2021
│ └── 2022
```


## Utilisation de l'Application

Après avoir configuré les données, vous pouvez lancer l'application. Assurez-vous que les chemins vers les dossiers `DATA_LOCAUX` et `DATA_PARCELLES` sont correctement configurés dans le script avant de lancer le traitement.
``python3 scitracker2.py``

### Premier lancement
Pour initialiser la base de données, entrez `init` dans le menu principal.
Selon le nombre d'années a insérer, il faudra patienter un "petit" moment le temps de construire la base.
En cas de mise à jour, relancez l'initialisation pour ajouter les nouveaux fichiers.

