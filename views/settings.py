import flet as ft
from api_client import APIClient
from utils.storage import load_settings, save_settings

class SettingsView:
    """View for application settings"""
    
    def __init__(self, page: ft.Page, api_client: APIClient):
        """
        Initialize the settings view
        
        Args:
            page: Flet page object
            api_client: APIClient instance
        """
        self.page = page
        self.api_client = api_client
        
        # Load current settings
        settings = load_settings()
        
        # Form fields
        self.base_url_field = ft.TextField(
            label="API Base URL",
            value=settings.get("base_url", "http://localhost:8000/"),
        )
        
        self.api_key_field = ft.TextField(
            label="API Key",
            value=settings.get("api_key", ""),
            password=True,
        )
        
        # Theme dropdown
        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            options=[
                ft.dropdown.Option("System"),
                ft.dropdown.Option("Light"),
                ft.dropdown.Option("Dark"),
            ],
            value=settings.get("theme", "System"),
        )
        
        # Save button
        self.save_button = ft.ElevatedButton(
            text="Save Settings",
            icon=ft.Icons.SAVE,
            on_click=self.save_settings,
        )
        
        # Test connection button
        self.test_button = ft.ElevatedButton(
            text="Test Connection",
            icon=ft.Icons.NETWORK_CHECK,
            on_click=self.test_connection,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # API status
        self.api_status = ft.Text("API Status: Unknown")
    
    def build(self):
        """Build and return the view"""
        return ft.Column(
            [
                ft.Container(
                    content=ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                    padding=10,
                    margin=ft.margin.only(top=30),
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("API Configuration", weight=ft.FontWeight.BOLD),
                            self.base_url_field,
                            self.api_key_field,
                            ft.Row(
                                [
                                    self.save_button,
                                    self.test_button,
                                    self.loading,
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            self.api_status,
                            ft.Divider(),
                            ft.Text("App Settings", weight=ft.FontWeight.BOLD),
                            self.theme_dropdown,
                        ],
                    ),
                    padding=20,
                    border_radius=10,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def save_settings(self, e=None):
        """Save settings to storage"""
        settings = {
            "base_url": self.base_url_field.value,
            "api_key": self.api_key_field.value,
            "theme": self.theme_dropdown.value,
        }
        
        if save_settings(settings):
            # Update API client
            self.api_client.set_base_url(settings["base_url"])
            self.api_client.set_api_key(settings["api_key"])
            
            # Apply theme
            theme_mode = {
                "System": ft.ThemeMode.SYSTEM,
                "Light": ft.ThemeMode.LIGHT,
                "Dark": ft.ThemeMode.DARK,
            }[settings["theme"]]
            self.page.theme_mode = theme_mode
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Settings saved successfully"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        else:
            # Show error message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Failed to save settings"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        
        self.page.update()
    
    def test_connection(self, e):
        """Test API connection"""
        # Show loading indicator
        self.loading.visible = True
        self.api_status.value = "API Status: Testing..."
        self.page.update()
        
        try:
            # Try simple health check first
            simple_health = self.api_client.simple_health_check()
            
            # Debug information
            print(f"Simple health check response: {simple_health}")
            
            # More flexible status check (case-insensitive, accepts multiple values)
            status = simple_health.get("status", "").lower()
            if status in ["ok", "up", "healthy"] or "success" in status:
                # If simple health check passes, try API v1 health check
                try:
                    health = self.api_client.health_check()
                    
                    self.api_status.value = f"API Status: Connected (v{health.get('version', 'Unknown')})"
                    
                    # Show success message
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("API connection successful"),
                        action="Dismiss",
                    )
                    self.page.snack_bar.open = True
                except Exception as api_error:
                    # If the API V1 health check fails but simple health succeeded
                    self.api_status.value = "API Status: Connected (Base API only)"
                    
                    # Show partial success message
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Connected to base API but API V1 health check failed"),
                        action="Dismiss",
                    )
                    self.page.snack_bar.open = True
            else:
                self.api_status.value = "API Status: Not Connected"
                
                # Show error message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"API connection failed: {simple_health.get('message', 'Unknown error')}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
        except Exception as e:
            self.api_status.value = "API Status: Not Connected"
            
            # Show error message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"API connection failed: {str(e)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        
        # Hide loading indicator
        self.loading.visible = False
        self.page.update()