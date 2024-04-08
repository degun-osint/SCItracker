# scitracker2.py
import sqlite3
from modules.create_db import create_database
from modules.import_data import import_data
from modules.query_and_export import find_properties_by_siren, export_properties_to_csv, find_properties_and_history_by_siren, find_past_properties
from modules.layout import display_properties
from colorama import Fore, Style

from colorama import Fore, Style


def display_menu():
    """Affiche le menu principal."""
    title = "  👀 SCITracker  🕵️‍"
    # Création d'une bordure autour du titre
    border = "+" + "-" * (len(title) + 2) + "+"
    print(Fore.CYAN + border + Style.RESET_ALL)
    print(Fore.CYAN + f"{title}" + Style.RESET_ALL)
    print(Fore.CYAN + border + Style.RESET_ALL + "\n")

    print(Fore.YELLOW + "Menu Principal" + Style.RESET_ALL)
    print(Fore.GREEN + "1 -" + Fore.WHITE + " Créer/mettre à jour la base de données 🔄")
    print(
        Fore.GREEN + "2 -" + Fore.WHITE + " Rechercher des parcelles appartenant à un ou plusieurs SIREN (année la plus récente) 🔍")
    print(
        Fore.GREEN + "3 -" + Fore.WHITE + " Rechercher des parcelles appartenant à un ou plusieurs SIREN (avec historique) 📚")
    print(
        Fore.GREEN + "4 -" + Fore.WHITE + " Rechercher toutes les propriétés d'un SIREN (actuel et ancien propriétaire) 🏠")
    print(Fore.RED + "5 - Quitter ❌" + Style.RESET_ALL)


def prompt_siren_input():
    """Demander à l'utilisateur d'entrer un ou plusieurs SIREN."""
    siren_input = input(Fore.CYAN + "Entrez un ou plusieurs N° SIREN séparés par une virgule : ")
    return [s.strip() for s in siren_input.split(',')]


def display_and_export_properties(conn, sirens, function_to_call):
    """Affiche et propose l'exportation des propriétés."""
    properties, column_names = function_to_call(conn, sirens)
    if properties:
        display_properties(properties, column_names)
        export_choice = input("Voulez-vous exporter ces résultats en CSV ? (Oui/Non) : ").lower()
        if export_choice == 'oui':
            filename = input(Fore.GREEN + "Entrez le nom du fichier à exporter :")
            export_properties_to_csv(properties, column_names, filename=filename+".csv")
    else:
        print("Aucune donnée disponible pour les SIREN spécifiés.")


def main():
    while True:
        display_menu()
        choice = input("Entrez votre choix (1-5) : ")

        if choice == '1':
            print("Initialisation de la base de données...")
            create_database()
            print("Importation des données...")
            data_directory = "DATA"
            import_data(data_directory)
        elif choice in ['2', '3', '4']:
            sirens = prompt_siren_input()
            with sqlite3.connect('cadastral_data.db') as conn:
                if choice == '2':
                    display_and_export_properties(conn, sirens, find_properties_by_siren)
                elif choice == '3':
                    display_and_export_properties(conn, sirens, find_properties_and_history_by_siren)
                elif choice == '4':
                    display_and_export_properties(conn, sirens, find_past_properties)
        elif choice == '5':
            print(Fore.GREEN + "Au revoir !" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Choix invalide. Veuillez réessayer." + Style.RESET_ALL)

if __name__ == '__main__':
    main()