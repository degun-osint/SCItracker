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

    # Création d'index pour accélérer les requêtes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_siren ON proprietaires(siren)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_parcelle_id ON propriete_historique(parcelle_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_proprietaire_id ON propriete_historique(proprietaire_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_annee ON propriete_historique(annee)')

    # Valider (commit) les changements et fermer la connexion à la base de données
    conn.commit()
    conn.close()

    print("La base de données et les tables ont été créées avec succès.")
