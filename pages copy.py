import flet as ft
from components import create_progress_bar
from config import get_checkin_data, update_config_npg, get_init_time, update_config_init_time
from utils import excel_to_datetime, read_google_sheet
import json
import pandas as pd
import re
import webbrowser
import os
import shutil  # Added for file backup

# ... (first_page, update_checked_in_number, get_next_lineup, write_html remain unchanged) ...

def second_page(page, data=None, url_input=None, result_text=None, submit_button=None, next_page_button=None, data_list_view=None):
    print("Showing the second page...")
    
    # Get initial data
    total_interviews, checked_in, npg = get_checkin_data()
    checked_in, df = update_checked_in_number(None)  # Refresh checked-in count
    total_interviews = 826  # Fixed total
    
    # Get the start time
    init_time_serial = get_init_time()
    init_time_display = excel_to_datetime(init_time_serial) if init_time_serial else "Not Set"
    
    # Show data status
    data_message = ft.Text("No Google Sheet data available") if data is None or data.empty else ft.Text(f"Loaded {len(data)} rows from Google Sheet")

    # Load config details
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    interviewed = config.get("interviewed", [])  # Who’s been called
    current_lineup = config.get("current_lineup", [])  # Current group
    lineup_history = config.get("lineup_history", [])  # Past groups
    group_number = len(lineup_history)  # How many groups so far

    # Progress bar container
    progress_box = ft.Container(
        content=ft.Column(
            [
                ft.Text("Check-in Status", size=20, weight="bold"),
                create_progress_bar(total_interviews, checked_in)  # Show progress
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=5,
        width=page.width / 3,
        alignment=ft.alignment.center,
    )

    # Display the current lineup
    lineup_display = ft.Column(
        [ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}") for person in current_lineup] if current_lineup else [ft.Text("No current lineup")],
        spacing=5
    )

    # Handle the "Lineup" button click (unchanged)
    def on_lineup_click(event):
        print("You clicked the Lineup button!")
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        current_npg = config["npg"]
        print(f"Fetching {current_npg} people for the lineup...")
        new_checked_in, df = update_checked_in_number(None)
        if isinstance(df, str):
            print(f"Problem fetching data: {df}")
            lineup_display.controls = [ft.Text("Failed to fetch lineup", color=ft.colors.RED)]
        else:
            next_group = get_next_lineup(df, current_npg, interviewed)
            if not next_group:
                lineup_display.controls = [ft.Text("No more people to line up", color=ft.colors.RED)]
            else:
                for person in next_group:
                    person["No"] = int(person["No"])
                group_number = len(config.get("lineup_history", [])) + 1
                current_lineup[:] = next_group
                interviewed.extend([person["No"] for person in next_group])
                config["current_lineup"] = current_lineup
                config["interviewed"] = interviewed
                lineup_history.append({
                    "group_number": group_number,
                    "people": next_group,
                    "npg": current_npg
                })
                config["lineup_history"] = lineup_history
                with open("config.json", "w") as config_file:
                    json.dump(config, config_file, indent=4)
                
                with open('data.json', 'r') as data_file:
                    data = json.load(data_file)
                for person in next_group:
                    data['line'].append(person["No"])
                data['npg'].append(current_npg)
                with open('data.json', 'w') as data_file:
                    json.dump(data, data_file, indent=4)

                lineup_display.controls = [ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}") for person in current_lineup]
                progress_box.content = ft.Column(
                    [ft.Text("Check-in Status", size=20, weight="bold"), create_progress_bar(total_interviews, new_checked_in)],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                print(f"Added Group #{group_number}: {[person['No'] for person in next_group]}")
                write_html()
        page.update()

    # Handle the "Reset" button click
    def on_reset_click(event):
        def confirm_reset(e):
            if e.control.text == "Yes":
                # Backup config.json to backup_config1.json
                shutil.copy("config.json", "backup_config1.json")
                print("Backed up config.json to backup_config1.json")

                # Reset interviewed list and clear lineup-related fields
                with open("config.json", "r") as config_file:
                    config = json.load(config_file)
                config["interviewed"] = []  # Reset interviewed
                config["current_lineup"] = []  # Clear current lineup
                config["lineup_history"] = []  # Clear history
                config["next_group"] = []  # Clear next group
                with open("config.json", "w") as config_file:
                    json.dump(config, config_file, indent=4)
                print("Reset config.json: interviewed, current_lineup, lineup_history, and next_group cleared")

                # Update UI
                lineup_display.controls = [ft.Text("No current lineup")]
                page.update()
            page.dialog.open = False
            page.update()

        # Show confirmation dialog
        page.dialog = ft.AlertDialog(
            title=ft.Text("Reset Confirmation"),
            content=ft.Text("Are you sure you want to reset? This will clear all interviewed data."),
            actions=[
                ft.TextButton("Yes", on_click=confirm_reset),
                ft.TextButton("No", on_click=lambda e: setattr(page.dialog, "open", False) or page.update()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()

    # Layout the second page
    page_layout = ft.Column(
        [
            ft.Row(
                [
                    progress_box,
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Number of people per group", size=16, weight="bold"),
                                ft.Row(
                                    [
                                        ft.Slider(
                                            min=0,
                                            max=6,
                                            value=npg,
                                            on_change=lambda e: [
                                                update_config_npg(e.control.value),
                                                e.control.parent.controls[1].__setattr__('value', str(int(e.control.value))),
                                                page.update()
                                            ],
                                            width=200,
                                        ),
                                        ft.Text(str(npg)),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=10,
                                ),
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        width=page.width / 3,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Start Time", size=16, weight="bold"),
                                ft.TextField(
                                    label="(YYYY-MM-DD HH:MM:SS)",
                                    value=init_time_display,
                                    on_change=lambda e: update_config_init_time(e.control.value),
                                    width=200,
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=10,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        width=page.width / 3,
                        alignment=ft.alignment.center,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Current Lineup", size=16, weight="bold"),
                        lineup_display,
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                width=500,
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Lineup",
                            bgcolor="blue",
                            on_click=on_lineup_click,
                            width=200,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                        ft.ElevatedButton(
                            text="Open HTML",
                            bgcolor="green",
                            on_click=lambda e: webbrowser.open(f"file://{os.getcwd()}/index.html", new=0, autoraise=True),
                            width=200,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                        ft.ElevatedButton(
                            text="Go Back to First Page",
                            bgcolor="red",
                            on_click=lambda e: page.clean() or page.add(first_page(page, url_input, result_text, submit_button, next_page_button, data_list_view)),
                            width=200,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                        ft.ElevatedButton(
                            text="Reset",
                            bgcolor="orange",
                            on_click=on_reset_click,
                            width=200,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                padding=10,
                alignment=ft.alignment.center,
                expand=True,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        expand=True,
    )
    return page_layout