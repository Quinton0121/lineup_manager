import flet as ft
from components import create_progress_bar
from config import get_checkin_data, update_config_npg, get_init_time, update_config_init_time
from utils import excel_to_datetime, read_google_sheet
import json
import pandas as pd
import re
import webbrowser
import os

def first_page(page, url_input, result_text, submit_button, next_page_button, data_list_view):
    print("Rendering first page...")
    return ft.Column(
        [
            ft.Text("Google Sheet Reader", size=20, weight="bold"),
            url_input,
            submit_button,
            result_text,
            ft.Container(
                content=data_list_view,
                width=500,
                height=300,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10,
            ),
            next_page_button,
        ],
        alignment="center"
    )

def update_checked_in_number(data, df=None):
    print("Updating checked-in number from Google Sheet...")
    if df is None:
        df = read_google_sheet("https://docs.google.com/spreadsheets/d/1YoOGKltmbHjstO6RIRQeZ3eA1A-YoexhyW7oyvolohg/edit?gid=1519050975#gid=1519050975")
    if isinstance(df, str):
        print(f"Failed to fetch sheet: {df}")
        return 0, None
    
    checked_in_count = len(df[df["Checked In"].isin([True, "Yes", 1, "TRUE"])])
    print(f"Found {checked_in_count} checked-in people")
    
    with open("config.json", "r") as f:
        config = json.load(f)
    config["number_of_checked_in"] = checked_in_count
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    return checked_in_count, df

def get_next_lineup(df, npg, interviewed):
    print(f"Fetching next lineup with npg={npg}...")
    available = df[(df["Checked In"].isin([True, "Yes", 1, "TRUE"])) & (~df["No"].isin(interviewed))].sort_values("timevalue")
    next_group = available.head(npg)
    if len(next_group) < npg:
        print(f"Warning: Only {len(next_group)} available, less than npg={npg}")
    return next_group[["No", "中文姓名", "timevalue"]].to_dict('records')

def write_html():
    print("Writing HTML file...")
    with open('config.json', 'r') as f:
        config = json.load(f)

    temp_number = ["000", "000", "000", "000", "000", "000"]
    number_on_card1, number_on_card2, number_on_card3, number_on_card4, number_on_card5, number_on_card6 = temp_number

    current_group = [str(person["No"]) for person in config["current_lineup"]]
    group_len = len(current_group)
    card_num = current_group + ["000"] * (6 - group_len)

    with open('index.html', 'r', encoding='utf-8') as f:
        html_string = f.read()

    html_string = re.sub(r'id="Qoos1">[0-9]*</h1>', f'id="Qoos1">{number_on_card1}</h1>', html_string)
    html_string = re.sub(r'id="Qoos2">[0-9]*</h1>', f'id="Qoos2">{card_num[0]}</h1>', html_string)
    html_string = re.sub(r'id="Qoos3">[0-9]*</h1>', f'id="Qoos3">{number_on_card2}</h1>', html_string)
    html_string = re.sub(r'id="Qoos4">[0-9]*</h1>', f'id="Qoos4">{card_num[1]}</h1>', html_string)
    html_string = re.sub(r'id="Qoos5">[0-9]*</h1>', f'id="Qoos5">{number_on_card3}</h1>', html_string)
    html_string = re.sub(r'id="Qoos6">[0-9]*</h1>', f'id="Qoos6">{card_num[2]}</h1>', html_string)
    html_string = re.sub(r'id="Qoos7">[0-9]*</h1>', f'id="Qoos7">{number_on_card4}</h1>', html_string)
    html_string = re.sub(r'id="Qoos8">[0-9]*</h1>', f'id="Qoos8">{card_num[3]}</h1>', html_string)
    html_string = re.sub(r'id="Qoos9">[0-9]*</h1>', f'id="Qoos9">{number_on_card5}</h1>', html_string)
    html_string = re.sub(r'id="Qoos10">[0-9]*</h1>', f'id="Qoos10">{card_num[4]}</h1>', html_string)
    html_string = re.sub(r'id="Qoos11">[0-9]*</h1>', f'id="Qoos11">{number_on_card6}</h1>', html_string)
    html_string = re.sub(r'id="Qoos12">[0-9]*</h1>', f'id="Qoos12">{card_num[5]}</h1>', html_string)
    html_string = html_string.replace('#ee6b6e;color: black;', 'QoosColor1')
    html_string = html_string.replace('#2980b9;color: white;', 'QoosColor2')
    html_string = html_string.replace('QoosColor2', '#ee6b6e;color: black;')
    html_string = html_string.replace('QoosColor1', '#2980b9;color: white;')

    with open("index.html", "w", encoding='utf-8') as file:
        file.write(html_string)
    print("HTML file updated")

