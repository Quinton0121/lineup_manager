import flet as ft
import re
import pandas as pd
import json  # Import json to read the config file
import math
from flet.canvas import Canvas  # Import Canvas from flet.canvas
from flet import Stack, Paint

# 提取 Sheet ID
def extract_sheet_id(url):
    print("Extracting Sheet ID from URL...")
    pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, url)
    if match:
        print(f"Sheet ID extracted: {match.group(1)}")
        return match.group(1)
    else:
        print("Invalid Google Sheet URL.")
        return None  # 返回 None 表示无效的 URL

# 读取 Google Sheet 数据
def read_google_sheet(url, sheet_name="lite"):
    print("Reading Google Sheet data...")
    sheet_id = extract_sheet_id(url)
    if not sheet_id:
        return "Invalid Google Sheet URL. Please check the URL and try again."

    # 构造指定工作表的 CSV 导出 URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        print(f"Fetching data from URL: {csv_url}")
        df = pd.read_csv(csv_url)
        print("Data loaded successfully!")
        return df
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}"

# Flet 应用
def main(page: ft.Page):
    print("Initializing Flet app...")
    page.title = "Google Sheet Reader"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    #page.transition = ft.PageTransitionTheme.OPEN_UPWARDS  # 设置页面切换动画为淡入淡出


    # UI 组件
    url_input = ft.TextField(label="Google Sheet URL", 
                             width=500, 
                             hint_text="Paste your Google Sheet URL here",
                             value="https://docs.google.com/spreadsheets/d/1YoOGKltmbHjstO6RIRQeZ3eA1A-YoexhyW7oyvolohg/edit?gid=1519050975#gid=1519050975"  # 设置默认值
                             )
    result_text = ft.Text()
    submit_button = ft.ElevatedButton(text="Submit",bgcolor="red")
    next_page_button = ft.ElevatedButton(
        text="Go to Next Page",
        bgcolor="red",
        visible=False
    )   


    # 创建一个 ListView 用于显示数据
    data_list_view = ft.ListView(expand=True, spacing=10, padding=20)

    # 第一页的内容
    def first_page():
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
                    border=ft.border.all(1, ft.Colors.GREY_400),  # 使用 ft.Colors 枚举
                    border_radius=5,
                    padding=10,
                ),
                next_page_button,
            ],
            alignment="center"
        )

    # 第二页的内容
    

