import flet as ft
import json
import os
import time
import requests
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

# Constants
APP_TITLE = "ChatDevApp"
DEFAULT_API_URL = "http://localhost:8000/api/v1"
SETTINGS_FILE = "settings.json"

class APIClient:
    """
    Client for communicating with the ChatDev API
    """
    def __init__(self, base_url: str = DEFAULT_API_URL, api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        
    def set_api_key(self, api_key: str):
        """Set the API key for authentication"""
        self.api_key = api_key
        
    def set_base_url(self, base_url: str):
        """Set the base URL for the API"""
        if base_url and not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
    
    def _get_auth_data(self) -> dict:
        """Get authentication data for API requests"""
        return {"api_key": self.api_key}
    
    def get_tasks(self) -> dict:
        """Get all tasks from the API"""
        try:
            response = requests.get(
                f"{self.base_url}tasks", 
                headers=self.headers,
                params=self._get_auth_data()
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get tasks: {str(e)}")
    
    def get_task_status(self, task_id: int) -> dict:
        """Get the status of a task"""
        try:
            response = requests.get(
                f"{self.base_url}status/{task_id}", 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get task status: {str(e)}")
    
    def create_task(self, task: str, name: str, config: str = "Default", 
                    org: str = "DefaultOrganization", 
                    model: str = "CLAUDE_3_5_SONNET",
                    build_apk: bool = True) -> dict:
        """Create a new task"""
        data = {
            "api_key": self.api_key,
            "task": task,
            "name": name,
            "config": config,
            "org": org,
            "model": model,
            "build_apk": build_apk
        }
        
        try:
            response = requests.post(
                f"{self.base_url}generate", 
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to create task: {str(e)}")

class SettingsManager:
    """
    Manager for app settings
    """
    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self) -> dict:
        """Load settings from file"""
        default_settings = {
            "api_url": DEFAULT_API_URL,
            "api_key": "",
            "theme_mode": "system"
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                    # Update with any missing default settings
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except:
                pass
        
        return default_settings
    
    def save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f)
    
    def get_setting(self, key: str, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save_settings()

def main(page: ft.Page):
    # Initialize settings and API client
    settings_manager = SettingsManager()
    api_client = APIClient(
        base_url=settings_manager.get_setting("api_url"),
        api_key=settings_manager.get_setting("api_key")
    )
    
    # Configure page theme
    page.title = APP_TITLE
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
        font_family="HYXuanSong45S"
    )
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.fonts = {"HYXuanSong45S": "fonts/HYXuanSong45S.ttf"}
    page.bgcolor = ft.Colors.SURFACE
    
    # Task tracking variables
    current_task_id = None
    task_status_timer = None
    
    # Create a snackbar for messages
    def show_message(message: str, color: str = "primary"):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=getattr(ft.Colors, color.upper()) if hasattr(ft.Colors, color.upper()) else ft.Colors.PRIMARY
        )
        page.snack_bar.open = True
        page.update()
    
    # Function to create app card
    def create_app_card(task: dict) -> ft.Container:
        # Extract app info from task
        app_name = task.get("request_data", {}).get("name", "Unknown App")
        status = task.get("status", "UNKNOWN")
        created_at = datetime.fromisoformat(task.get("created_at", datetime.now().isoformat()))
        
        # Determine color based on status
        status_colors = {
            "COMPLETED": ft.colors.GREEN,
            "FAILED": ft.colors.RED,
            "RUNNING": ft.colors.BLUE,
            "PENDING": ft.colors.ORANGE,
        }
        status_color = status_colors.get(status, ft.colors.GREY)
        
        # Create download URL if available
        apk_path = task.get("apk_path")
        download_url = f"{api_client.base_url}download?path={apk_path}" if apk_path else None
        
        # Create tooltip text based on status
        tooltip = "Download APK" if status == "COMPLETED" and apk_path else "View Details"
        
        # Create action button based on status
        action_button = ft.IconButton(
            icon=ft.icons.DOWNLOAD if status == "COMPLETED" and apk_path else ft.icons.INFO,
            icon_color=ft.Colors.PRIMARY,
            tooltip=tooltip,
            url=download_url,
            on_click=lambda e, task_id=task.get("task_id"): view_task_details(task_id) if not download_url else None
        )
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                app_name,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_SURFACE
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            status,
                                            size=12,
                                            color=ft.colors.WHITE
                                        ),
                                        bgcolor=status_color,
                                        border_radius=4,
                                        padding=4
                                    ),
                                    ft.Text("-", color=ft.Colors.OUTLINE),
                                    ft.Text(
                                        f"创建: {created_at.strftime('%Y-%m-%d %H:%M')}",
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT
                                    )
                                ],
                                spacing=10
                            )
                        ],
                        expand=True
                    ),
                    action_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=20,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=12,
            margin=ft.margin.only(bottom=10),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
        )
    
    # View task details
    def view_task_details(task_id: int):
        try:
            task = api_client.get_task_status(task_id)
            task_dialog.title = ft.Text(f"任务 #{task_id} 详情")
            
            # Create content based on task data
            status = task.get("status", "UNKNOWN")
            created_at = datetime.fromisoformat(task.get("created_at", datetime.now().isoformat()))
            updated_at = datetime.fromisoformat(task.get("updated_at", datetime.now().isoformat()))
            
            details = [
                ft.Text(f"状态: {status}", size=16),
                ft.Text(f"创建时间: {created_at.strftime('%Y-%m-%d %H:%M:%S')}", size=14),
                ft.Text(f"更新时间: {updated_at.strftime('%Y-%m-%d %H:%M:%S')}", size=14),
            ]
            
            # Add result path if available
            if task.get("result_path"):
                details.append(ft.Text(f"结果路径: {task.get('result_path')}", size=14))
            
            # Add APK path if available
            if task.get("apk_path"):
                details.append(ft.Text(f"APK路径: {task.get('apk_path')}", size=14))
                details.append(
                    ft.ElevatedButton(
                        "下载APK",
                        icon=ft.icons.DOWNLOAD,
                        url=f"{api_client.base_url}download?path={task.get('apk_path')}"
                    )
                )
            
            # Add error message if failed
            if status == "FAILED" and task.get("error_message"):
                details.append(ft.Text("错误信息:", size=16, weight=ft.FontWeight.BOLD))
                details.append(
                    ft.Container(
                        content=ft.Text(task.get("error_message"), size=14),
                        bgcolor=ft.colors.ERROR_CONTAINER,
                        border_radius=8,
                        padding=10,
                        width=400
                    )
                )
            
            # Update dialog content
            task_dialog.content = ft.Column(controls=details, spacing=10, scroll=ft.ScrollMode.AUTO)
            task_dialog.open = True
            page.update()
            
        except Exception as e:
            show_message(f"获取任务详情失败: {str(e)}", "error")
    
    # Create task dialog
    task_dialog = ft.AlertDialog(
        title=ft.Text("任务详情"),
        content=ft.Text("加载中..."),
        actions=[
            ft.TextButton("关闭", on_click=lambda e: setattr(task_dialog, "open", False))
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    
    # Function to refresh app list
    def refresh_app_list():
        try:
            # Show loading indicator
            list_loading.visible = True
            list_view_content.visible = False
            page.update()
            
            # Get tasks from API
            response = api_client.get_tasks()
            tasks = response.get("tasks", [])
            
            # Clear existing app cards
            app_list.controls.clear()
            
            # Add new app cards
            for task in tasks:
                app_list.controls.append(create_app_card(task))
            
            # Hide loading indicator
            list_loading.visible = False
            list_view_content.visible = True
            page.update()
            
        except Exception as e:
            list_loading.visible = False
            list_view_content.visible = True
            show_message(f"刷新应用列表失败: {str(e)}", "error")
            page.update()
    
    # List view loading indicator
    list_loading = ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(),
                ft.Text("正在加载应用列表...", size=16)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.alignment.center,
        expand=True,
        visible=False
    )
    
    # App list
    app_list = ft.ListView(
        spacing=0,
        padding=20,
        expand=True
    )
    
    # List view content
    list_view_content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("应用列表",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE
                    ),
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        tooltip="刷新",
                        on_click=lambda e: refresh_app_list()
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            app_list
        ],
        spacing=20,
        expand=True,
    )
    
    # List view
    list_view = ft.Container(
        content=ft.Stack(
            controls=[
                list_view_content,
                list_loading
            ]
        ),
        padding=ft.padding.only(top=50, left=20, right=20),
        expand=True,
        visible=False
    )
    
    # Function to start polling task status
    def start_task_polling(task_id: int):
        def poll_task_status():
            nonlocal task_status_timer
            
            try:
                task = api_client.get_task_status(task_id)
                status = task.get("status")
                
                # Update progress indicator and status text
                generate_progress.visible = status in ["PENDING", "RUNNING"]
                generate_status_text.value = f"状态: {status}"
                
                if status == "COMPLETED":
                    generate_status_container.bgcolor = ft.colors.GREEN_100
                    generate_progress.visible = False
                    generate_status_text.value = "生成完成！"
                    generate_view_button.visible = True
                    generate_button.text = "重新生成"
                    generate_button.disabled = False
                    
                    # Stop polling
                    if task_status_timer:
                        task_status_timer.cancel()
                        task_status_timer = None
                
                elif status == "FAILED":
                    generate_status_container.bgcolor = ft.colors.RED_100
                    generate_progress.visible = False
                    generate_status_text.value = f"生成失败: {task.get('error_message', '未知错误')}"
                    generate_button.text = "重试"
                    generate_button.disabled = False
                    
                    # Stop polling
                    if task_status_timer:
                        task_status_timer.cancel()
                        task_status_timer = None
                
                # Continue polling if still in progress
                elif status in ["PENDING", "RUNNING"]:
                    # Schedule next poll
                    task_status_timer = threading.Timer(5.0, poll_task_status)
                    task_status_timer.daemon = True
                    task_status_timer.start()
                
                page.update()
                
            except Exception as e:
                generate_status_container.bgcolor = ft.colors.RED_100
                generate_progress.visible = False
                generate_status_text.value = f"状态更新失败: {str(e)}"
                generate_button.text = "重试"
                generate_button.disabled = False
                page.update()
                
                # Stop polling on error
                if task_status_timer:
                    task_status_timer.cancel()
                    task_status_timer = None
        
        # Start initial polling
        poll_task_status()
    
    # Function to handle generate button click
    def on_generate_click(e):
        nonlocal current_task_id
        
        # Get prompt and check if empty
        prompt = prompt_field.value.strip()
        name = project_name_field.value.strip()
        
        if not prompt:
            show_message("请输入提示词", "error")
            return
        
        if not name:
            # Extract a name from the prompt if not provided
            words = prompt.split()
            name = "".join([word.capitalize() for word in words[:2] if len(word) > 2])
            if not name:
                name = "App" + str(int(time.time()))
            project_name_field.value = name
        
        try:
            # Validate settings
            if not api_client.api_key:
                show_message("请先在设置中配置API密钥", "error")
                navigation_bar.selected_index = 2  # Switch to settings view
                page.update()
                return
            
            # Disable button and show progress
            generate_button.disabled = True
            generate_button.text = "生成中..."
            generate_progress.visible = True
            generate_status_container.visible = True
            generate_status_container.bgcolor = ft.colors.BLUE_100
            generate_status_text.value = "正在提交任务..."
            generate_view_button.visible = False
            page.update()
            
            # Create task
            response = api_client.create_task(
                task=prompt,
                name=name,
                model=model_dropdown.value,
                build_apk=build_apk_switch.value
            )
            
            # Get task ID and start polling
            current_task_id = response.get("task_id")
            generate_status_text.value = f"状态: 任务已提交 (ID: {current_task_id})"
            page.update()
            
            # Start polling task status
            start_task_polling(current_task_id)
            
        except Exception as e:
            generate_button.disabled = False
            generate_button.text = "生成"
            generate_progress.visible = False
            generate_status_container.bgcolor = ft.colors.RED_100
            generate_status_text.value = f"提交失败: {str(e)}"
            page.update()
    
    # Function to view current task details
    def view_current_task(e):
        if current_task_id:
            view_task_details(current_task_id)
    
    # Generate view progress indicator
    generate_progress = ft.ProgressRing(visible=False)
    
    # Generate view status text
    generate_status_text = ft.Text("", size=14)
    
    # Generate view status container
    generate_status_container = ft.Container(
        content=ft.Row(
            controls=[
                generate_progress,
                generate_status_text
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        padding=10,
        border_radius=8,
        visible=False,
        bgcolor=ft.colors.BLUE_100
    )
    
    # Generate view button
    generate_view_button = ft.ElevatedButton(
        text="查看详情",
        icon=ft.icons.VISIBILITY,
        on_click=view_current_task,
        visible=False
    )
    
    # Available models
    models = [
        "GPT_3_5_TURBO",
        "GPT_4",
        "GPT_4_TURBO",
        "GPT_4O",
        "GPT_4O_MINI",
        "CLAUDE_3_5_SONNET",
        "DEEPSEEK_R1"
    ]
    
    # Model dropdown
    model_dropdown = ft.Dropdown(
        width=400,
        options=[ft.dropdown.Option(model) for model in models],
        value="CLAUDE_3_5_SONNET",
        label="模型选择",
        hint_text="选择生成模型",
        border_color=ft.Colors.OUTLINE,
        border_width=2,
        text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
        hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT)
    )
    
    # Build APK switch
    build_apk_switch = ft.Switch(
        label="生成APK",
        value=True,
        label_position=ft.LabelPosition.LEFT
    )
    
    # Project name field
    project_name_field = ft.TextField(
        width=400,
        multiline=False,
        text_align=ft.TextAlign.LEFT,
        border_color=ft.Colors.OUTLINE,
        border_width=2,
        label="项目名称",
        hint_text="输入项目名称",
        hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
        text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
        cursor_color=ft.Colors.PRIMARY,
    )
    
    # Prompt field
    prompt_field = ft.TextField(
        width=400,
        multiline=True,
        min_lines=3,
        max_lines=5,
        text_align=ft.TextAlign.LEFT,
        border_color=ft.Colors.OUTLINE,
        border_width=2,
        label="提示词",
        hint_text="在此填写您的提示词......",
        hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
        text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
        cursor_color=ft.Colors.PRIMARY,
    )
    
    # Generate button
    generate_button = ft.ElevatedButton(
        text="生成",
        width=200,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
            elevation=1,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8)
        ),
        on_click=on_generate_click
    )
    
    # Generate view
    generate_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("ChatDev for APP",
                       size=32,
                       weight=ft.FontWeight.BOLD,
                       color=ft.Colors.ON_SURFACE),
                project_name_field,
                prompt_field,
                ft.Row(
                    controls=[
                        model_dropdown,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    controls=[
                        build_apk_switch,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                generate_button,
                generate_status_container,
                generate_view_button
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            expand=True
        ),
        padding=ft.padding.only(top=50, left=20, right=20),
        expand=True,
        visible=True
    )
    
    # Function to save settings
    def save_settings_click(e):
        try:
            # Get values from fields
            api_url = server_field.value.strip()
            api_key = api_key_field.value.strip()
            
            # Validate
            if not api_url:
                show_message("服务器地址不能为空", "error")
                return
            
            if not api_key:
                show_message("API密钥不能为空", "error")
                return
            
            # Update settings
            api_client.set_base_url(api_url)
            api_client.set_api_key(api_key)
            
            # Save to settings manager
            settings_manager.set_setting("api_url", api_url)
            settings_manager.set_setting("api_key", api_key)
            
            show_message("设置已保存")
            
        except Exception as e:
            show_message(f"保存设置失败: {str(e)}", "error")
    
    # Server field
    server_field = ft.TextField(
        expand=True,
        multiline=False,
        text_align=ft.TextAlign.LEFT,
        border_color=ft.Colors.OUTLINE,
        border_width=2,
        label="服务器地址",
        value=settings_manager.get_setting("api_url"),
        hint_text="请输入服务器地址，如：http://localhost:8000/api/v1",
        hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
        text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
    )
    
    # API key field
    api_key_field = ft.TextField(
        expand=True,
        multiline=False,
        text_align=ft.TextAlign.LEFT,
        label="API密钥",
        hint_text="请输入您的 OpenAI API 密钥",
        value=settings_manager.get_setting("api_key"),
        border_color=ft.Colors.OUTLINE,
        border_width=2,
        password=True,
        can_reveal_password=True,
        hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
        text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
    )
    
    # Save settings button
    save_settings_button = ft.ElevatedButton(
        text="保存设置",
        width=200,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.ON_PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=8)
        ),
        on_click=save_settings_click
    )
    
    # Settings view
    settings_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("设置",
                       size=28,
                       weight=ft.FontWeight.BOLD,
                       color=ft.Colors.ON_SURFACE),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("服务器地址",
                                   size=16,
                                   weight=ft.FontWeight.W_500,
                                   color=ft.Colors.ON_SURFACE),
                            server_field,
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("API密钥",
                                   size=16,
                                   weight=ft.FontWeight.W_500,
                                   color=ft.Colors.ON_SURFACE),
                            api_key_field,
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                ft.Container(
                    content=save_settings_button,
                    padding=ft.padding.only(top=20),
                    alignment=ft.alignment.center
                ),
            ],
            spacing=20,
            expand=True,
        ),
        padding=ft.padding.only(top=50, left=20, right=20),
        expand=True,
        visible=False
    )
    
    # Function to handle navigation change
    def navigation_change(e):
        # Update view visibility
        list_view.visible = e.control.selected_index == 0
        generate_view.visible = e.control.selected_index == 1
        settings_view.visible = e.control.selected_index == 2
        
        # Refresh app list when switching to list view
        if e.control.selected_index == 0:
            refresh_app_list()
            
        page.update()
    
    # Navigation bar
    navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.LIST_ALT_OUTLINED,
                selected_icon=ft.Icons.LIST_ALT,
                label="列表"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="生成"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="设置"
            ),
        ],
        selected_index=1,
        on_change=navigation_change,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        indicator_color=ft.Colors.PRIMARY_CONTAINER,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        height=70,
        shadow_color=ft.Colors.SHADOW,
        surface_tint_color=ft.Colors.PRIMARY
    )
    
    # Add views to page
    page.add(
        list_view,
        generate_view,
        settings_view,
        navigation_bar,
        task_dialog,
    )

ft.app(main)