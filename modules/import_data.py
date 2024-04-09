# modules/import_data.py

import csv
import sqlite3
from os import walk, path
from tqdm import tqdm


def import_data(data_directory):
    conn = sqlite3.connect('cadastral_data.db')
    cursor = conn.cursor()
    # Réglages d'optimisation
    cursor.execute('PRAGMA synchronous = OFF')
    cursor.execute('PRAGMA journal_mode = MEMORY')
    cursor.execute('PRAGMA cache_size = -200000')  # Cache de 200 000 pages
    cursor.execute('BEGIN TRANSACTION')

    for root, _, files in walk(data_directory):
        year = path.basename(root)
        if year.isdigit():  # Vérifier que le dossier est une année
            txt_files = [file for file in files if file.endswith(".txt")]
            if not txt_files:
                continue

            print(f"Traitement des données pour l'année : {year}")
            with tqdm(total=len(txt_files), desc="Fichiers traités", leave=True) as pbar:
                for file in txt_files:
                    full_path = path.join(root, file)
                    # Vérifier si le fichier a déjà été importé
                    cursor.execute('SELECT fichier_nom FROM fichiers_importes WHERE fichier_nom = ?', (full_path,))
                    if cursor.fetchone() is None:
                        process_file(full_path, year, conn)
                        # Enregistrer le fichier comme importé
                        cursor.execute('INSERT INTO fichiers_importes (fichier_nom) VALUES (?)', (full_path,))
                    pbar.update(1)

    conn.commit()
    conn.close()
    print("Importation terminée avec succès.")


def process_file(full_path, year, conn):
    cursor = conn.cursor()
    with open(full_path, 'r', encoding='iso-8859-1') as data_file:
        csv_reader = csv.reader(data_file, delimiter=';')
        next(csv_reader)  # Passer l'en-tête
        for row in csv_reader:
            # Extraire toutes les colonnes nécessaires du fichier CSV
            departement, code_commune, nom_commune, section, numero_plan = row[0], row[2], row[3], row[5], row[6]
            numero_voirie, nature_voie, nom_voie = row[7], row[11], row[12]
            contenance = row[13]  # Assurez-vous que cette colonne correspond à la contenance dans vos fichiers
            siren, forme_juridique_abregee, denomination = row[19], row[22], row[23]

            # Vérifier et insérer le propriétaire si nécessaire, récupérer l'ID existant ou nouvellement inséré
            cursor.execute('''
                INSERT INTO proprietaires (siren, forme_juridique_abregee, denomination)
                VALUES (?, ?, ?)
                ON CONFLICT(siren) DO NOTHING;
            ''', (siren, forme_juridique_abregee, denomination))
            cursor.execute('SELECT proprietaire_id FROM proprietaires WHERE siren = ?', (siren,))
            proprietaire_id = cursor.fetchone()[0]

            # Vérifier et insérer la parcelle si nécessaire, récupérer l'ID existant ou nouvellement inséré
            cursor.execute('''
                INSERT INTO parcelles (departement, code_commune, nom_commune, section, numero_plan, numero_voirie, nature_voie, nom_voie, contenance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(departement, code_commune, section, numero_plan) DO NOTHING;
            ''', (departement, code_commune, nom_commune, section, numero_plan, numero_voirie, nature_voie, nom_voie, contenance))
            cursor.execute('''
                SELECT parcelle_id FROM parcelles WHERE departement = ? AND code_commune = ? AND section = ? AND numero_plan = ?
            ''', (departement, code_commune, section, numero_plan))
            parcelle_id = cursor.fetchone()[0]

            # Insérer dans propriete_historique
            cursor.execute('''
                INSERT INTO propriete_historique (parcelle_id, proprietaire_id, annee)
                VALUES (?, ?, ?);
            ''', (parcelle_id, proprietaire_id, year))
