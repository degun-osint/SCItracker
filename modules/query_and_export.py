# modules/query_and_export.py

import csv


def get_most_recent_year(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(annee) FROM propriete_historique')
    return cursor.fetchone()[0]


def properties_simple(conn, sirens):
    year = get_most_recent_year(conn)
    cursor = conn.cursor()
    siren_placeholders = ', '.join(['?'] * len(sirens))
    query = f'''
    SELECT p.departement, p.nom_commune, p.section, p.numero_plan, p.numero_voirie, 
           p.nature_voie, p.nom_voie, p.contenance, pr.siren, pr.forme_juridique_abregee, pr.denomination
    FROM parcelles AS p
    JOIN propriete_historique AS ph ON p.parcelle_id = ph.parcelle_id
    JOIN proprietaires AS pr ON ph.proprietaire_id = pr.proprietaire_id
    WHERE ph.annee = ? AND pr.siren IN ({siren_placeholders})
    '''
    cursor.execute(query, [year] + sirens)
    rows = cursor.fetchall()

    # Noms des colonnes basés sur la requête SQL
    column_names = ['Département', 'Commune', 'Section', 'N° plan', 'N° voirie',
                    'Nature voie', 'Nom voie', 'Contenance', 'SIREN', 'Forme jur.', 'Dénomination']
    return rows, column_names



def properties_and_history(conn, sirens):
    cursor = conn.cursor()
    # Trouver l'année la plus récente pour les SIREN spécifiés
    cursor.execute('SELECT MAX(annee) FROM propriete_historique')
    max_year = cursor.fetchone()[0]

    # Identifier les parcelles pour l'année la plus récente et récupérer toutes les années concernées
    siren_placeholders = ', '.join(['?'] * len(sirens))
    cursor.execute(f'''
        SELECT DISTINCT ph.parcelle_id
        FROM propriete_historique AS ph
        JOIN proprietaires AS pr ON ph.proprietaire_id = pr.proprietaire_id
        WHERE ph.annee = {max_year} AND pr.siren IN ({siren_placeholders})
    ''', sirens)
    parcelle_ids = [row[0] for row in cursor.fetchall()]

    # Récupérer l'ensemble des années concernées pour ces parcelles
    cursor.execute('''
        SELECT DISTINCT annee FROM propriete_historique
        WHERE parcelle_id IN ({})
        ORDER BY annee
    '''.format(', '.join(['?'] * len(parcelle_ids))), parcelle_ids)
    years = [row[0] for row in cursor.fetchall()]

    properties_data = []
    for parcelle_id in parcelle_ids:
        row = []
        for year in years:
            cursor.execute('''
                SELECT pr.siren, pr.forme_juridique_abregee, pr.denomination
                FROM propriete_historique AS ph
                JOIN proprietaires AS pr ON ph.proprietaire_id = pr.proprietaire_id
                WHERE ph.parcelle_id = ? AND ph.annee = ?
            ''', (parcelle_id, year))
            info = cursor.fetchone() or ("", "", "")
            row.extend(info)

        # Préfixer la ligne avec des informations de base de la parcelle si nécessaire
        cursor.execute('''
            SELECT departement, nom_commune, section, numero_plan, numero_voirie, 
                   nature_voie, nom_voie, contenance
            FROM parcelles
            WHERE parcelle_id = ?
        ''', (parcelle_id,))
        base_info = cursor.fetchone()
        properties_data.append(base_info + tuple(row))

    # Préparation des entêtes
    base_columns = ['Département', 'Commune', 'Section', 'N° plan', 'N° voirie', 'Nature voie', 'Nom voie',
                    'Contenance']
    dynamic_columns = [f'{item} [{year}]' for year in years for item in ('SIREN', 'Forme jur.', 'Dénomination')]
    column_names = base_columns + dynamic_columns

    return properties_data, column_names


def past_properties(conn, sirens):
    cursor = conn.cursor()
    # Trouver l'année la plus récente dans la base de données
    cursor.execute('SELECT MAX(annee) FROM propriete_historique')
    max_year = cursor.fetchone()[0]

    # Identifier les parcelles associées aux SIREN donnés dans les années précédentes
    siren_placeholders = ', '.join(['?'] * len(sirens))
    cursor.execute(f'''
        SELECT DISTINCT ph.parcelle_id
        FROM propriete_historique AS ph
        JOIN proprietaires AS pr ON ph.proprietaire_id = pr.proprietaire_id
        WHERE pr.siren IN ({siren_placeholders})
    ''', sirens)
    all_parcelle_ids = {row[0] for row in cursor.fetchall()}

    # Exclure les parcelles où le SIREN est propriétaire dans l'année la plus récente
    cursor.execute(f'''
        SELECT DISTINCT ph.parcelle_id
        FROM propriete_historique AS ph
        JOIN proprietaires AS pr ON ph.proprietaire_id = pr.proprietaire_id
        WHERE ph.annee = {max_year} AND pr.siren IN ({siren_placeholders})
    ''', sirens)
    recent_parcelle_ids = {row[0] for row in cursor.fetchall()}

    past_parcelle_ids = all_parcelle_ids - recent_parcelle_ids

    # Récupérer toutes les années concernées par les parcelles identifiées
    if past_parcelle_ids:
        cursor.execute('''
            SELECT DISTINCT annee FROM propriete_historique
            WHERE parcelle_id IN ({})
            ORDER BY annee
        '''.format(', '.join(['?']*len(past_parcelle_ids))), tuple(past_parcelle_ids))
        years = [row[0] for row in cursor.fetchall()]

        properties_data = []
        for parcelle_id in past_parcelle_ids:
            row = []
            for year in years:
                cursor.execute('''
                    SELECT pr.siren, pr.forme_juridique_abregee, pr.denomination
                    FROM propriete_historique AS ph
                    JOIN proprietaires AS pr ON ph.proprietaire_id = pr.proprietaire_id
                    WHERE ph.parcelle_id = ? AND ph.annee = ?
                ''', (parcelle_id, year))
                info = cursor.fetchone() or ("", "", "")
                row.extend(info)

            cursor.execute('''
                SELECT departement, nom_commune, section, numero_plan, numero_voirie, 
                       nature_voie, nom_voie, contenance
                FROM parcelles
                WHERE parcelle_id = ?
            ''', (parcelle_id,))
            base_info = cursor.fetchone()
            properties_data.append(base_info + tuple(row))

        # Préparation des entêtes
        base_columns = ['Département', 'Commune', 'Section', 'N° plan', 'N° voirie', 'Nature voie', 'Nom voie', 'Contenance']
        dynamic_columns = [f'{item} [{year}]' for year in years for item in ('SIREN', 'Forme jur.', 'Dénomination')]
        column_names = base_columns + dynamic_columns

        return properties_data, column_names
    else:
        return "Aucune donnée historique disponible pour les SIREN spécifiés"


def properties_to_csv(properties, column_names, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        writer.writerows(properties)
        print(f"Les données ont été exportées avec succès dans {filename}.")
