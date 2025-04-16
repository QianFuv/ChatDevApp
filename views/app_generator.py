import flet as ft
from api_client import APIClient
from utils.constants import MODELS, CONFIGURATIONS

class AppGeneratorView:
    """View for generating new ChatDev projects"""
    
    def __init__(self, page: ft.Page, api_client: APIClient):
        """
        Initialize the app generator view
        
        Args:
            page: Flet page object
            api_client: APIClient instance
        """
        self.page = page
        self.api_client = api_client
        
        # Form fields
        self.task_field = ft.TextField(
            label="Task Description",
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Describe the software you want to build (10-2000 characters)",
        )
        
        self.name_field = ft.TextField(
            label="Project Name",
            hint_text="Name of the software project",
        )
        
        self.config_dropdown = ft.Dropdown(
            label="Configuration",
            options=[ft.dropdown.Option(config) for config in CONFIGURATIONS],
            value=CONFIGURATIONS[3],
        )
        
        self.org_field = ft.TextField(
            label="Organization",
            hint_text="Name of the organization",
            value="DefaultOrganization",
        )
        
        self.model_dropdown = ft.Dropdown(
            label="Model",
            options=[ft.dropdown.Option(model) for model in MODELS],
            value=MODELS[6],
        )
        
        self.path_field = ft.TextField(
            label="Existing Code Path (Optional)",
            hint_text="Path to existing code for incremental development",
        )
        
        self.build_apk_checkbox = ft.Checkbox(
            label="Build APK after generation",
            value=False,
        )
        
        self.base_url_field = ft.TextField(
            label="Base URL (Optional)",
            hint_text="Optional base URL for API calls (useful for proxies)",
            value="https://openrouter.ai/api/v1"
        )
        
        # Generate button
        self.generate_button = ft.ElevatedButton(
            text="Generate Project",
            icon=ft.Icons.CREATE,
            on_click=self.generate_project,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Task status display
        self.task_status = ft.Column(
            [
                ft.Text("Task Status", weight=ft.FontWeight.BOLD),
                ft.Text("No active task"),
            ],
            visible=False,
        )
    
    def build(self):
        """Build and return the view"""
        return ft.Column(
            [
                ft.Container(
                    content=ft.Text("Generate New App", size=24, weight=ft.FontWeight.BOLD),
                    padding=10,
                    margin=ft.margin.only(top=30),
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            self.name_field,
                            self.task_field,
                            self.config_dropdown,
                            self.org_field,
                            self.model_dropdown,
                            self.path_field,
                            self.build_apk_checkbox,
                            self.base_url_field,
                            ft.Row(
                                [
                                    self.generate_button,
                                    self.loading,
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            self.task_status,
                        ],
                    ),
                    padding=20,
                    border_radius=10,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def generate_project(self, e):
        """Generate a new project"""
        # Validate inputs
        if not self.task_field.value or len(self.task_field.value) < 10:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Task description must be at least 10 characters"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        if not self.name_field.value:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Project name is required"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # Show loading indicator
        self.loading.visible = True
        self.page.update()
        
        try:
            # Call API to generate project
            result = self.api_client.generate_project(
                task=self.task_field.value,
                name=self.name_field.value,
                config=self.config_dropdown.value,
                org=self.org_field.value,
                model=self.model_dropdown.value,
                path=self.path_field.value,
                build_apk=self.build_apk_checkbox.value,
                base_url=self.base_url_field.value if self.base_url_field.value else None,
            )
            
            task_id = result.get("task_id")
            
            if task_id:
                # Show success message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Project generation started. Task ID: {task_id}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
                
                # Show task status
                self.task_status.controls[0].value = f"Task #{task_id} Status"
                self.task_status.controls[1].value = result.get("status", "Unknown")
                self.task_status.visible = True
                
                # Add a "Check Status" button
                check_status_button = ft.TextButton(
                    text="Check Status",
                    on_click=lambda e, task_id=task_id: self.check_task_status(task_id),
                )
                
                if len(self.task_status.controls) > 2:
                    self.task_status.controls[2] = check_status_button
                else:
                    self.task_status.controls.append(check_status_button)
            else:
                # Show error message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to start project generation: {result.get('message', 'Unknown error')}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
        except Exception as e:
            # Show error message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        
        # Hide loading indicator
        self.loading.visible = False
        self.page.update()
    
    def check_task_status(self, task_id):
        """Check the status of a task"""
        try:
            result = self.api_client.get_task_status(task_id)
            
            # Update status display
            self.task_status.controls[1].value = result.get("status", "Unknown")
            
            # Show message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Task #{task_id} status: {result.get('status', 'Unknown')}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        except Exception as e:
            # Show error message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        
        self.page.update()