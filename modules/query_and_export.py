# modules/query_and_export.py

import csv


def build_dvf_link(departement, code_commune, section, numero_plan):
    """
    Construit un lien DVF pour la parcelle spécifiée.

    Args:
    departement (str): Code du département, doit être de 2 chiffres.
    code_commune (str): Code de la commune, doit être de 3 chiffres.
    section (str): Code de la section, doit être ajusté à 5 caractères avec des zéros initiaux si nécessaire.
    numero_plan (str): Numéro du plan, doit être ajusté à 4 caractères avec des zéros initiaux si nécessaire.

    Returns:
    str: URL complète du lien DVF.
    """
    code_parcelle = f"{int(departement):02}{int(code_commune):03}{section:0>5}{numero_plan:0>4}"
    return f"https://explore.data.gouv.fr/fr/immobilier?onglet=carte&filtre=tous&level=parcelle&code={code_parcelle}"



def get_most_recent_year(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(annee) FROM propriete_historique')
    return cursor.fetchone()[0]


def properties_simple(conn, sirens):
    year = get_most_recent_year(conn)
    cursor = conn.cursor()
    siren_placeholders = ', '.join(['?'] * len(sirens))
    query = f'''
        SELECT p.departement, p.code_commune, p.nom_commune, p.section, p.numero_plan, p.numero_voirie, 
               p.nature_voie, p.nom_voie, p.contenance, pr.siren, pr.forme_juridique_abregee, pr.denomination
        FROM parcelles AS p
        JOIN propriete_historique AS ph ON p.parcelle_id = ph.parcelle_id
        JOIN proprietaires AS pr ON ph.proprietaire_id = pr.proprietaire_id
        WHERE ph.annee = ? AND pr.siren IN ({siren_placeholders})
        '''
    cursor.execute(query, [year] + sirens)
    rows = cursor.fetchall()

    enhanced_rows = []
    for row in rows:
        departement, code_commune, section, numero_plan = row[0], row[1], row[3], row[4]
        dvf_link = build_dvf_link(departement, code_commune, section, numero_plan)
        enhanced_rows.append(row + (dvf_link,))

    column_names = ['Département', 'Code Commune', 'Commune', 'Section', 'N° plan', 'N° voirie',
                    'Nature voie', 'Nom voie', 'Contenance', 'SIREN', 'Forme jur.', 'Dénomination', 'DVF Link']
    return enhanced_rows, column_names


def properties_and_history(conn, sirens):
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(annee) FROM propriete_historique')
    max_year = cursor.fetchone()[0]

    siren_placeholders = ', '.join(['?'] * len(sirens))
    cursor.execute(f'''
        SELECT DISTINCT ph.parcelle_id
        FROM propriete_historique AS ph
        JOIN proprietaires AS pr ON ph.proprietaire_id = pr.proprietaire_id
        WHERE ph.annee = {max_year} AND pr.siren IN ({siren_placeholders})
    ''', sirens)
    parcelle_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute('''
        SELECT DISTINCT annee FROM propriete_historique
        WHERE parcelle_id IN ({})
        ORDER BY annee
    '''.format(', '.join(['?'] * len(parcelle_ids))), parcelle_ids)
    years = [row[0] for row in cursor.fetchall()]

    properties_data = []
    for parcelle_id in parcelle_ids:
        cursor.execute('''
            SELECT departement, code_commune, nom_commune, section, numero_plan, numero_voirie, 
                   nature_voie, nom_voie, contenance
            FROM parcelles
            WHERE parcelle_id = ?
        ''', (parcelle_id,))
        base_info = cursor.fetchone()
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

        departement, code_commune, section, numero_plan = base_info[0], base_info[1], base_info[3], base_info[4]
        dvf_link = build_dvf_link(departement, code_commune, section, numero_plan)
        properties_data.append(base_info + tuple(row) + (dvf_link,))

    dynamic_columns = [f'{item} [{year}]' for year in years for item in ('SIREN', 'Forme jur.', 'Dénomination')]
    column_names = ['Département', 'Code Commune', 'Commune', 'Section', 'N° plan', 'N° voirie', 'Nature voie',
                    'Nom voie', 'Contenance'] + dynamic_columns + ['DVF Link']

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

    if not past_parcelle_ids:
        return [], ['Département', 'Code Commune', 'Commune', 'Section', 'N° plan', 'N° voirie', 'Nature voie',
                    'Nom voie', 'Contenance', 'DVF Link']

    cursor.execute('''
        SELECT DISTINCT annee FROM propriete_historique
        WHERE parcelle_id IN ({})
        ORDER BY annee DESC
    '''.format(', '.join(['?'] * len(past_parcelle_ids))), tuple(past_parcelle_ids))
    years = [row[0] for row in cursor.fetchall()]

    properties_data = []
    for parcelle_id in past_parcelle_ids:
        cursor.execute('''
            SELECT departement, code_commune, nom_commune, section, numero_plan, numero_voirie, 
                   nature_voie, nom_voie, contenance
            FROM parcelles
            WHERE parcelle_id = ?
        ''', (parcelle_id,))
        base_info = cursor.fetchone()
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

        departement, code_commune, section, numero_plan = base_info[0], base_info[1], base_info[3], base_info[4]
        dvf_link = build_dvf_link(departement, code_commune, section, numero_plan)
        properties_data.append(base_info + tuple(row) + (dvf_link,))

    dynamic_columns = [f'{item} [{year}]' for year in years for item in ('SIREN', 'Forme jur.', 'Dénomination')]
    column_names = ['Département', 'Code Commune', 'Commune', 'Section', 'N° plan', 'N° voirie', 'Nature voie',
                    'Nom voie', 'Contenance'] + dynamic_columns + ['DVF Link']

    return properties_data, column_names


def properties_to_csv(properties, column_names, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        writer.writerows(properties)
        print(f"Les données ont été exportées avec succès dans {filename}.")
