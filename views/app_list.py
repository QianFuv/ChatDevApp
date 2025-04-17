import flet as ft
from api_client import APIClient
from utils.constants import (
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_CANCELLED,
)

# APK build status constants
APK_STATUS_BUILDING = "BUILDING"
APK_STATUS_BUILDED = "BUILDED"
APK_STATUS_BUILDFAILED = "BUILDFAILED"

class AppListView:
    """View for displaying and managing ChatDev tasks"""
    
    def __init__(self, page: ft.Page, api_client: APIClient):
        """
        Initialize the app list view
        
        Args:
            page: Flet page object
            api_client: APIClient instance
        """
        self.page = page
        self.api_client = api_client
        self.tasks = []
        self.status_filter = None
        self.limit = 10
        self.offset = 0
        self.total_tasks = 0
        
        # UI elements
        self.tasks_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )
        
        self.status_dropdown = ft.Dropdown(
            label="Filter by status",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option(TASK_STATUS_PENDING),
                ft.dropdown.Option(TASK_STATUS_RUNNING),
                ft.dropdown.Option(TASK_STATUS_COMPLETED),
                ft.dropdown.Option(TASK_STATUS_FAILED),
                ft.dropdown.Option(TASK_STATUS_CANCELLED),
            ],
            value="All",
            on_change=self.change_status_filter,
            content_padding=ft.padding.only(right=10),  # Add padding for better appearance
        )
        
        self.pagination = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=self.prev_page,
                    disabled=True,
                ),
                ft.Text("Page 1"),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=self.next_page,
                    disabled=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            on_click=self.fetch_tasks,
            tooltip="Refresh",
        )
        
        self.loading = ft.ProgressRing(visible=False, width=24, height=24)
    
    def build(self):
        """Build and return the view"""
        view = ft.Column(
            [
                ft.Container(
                    content=ft.Text("App List", size=24, weight=ft.FontWeight.BOLD),
                    padding=10,
                    margin=ft.margin.only(top=30),
                ),
                # Filter and action buttons in a container with consistent padding
                ft.Container(
                    content=ft.Column(
                        [
                            # Filter and action buttons that stay on the same line
                            ft.Row(
                                [
                                    # Dropdown expands to fill available space
                                    ft.Container(
                                        content=self.status_dropdown,
                                        expand=True,
                                    ),
                                    # Actions stay together in a compact layout
                                    ft.Container(
                                        content=ft.Row(
                                            [self.refresh_button, self.loading],
                                            spacing=0,
                                            wrap=False,  # Prevent wrapping
                                        ),
                                        padding=ft.padding.only(left=8),
                                    ),
                                ],
                                spacing=0,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            self.tasks_list,
                            self.pagination,
                        ],
                    ),
                    padding=20,
                    border_radius=10,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Load tasks when view is first built
        self.fetch_tasks()
        return view
    
    def fetch_tasks(self, e=None):
        """Fetch tasks from API"""
        self.loading.visible = True
        self.page.update()
        
        try:
            result = self.api_client.list_tasks(
                status=self.status_filter if self.status_filter != "All" else None,
                limit=self.limit,
                offset=self.offset,
            )
            
            self.tasks = result.get("tasks", [])
            self.total_tasks = result.get("total", 0)
            self.update_task_list()
            self.update_pagination()
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        
        self.loading.visible = False
        self.page.update()
    
    def update_task_list(self):
        """Update task list with fetched tasks"""
        self.tasks_list.controls.clear()
        
        for task in self.tasks:
            task_card = self.create_task_card(task)
            self.tasks_list.controls.append(task_card)
        
        self.page.update()
    
    def create_task_card(self, task):
        """Create a card for a task"""
        # Task status
        status = task.get("status", "Unknown")
        status_color = {
            TASK_STATUS_PENDING: ft.Colors.ORANGE,
            TASK_STATUS_RUNNING: ft.Colors.BLUE,
            TASK_STATUS_COMPLETED: ft.Colors.GREEN,
            TASK_STATUS_FAILED: ft.Colors.RED,
            TASK_STATUS_CANCELLED: ft.Colors.GREY,
        }.get(status, ft.Colors.GREY)
        
        # APK build status
        apk_build_status = task.get("apk_build_status")
        apk_status_color = {
            APK_STATUS_BUILDING: ft.Colors.BLUE,
            APK_STATUS_BUILDED: ft.Colors.GREEN,
            APK_STATUS_BUILDFAILED: ft.Colors.RED,
        }.get(apk_build_status, None)
        
        task_id = task.get("task_id", 0)
        result_path = task.get("result_path", "")
        apk_path = task.get("apk_path", "")
        
        # Extract project name, organization, and timestamp from result_path
        project_name = "Unknown"
        organization = "DefaultOrganization"
        timestamp = ""
        
        if result_path:
            # Parse result_path to extract project information
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
                pass
                
        created_at = task.get("created_at", "Unknown")
        
        # Actions based on status
        actions = []
        
        # Cancel button for pending or running tasks
        if status in [TASK_STATUS_PENDING, TASK_STATUS_RUNNING]:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.CANCEL,
                    tooltip="Cancel task",
                    on_click=lambda e, task_id=task_id: self.cancel_task(task_id),
                )
            )
        
        # Delete button for all tasks
        actions.append(
            ft.IconButton(
                icon=ft.Icons.DELETE,
                tooltip="Delete task",
                on_click=lambda e, task_id=task_id: self.delete_task(task_id),
            )
        )
        
        # Build APK button based on status and APK build status
        if status == TASK_STATUS_COMPLETED and project_name != "Unknown" and result_path:
            # Show build button when completed and no APK status, or when APK build failed
            if not apk_build_status or apk_build_status == APK_STATUS_BUILDFAILED:
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.BUILD,
                        tooltip="Build APK",
                        on_click=lambda e, pn=project_name, org=organization, ts=timestamp, tid=task_id: 
                            self.build_apk(pn, org, ts, tid),
                    )
                )
            # Show download button when APK is built
            elif apk_build_status == APK_STATUS_BUILDED and apk_path:
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        tooltip="Download APK",
                        on_click=lambda e, path=apk_path: self.show_apk_info(path),
                    )
                )
        
        # Create status badges
        status_badges = [
            ft.Container(
                content=ft.Text(
                    status,
                    size=10,  # Reduced font size (approximately 50% smaller)
                ),
                bgcolor=status_color,
                padding=2.5,  # Reduced padding by 50%
                border_radius=3,  # Reduced border radius for better proportions
            )
        ]

        # Add APK build status badge if available
        if apk_build_status and apk_status_color:
            status_badges.append(
                ft.Container(
                    content=ft.Text(
                        f"APK: {apk_build_status}",
                        size=10,  # Reduced font size
                    ),
                    bgcolor=apk_status_color,
                    padding=2.5,  # Reduced padding by 50%
                    border_radius=3,  # Reduced border radius
                    margin=ft.margin.only(left=3),  # Reduced margin as well
                )
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(f"#{task_id}: {project_name}", weight=ft.FontWeight.BOLD),
                                ft.Row(status_badges),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(f"Created: {created_at}"),
                        # Show APK path if available
                        ft.Text(
                            f"APK: {apk_path}" if apk_path else "",
                            visible=bool(apk_path),
                            style=ft.TextStyle(
                                italic=True,
                                size=12,
                            ),
                        ),
                        ft.Row(
                            actions,
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                ),
                padding=10,
            ),
        )
    
    def update_pagination(self):
        """Update pagination controls"""
        current_page = (self.offset // self.limit) + 1
        total_pages = (self.total_tasks + self.limit - 1) // self.limit
        
        self.pagination.controls[1].value = f"Page {current_page} of {total_pages}"
        
        # Update button states
        self.pagination.controls[0].disabled = current_page <= 1
        self.pagination.controls[2].disabled = current_page >= total_pages
        
        self.page.update()
    
    def change_status_filter(self, e):
        """Change status filter"""
        selected = e.control.value
        self.status_filter = None if selected == "All" else selected
        self.offset = 0  # Reset to first page
        self.fetch_tasks()
    
    def prev_page(self, e):
        """Go to previous page"""
        if self.offset >= self.limit:
            self.offset -= self.limit
            self.fetch_tasks()
    
    def next_page(self, e):
        """Go to next page"""
        if self.offset + self.limit < self.total_tasks:
            self.offset += self.limit
            self.fetch_tasks()
    
    def cancel_task(self, task_id):
        """Cancel a task"""
        try:
            result = self.api_client.cancel_task(task_id)
            
            if result.get("status") == TASK_STATUS_CANCELLED:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Task #{task_id} cancelled successfully"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
                self.fetch_tasks()
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to cancel task: {result.get('message', 'Unknown error')}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        
        self.page.update()
    
    def delete_task(self, task_id):
        """Delete a task"""
        try:
            result = self.api_client.delete_task(task_id)
            
            # The delete API returns a message field, not a success field
            # Check for a message that indicates success
            if "deleted successfully" in result.get("message", ""):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Task #{task_id} deleted successfully"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
                self.fetch_tasks()
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to delete task: {result.get('message', 'Unknown error')}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                action="Dismiss",
            )
            self.page.snack_bar.open = True
        
        self.page.update()
    
    def build_apk(self, project_name, organization, timestamp, task_id=None):
        """Build APK for a task"""
        self.loading.visible = True
        self.page.update()
        
        try:
            # Validate project name before sending request
            if not project_name or project_name == "Unknown":
                raise ValueError("Invalid project name")
                
            result = self.api_client.build_apk(
                project_name=project_name,
                organization=organization,
                timestamp=timestamp,
                task_id=task_id,
            )
            
            if result.get("success", False):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"APK build initiated successfully"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
                # Refresh the task list to show updated status
                self.fetch_tasks()
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