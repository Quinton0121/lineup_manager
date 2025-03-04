import flet as ft
from components import create_progress_bar
from config import get_checkin_data, update_config_npg, get_init_time, update_config_init_time
from utils import excel_to_datetime, read_google_sheet
import json
import pandas as pd
import re
import webbrowser
import os

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
    available = df[checked_in & not_interviewed].sort_values("timevalue")  # Sort by check-in time
    
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
    # Your implementation goes here
    with open('config.json') as f:
        new_config = json.load(f)

    #for the beginning of the card number
    temp_number = ["000","000","000","000","000","000"]

    if len(new_config['lineup_history']) >= 2:
        prev_group = new_config["lineup_history"][-2]["people"]
        for i, person in enumerate(prev_group[:6]):
            temp_number[i] = str(person["No"])

    #number on the back 
    number_on_card1,number_on_card2,number_on_card3,number_on_card4,number_on_card5,number_on_card6 = temp_number



    # In on_lineup_click or elsewhere
    new_next_group = [person["No"] for person in new_config["current_lineup"]]
    card_num = new_next_group
    group_len = len(new_next_group)

    for i in range( 6 - group_len):
        card_num.append("000")
    print(f'Quinton Logging************: card_num = {card_num} , temp_number = {temp_number}' )
     #--------------------------------------------writing html--------------------------------------   

    #html_string = ""
    f = open('index.html', 'r',encoding='utf-8')
    # writing the code into the file


    html_string = f.read()

    # close the file
    f.close()
    #print("card_num: ",card_num)
    #html_string = html_string.replace('Qoos2',df_time)
    html_string = re.sub(r'id="Qoos1">[0-9]*</h1>', 'id="Qoos1">'+str(number_on_card1)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos2">[0-9]*</h1>', 'id="Qoos2">'+str(card_num[0])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos3">[0-9]*</h1>', 'id="Qoos3">'+str(number_on_card2)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos4">[0-9]*</h1>', 'id="Qoos4">'+str(card_num[1])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos5">[0-9]*</h1>', 'id="Qoos5">'+str(number_on_card3)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos6">[0-9]*</h1>', 'id="Qoos6">'+str(card_num[2])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos7">[0-9]*</h1>', 'id="Qoos7">'+str(number_on_card4)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos8">[0-9]*</h1>', 'id="Qoos8">'+str(card_num[3])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos9">[0-9]*</h1>', 'id="Qoos9">'+str(number_on_card5)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos10">[0-9]*</h1>', 'id="Qoos10">'+str(card_num[4])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos11">[0-9]*</h1>', 'id="Qoos11">'+str(number_on_card6)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos12">[0-9]*</h1>', 'id="Qoos12">'+str(card_num[5])+'</h1>', html_string)
    html_string = html_string.replace('#ee6b6e;color: white;','QoosColor1')
    html_string = html_string.replace('#2980b9;color: white;','QoosColor2')
    html_string = html_string.replace('QoosColor2','#ee6b6e;color: white;')
    html_string = html_string.replace('QoosColor1','#2980b9;color: white;')
    

    
    
    with open("index.html", "w",encoding='utf-8') as file:
        file.write(html_string)

# Show the second page with lineup controls
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

    # Handle the "Lineup" button click
    def on_lineup_click(event):
        print("You clicked the Lineup button!")
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
        current_npg = config["npg"]  # Number per group
        print(f"Fetching {current_npg} people for the lineup...")

        # Update checked-in count and get data
        new_checked_in, df = update_checked_in_number(None)
        if isinstance(df, str):  # If data fetch fails
            print(f"Problem fetching data: {df}")
            lineup_display.controls = [ft.Text("Failed to fetch lineup", color=ft.colors.RED)]
        else:
            # Get the next group
            next_group = get_next_lineup(df, current_npg, interviewed)
            if not next_group:  # If no one’s left
                lineup_display.controls = [ft.Text("No more people to line up", color=ft.colors.RED)]
            else:
                # Convert "No" to integer for each person in next_group
                for person in next_group:
                    person["No"] = int(person["No"]) 
                # Update group number and config
                group_number = len(config.get("lineup_history", [])) + 1
                current_lineup[:] = next_group  # Set new lineup
                interviewed.extend([person["No"] for person in next_group])  # Mark them as interviewed
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
                
                # Update data file
                with open('data.json', 'r') as data_file:
                    data = json.load(data_file)
                for person in next_group:
                    data['line'].append(person["No"])  # Add to lineup history
                data['npg'].append(current_npg)  # Record group size
                with open('data.json', 'w') as data_file:
                    json.dump(data, data_file, indent=4)

                # Refresh the display
                lineup_display.controls = [ft.Text(f"No: {person['No']} - {person['中文姓名']} - {person['timevalue']}") for person in current_lineup]
                progress_box.content = ft.Column(
                    [ft.Text("Check-in Status", size=20, weight="bold"), create_progress_bar(total_interviews, new_checked_in)],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                print(f"Added Group #{group_number}: {[person['No'] for person in next_group]}")
                write_html()  # Call your custom HTML writer
        page.update()  # Refresh the page

    # Layout the second page
    page_layout = ft.Column(
        [
            ft.Row(  # Top row with controls
                [
                    progress_box,  # Progress bar
                    ft.Container(  # Slider for people per group
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
                                                update_config_npg(e.control.value),  # Update npg
                                                e.control.parent.controls[1].__setattr__('value', str(int(e.control.value))),  # Update text
                                                page.update()  # Refresh page
                                            ],
                                            width=200,
                                        ),
                                        ft.Text(str(npg)),  # Show current npg
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
                    ft.Container(  # Start time input
                        content=ft.Column(
                            [
                                ft.Text("Start Time", size=16, weight="bold"),
                                ft.TextField(
                                    label="(YYYY-MM-DD HH:MM:SS)",
                                    value=init_time_display,
                                    on_change=lambda e: update_config_init_time(e.control.value),  # Update init time
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
            ft.Container(  # Current lineup display
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
            ft.Container(  # Buttons
                content=ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Lineup",
                            bgcolor="blue",
                            on_click=on_lineup_click,  # Handle lineup click
                            width=200,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                        ft.ElevatedButton(
                            text="Open HTML",
                            bgcolor="green",
                            on_click=lambda e: webbrowser.open(f"file://{os.getcwd()}/index.html", new=0, autoraise=True),  # Open HTML
                            width=200,
                            height=60,
                            style=ft.ButtonStyle(padding=20),
                        ),
                        ft.ElevatedButton(
                            text="Go Back to First Page",
                            bgcolor="red",
                            on_click=lambda e: page.clean() or page.add(first_page(page, url_input, result_text, submit_button, next_page_button, data_list_view)),  # Go back
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