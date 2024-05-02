from prettytable.colortable import ColorTable, Themes
import time
from colorama import Fore, Style


def display_menu():
    """Affiche le menu principal."""
    title = """

███████╗ ██████╗██╗████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔════╝██║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████╗██║     ██║   ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
╚════██║██║     ██║   ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
███████║╚██████╗██║   ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚══════╝ ╚═════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ v2.0
            ### Trouvez les parcelles et locaux via SIREN ###                                                                      
    """
    titre_menu = """
 +-+-+-+-+-+-+-+-+-+
 | Menu  Principal |
 +-+-+-+-+-+-+-+-+-+
    """
    # Création d'une bordure autour du titre
    print(Fore.CYAN + f"{title}" + Style.RESET_ALL)

    print(Fore.YELLOW + titre_menu + Style.RESET_ALL)
    print(Fore.BLUE + "# init -" + Fore.BLUE + " Créer/mettre à jour la base de données 🔄")
    print(
        Fore.GREEN + "# 1 -" + Fore.WHITE + " Rechercher des parcelles appartenant à un ou plusieurs SIREN (année la plus récente) 🔍")
    print(
        Fore.GREEN + "# 2 -" + Fore.WHITE + " Rechercher des parcelles appartenant à un ou plusieurs SIREN (avec historique) 📚")
    print(
        Fore.GREEN + "# 3 -" + Fore.WHITE + " Rechercher toutes les anciennes propriétés d'un SIREN 🏠")
    print(Fore.RED + "# q - Quitter ❌" + Style.RESET_ALL)


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


def display_tables(properties, column_names):
    """
    Affiche les propriétés dans un tableau formaté.

    :param properties: Une liste de tuples contenant les données des propriétés.
    :param column_names: Une liste de chaînes de caractères représentant les noms des colonnes.
    """
    table = ColorTable(Themes=Themes.OCEAN, header=True)
    table.field_names = column_names
    for prop in properties:
        table.add_row(prop)
    print(table)
