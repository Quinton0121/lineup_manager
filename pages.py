import flet as ft
from components import create_progress_bar
from config import get_checkin_data, update_config_npg, get_init_time, update_config_init_time
from utils import excel_to_datetime, read_google_sheet
import json
import pandas as pd
import re
import webbrowser
import os
import shutil

# Show the first page where users enter the Google Sheet URL
def first_page(page, url_input, result_text, submit_button, next_page_button, data_list_view):
    print("Showing the first page...")
    page_layout = ft.Column(
        [
            ft.Text("Google Sheet Reader", size=20, weight="bold"),  # Title
            url_input,  # Text box for URL
            submit_button,  # Button to submit URL
            result_text,  # Where results will show
            ft.Container(  # Box to display data
                content=data_list_view,
                width=500,
                height=300,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                padding=10,
            ),
            next_page_button,  # Button to go to next page
        ],
        alignment="center"  # Center everything
    )
    return page_layout

# Check how many people have checked in from the Google Sheet
def update_checked_in_number(data, df=None):
    print("Checking how many people checked in...")
    if df is None:  # If no data frame provided, fetch it
        df = read_google_sheet("https://docs.google.com/spreadsheets/d/1YoOGKltmbHjstO6RIRQeZ3eA1A-YoexhyW7oyvolohg/edit?gid=1519050975#gid=1519050975")
    if isinstance(df, str):  # If fetching failed
        print(f"Couldn’t get the sheet: {df}")
        return 0, None
    
    # Count people marked as checked in
    checked_in_count = len(df[df["Checked In"].isin([True, "Yes", 1, "TRUE"])])
    print(f"Found {checked_in_count} people checked in!")

    # Update the config file with the count
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    config["number_of_checked_in"] = checked_in_count
    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)
    
    return checked_in_count, df  # Return count and data frame

# Pick the next group of people to line up
def get_next_lineup(df, npg, interviewed):
    print(f"Fetching the next {npg} people for lineup...")
    # Find people who checked in but haven’t been interviewed
    checked_in = df["Checked In"].isin([True, "Yes", 1, "TRUE"])
    not_interviewed = ~df["No"].isin(interviewed)
    
    # Debug: Inspect data
    print(f"Total rows in DataFrame: {len(df)}")
    print(f"Checked In values: {df['Checked In'].unique()}")
    print(f"Interviewed list: {interviewed}")
    print(f"Rows marked as checked in: {len(df[checked_in])}")
    print(f"Rows not interviewed: {len(df[not_interviewed])}")
    
    available = df[checked_in & not_interviewed].sort_values("timevalue")
    print(f"Available people after filtering: {len(available)}")
    if len(available) > 0:
        print(f"Available 'No' values: {available['No'].tolist()}")

    # Take the first 'npg' people
    next_group = available.head(npg)
    
    # Warn if we don’t have enough people
    if len(next_group) < npg:
        print(f"Warning: Only {len(next_group)} people available, needed {npg}!")
    
    # Return their details
    group_details = next_group[["No", "中文姓名", "timevalue"]].to_dict('records')
    print(f"Next group: {[person['No'] for person in group_details]}")
    return group_details

