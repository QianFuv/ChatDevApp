import flet as ft
from datetime import datetime

def main(page: ft.Page):
    # 配置主题
    page.title = "ChatDevApp"
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
        font_family="HYXuanSong45S"
    )
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.fonts = {"HYXuanSong45S": "fonts/HYXuanSong45S.ttf"}
    page.bgcolor = ft.Colors.SURFACE

    # 创建应用卡片函数
    def create_app_card(app_name: str, app_size: str, build_time: datetime, download_url: str):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(app_name,
                                   size=16,
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.Colors.ON_SURFACE),
                            ft.Row(
                                controls=[
                                    ft.Text(f"大小：{app_size}",
                                           size=12,
                                           color=ft.Colors.ON_SURFACE_VARIANT),
                                    ft.Text("-", color=ft.Colors.OUTLINE),
                                    ft.Text(f"构建：{build_time.strftime('%Y-%m-%d %H:%M')}",
                                           size=12,
                                           color=ft.Colors.ON_SURFACE_VARIANT)
                                ],
                                spacing=10
                            )
                        ],
                        expand=True
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        icon_color=ft.Colors.PRIMARY,
                        tooltip="Download",
                        url=download_url,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=20,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=12,
            margin=ft.margin.only(bottom=10),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
        )

    # 示例应用列表
    apps = [
        create_app_card("Chat App", "2.3 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Todo List", "1.5 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Calculator", "0.8 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Chat App", "2.3 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Todo List", "1.5 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Calculator", "0.8 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Chat App", "2.3 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Todo List", "1.5 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Calculator", "0.8 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Chat App", "2.3 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Todo List", "1.5 MB", datetime.now(), "https://example.com/download/myapp"),
        create_app_card("Calculator", "0.8 MB", datetime.now(), "https://example.com/download/myapp"),
    ]

    # 列表页面布局
    list_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("应用列表",
                       size=28,
                       weight=ft.FontWeight.BOLD,
                       color=ft.Colors.ON_SURFACE),
                ft.ListView(
                    controls=apps,
                    spacing=0,
                    padding=20,
                    expand=True
                )
            ],
            spacing=20,
            expand=True,
        ),
        padding=ft.padding.only(top=50),
        expand=True,
        visible=False
    )

    # 生成页面布局
    generate_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("ChatDev for APP",
                       size=32,
                       weight=ft.FontWeight.BOLD,
                       color=ft.Colors.ON_SURFACE),
                ft.TextField(
                    width=400,
                    multiline=False,
                    text_align=ft.TextAlign.LEFT,
                    border_color=ft.Colors.OUTLINE,
                    border_width=2,
                    hint_text="在此填写您的提示词......",
                    hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
                    text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
                    cursor_color=ft.Colors.PRIMARY,
                ),
                ft.ElevatedButton(
                    text="生成",
                    width=200,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY,
                        elevation=1,
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=8)
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            expand=True
        ),
        alignment=ft.alignment.center,
        expand=True,
        visible=True
    )

    # 设置页面布局
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
                            ft.TextField(
                                expand=True,
                                multiline=False,
                                text_align=ft.TextAlign.LEFT,
                                border_color=ft.Colors.OUTLINE,
                                border_width=2,
                                hint_text="请输入服务器地址，如：http://localhost:8000",
                                hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
                                text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
                            ),
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
                            ft.TextField(
                                expand=True,
                                multiline=False,
                                text_align=ft.TextAlign.LEFT,
                                hint_text="请输入您的 OpenAI API 密钥",
                                border_color=ft.Colors.OUTLINE,
                                border_width=2,
                                password=True,
                                hint_style=ft.TextStyle(color=ft.Colors.ON_SURFACE_VARIANT),
                                text_style=ft.TextStyle(color=ft.Colors.ON_SURFACE),
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        text="保存设置",
                        width=200,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.ON_PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        )
                    ),
                    padding=ft.padding.only(top=20),
                    alignment=ft.alignment.center
                ),
            ],
            spacing=20,
            expand=True,
        ),
        padding=ft.padding.only(top=50),
        expand=True,
        visible=False
    )

    def navigation_change(e):
        list_view.visible = e.control.selected_index == 0
        generate_view.visible = e.control.selected_index == 1
        settings_view.visible = e.control.selected_index == 2
        page.update()

    # 导航栏
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

    page.add(
        list_view,
        generate_view,
        settings_view,
        navigation_bar
    )

ft.app(main)