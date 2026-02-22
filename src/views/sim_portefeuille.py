import flet as ft
from src.api_client.api_client import *
from src.components.components_views import *

# Connexion DB
datas_indices = FinanceDatabaseIndice()
liste_indices = datas_indices.get_list_indices()
indice_default = "S&P 500"

datas_stocks = FinanceDatabaseStocks()
liste_stocks = datas_stocks.get_list_stocks()
stock_default = "Apple Inc."

datas_cryptos = FinanceDatabaseCryptos()
liste_cryptos = datas_cryptos.get_list_cryptos()
crypto_default = "Bitcoin"

datas_etfs = FinanceDatabaseEtfs()
liste_etfs = [e for e in datas_etfs.get_list_etfs() if e and isinstance(e, str)]
etf_default = "Amundi NYSE Arca Gold"

couleur_titre_separateur = ft.Colors.PURPLE_300
couleur_bouton_fleche = ft.Colors.PURPLE_600


################################## SECTION PRINCIPALE ################################

def create_rendement_section(page):

    periods_selectionnees = [6, 12, 24, 60, 120, 180]
    actifs_selectionnes = [indice_default, stock_default, crypto_default, etf_default]
    poids_actifs = {indice_default: 25.0, stock_default: 25.0, crypto_default: 25.0, etf_default: 25.0}

    # ------- TITRE -------
    titre = titre_separateur(text="👛 Simulation portefeuille",
                             padding_text_top=0,
                             couleur_titre_separateur=couleur_titre_separateur)

    # ------- DROPDOWNS -------
    dropdown_indices = dropdown("📈 Ajouter un indice", indice_default, liste_indices, handler=lambda e: ajouter_actif(e.control.value))
    dropdown_stocks = dropdown("🏢 Ajouter une entreprise", stock_default, liste_stocks, handler=lambda e: ajouter_actif(e.control.value))
    dropdown_cryptos = dropdown("₿ Ajouter une crypto", crypto_default, liste_cryptos, handler=lambda e: ajouter_actif(e.control.value))
    dropdown_etfs = dropdown("💼 Ajouter un ETF", etf_default, liste_etfs, handler=lambda e: ajouter_actif(e.control.value))

    # ------- LISTE ACTIFS + PONDÉRATIONS -------
    titre_portefeuille = ft.Text("📊 Composition du portefeuille (%)",
                                  size=14,
                                  weight=ft.FontWeight.BOLD,
                                  style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))

    liste_poids = ft.Column(spacing=5)
    texte_total = ft.Text("Total : 100.00%", size=12, color=ft.Colors.GREEN)

    cadre_portefeuille = ft.Container(
        content=ft.Column([titre_portefeuille, liste_poids, texte_total], spacing=8),
        padding=10,
        border=ft.border.all(2, ft.Colors.WHITE30),
        border_radius=10,
        expand=True
    )

    # ------- PÉRIODES -------
    text_periode = ft.Text("⏳ Ajouter une période (en mois)", size=11,
                           style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))
    input_periode = periode_input(fonc_ajouter_periode=lambda e: ajouter_periode(e.control.value))
    bouton_ajouter_periode = ft.IconButton(icon=ft.Icons.ADD, tooltip="Ajouter la période",
                                           on_click=lambda e: ajouter_periode(input_periode.value))
    ligne_ajout_periode = ft.Row([input_periode, bouton_ajouter_periode],
                                 alignment=ft.MainAxisAlignment.START, spacing=10)
    liste_periodes = ft.Row(scroll=ft.ScrollMode.AUTO)

    cadre_periodes = ft.Container(
        content=ft.Column([
            text_periode,
            ligne_ajout_periode,
            ft.Text("Périodes sélectionnées (en mois) :", size=11,
                    style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)),
            liste_periodes,
        ], spacing=10, alignment=ft.MainAxisAlignment.START),
        padding=10,
        border=ft.border.all(2, ft.Colors.WHITE30),
        border_radius=10,
        expand=True
    )

    # ------- TABLEAU -------
    table, cadre_tableau = tableau_cadre(expands=False, couleur=couleur_titre_separateur, heights=None)

    # ===================== FONCTIONS =====================

    def get_df_prix(actif):
        if actif in liste_indices:
            return datas_indices.get_prix_date(actif)
        elif actif in liste_stocks:
            return datas_stocks.get_prix_date(actif)
        elif actif in liste_cryptos:
            return datas_cryptos.get_prix_date(actif)
        elif actif in liste_etfs:
            return datas_etfs.get_prix_date(actif)
        return None

    def update_total_poids():
        total = sum(poids_actifs.values())
        texte_total.value = f"Total : {total:.2f}%"
        if abs(total - 100.0) < 0.01:
            texte_total.color = ft.Colors.GREEN
        elif total > 100.0:
            texte_total.color = ft.Colors.RED
        else:
            texte_total.color = ft.Colors.ORANGE
        page.update()

    def update_liste_poids():
        liste_poids.controls.clear()
        for actif in actifs_selectionnes:
            poids_field = ft.TextField(
                value=str(poids_actifs.get(actif, 0.0)),
                width=80,
                height=35,
                text_style=ft.TextStyle(size=11),
                border_color=ft.Colors.WHITE30,
                border_radius=6,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=lambda e, a=actif: on_poids_change(e, a)
            )
            liste_poids.controls.append(
                ft.Row([
                    ft.Text(actif, size=11, expand=True),
                    poids_field,
                    ft.Text("%", size=11),
                    ft.IconButton(icon=ft.Icons.CLOSE, icon_size=14,
                                  on_click=lambda e, a=actif: retirer_actif(a))
                ], spacing=5)
            )
        page.update()

    def on_poids_change(e, actif):
        try:
            val = float(e.control.value)
            if 0.0 <= val <= 100.0:
                poids_actifs[actif] = val
                update_total_poids()
                update_table()
        except (ValueError, TypeError):
            pass

    def ajouter_actif(actif):
        if actif and actif not in actifs_selectionnes:
            actifs_selectionnes.append(actif)
            poids_actifs[actif] = 0.0
            update_liste_poids()
            update_total_poids()
            update_table()

    def retirer_actif(actif):
        if actif in actifs_selectionnes:
            actifs_selectionnes.remove(actif)
            poids_actifs.pop(actif, None)
            update_liste_poids()
            update_total_poids()
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
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_size=16,
                                      on_click=lambda e, p=p: retirer_periode(p))], spacing=0))
        page.update()

    def update_table():
        table.columns.clear()
        table.rows.clear()

        # Colonnes
        columns = [ft.DataColumn(ft.Text("Actifs", weight=ft.FontWeight.BOLD, size=12))]
        for period in sorted(periods_selectionnees):
            columns.append(ft.DataColumn(ft.Text(f"{period}m", weight=ft.FontWeight.BOLD, size=12)))
        table.columns = columns

        # Rendements par actif + calcul portefeuille
        portfolio_rendements = {p: 0.0 for p in sorted(periods_selectionnees)}

        for actif in actifs_selectionnes:
            df = get_df_prix(actif)
            if df is None or df.empty:
                continue

            rendements = calculate_rendement(df, periods_selectionnees)
            cells = [ft.DataCell(ft.Text(actif, size=11))]
            poids = poids_actifs.get(actif, 0.0) / 100.0

            for period in sorted(periods_selectionnees):
                valeur = rendements.get(f'{period} mois', 0)
                try:
                    valeur_float = float(valeur)
                    texte = f"{valeur_float:.1f}%"
                    couleur_texte = (ft.Colors.GREEN if valeur_float > 0
                                     else ft.Colors.RED if valeur_float < 0
                                     else ft.Colors.BLACK)
                    portfolio_rendements[period] += valeur_float * poids
                except (ValueError, TypeError):
                    texte = str(valeur)
                    couleur_texte = ft.Colors.BLACK
                cells.append(ft.DataCell(ft.Text(texte, size=10, color=couleur_texte)))
            table.rows.append(ft.DataRow(cells=cells))

        # Ligne portefeuille pondéré
        portfolio_cells = [ft.DataCell(ft.Text("👛 PORTEFEUILLE", size=11, weight=ft.FontWeight.BOLD))]
        for period in sorted(periods_selectionnees):
            val = portfolio_rendements[period]
            texte = f"{val:.2f}%"
            couleur = ft.Colors.GREEN if val > 0 else ft.Colors.RED if val < 0 else ft.Colors.BLACK
            portfolio_cells.append(ft.DataCell(ft.Text(texte, size=10, color=couleur, weight=ft.FontWeight.BOLD)))
        table.rows.append(ft.DataRow(cells=portfolio_cells, color=ft.Colors.with_opacity(0.15, couleur_titre_separateur)))

        page.update()

    # Initialisation
    update_liste_poids()
    update_periodes_list()
    update_table()

    contenu = contenu_widget(titre, [
        dropdown_indices,
        dropdown_stocks,
        dropdown_cryptos,
        dropdown_etfs,
        cadre_portefeuille,
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