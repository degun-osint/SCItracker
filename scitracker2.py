# scitracker2.py
import sqlite3
from modules.create_db import create_database
from modules.import_data import import_data
from modules.query_and_export import parcelles_simple, \
    locaux_simple, export_to_csv, parcelles_history, \
    past_parcelles, locaux_history, past_locaux
from modules.layout import display_tables, display_menu, searching
from colorama import Fore, Style
import threading


def prompt_siren():
    """Demander à l'utilisateur d'entrer un ou plusieurs SIREN corrects."""
    from colorama import Fore

    while True:
        siren_input = input(Fore.CYAN + "ℹ️ Entrez un ou plusieurs N° SIREN séparés par une virgule : ")
        sirens = [s.strip().replace(',', '') for s in siren_input.split(',')]  # Nettoyer les entrées

        correct_sirens = [s for s in sirens if s.isdigit() and len(s) == 9]
        incorrect_sirens = [s for s in sirens if not (s.isdigit() and len(s) == 9)]

        if incorrect_sirens:
            print(Fore.RED + " ❌Certains des SIREN entrés sont incorrects : " + ", ".join(incorrect_sirens))
            print(
                Fore.RED + "Un numéro SIREN valide doit contenir exactement 9 chiffres numériques.")
        else:
            return correct_sirens  # Retourner les SIREN corrects si tout est bon


def display_export(conn, sirens, properties_function, locaux_function):
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=searching, args=(stop_event,))
    loading_thread.start()

    result_properties = properties_function(conn, sirens)
    result_locaux = locaux_function(conn, sirens)

    stop_event.set()
    loading_thread.join()
    export_result(result_properties, "parcelles")
    export_result(result_locaux, "locaux")


def export_result(result, suffix):
    if isinstance(result, str):
        print(result)
    else:
        properties, column_names = result
        if properties:
            display_tables(properties, column_names)
            export_choice = input(f"Voulez-vous exporter ces résultats ({suffix}) en CSV ? (Oui/Non) : ").lower()
            if export_choice == 'oui':
                filename = input(Fore.GREEN + f"Entrez le nom de base du fichier à exporter pour les {suffix} :")
                export_to_csv(properties, column_names, filename=f"{filename}-{suffix}.csv")
        else:
            print(f"Aucune donnée disponible pour les SIREN spécifiés pour les {suffix}.")


def main():
    while True:
        display_menu()
        choice = input("Entrez votre choix (1-5) : ")

        if choice == 'init':
            print(Fore.RED + "⚠️ ATTENTION ! Vous allez lancer l'initialisation de la base de données." + Style.RESET_ALL)
            launch_init = input(Fore.RED + "Voulez vous continuer ? (oui/non) : " + Style.RESET_ALL)
            if launch_init == "oui":
                print("Initialisation de la base de données...")
                create_database()
                print("Importation des données...")
                data_directory = "DATA_PARCELLES"
                dataloc_directory = "DATA_LOCAUX"
                import_data(data_directory, dataloc_directory)
            else:
                pass
        elif choice in ['1', '2', '3']:
            sirens = prompt_siren()
            with sqlite3.connect('cadastral_data.db') as conn:
                if choice == '2':
                    display_export(conn, sirens, parcelles_simple, locaux_simple)
                elif choice == '3':
                    display_export(conn, sirens, parcelles_history, locaux_history)
                elif choice == '4':
                    display_export(conn, sirens, past_parcelles, past_locaux)
        elif choice == 'q':
            print(Fore.GREEN + "Au revoir !" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Choix invalide. Veuillez réessayer." + Style.RESET_ALL)


if __name__ == '__main__':
    main()
