import flet as ft
from src.api_client.api_client import *
from src.components.components_views import *

# Connexion DB indices
datas_indices = FinanceDatabaseIndice()
liste_indices = datas_indices.get_list_indices()
indice_default = "S&P 500"

# Connexion DB stocks
datas_stocks = FinanceDatabaseStocks()
liste_stocks = datas_stocks.get_list_stocks()
stock_default = "Apple Inc."

# Connexion DB cryptos
datas_cryptos = FinanceDatabaseCryptos()
liste_cryptos = datas_cryptos.get_list_cryptos()
crypto_default = "Bitcoin"

# Connexion DB ETFs
datas_etfs = FinanceDatabaseEtfs()
liste_etfs = [e for e in datas_etfs.get_list_etfs() if e and isinstance(e, str)]
etf_default = "Amundi NYSE Arca Gold"

# Couleurs
couleur_titre_separateur = ft.Colors.PURPLE_300
couleur_bouton_fleche = ft.Colors.PURPLE_600


################################## TABLEAU COMPARATIF RENDEMENTS ################################

def create_rendement_section(page):

    periods_selectionnees = [6, 12, 24, 60, 120, 180]

    titre = titre_separateur(text="💯 Rendements actifs (%)", padding_text_top=0, couleur_titre_separateur=couleur_titre_separateur)

    # Dropdowns
    dropdown_indices = dropdown("Sélectionnez un indice", indice_default, liste_indices, handler=lambda e: ajouter_actif(e.control.value))
    dropdown_stocks = dropdown("Sélectionnez une entreprise", stock_default, liste_stocks, handler=lambda e: ajouter_actif(e.control.value))
    dropdown_cryptos = dropdown("Sélectionnez une crypto", crypto_default, liste_cryptos, handler=lambda e: ajouter_actif(e.control.value))
    dropdown_etfs = dropdown("Sélectionnez un ETF", etf_default, liste_etfs, handler=lambda e: ajouter_actif(e.control.value))

    # Actifs sélectionnés par défaut
    actifs_selectionnes = [indice_default, stock_default, crypto_default, etf_default]

    liste_selection = ft.Row(scroll=ft.ScrollMode.AUTO)

    cadre_text = ft.Container(
        content=ft.Column([
            ft.Text("Actifs sélectionnés:", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
            liste_selection
        ], horizontal_alignment=ft.CrossAxisAlignment.START),
        padding=5,
        border=ft.border.all(2, ft.Colors.WHITE30),
        border_radius=10,
        expand=True,
        alignment=ft.alignment.top_left
    )

    text_periode = ft.Text("Ajouter une période (en mois)", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))
    input_periode = periode_input(fonc_ajouter_periode=lambda e: ajouter_periode(e.control.value))
    bouton_ajouter_periode = ft.IconButton(icon=ft.Icons.ADD, tooltip="Ajouter la période", on_click=lambda e: ajouter_periode(input_periode.value))
    ligne_ajout_periode = ft.Row([input_periode, bouton_ajouter_periode], alignment=ft.MainAxisAlignment.START, spacing=10)
    liste_periodes = ft.Row(scroll=ft.ScrollMode.AUTO)

    cadre_periodes = ft.Container(
        content=ft.Column([
            text_periode,
            ligne_ajout_periode,
            ft.Text("Périodes sélectionnées (en mois) :", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
            liste_periodes,
        ], spacing=10, alignment=ft.MainAxisAlignment.START),
        padding=10,
        border=ft.border.all(2, ft.Colors.WHITE30),
        border_radius=10,
        expand=True,
        alignment=ft.alignment.top_left
    )

    table, cadre_tableau = tableau_cadre(expands=False, couleur=couleur_titre_separateur, heights=None)

    # --- Fonctions ---
    def update_selection_list():
        liste_selection.controls.clear()
        for i in actifs_selectionnes:
            liste_selection.controls.append(
                ft.Row([ft.Text(i, size=12),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, i=i: retirer_actif(i))],
                       spacing=0))
        page.update()

    def ajouter_actif(actif):
        if actif and actif not in actifs_selectionnes:
            actifs_selectionnes.append(actif)
            update_selection_list()
            update_table()

    def retirer_actif(actif):
        if actif in actifs_selectionnes:
            actifs_selectionnes.remove(actif)
            update_selection_list()
            update_table()

    def ajouter_periode(p):
        try:
            p = int(p)
            if p <= 0:
                return
        except (ValueError, TypeError):
            return
        if p not in periods_selectionnees:
            periods_selectionnees.append(p)
            update_periodes_list()
            update_table()
        input_periode.value = ""
        page.update()

    def retirer_periode(p):
        if p in periods_selectionnees:
            periods_selectionnees.remove(p)
            update_periodes_list()
            update_table()

    def update_periodes_list():
        liste_periodes.controls.clear()
        for p in sorted(periods_selectionnees):
            liste_periodes.controls.append(
                ft.Row([ft.Text(f"{p}m", size=12),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, p=p: retirer_periode(p))],
                       spacing=0))
        page.update()

    def update_table():
        table.columns.clear()
        table.rows.clear()

        columns = [ft.DataColumn(ft.Text("Actifs", weight=ft.FontWeight.BOLD, size=12))]
        for period in sorted(periods_selectionnees):
            columns.append(ft.DataColumn(ft.Text(f"{period}m", weight=ft.FontWeight.BOLD, size=12)))
        table.columns = columns

        for actif in actifs_selectionnes:
            # Routing vers la bonne DB selon le type d'actif
            if actif in liste_indices:
                df = datas_indices.get_prix_date(actif)
            elif actif in liste_stocks:
                df = datas_stocks.get_prix_date(actif)
            elif actif in liste_cryptos:
                df = datas_cryptos.get_prix_date(actif)
            elif actif in liste_etfs:
                df = datas_etfs.get_prix_date(actif)
            else:
                continue

            if not df.empty:
                rendements = calculate_rendement(df, periods_selectionnees)
                cells = [ft.DataCell(ft.Text(actif, size=11))]
                for period in sorted(periods_selectionnees):
                    valeur = rendements.get(f'{period} mois', 0)
                    try:
                        valeur_float = float(valeur)
                        texte = f"{valeur_float:.1f}%"
                        couleur_texte = (
                            ft.Colors.GREEN if valeur_float > 0
                            else ft.Colors.RED if valeur_float < 0
                            else ft.Colors.BLACK
                        )
                    except (ValueError, TypeError):
                        texte = str(valeur)
                        couleur_texte = ft.Colors.BLACK
                    cells.append(ft.DataCell(ft.Text(texte, size=10, color=couleur_texte)))
                table.rows.append(ft.DataRow(cells=cells))

        page.update()

    # Initialisation
    update_selection_list()
    update_periodes_list()
    update_table()

    contenu = contenu_widget(titre, [
        dropdown_indices,
        dropdown_stocks,
        dropdown_cryptos,
        dropdown_etfs,  # ⭐ AJOUT
        cadre_text,
        cadre_periodes,
        cadre_tableau
    ])

    return [contenu]


################################### FONCTION PRINCIPALE ################################

def actifs_page(page: ft.Page):
    page.clean()
    page.title = "Comparaison des actifs"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    loader_global = loader_globale(couleur_titre_separateur)
    page.add(loader_global)

    rendement_elements = create_rendement_section(page)

    bouton_retour_haut = bout_ret_haut(couleur_bouton_fleche, handler=lambda e: page.go("/"))
    bouton_retour = bout_ret_acceuil(couleur_bouton_fleche, handler=lambda e: page.go("/"))

    loader_global.visible = False

    page.add(
        bouton_retour_haut,
        *rendement_elements,
        bouton_retour
    ) 