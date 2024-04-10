# scitracker2.py
import sqlite3
from modules.create_db import create_database
from modules.import_data import import_data
from modules.query_and_export import properties_simple, properties_to_csv, properties_and_history, past_properties
from modules.layout import display_tables, display_menu, searching
from colorama import Fore, Style
import threading


def prompt_siren_input():
    """Demander à l'utilisateur d'entrer un ou plusieurs SIREN corrects."""
    from colorama import Fore  # Assurez-vous que colorama est installé et importé correctement

    while True:  # Boucler jusqu'à ce que l'input soit correct
        siren_input = input(Fore.CYAN + "ℹ️ Entrez un ou plusieurs N° SIREN séparés par une virgule : ")
        sirens = [s.strip().replace(',', '') for s in siren_input.split(',')]  # Nettoyer les entrées

        # Vérifier que chaque SIREN est au bon format
        correct_sirens = [s for s in sirens if s.isdigit() and len(s) == 9]
        incorrect_sirens = [s for s in sirens if not (s.isdigit() and len(s) == 9)]

        if incorrect_sirens:  # S'il y a des erreurs, les afficher
            print(Fore.RED + " ❌Certains des SIREN entrés sont incorrects : " + ", ".join(incorrect_sirens))
            print(
                Fore.RED + "Un numéro SIREN valide doit contenir exactement 9 chiffres numériques.")
        else:
            return correct_sirens  # Retourner les SIREN corrects si tout est bon


def display_export(conn, sirens, function_to_call):
    """Affiche et propose l'exportation des propriétés."""

    stop_event = threading.Event()
    loading_thread = threading.Thread(target=searching, args=(stop_event,))
    loading_thread.start()

    result = function_to_call(conn, sirens)

    stop_event.set()  # Stoppe l'animation
    loading_thread.join()  # Attend que le thread de l'animation se termine
    if isinstance(result, str):
        print(result)
    else:
        properties, column_names = result
        if properties:
            display_tables(properties, column_names)
            export_choice = input("Voulez-vous exporter ces résultats en CSV ? (Oui/Non) : ").lower()
            if export_choice == 'oui':
                filename = input(Fore.GREEN + "Entrez le nom du fichier à exporter :")
                properties_to_csv(properties, column_names, filename=filename + ".csv")
        else:
            print("Aucune donnée disponible pour les SIREN spécifiés.")


def main():
    while True:
        display_menu()
        choice = input("Entrez votre choix (1-5) : ")

        if choice == '1':
            print(Fore.RED + "⚠️ ATTENTION ! Vous allez lancer l'initialisation de la base de données." + Style.RESET_ALL)
            launch_init = input(Fore.RED + "Voulez vous continuer ? (oui/non) : " + Style.RESET_ALL)
            if launch_init == "oui":
                print("Initialisation de la base de données...")
                create_database()
                print("Importation des données...")
                data_directory = "DATA"
                import_data(data_directory)
            else:
                pass
        elif choice in ['2', '3', '4']:
            sirens = prompt_siren_input()
            with sqlite3.connect('cadastral_data.db') as conn:
                if choice == '2':
                    display_export(conn, sirens, properties_simple)
                elif choice == '3':
                    display_export(conn, sirens, properties_and_history)
                elif choice == '4':
                    display_export(conn, sirens, past_properties)
        elif choice == '5':
            print(Fore.GREEN + "Au revoir !" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Choix invalide. Veuillez réessayer." + Style.RESET_ALL)


if __name__ == '__main__':
    main()