# Second page content
    def second_page():
        print("Rendering second page...")
        
        # Function to read config and get interview numbers
        def get_checkin_data():
            try:
                with open('config.json', 'r') as file:
                    config = json.load(file)
                    total = config.get('total_interview', 100)
                    checked_in = config.get('number_of_checked_in', 0)
                    npg = config.get('npg', 0)  # Default to 0 if not found
                    return total, checked_in, npg
            except Exception as e:
                print(f"Error reading config: {str(e)}")
                return 100, 0, 0  # Default values in case of error

        # Get the data
        total_interviews, checked_in, npg = get_checkin_data()
        
        # Create horizontal progress bar
        def create_progress_bar():
            original_width = 500
            scale_factor = 2.5
            width = original_width / scale_factor  # New width = 200 pixels
            height = 30  # Revert to original height = 30 pixels
            
            # Log the inputs for verification
            print(f"Debug - Checked In: {checked_in}, Total Interviews: {total_interviews}")
            
            # Calculate progress width, ensuring correct proportion
            proportion = checked_in / total_interviews if total_interviews > 0 else 0
            progress_width = min(proportion * width, width)  # Cap at new max width
            indicator_position = min(progress_width - (2 / scale_factor), width - (4 / scale_factor))  # Scale indicator offsets
            
            # Log the calculated values
            print(f"Debug - Proportion: {proportion}, Progress Width: {progress_width}, Indicator Position: {indicator_position}")
            
            # Create the blue bar container
            blue_bar = ft.Container(
                width=progress_width,
                height=height,
                bgcolor=ft.Colors.BLUE_500,
                border_radius=5 / scale_factor,
            )
            
            # Log blue bar properties after creation
            print(f"Debug - Blue Bar Config - Width: {blue_bar.width}, Height: {blue_bar.height}, BGCOLOR: {blue_bar.bgcolor}")
            
            # Assemble the full progress bar
            progress_bar = ft.Container(
                content=ft.Column(
                    [
                        # Progress bar with grey background and text overlay
                        ft.Container(
                            content=ft.Stack(
                                controls=[
                                    ft.Row(
                                        [
                                            blue_bar,
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        spacing=0,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            f"Checked In: {checked_in}/{total_interviews}",
                                            size=12,  # Increased size for readability (adjust as needed)
                                            color=ft.Colors.RED_500,  # Changed to red
                                            weight=ft.FontWeight.BOLD,
                                            text_align=ft.TextAlign.CENTER,
                                        ),
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
                        # Indicator as a separate layer
                        ft.Stack(
                            controls=[
                                ft.Container(
                                    left=indicator_position,
                                    content=ft.Container(
                                        width=4 / scale_factor,  # Red line width = 1.6 pixels
                                        height=height + 10,  # Match original height adjustment
                                        bgcolor=ft.Colors.RED_500
                                    ),
                                ),
                            ],
                        ),
                    ],
                    spacing=0,
                ),
                width=width,
                height=height + 10,  # Adjust total height to match original offset
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
            
            # Log the outer container properties
            print(f"Debug - Outer Container - Width: {progress_bar.width}, Height: {progress_bar.height}, Clip Behavior: {progress_bar.clip_behavior}")
            
            return progress_bar
        
        def update_config_npg(new_value):
            try:
                with open('config.json', 'r') as file:
                    config = json.load(file)
                config['npg'] = int(new_value) if new_value else 0  # Convert to int, default to 0 if empty
                with open('config.json', 'w') as file:
                    json.dump(config, file, indent=2)
                print(f"Updated config.json with npg: {config['npg']}")
            except Exception as e:
                print(f"Error updating config: {str(e)}")

        # Updated layout using page.width
        return ft.Column(
            [
                # First part (full width, divided into 3 sections)
                ft.Row(
                    [
                        # First section (with progress bar)
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Check-in Status", size=20, weight="bold"),
                                    ft.Container(
                                        content=create_progress_bar(),
                                        padding=10,
                                        border=ft.border.all(1, ft.Colors.GREY_400),
                                        border_radius=5,
                                    ),
                                ],
                                spacing=10,
                            ),
                            width=page.width / 3,  # Use page.width instead of ft.Page.width
                            alignment=ft.alignment.top_left,
                        ),
                        # Second section
                        # Second section (with numeric input for npg)
                        # Second section (with slider for npg)
                        # Second section (with slider and current value display)
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("NPG Value", size=16, weight="bold"),
                                    ft.Row(
                                        [
                                            ft.Slider(
                                                min=0,
                                                max=6,
                                                value=get_checkin_data()[2] if len(get_checkin_data()) > 2 else 0,
                                                on_change=lambda e: [
                                                    update_config_npg(e.control.value),
                                                    e.control.parent.controls[1].__setattr__('value', str(int(e.control.value))),
                                                    page.update()
                                                ],  # Update config and text
                                                width=200,
                                            ),
                                            ft.Text(str(get_checkin_data()[2] if len(get_checkin_data()) > 2 else 0)),  # Initial value
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        spacing=10,
                                    ),
                                ],
                                spacing=10,
                            ),
                            padding=10,
                            border=ft.border.all(1, ft.Colors.GREY_400),
                            border_radius=5,
                            width=page.width / 3,
                            alignment=ft.alignment.top_center,
                        ),
                        # Third section
                        ft.Container(
                            content=ft.Text("Section 3 Content"),
                            padding=10,
                            border=ft.border.all(1, ft.Colors.GREY_400),
                            border_radius=5,
                            width=page.width / 3,  # Use page.width
                            alignment=ft.alignment.top_center,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                ),
                # Second part
                ft.Container(
                    content=ft.Text("Additional Content Here (Part 2)"),
                    padding=10,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=5,
                    width=500,
                    expand=True,
                ),
                # Third part
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Go Back to First Page",
                        bgcolor="red",
                        on_click=on_go_back_click
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

    # 事件处理函数：提交 URL
    def on_submit_click(e):
        print("Submit button clicked...")
        url = url_input.value
        if not url:
            print("URL is empty.")
            result_text.value = "Please enter a Google Sheet URL."
            page.update()
            return

        print(f"URL entered: {url}")
        data = read_google_sheet(url)
        if isinstance(data, str):  # 如果返回的是错误信息
            print(f"Error: {data}")
            result_text.value = data
            data_list_view.controls.clear()  # 清空 ListView
            next_page_button.visible = False  # 隐藏 "Go to Next Page" 按钮
        else:  # 如果返回的是 DataFrame
            print("Data loaded successfully. Updating UI...")
            result_text.value = "Data loaded successfully!"
            data_list_view.controls.clear()  # 清空 ListView

            # 将 DataFrame 的每一行添加到 ListView 中
            for index, row in data.iterrows():
                row_text = ", ".join([str(item) for item in row])
                data_list_view.controls.append(ft.Text(row_text))

            next_page_button.visible = True  # 显示 "Go to Next Page" 按钮

        page.update()

    # 事件处理函数：导航到第二页
    def on_next_page_click(e):
        print("Navigating to second page...")
        page.clean()  # 清空当前页面
        page.add(second_page())  # 显示第二页内容
        page.update()

    # 事件处理函数：返回第一页
    def on_go_back_click(e):
        print("Navigating back to first page...")
        page.clean()  # 清空当前页面
        page.add(first_page())  # 显示第一页内容
        page.update()  # 触发页面更新，应用过渡动画

    # 绑定事件
    submit_button.on_click = on_submit_click
    next_page_button.on_click = on_next_page_click

    # 初始化页面
    print("Adding first page to the app...")
    page.add(first_page())

# 运行应用
print("Starting Flet app...")
ft.app(target=main)