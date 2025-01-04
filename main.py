import flet as ft

def main(page: ft.Page):
    page.title = "ChatDevApp"

    # “列表”页面布局
    list_view = ft.Container(visible=False)

    # “生成”页面布局
    generate_view = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("ChatDev for APP", size=32, weight=ft.FontWeight.BOLD),
                ft.TextField(
                    width=400,
                    multiline=False,
                    text_align=ft.TextAlign.LEFT,
                    hint_text="在此填写您的提示词......"
                ),
                ft.ElevatedButton(
                    text="生成",
                    width=200,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        padding=ft.padding.only(top=100)
    )

    # “设置”页面布局
    settings_view = ft.Container(visible=False)

    # 页面切换
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

    # 调用页面
    page.add(
        list_view,
        generate_view,
        settings_view,
        navigation_bar
    )

ft.app(main)