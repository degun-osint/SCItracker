# scitracker2.py
import sqlite3
from modules.create_db import create_database
from modules.import_data import import_data
from modules.query_and_export import properties_simple, properties_to_csv, properties_and_history, past_properties
from modules.layout import display_properties
from colorama import Fore, Style
import threading
import time


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
        Fore.GREEN + "4 -" + Fore.WHITE + " Rechercher toutes les anciennes propriétés d'un SIREN 🏠")
    print(Fore.RED + "5 - Quitter ❌" + Style.RESET_ALL)


def searching(stop_event):
    """Affiche un message de chargement jusqu'à ce que stop_event soit défini."""
    etats_oeil = [Fore.YELLOW + "🐵" + Style.RESET_ALL, Fore.YELLOW + "🙈" + Style.RESET_ALL]
    idx_etat = 0
    start_time = time.time()
    while not stop_event.is_set():
        print("\r" + Fore.YELLOW + "Recherche en cours " + etats_oeil[idx_etat], end="", flush=True)
        idx_etat = (idx_etat + 1) % len(etats_oeil)
        time.sleep(0.5)

    end_time = time.time()
    duree = end_time - start_time
    print(Fore.GREEN + "\rRecherche terminée en {:.2f} secondes. 🤘".format(duree) + Style.RESET_ALL)

def prompt_siren_input():
    """Demander à l'utilisateur d'entrer un ou plusieurs SIREN."""
    siren_input = input(Fore.CYAN + "Entrez un ou plusieurs N° SIREN séparés par une virgule : ")
    return [s.strip() for s in siren_input.split(',')]


def display_and_export_properties(conn, sirens, function_to_call):
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
            display_properties(properties, column_names)
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
            if launch_init == "oui" :
                print("Initialisation de la base de données...")
                create_database()
                print("Importation des données...")
                data_directory = "DATA"
                import_data(data_directory)
            else :
                pass
        elif choice in ['2', '3', '4']:
            sirens = prompt_siren_input()
            with sqlite3.connect('cadastral_data.db') as conn:
                if choice == '2':
                    display_and_export_properties(conn, sirens, properties_simple)
                elif choice == '3':
                    display_and_export_properties(conn, sirens, properties_and_history)
                elif choice == '4':
                    display_and_export_properties(conn, sirens, past_properties)
        elif choice == '5':
            print(Fore.GREEN + "Au revoir !" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Choix invalide. Veuillez réessayer." + Style.RESET_ALL)

if __name__ == '__main__':
    main()