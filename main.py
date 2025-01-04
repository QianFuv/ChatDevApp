import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "ChatDevApp"

    page.fonts = {
        "HYXuanSong45S": "fonts/HYXuanSong45S.ttf"
    }

    page.theme = ft.Theme(font_family="HYXuanSong45S")

    # 创建应用卡片函数
    def create_app_card(app_name: str, app_size: str, build_time: datetime):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(app_name, size=16, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            ft.Text(f"Size: {app_size}"),
                            ft.Text("•"),
                            ft.Text(f"Built: {build_time.strftime('%Y-%m-%d %H:%M')}")
                        ],
                        spacing=10
                    )
                ]
            ),
            padding=20,
            border=ft.border.all(2, ft.Colors.OUTLINE),
            border_radius=8,
            margin=ft.margin.only(bottom=10)
        )

    # 示例应用列表
    apps = [
        create_app_card("Chat App", "2.3 MB", datetime.now()),
        create_app_card("Todo List", "1.5 MB", datetime.now()),
        create_app_card("Calculator", "0.8 MB", datetime.now()),
        create_app_card("Chat App", "2.3 MB", datetime.now()),
        create_app_card("Todo List", "1.5 MB", datetime.now()),
        create_app_card("Calculator", "0.8 MB", datetime.now()),
        create_app_card("Chat App", "2.3 MB", datetime.now()),
        create_app_card("Todo List", "1.5 MB", datetime.now()),
        create_app_card("Calculator", "0.8 MB", datetime.now()),
        create_app_card("Chat App", "2.3 MB", datetime.now()),
        create_app_card("Todo List", "1.5 MB", datetime.now()),
        create_app_card("Calculator", "0.8 MB", datetime.now())
    ]

    # “列表”页面布局
    list_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("应用列表", size=28, weight=ft.FontWeight.BOLD),
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

    # "生成"页面布局
    generate_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("ChatDev for APP", size=32, weight=ft.FontWeight.BOLD),
                ft.TextField(
                    width=400,
                    multiline=False,
                    text_align=ft.TextAlign.LEFT,
                    border_color = ft.Colors.OUTLINE,
                    border_width = 2,
                    hint_text="在此填写您的提示词......",
                ),
                ft.ElevatedButton(
                    text="生成",
                    width=200,
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

    # "设置"页面布局
    settings_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("设置", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("服务器地址", size=16, weight=ft.FontWeight.W_500),
                            ft.TextField(
                                expand=True,
                                multiline=False,
                                text_align=ft.TextAlign.LEFT,
                                border_color=ft.Colors.OUTLINE,
                                border_width=2,
                                hint_text="请输入服务器地址，如：http://localhost:8000"
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.only(left=20, right=20),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("API密钥", size=16, weight=ft.FontWeight.W_500),
                            ft.TextField(
                                expand=True,
                                multiline=False,
                                text_align=ft.TextAlign.LEFT,
                                hint_text="请输入您的 OpenAI API 密钥",
                                border_color=ft.Colors.OUTLINE,
                                border_width=2,
                                password=True  # 密码模式，显示为星号
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.only(left=20, right=20),
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        text="保存设置",
                        width=200,
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
            ft.NavigationBarDestination(icon=ft.Icons.LIST, label="列表"),
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="生成"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="设置"),
        ],
        selected_index=1,
        on_change=navigation_change
    )

    # 添加所有视图到页面
    page.add(
        list_view,
        generate_view,
        settings_view,
        navigation_bar
    )

ft.app(main)