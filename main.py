# Créer un venv : python3 -m venv .venv
# L’activer : "source .venv/bin/activate" ou "source venv/bin/activate"
# Désactiver : deactivate
# Installer les dépendances : pip install -r requirements.txt
# Lancer l’application : python main.py

import asyncio

import flet as ft
from src.controllers.navigation import route_change
from src.api_client.api_client import ClientStorageWrapper
from src.authmanager_share import auth_manager 
from src.components.components_views import loader_globale


async def main(page: ft.Page):
    page.clean()
    page.title = "FinSim - Finance facile"
    page.window.width = 360
    page.window.height = 640
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 10
    page.spacing = 5
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.DARK

    # 🔄 Loader de démarrage
    loader = loader_globale("#3A8A4A")
    page.add(loader)
    page.update()

    # 🔧 Brancher le stockage de session
    # page.client_storage a disparu en Flet 0.86 : on passe par le service
    # ft.SharedPreferences, qui s'enregistre tout seul aupres de la page.
    # Le wrapper lit la valeur une fois ici, puis sert les lectures en
    # synchrone depuis son cache (voir ClientStorageWrapper).
    storage = ClientStorageWrapper(page, ft.SharedPreferences())
    await storage.load(auth_manager.cookie_name)
    auth_manager.cookies = storage

    # 🔒 Vérifier la session
    # get_current_user() fait un appel reseau bloquant (timeout 10 s) : on le
    # sort de la boucle d'evenements pour ne pas figer l'affichage du loader.
    current_user = await asyncio.to_thread(auth_manager.get_current_user)

    if current_user:
        page.route = "/"
    else:
        page.route = "/auth_manag"

    def on_route_change(e):
        route_change(page)

    page.on_route_change = on_route_change
    route_change(page)

ft.run(main)

'''ft.run(
    main,
    view=ft.AppView.WEB_BROWSER,  # ouvre dans le navigateur
    port=8550)                     # important : même port que dans l'email
'''