def open_html(e):
    print("Opening HTML file...")
    filename = 'file://' + os.getcwd() + '/index.html'
    webbrowser.open(filename, new=0, autoraise=True)
    print("HTML file opened")

def second_page(page, data=None, url_input=None, result_text=None, submit_button=None, next_page_button=None, data_list_view=None):
    print("Rendering second page...")
    total_interviews, checked_in, npg = get_checkin_data()
    
    checked_in, df = update_checked_in_number(data)
    total_interviews = 826
    
    init_time_serial = get_init_time()
    init_time_display = excel_to_datetime(init_time_serial) if init_time_serial else "Not Set"
    data_text = ft.Text("No Google Sheet data available") if data is None or data.empty else ft.Text(f"Loaded {len(data)} rows from Google Sheet")

    with open("config.json", "r") as f:
        config = json.load(f)
    interviewed = config.get("interviewed", [])
    current_lineup = config.get("current_lineup", [])
    lineup_history = config.get("lineup_history", [])
    group_number = len(lineup_history)

    progress_container = ft.Container(
        content=ft.Column(
            [ft.Text("Check-in Status", size=20, weight="bold"), create_progress_bar(total_interviews, checked_in)],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=10,
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=5,
        width=page.width / 3,
        alignment=ft.alignment.center,
    )

    current_lineup_display = ft.Column(
        [ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}") for person in current_lineup] if current_lineup else [ft.Text("No current lineup")],
        spacing=5
    )

    def on_lineup_click(e):
        print("Lineup button clicked...")
        with open("config.json", "r") as f:
            config = json.load(f)
        current_npg = config["npg"]
        print(f"Using npg={current_npg} for lineup")

        new_checked_in, df = update_checked_in_number(data)
        if isinstance(df, str):
            print(f"Failed to fetch sheet: {df}")
            current_lineup_display.controls = [ft.Text("Failed to fetch lineup", color=ft.colors.RED)]
        else:
            next_group = get_next_lineup(df, current_npg, interviewed)
            if not next_group:
                current_lineup_display.controls = [ft.Text("No more people to line up", color=ft.colors.RED)]
            else:
                group_number = len(config.get("lineup_history", [])) + 1
                current_lineup[:] = next_group
                interviewed.extend([person["No"] for person in next_group])
                lineup_history.append({
                    "group_number": group_number,
                    "people": next_group,
                    "npg": current_npg
                })
                config["current_lineup"] = current_lineup
                config["interviewed"] = interviewed
                config["lineup_history"] = lineup_history
                with open("config.json", "w") as f:
                    json.dump(config, f, indent=4)
                current_lineup_display.controls = [ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}") for person in current_lineup]
                progress_container.content = ft.Column(
                    [ft.Text("Check-in Status", size=20, weight="bold"), create_progress_bar(total_interviews, new_checked_in)],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                print(f"Group #{group_number} added to history: {[person['No'] for person in next_group]}")
                write_html()
        page.update()

    return ft.Column(
        [
            ft.Row(
                [
                    progress_container,
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
                                            on_change=lambda e: [update_config_npg(e.control.value), e.control.parent.controls[1].__setattr__('value', str(int(e.control.value))), page.update()],
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
                        current_lineup_display,
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
                            on_click=open_html,
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