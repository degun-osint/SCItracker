# modules/create_db.py

import sqlite3


def create_database():
    # Connexion à la base de données SQLite
    conn = sqlite3.connect('cadastral_data.db')
    cursor = conn.cursor()

    # Création de la table 'proprietaires'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proprietaires (
        proprietaire_id INTEGER PRIMARY KEY AUTOINCREMENT,
        siren VARCHAR(14) UNIQUE,
        forme_juridique_abregee VARCHAR(50),
        denomination VARCHAR(100)
    )
    ''')

    # Création de la table 'parcelles'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parcelles (
        parcelle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        departement VARCHAR(5),
        code_commune VARCHAR(5),
        nom_commune VARCHAR(100),
        section VARCHAR(10),
        numero_plan VARCHAR(10),
        numero_voirie VARCHAR(50),
        nature_voie VARCHAR(50),
        nom_voie VARCHAR(100),
        contenance INTEGER,
        UNIQUE(departement, code_commune, section, numero_plan)
    )
    ''')
    # Création table locaux
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locaux (
        locaux_id INTEGER PRIMARY KEY,
        departement TEXT,
        code_commune TEXT,
        prefixe TEXT,
        section TEXT,
        numero_plan TEXT,
        batiment TEXT,
        entree TEXT,
        niveau TEXT,
        porte TEXT,
        nom_commune TEXT,
        numero_voirie TEXT,
        indice_repetition TEXT,
        nature_voie TEXT,
        nom_voie TEXT,
        UNIQUE(departement, code_commune, prefixe, section, numero_plan, batiment, entree, niveau, porte)
        )
        ''')

    # Création de la table 'propriete_historique'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS propriete_historique (
        historique_id INTEGER PRIMARY KEY AUTOINCREMENT,
        parcelle_id INTEGER,
        proprietaire_id INTEGER,
        annee INTEGER,
        FOREIGN KEY(parcelle_id) REFERENCES parcelles(parcelle_id),
        FOREIGN KEY(proprietaire_id) REFERENCES proprietaires(proprietaire_id)
    )
    ''')

    # Historique de fichiers déjà importés
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fichiers_importes (
        fichier_nom VARCHAR(255) PRIMARY KEY
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS locaux_historique (
    locaux_historique_id INTEGER PRIMARY KEY,
    locaux_id INTEGER NOT NULL,
    proprietaire_id INTEGER NOT NULL,
    annee TEXT,
    FOREIGN KEY (locaux_id) REFERENCES locaux (locaux_id),
    FOREIGN KEY (proprietaire_id) REFERENCES proprietaires (proprietaire_id)
    )
    ''')

    # Création d'index pour accélérer les requêtes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_siren ON proprietaires(siren)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_parcelle_id ON propriete_historique(parcelle_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_proprietaire_id ON propriete_historique(proprietaire_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_annee ON propriete_historique(annee)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_locaux_id ON locaux_historique(locaux_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_locaux_annee ON locaux_historique(annee)')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_locaux_id_annee ON locaux_historique(locaux_id, annee)
    ''')

    # Valider (commit) les changements et fermer la connexion à la base de données
    conn.commit()
    conn.close()

    print("La base de données et les tables ont été créées avec succès.")
