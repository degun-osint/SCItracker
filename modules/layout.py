from prettytable import PrettyTable

def display_properties(properties, column_names):
    """
    Affiche les propriétés dans un tableau formaté.

    :param properties: Une liste de tuples contenant les données des propriétés.
    :param column_names: Une liste de chaînes de caractères représentant les noms des colonnes.
    """
    table = PrettyTable()
    table.field_names = column_names
    for prop in properties:
        table.add_row(prop)
    print(table)