# Placeholder for your custom HTML writer
def write_html():
    print("Writing HTML file (your custom version)...")
    try:
        with open('config.json', 'r') as f:
            new_config = json.load(f)

        # For the beginning of the card number (previous group)
        temp_number = ["000", "000", "000", "000", "000", "000"]
        if len(new_config['lineup_history']) >= 2:
            prev_group = new_config["lineup_history"][-2]["people"]
            for i, person in enumerate(prev_group[:6]):
                temp_number[i] = str(person["No"])
        number_on_card1, number_on_card2, number_on_card3, number_on_card4, number_on_card5, number_on_card6 = temp_number

        # Current lineup for next group
        new_next_group = [person["No"] for person in new_config["current_lineup"]]
        card_num = new_next_group
        group_len = len(new_next_group)
        for i in range(6 - group_len):
            card_num.append("000")
        print(f'Quinton Logging************: card_num = {card_num} , temp_number = {temp_number}')

        # Read current HTML
        with open('index.html', 'r', encoding='utf-8') as f:
            html_string = f.read()
            print("Successfully read index.html")

        # Replace numbers in HTML
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
        html_string = html_string.replace('#ee6b6e;color: white;', 'QoosColor1')
        html_string = html_string.replace('#2980b9;color: white;', 'QoosColor2')
        html_string = html_string.replace('QoosColor2', '#ee6b6e;color: white;')
        html_string = html_string.replace('QoosColor1', '#2980b9;color: white;')

        # Write updated HTML
        with open("index.html", "w", encoding='utf-8') as file:
            file.write(html_string)
            print("HTML file successfully written to disk")
        
        # Verify the update
        with open("index.html", "r", encoding='utf-8') as f:
            updated_content = f.read()
            if str(card_num[0]) in updated_content:
                print("HTML file successfully updated with new numbers!")
            else:
                print("Error: New numbers not found in updated HTML!")
    except Exception as e:
        print(f"Error in write_html: {str(e)}")
        file.write(html_string)

