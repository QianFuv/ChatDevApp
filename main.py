import flet as ft

def main(page: ft.Page):
    page.title = "ChatDevApp"
    navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.LIST, label="列表"),
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="生成"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS,label="设置"),
        ]
    )
    page.add(navigation_bar)

ft.app(main)