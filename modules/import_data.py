# modules/import_data.py

import csv
import sqlite3
from os import walk, path
from tqdm import tqdm


def import_data(data_directory, local_data_directory):
    conn = sqlite3.connect('cadastral_data.db')
    cursor = conn.cursor()
    # Réglages d'optimisation
    cursor.execute('PRAGMA synchronous = OFF')
    cursor.execute('PRAGMA journal_mode = MEMORY')
    cursor.execute('PRAGMA cache_size = -200000')  # Cache de 200 000 pages
    cursor.execute('BEGIN TRANSACTION')

    # Traitement des parcelles
    process_directory(data_directory, conn, process_parcelle_file)

    # Traitement des locaux
    process_directory(local_data_directory, conn, process_local_file)

    conn.commit()
    conn.close()
    print("Importation terminée avec succès.")


def process_directory(directory, conn, file_processor):
    cursor = conn.cursor()
    for root, _, files in walk(directory):
        year = path.basename(root)
        if year.isdigit():  # Vérifier que le dossier est une année
            txt_files = [file for file in files if file.endswith(".txt")]
            if not txt_files:
                continue

            with tqdm(total=len(txt_files), desc=f"{directory} - Fichiers traités pour : {year}", leave=True) as pbar:
                for file in txt_files:
                    full_path = path.join(root, file)
                    # Vérifier si le fichier a déjà été importé
                    cursor.execute('SELECT fichier_nom FROM fichiers_importes WHERE fichier_nom = ?', (full_path,))
                    if cursor.fetchone() is None:
                        file_processor(full_path, year, conn)
                        # Enregistrer le fichier comme importé
                        cursor.execute('INSERT INTO fichiers_importes (fichier_nom) VALUES (?)', (full_path,))
                    pbar.update(1)


def process_parcelle_file(full_path, year, conn):
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
                ''', (
                departement, code_commune, nom_commune, section, numero_plan, numero_voirie, nature_voie, nom_voie,
                contenance))
            cursor.execute('''
                    SELECT parcelle_id FROM parcelles WHERE departement = ? AND code_commune = ? AND section = ? AND numero_plan = ?
                ''', (departement, code_commune, section, numero_plan))
            parcelle_id = cursor.fetchone()[0]

            # Insérer dans propriete_historique
            cursor.execute('''
                    INSERT INTO propriete_historique (parcelle_id, proprietaire_id, annee)
                    VALUES (?, ?, ?);
                ''', (parcelle_id, proprietaire_id, year))


def process_local_file(full_path, year, conn):
    cursor = conn.cursor()
    with open(full_path, 'r', encoding='iso-8859-1') as data_file:
        csv_reader = csv.reader(data_file, delimiter=';')
        next(csv_reader)  # Passer l'en-tête
        for row in csv_reader:
            # Extraction des champs pour la table `locaux`
            departement, code_commune, prefixe, section, numero_plan, nom_commune, \
                numero_voirie, indice_repetition, nature_voie, nom_voie, \
                batiment, entree, niveau, porte = row[0], row[2], row[4], row[5], row[6], \
                row[3], row[11], row[12], row[15], row[16], \
                row[7], row[8], row[9], row[10]

            # Insertion des locaux
            cursor.execute('''
                INSERT INTO locaux (departement, code_commune, prefixe, section, numero_plan, 
                                    nom_commune, numero_voirie, indice_repetition, nature_voie, nom_voie,
                                    batiment, entree, niveau, porte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(departement, code_commune, prefixe, section, numero_plan, 
                            batiment, entree, niveau, porte) DO UPDATE SET
                            nom_commune=excluded.nom_commune, numero_voirie=excluded.numero_voirie, 
                            indice_repetition=excluded.indice_repetition, nature_voie=excluded.nature_voie,
                            nom_voie=excluded.nom_voie;
            ''', (departement, code_commune, prefixe, section, numero_plan, nom_commune,
                  numero_voirie, indice_repetition, nature_voie, nom_voie,
                  batiment, entree, niveau, porte))
