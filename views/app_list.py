import flet as ft
from api_client import APIClient
from utils.constants import (
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_CANCELLED,
)

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
        )
        
        self.loading = ft.ProgressRing(visible=False)
    
    def build(self):
        """Build and return the view"""
        view = ft.Column(
            [
                ft.Container(
                    content=ft.Text("App List", size=24, weight=ft.FontWeight.BOLD),
                    padding=10,
                ),
                ft.Row(
                    [
                        self.status_dropdown,
                        self.refresh_button,
                        self.loading,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.tasks_list,
                self.pagination,
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
        status = task.get("status", "Unknown")
        status_color = {
            TASK_STATUS_PENDING: ft.Colors.ORANGE,
            TASK_STATUS_RUNNING: ft.Colors.BLUE,
            TASK_STATUS_COMPLETED: ft.Colors.GREEN,
            TASK_STATUS_FAILED: ft.Colors.RED,
            TASK_STATUS_CANCELLED: ft.Colors.GREY,
        }.get(status, ft.Colors.GREY)
        
        task_id = task.get("task_id", 0)
        
        # Extract name from result_path if available
        result_path = task.get("result_path", "")
        name = "Unknown"
        
        if result_path:
            # Parse result_path to extract project name
            try:
                # Expected format: "WareHouse/ProjectName_Organization_Timestamp"
                parts = result_path.split('/')
                if len(parts) >= 2:
                    # Get the last part and split by underscore
                    name_parts = parts[-1].split('_')
                    if name_parts:
                        name = name_parts[0]
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
        
        # Build APK button for completed tasks
        if status == TASK_STATUS_COMPLETED:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.BUILD,
                    tooltip="Build APK",
                    on_click=lambda e, task=task: self.build_apk(task),
                )
            )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(f"#{task_id}: {name}", weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text(status),
                                    bgcolor=status_color,
                                    padding=5,
                                    border_radius=5,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(f"Created: {created_at}"),
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
    
    def build_apk(self, task):
        """Build APK for a task"""
        project_name = task.get("name", "")
        organization = task.get("org", "DefaultOrganization")
        timestamp = task.get("created_at", "").split(" ")[0]  # Extract date part
        
        try:
            result = self.api_client.build_apk(
                project_name=project_name,
                organization=organization,
                timestamp=timestamp,
            )
            
            if result.get("success", False):
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"APK built successfully: {result.get('apk_path', '')}"),
                    action="Dismiss",
                )
                self.page.snack_bar.open = True
            else:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Failed to build APK: {result.get('message', 'Unknown error')}"),
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