def add_latecomer(latecomer_no, df, current_lineup, interviewed, lineup_history, page, lineup_display, progress_box, error_message, latecomer_input):  # Added latecomer_input parameter
    print(f"Attempting to add latecomer No: {latecomer_no} (type: {type(latecomer_no)})")
    error_message.value = ""  # Clear any previous error message
    latecomer_input.value = ""  # Clear the input field immediately after button press

    # Validate input
    if not latecomer_no or not str(latecomer_no).strip():
        print("Validation failed: Empty or invalid input")
        error_message.value = "Please enter a valid number"
        page.update()
        return

    try:
        latecomer_no = int(float(str(latecomer_no)))
        print(f"Normalized latecomer No: {latecomer_no}")
    except ValueError:
        print("Validation failed: Cannot convert to integer")
        error_message.value = "Please enter a valid number"
        page.update()
        return

    # Refresh checked-in data
    checked_in, df = update_checked_in_number(None)
    print(f"Refreshed DataFrame with {checked_in} checked-in rows")

    # Clean and prepare DataFrame
    df["No"] = pd.to_numeric(df["No"], errors='coerce')
    clean_df = df.dropna(subset=["No"]).copy()
    clean_df["No"] = clean_df["No"].astype(int)
    print(f"Cleaned DataFrame 'No' values: {clean_df['No'].tolist()}")

    # Check if the person exists in the DataFrame
    person_row = clean_df[clean_df["No"] == latecomer_no]
    if person_row.empty:
        print(f"No {latecomer_no} not found in DataFrame")
        error_message.value = f"No {latecomer_no} not found"
        page.update()
        return

    # Check if the person has checked in
    checked_in_df = clean_df[clean_df["Checked In"].isin([True, "Yes", 1, "TRUE"])]
    latecomer_row = checked_in_df[checked_in_df["No"] == latecomer_no]
    if latecomer_row.empty:
        print(f"No {latecomer_no} is not checked in")
        error_message.value = f"No {latecomer_no} is not checked in"  # Updated message
        page.update()
        return

    # Check if the person is already interviewed or in the current lineup
    current_lineup_nos = [int(p["No"]) for p in current_lineup]
    if latecomer_no in interviewed:
        print(f"No {latecomer_no} is already interviewed")
        error_message.value = f"No {latecomer_no} is already interviewed"  # Updated message
        page.update()
        return
    elif latecomer_no in current_lineup_nos:
        print(f"No {latecomer_no} is already in the current lineup")
        error_message.value = f"No {latecomer_no} is already in the current lineup"  # Updated message
        page.update()
        return

    # If all checks pass, proceed with confirmation
    def confirm_jump(e):
        if e.control.text == "Yes":
            print(f"Confirmed: Adding No {latecomer_no} as latecomer")
            latecomer_data = {
                "No": latecomer_no,
                "中文姓名": latecomer_row["中文姓名"].values[0] if "中文姓名" in latecomer_row else "N/A",
                "timevalue": latecomer_row["timevalue"].values[0] if "timevalue" in latecomer_row else 0,
                "latecomer": True
            }
            current_lineup.append(latecomer_data)
            interviewed.append(latecomer_no)

            with open("config.json", "r") as config_file:
                config = json.load(config_file)
            config["current_lineup"] = current_lineup
            config["interviewed"] = interviewed
            if lineup_history:
                config["lineup_history"][-1]["people"] = current_lineup
            with open("config.json", "w") as config_file:
                json.dump(config, config_file, indent=4)
                print("Config updated with latecomer")

            lineup_display.controls = [
                ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}{' (Latecomer)' if person.get('latecomer', False) else ''}")
                for person in current_lineup
            ]
            print("Lineup display updated")

            progress_box.content.controls[3] = create_progress_bar(checked_in, len(interviewed))
            write_html()
            print("HTML updated")
            page.update()
        else:
            print("Jump in line canceled")
        dlg.open = False
        page.update()

    print(f"Showing confirmation dialog for No: {latecomer_no}")
    dlg = ft.AlertDialog(
        title=ft.Text("Confirm Jump In Line"),
        content=ft.Text(f"Add No {latecomer_no} to the current lineup?"),
        actions=[
            ft.TextButton("Yes", on_click=confirm_jump),
            ft.TextButton("No", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dlg)
    dlg.open = True
    page.update()

def second_page(page, data=None, url_input=None, result_text=None, submit_button=None, next_page_button=None, data_list_view=None):
    print("Showing the second page...")
    
    total_interviews, checked_in, npg = get_checkin_data()
    checked_in, df = update_checked_in_number(None)
    total_interviews = 826
    
    init_time_serial = get_init_time()
    init_time_display = excel_to_datetime(init_time_serial) if init_time_serial else "Not Set"
    
    data_message = ft.Text("No Google Sheet data available") if data is None or data.empty else ft.Text(f"Loaded {len(data)} rows from Google Sheet")

    with open("config.json", "r") as config_file:
        config = json.load(config_file)
    interviewed = config.get("interviewed", [])
    current_lineup = config.get("current_lineup", [])
    lineup_history = config.get("lineup_history", [])
    group_number = len(lineup_history)
    print(f"second page opened, Interviewed list: {interviewed}")

    # Get the last lineup (lineup_history[-2]) if it exists
    last_lineup = []
    if len(lineup_history) >= 2:
        last_lineup = lineup_history[-2]["people"]
        print(f"Last lineup (Group #{lineup_history[-2]['group_number']}): {[person['No'] for person in last_lineup]}")
    else:
        print("No previous lineup available (less than 2 groups in history)")

    # Get the next potential lineup
    next_potential_lineup = get_next_lineup(df, npg, interviewed) if not isinstance(df, str) else []
    print(f"Next potential lineup: {[person['No'] for person in next_potential_lineup]}")

    latecomer_input = ft.TextField(
        label="Latecomer No",
        width=200,
        hint_text="Enter No",
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
    )
    jump_button = ft.ElevatedButton(
        text="Jump In Line",
        bgcolor="Green",
        width=150,
        height=40,
        style=ft.ButtonStyle(padding=10),
    )
    
    error_message = ft.Text("", color=ft.colors.RED, size=14)

    progress_box = ft.Container(
        content=ft.Column(
            [
                ft.Text("Check-in Status", size=20, weight="bold"),
                create_progress_bar(total_interviews, checked_in),
                ft.Text("Interview Status", size=20, weight="bold"),
                create_progress_bar(checked_in, len(interviewed)),
            ],
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.only(top=10, bottom=5, left=10, right=10),
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=5,
        width=page.width / 3,
        alignment=ft.alignment.center,
        height=250,
    )

    # Current Lineup Display
    lineup_display = ft.Column(
        [ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}{' (Latecomer)' if person.get('latecomer', False) else ''}") for person in current_lineup] if current_lineup else [ft.Text("No current lineup")],
        spacing=5
    )

    # Last Lineup Display
    last_lineup_display = ft.Column(
        [ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}{' (Latecomer)' if person.get('latecomer', False) else ''}") for person in last_lineup] if last_lineup else [ft.Text("No previous lineup")],
        spacing=5
    )

    # Next Potential Lineup Display
    next_lineup_display = ft.Column(
        [ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}") for person in next_potential_lineup] if next_potential_lineup else [ft.Text("No next lineup available")],
        spacing=5
    )

    jump_button.on_click = lambda e: add_latecomer(
        latecomer_input.value, df, current_lineup, interviewed, lineup_history, page, lineup_display, progress_box, error_message, latecomer_input
    )

    def on_lineup_click(event):
        nonlocal interviewed, current_lineup, lineup_history, group_number, next_potential_lineup
        print("You clicked the Lineup button!")
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        current_npg = config["npg"]
        print(f"Fetching {current_npg} people for the lineup...")
        new_checked_in, df = update_checked_in_number(None)
        print(f"Quinton Logging************: new_checked_in = {new_checked_in} , df = {df}")
        if isinstance(df, str):
            print(f"Problem fetching data: {df}")
            lineup_display.controls = [ft.Text("Failed to fetch lineup", color=ft.colors.RED)]
            next_lineup_display.controls = [ft.Text("No next lineup available")]
        else:
            next_group = get_next_lineup(df, current_npg, interviewed)
            if not next_group:
                lineup_display.controls = [ft.Text("No more people to line up", color=ft.colors.RED)]
                next_lineup_display.controls = [ft.Text("No next lineup available")]
            else:
                for person in next_group:
                    person["No"] = int(person["No"])
                group_number = len(config.get("lineup_history", [])) + 1
                current_lineup[:] = next_group
                interviewed.extend([person["No"] for person in next_group])
                config["current_lineup"] = current_lineup
                config["interviewed"] = interviewed
                lineup_history.append({"group_number": group_number, "people": next_group, "npg": current_npg})
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
                if len(lineup_history) >= 2:
                    last_lineup_display.controls = [
                        ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}{' (Latecomer)' if person.get('latecomer', False) else ''}")
                        for person in lineup_history[-2]["people"]
                    ]
                else:
                    last_lineup_display.controls = [ft.Text("No previous lineup")]
                # Update next potential lineup
                next_potential_lineup = get_next_lineup(df, current_npg, interviewed)
                next_lineup_display.controls = [
                    ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}") 
                    for person in next_potential_lineup
                ] if next_potential_lineup else [ft.Text("No next lineup available")]
                progress_box.content = ft.Column(
                    [
                        ft.Text("Check-in Status", size=20, weight="bold"),
                        create_progress_bar(total_interviews, new_checked_in),
                        ft.Text("Interview Status", size=20, weight="bold"),
                        create_progress_bar(new_checked_in, len(interviewed)),
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                print(f"Added Group #{group_number}: {[person['No'] for person in next_group]}")
                write_html()
        page.update()

    def on_reset_click(event):
        nonlocal interviewed, current_lineup, lineup_history, group_number, next_potential_lineup
        print("Reset button clicked!")

        def confirm_reset(e):
            print(f"Dialog button clicked: {e.control.text}")
            if e.control.text == "Yes":
                shutil.copy("config.json", "backup_config1.json")
                print("Backed up config.json to backup_config1.json")
                
                with open("config.json", "r") as config_file:
                    config = json.load(config_file)
                config["interviewed"] = []
                config["current_lineup"] = []
                config["lineup_history"] = []
                config["next_group"] = []
                with open("config.json", "w") as config_file:
                    json.dump(config, config_file, indent=4)
                print("Reset config.json: interviewed, current_lineup, lineup_history, and next_group cleared")

                interviewed.clear()
                current_lineup.clear()
                lineup_history.clear()
                group_number = 0
                lineup_display.controls = [ft.Text("No current lineup")]
                last_lineup_display.controls = [ft.Text("No previous lineup")]
                next_potential_lineup = get_next_lineup(df, npg, interviewed) if not isinstance(df, str) else []
                next_lineup_display.controls = [
                    ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}") 
                    for person in next_potential_lineup
                ] if next_potential_lineup else [ft.Text("No next lineup available")]
                progress_box.content = ft.Column(
                    [
                        ft.Text("Check-in Status", size=20, weight="bold"),
                        create_progress_bar(total_interviews, checked_in),
                        ft.Text("Interview Status", size=20, weight="bold"),
                        create_progress_bar(checked_in, len(interviewed)),
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                page.update()
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Reset Confirmation"),
            content=ft.Text("Are you sure you want to reset? This will clear all interviewed data."),
            actions=[
                ft.TextButton("Yes", on_click=confirm_reset),
                ft.TextButton("No", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        print("Opening reset confirmation dialog")
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    page_layout = ft.Column(
        [
            ft.Row(
                [
                    progress_box,
                    ft.Container(
                        height=250,
                        content=ft.Column(
                            [
                                ft.Text("Number of people per group", size=16, weight="bold"),
                                ft.Container(height=-5),
                                ft.Row(
                                    [
                                        ft.Slider(
                                            min=0,
                                            max=6,
                                            value=npg,
                                            on_change=lambda e: [
                                                update_config_npg(e.control.value),
                                                e.control.parent.controls[1].__setattr__('value', str(int(e.control.value))),
                                                setattr(next_lineup_display, 'controls', [
                                                    ft.Text(f"No: {p['No']} - {p['中文姓名']} - {p['timevalue']}")
                                                    for p in get_next_lineup(df, int(e.control.value), interviewed)
                                                ] if get_next_lineup(df, int(e.control.value), interviewed) else [ft.Text("No next lineup available")]),
                                                page.update()
                                            ],
                                            width=200,
                                        ),
                                        ft.Text(str(npg)),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=10,
                                ),
                                ft.Container(height=35),
                                ft.Column(
                                    [
                                        ft.Text("Jump In Line", size=16, weight="bold"),
                                        ft.Row(
                                            [
                                                latecomer_input,
                                                jump_button,
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=10,
                                        ),
                                    ],
                                    spacing=10,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                error_message,
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=3,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        width=page.width / 3,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(
                        height=250,
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
                        padding=3,
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
            ft.Row(
                [
                    ft.Container(
                        height=350,
                        content=ft.Column(
                            [
                                ft.Text("Last Lineup", size=16, weight="bold"),
                                last_lineup_display,
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        width=500,
                    ),
                    ft.Container(
                        height=350,
                        content=ft.Column(
                            [
                                ft.Text("Current Lineup", size=16, weight="bold"),
                                lineup_display,
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        width=500,
                    ),
                    ft.Container(
                        height=350,
                        content=ft.Column(
                            [
                                ft.Text("Next Potential Lineup", size=16, weight="bold"),
                                next_lineup_display,
                            ],
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=20,
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=5,
                        width=500,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.Container(
                content=ft.Row(
                    [
                        ft.ElevatedButton(
                            text="<---- Back",
                            bgcolor="red",
                            on_click=lambda e: page.clean() or page.add(first_page(page, url_input, result_text, submit_button, next_page_button, data_list_view)),
                            width=80,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                        ft.ElevatedButton(
                            text="Lineup",
                            bgcolor="orange",
                            on_click=on_lineup_click,
                            width=200,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                        ft.ElevatedButton(
                            text="Open HTML",
                            bgcolor="yellow",
                            on_click=lambda e: webbrowser.open(f"file://{os.getcwd()}/index.html", new=0, autoraise=True),
                            width=200,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                        ft.ElevatedButton(
                            text="Reset",
                            bgcolor="red",
                            on_click=on_reset_click,
                            width=80,
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