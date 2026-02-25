import flet as ft
from src.components.components_views import *
from src.api_client.api_client import *
from src.authmanager_share import auth_manager  # instance globale

couleur_titre_separateur = "#00B388"
couleur_bouton_fleche = "#21C4A0"

def main_page(page: ft.Page):
    page.clean()

    # --- Titre ---
    titre = titre_separateur("🏠 Bienvenue sur FinSim", couleur_titre_separateur, padding_text_top = 45)

    # --- Texte explicatif ---
    texte_explication = ft.Container(content=ft.Text("Analysez les performances historiques des indices, actions, cryptos et ETF en un clin d'œil.\n"
                                                    "Simulez vos stratégies DCA (progressif) ou Lump Sum (en une fois).\n" 
                                                    "Construisez votre portefeuille pour simuler des rendements passés.\n"
                                                    "Outil pédagogique sans risque : apprenez à investir sans conseil financier.\n\n" 
                                                    "Bonne visite !",
                                                 color=couleur_titre_separateur, 
                                                 size=12, 
                                                 text_align=ft.TextAlign.JUSTIFY,),
                                padding=ft.padding.symmetric(vertical=10, horizontal=10),
                                alignment=ft.alignment.center,)

    # --- Liste des boutons selon rôle ---
    current_user = auth_manager.get_current_user()
    user_role = current_user["role"] if current_user else None

    if user_role == "admin":
        tiles_button = [
            ("Indices", "#21C4A0", "/indices"),
            ("Stocks", "#81D4FA", "/stocks"),
            ("ETFs", ft.Colors.CYAN_200, "/ETFs"),
            ("Cryptos", "#F7931A", "/cryptos"),
            ("Tous Actifs", ft.Colors.PURPLE_200, "/tous_actifs"),
            ("DCAvsLP", ft.Colors.CYAN_400, "/dca_vs_lp"),
            ("🔧 Admin", "#D67C7C", "/admin"),
            ("Auth manag", "#D67C7C", "/auth_manag"),
            ("Inscription", "#D67C7C", "/inscription"),
            ("Mdp oublié", "#D67C7C", "/mdp_oublie"),
            ("Reset mdp", "#D67C7C", "/reset_mdp"),
            ("Test", ft.Colors.CYAN_500, "/test"),
            #("Test_matplot", ft.Colors.CYAN_500, "/test_matplot"),
        ]
    else:
        tiles_button = [
            ("Indices", "#21C4A0", "/indices"),
            ("Stocks", "#81D4FA", "/stocks"),
            ("ETFs", ft.Colors.CYAN_200, "/etfs"),
            ("Cryptos", "#F7931A", "/cryptos"),
            ("Tous Actifs", ft.Colors.PURPLE_200, "/tous_actifs"),
            ("DCAvsLP", ft.Colors.CYAN_400, "/dca_vs_lp"),
        ]

    # --- Séparation ---
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur), padding=ft.padding.only(top=25, bottom=0),)

    # --- Création des boutons ---
    buttons = []
    for name, color, route in tiles_button:
        btn = ft.ElevatedButton(
            content=ft.Text(name, size=12),
            bgcolor=color,
            color=ft.Colors.BLACK,
            on_click=lambda e, r=route: page.go(r),
            width=105,
            height=55,
        )
        buttons.append(btn)

    centered_grid = ft.Row(controls=buttons,
                            wrap=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                            run_spacing=10,
                            expand=True,)

    grid_avec_espace = ft.Container(content=centered_grid,
                                    padding=ft.padding.only(top=10),)

    # --- Fonction logout ---
    def handle_logout(e):
        auth_manager.logout()       # utilise l'instance globale
        page.go("/auth_manag")      # redirige vers la page login
        page.update()

    # --- Bouton Logout ---
    bout_logout = bout_ret_acceuil("#D9534F", text="Déconnection", handler = handle_logout, icons=ft.Icons.LOGOUT)

    # --- Tous droits réservés ---
    texte_droit = ft.Container(content=ft.Text("© 2025 FinSim — Bastien Maurières. Tous droits réservés.",
                                               color="#F7F7F7",
                                               size=9,),
                                alignment=ft.alignment.center,)

    # --- Ajout des éléments à la page ---
    page.add(
        *titre,
        grid_avec_espace,
        separation, 
        texte_explication,
        bout_logout,
        texte_droit
    )
    page.update()
