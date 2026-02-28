import flet as ft
from src.api_client.api_client import *
from src.components.components_views import *

# Connexion DB et récupération des données
actif_default = "Amundi NYSE Arca Gold"
datas_actifs = FinanceDatabaseEtfs()
liste_actifs = datas_actifs.get_list_etfs()
#liste_actifs = [e for e in datas_actifs.get_list_etfs() if e and isinstance(e, str)] # Filtre les valeurs nulles car Flet plante contrairement à streamlit (il y a un shotname vide dans la liste (bug yfinance?))
infos_actifs = datas_actifs.get_infos_etfs(actif_default)

couleur_titre_separateur = "#BA68C8"
couleur_bouton_fleche = "#8E24AA" 


################################## GRAPHIQUE #################################################
def create_graph_section(page):
    page.scroll = "auto"

    titre = titre_separateur(text="📈 Graphiques des l'ETFs", padding_text_top=0, couleur_titre_separateur=couleur_titre_separateur)

    dropdown_actif = dropdown("Sélectionnez un ETF", actif_default, liste_actifs, handler=None)

    chart_container = ft.Container(content=ft.Text("Chargement du graphique...", color="white"), expand=True)

    loader = loader_page(couleur_titre_separateur)

    def update_graph(e):
        return graphique_matplot_actif(page, couleur_titre_separateur, loader, chart_container, datas_actifs, dropdown_actif)

    dropdown_actif.on_change = update_graph
    update_graph(None)

    contenu = contenu_widget(titre, [dropdown_actif, loader, chart_container])
    return [contenu]


################################## TABLEAU COMPARATIF RENDEMENTS ################################
def create_rendement_section(page):

    periods_selectionnees = [6, 12, 24, 60, 120, 180]

    titre = titre_separateur(text="💯 Rendements des ETFs (%)", padding_text_top=35, couleur_titre_separateur=couleur_titre_separateur)

    dropdown_actif = dropdown("Sélectionnez les ETFs à comparer", actif_default, liste_actifs, handler=lambda e: ajouter_etf(e.control.value))

    etfs_selectionnes = [actif_default]
    liste_selection = ft.Row(scroll=ft.ScrollMode.AUTO)

    cadre_text = ft.Container(
        content=ft.Column([
            ft.Text("ETFs sélectionnés :", size=11, style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
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

    def update_selection_list():
        liste_selection.controls.clear()
        for i in etfs_selectionnes:
            liste_selection.controls.append(
                ft.Row([ft.Text(i, size=12),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16, on_click=lambda e, i=i: retirer_etf(i))],
                       spacing=0))
        page.update()

    def ajouter_etf(etf):
        if etf and etf not in etfs_selectionnes:
            etfs_selectionnes.append(etf)
            update_selection_list()
            update_table()

    def retirer_etf(etf):
        if etf in etfs_selectionnes:
            etfs_selectionnes.remove(etf)
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
        columns = [ft.DataColumn(ft.Text("ETF", weight=ft.FontWeight.BOLD, size=12))]
        for period in sorted(periods_selectionnees):
            columns.append(ft.DataColumn(ft.Text(f"{period}m", weight=ft.FontWeight.BOLD, size=12)))
        table.columns = columns
        for etf in etfs_selectionnes:
            df = datas_actifs.get_prix_date(etf)
            if not df.empty:
                rendements = calculate_rendement(df, periods_selectionnees)
                cells = [ft.DataCell(ft.Text(etf, size=11))]
                for period in sorted(periods_selectionnees):
                    valeur = rendements.get(f'{period} mois', 0)
                    try:
                        valeur_float = float(valeur)
                        texte = f"{valeur_float:.1f}%"
                        couleur_texte = (ft.Colors.GREEN if valeur_float > 0 else ft.Colors.RED if valeur_float < 0 else ft.Colors.BLACK)
                    except (ValueError, TypeError):
                        texte = str(valeur)
                        couleur_texte = ft.Colors.BLACK
                    cells.append(ft.DataCell(ft.Text(texte, size=10, color=couleur_texte)))
                table.rows.append(ft.DataRow(cells=cells))
        page.update()

    update_selection_list()
    update_periodes_list()
    update_table()

    contenu = contenu_widget(titre, [dropdown_actif, cadre_text, cadre_periodes, cadre_tableau])
    return [contenu]


################################## INFOS ETF ################################
def create_infos_section(page):

    titre = titre_separateur(text="🗂 Informations ETF", padding_text_top=35, couleur_titre_separateur=couleur_titre_separateur)

    dropdown_actif = dropdown("Sélectionnez un ETF", actif_default, liste_actifs, handler=None)

    table_infos, cadre_table_infos = tableau_cadre(expands=False, couleur=couleur_titre_separateur, heights=None)

    def update_table_infos(e):
        selected_etf = dropdown_actif.value
        df = datas_actifs.get_infos_etfs(selected_etf)
        table_infos.columns.clear()
        table_infos.rows.clear()
        for col in df.columns:
            table_infos.columns.append(ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD, size=11)))
        for _, row in df.iterrows():
            table_infos.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(v), size=10)) for v in row]))
        page.update()

    dropdown_actif.on_change = update_table_infos
    update_table_infos(actif_default)

    contenu = contenu_widget(titre, [dropdown_actif, cadre_table_infos])
    return [contenu]


################################### FONCTION PRINCIPALE ################################
def etfs_page(page: ft.Page):
    page.clean()
    page.title = "Les ETFs"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    loader_global = loader_globale(couleur_titre_separateur)
    page.add(loader_global)

    graph_elements = create_graph_section(page)
    rendement_elements = create_rendement_section(page)
    infos_elements = create_infos_section(page)

    bouton_retour_haut = bout_ret_haut(couleur_bouton_fleche, handler=lambda e: page.go("/"))
    bouton_acceuil = bout_ret_acceuil(couleur_bouton_fleche, handler=lambda e: page.go("/"))

    loader_global.visible = False

    page.add(
        bouton_retour_haut,
        *graph_elements,
        *rendement_elements,
        *infos_elements,
        bouton_acceuil
    )