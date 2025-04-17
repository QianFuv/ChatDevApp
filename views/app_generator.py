import flet as ft
from api_client import APIClient
from utils.constants import MODELS, CONFIGURATIONS

# APK build status constants
APK_STATUS_BUILDING = "BUILDING"
APK_STATUS_BUILDED = "BUILDED"
APK_STATUS_BUILDFAILED = "BUILDFAILED"

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
        self.current_task_id = None
        
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
            value=CONFIGURATIONS[3],  # Default to "Flet"
        )
        
        self.org_field = ft.TextField(
            label="Organization",
            hint_text="Name of the organization",
            value="DefaultOrganization",
        )
        
        self.model_dropdown = ft.Dropdown(
            label="Model",
            options=[ft.dropdown.Option(model) for model in MODELS],
            value=MODELS[0],  # Default to "CLAUDE_3_5_SONNET"
        )
        
        self.path_field = ft.TextField(
            label="Existing Code Path (Optional)",
            hint_text="Path to existing code for incremental development",
        )
        
        self.build_apk_checkbox = ft.Checkbox(
            label="Build APK after generation",
            value=True,  # Default to building APK
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
                # Status indicators row will be added when a task is created
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
                # Store current task ID
                self.current_task_id = task_id
                
                # Show success message
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Project generation started. Task ID: {task_id}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
                
                # Update task status display with better styling
                self.task_status.controls[0].value = f"Task #{task_id} Status"
                
                # Create status indicator
                task_status = result.get("status", "Unknown")
                status_color = self._get_status_color(task_status)
                
                status_indicator = ft.Row([
                    ft.Container(
                        content=ft.Text(task_status),
                        bgcolor=status_color,
                        padding=5,
                        border_radius=5,
                    )
                ])
                
                # Update status text and add indicator
                self.task_status.controls[1].value = f"Created: {result.get('created_at', 'Unknown')}"
                
                # Replace or add status indicator
                if len(self.task_status.controls) > 2:
                    self.task_status.controls[2] = status_indicator
                else:
                    self.task_status.controls.append(status_indicator)
                
                # Add buttons row
                buttons_row = ft.Row([
                    ft.TextButton(
                        text="Check Status",
                        on_click=lambda e: self.check_task_status(task_id),
                    ),
                    ft.TextButton(
                        text="Cancel Task",
                        on_click=lambda e: self.cancel_task(task_id),
                    ),
                ])
                
                # Replace or add buttons row
                if len(self.task_status.controls) > 3:
                    self.task_status.controls[3] = buttons_row
                else:
                    self.task_status.controls.append(buttons_row)
                
                # Show the task status section
                self.task_status.visible = True
                
                # Start the status refresh timer
                self.schedule_status_check()
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
    
    def _get_status_color(self, status):
        """Get the color for a status"""
        status_colors = {
            "PENDING": ft.colors.ORANGE,
            "RUNNING": ft.colors.BLUE,
            "COMPLETED": ft.colors.GREEN,
            "FAILED": ft.colors.RED,
            "CANCELLED": ft.colors.GREY,
            APK_STATUS_BUILDING: ft.colors.BLUE,
            APK_STATUS_BUILDED: ft.colors.GREEN,
            APK_STATUS_BUILDFAILED: ft.colors.RED,
        }
        return status_colors.get(status, ft.colors.GREY)
    
    def schedule_status_check(self):
        """Schedule a periodic status check"""
        if self.current_task_id:
            self.page.set_timer(5000, lambda _: self.check_task_status(self.current_task_id, auto=True))
    
    def check_task_status(self, task_id, auto=False):
        """Check the status of a task"""
        try:
            result = self.api_client.get_task_status(task_id)
            
            # Get task status
            task_status = result.get("status", "Unknown")
            
            # Check if task is complete or failed
            task_complete = task_status in ["COMPLETED", "FAILED", "CANCELLED"]
            
            # Get APK build status
            apk_build_status = result.get("apk_build_status")
            apk_path = result.get("apk_path", "")
            
            # Create indicators list
            indicators = []
            
            # Add task status indicator
            task_status_color = self._get_status_color(task_status)
            indicators.append(
                ft.Container(
                    content=ft.Text(task_status),
                    bgcolor=task_status_color,
                    padding=5,
                    border_radius=5,
                )
            )
            
            # Add APK build status indicator if available
            if apk_build_status:
                apk_status_color = self._get_status_color(apk_build_status)
                indicators.append(
                    ft.Container(
                        content=ft.Text(f"APK: {apk_build_status}"),
                        bgcolor=apk_status_color,
                        padding=5,
                        border_radius=5,
                        margin=ft.margin.only(left=5),
                    )
                )
            
            # Update status text with last updated time
            self.task_status.controls[1].value = f"Last updated: {result.get('updated_at', 'Unknown')}"
            
            # Update status indicators
            if len(self.task_status.controls) > 2:
                self.task_status.controls[2] = ft.Row(indicators)
            
            # Update action buttons based on status
            button_row = []
            
            # Always add Check Status button
            button_row.append(
                ft.TextButton(
                    text="Check Status",
                    on_click=lambda e: self.check_task_status(task_id),
                )
            )
            
            # Add Cancel button for active tasks
            if not task_complete:
                button_row.append(
                    ft.TextButton(
                        text="Cancel Task",
                        on_click=lambda e: self.cancel_task(task_id),
                    )
                )
            
            # Add Build APK button if completed but no APK
            if task_status == "COMPLETED" and not apk_build_status:
                button_row.append(
                    ft.TextButton(
                        text="Build APK",
                        on_click=lambda e: self.build_apk(task_id, result),
                    )
                )
            
            # Add Retry APK button if APK build failed
            if apk_build_status == APK_STATUS_BUILDFAILED:
                button_row.append(
                    ft.TextButton(
                        text="Retry APK Build",
                        on_click=lambda e: self.build_apk(task_id, result),
                    )
                )
            
            # Add Download APK button if APK is built
            if apk_build_status == APK_STATUS_BUILDED and apk_path:
                button_row.append(
                    ft.TextButton(
                        text="APK Info",
                        on_click=lambda e: self.show_apk_info(apk_path),
                    )
                )
            
            # Update button row
            if len(self.task_status.controls) > 3:
                self.task_status.controls[3] = ft.Row(button_row)
            else:
                self.task_status.controls.append(ft.Row(button_row))
            
            # Add APK path if available
            if apk_path:
                # Check if we already have an APK path display
                found = False
                for i, control in enumerate(self.task_status.controls):
                    if i > 3 and isinstance(control, ft.Text) and control.value.startswith("APK:"):
                        control.value = f"APK: {apk_path}"
                        found = True
                        break
                
                # Add new APK path display if not found
                if not found:
                    self.task_status.controls.append(
                        ft.Text(
                            f"APK: {apk_path}",
                            style=ft.TextStyle(
                                italic=True,
                                size=12,
                            ),
                        )
                    )
            
            # Show message but only if manual check
            if not auto:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Task #{task_id} status: {task_status}" + 
                                    (f", APK: {apk_build_status}" if apk_build_status else "")),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
            
            # Schedule another check if task is not complete
            if not task_complete:
                self.schedule_status_check()
            else:
                # If APK is building, keep checking
                if apk_build_status == APK_STATUS_BUILDING:
                    self.schedule_status_check()
                    
        except Exception as e:
            # Show error message but only if manual check
            if not auto:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
            
            # If auto-check failed, try again later
            if auto:
                self.schedule_status_check()
        
        self.page.update()
    
    def cancel_task(self, task_id):
        """Cancel a task"""
        try:
            result = self.api_client.cancel_task(task_id)
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Task #{task_id} cancellation requested. New status: {result.get('status', 'Unknown')}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
            
            # Update task status
            self.check_task_status(task_id)
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error cancelling task: {str(e)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
            
        self.page.update()
    
    def build_apk(self, task_id, task_result):
        """Build APK for the task"""
        try:
            # Extract project info from result path
            result_path = task_result.get("result_path", "")
            if not result_path:
                raise ValueError("No result path available to build APK")
            
            # Parse result_path to extract project information
            project_name = "Unknown"
            organization = "DefaultOrganization"
            timestamp = ""
            
            try:
                # Expected format: "WareHouse/ProjectName_Organization_Timestamp"
                parts = result_path.split('/')
                if len(parts) >= 2:
                    # Get the last part and split by underscore
                    project_parts = parts[-1].split('_')
                    if len(project_parts) >= 3:
                        project_name = project_parts[0]
                        organization = project_parts[1]
                        timestamp = project_parts[2]
            except Exception:
                raise ValueError("Could not parse project information from result path")
            
            # Show loading indicator
            self.loading.visible = True
            self.page.update()
            
            # Build APK
            result = self.api_client.build_apk(
                project_name=project_name,
                organization=organization,
                timestamp=timestamp,
                task_id=task_id
            )
            
            if result.get("success", False):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("APK build initiated successfully"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
                
                # Update status to show building
                self.check_task_status(task_id)
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to build APK: {result.get('message', 'Unknown error')}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
        except ValueError as ve:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(ve)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        finally:
            # Hide loading indicator
            self.loading.visible = False
            self.page.update()
    
    def show_apk_info(self, apk_path):
        """Show APK information and download options"""
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        # Create dialog content
        dialog = ft.AlertDialog(
            title=ft.Text("APK Download Information"),
            content=ft.Column([
                ft.Text("APK is available on the server at:"),
                ft.Text(apk_path, selectable=True),
                ft.Text("\nTo download, connect to the server and locate this file."),
            ], tight=True, spacing=10, width=400),
            actions=[
                ft.TextButton("Close", on_click=close_dialog),
            ],
        )
        
        # Show dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()