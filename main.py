import flet as ft
from views.app_list import AppListView
from views.app_generator import AppGeneratorView
from views.settings import SettingsView
from api_client import APIClient
from utils.storage import load_settings

def main(page: ft.Page):
    """
    Main entry point for the ChatDev mobile application
    
    Args:
        page: Flet page object
    """
    # Set up page
    page.title = "ChatDev Mobile"
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    # Initialize API client with settings
    settings = load_settings()
    api_client = APIClient(
        base_url=settings.get("base_url", "http://localhost:8000/"),
        api_key=settings.get("api_key", "")
    )
    
    # Initialize views
    app_list_view = AppListView(page, api_client)
    app_generator_view = AppGeneratorView(page, api_client)
    settings_view = SettingsView(page, api_client)
    
    # Function to change views
    def change_view(e):
        selected_index = e.control.selected_index
        content_container.content = views[selected_index]
        page.update()
    
    # Create navigation bar
    navigation = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.LIST, label="App List"),
            ft.NavigationBarDestination(icon=ft.Icons.CREATE, label="Generate"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        selected_index=0,
        on_change=change_view,
    )
    
    # Store views for navigation
    views = [
        app_list_view.build(),
        app_generator_view.build(),
        settings_view.build(),
    ]
    
    # Content container
    content_container = ft.Container(
        content=views[0],
        expand=True,
    )
    
    # Main layout
    page.add(
        ft.Column(
            [
                content_container,
                navigation,
            ],
            expand=True,
        )
    )

# Launch the app
ft.app(target=main)