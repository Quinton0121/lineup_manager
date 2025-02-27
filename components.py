import flet as ft
import math

def create_progress_bar(total_interviews, checked_in):
    original_width = 500
    scale_factor = 2.5
    width = original_width / scale_factor
    height = 30
    print(f"Debug - Checked In: {checked_in}, Total Interviews: {total_interviews}")
    proportion = checked_in / total_interviews if total_interviews > 0 else 0
    progress_width = min(proportion * width, width)
    indicator_position = min(progress_width - (2 / scale_factor), width - (4 / scale_factor))
    print(f"Debug - Proportion: {proportion}, Progress Width: {progress_width}, Indicator Position: {indicator_position}")
    blue_bar = ft.Container(
        width=progress_width,
        height=height,
        bgcolor=ft.Colors.BLUE_500,
        border_radius=5 / scale_factor,
    )
    print(f"Debug - Blue Bar Config - Width: {blue_bar.width}, Height: {blue_bar.height}, BGCOLOR: {blue_bar.bgcolor}")
    progress_bar = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Stack(
                        controls=[
                            ft.Row([blue_bar], alignment=ft.MainAxisAlignment.START, spacing=0),
                            ft.Container(
                                content=ft.Text(f"Checked In: {checked_in}/{total_interviews}", size=12, color=ft.Colors.RED_500, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                                width=width,
                                height=height,
                                alignment=ft.alignment.center,
                            ),
                        ],
                    ),
                    width=width,
                    height=height,
                    bgcolor=ft.Colors.GREY_300,
                    border_radius=5 / scale_factor,
                ),
                ft.Stack(
                    controls=[
                        ft.Container(
                            left=indicator_position,
                            content=ft.Container(width=4 / scale_factor, height=height + 10, bgcolor=ft.Colors.RED_500),
                        ),
                    ],
                ),
            ],
            spacing=0,
        ),
        width=width,
        height=height + 10,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )
    print(f"Debug - Outer Container - Width: {progress_bar.width}, Height: {progress_bar.height}, Clip Behavior: {progress_bar.clip_behavior}")
    return progress_bar