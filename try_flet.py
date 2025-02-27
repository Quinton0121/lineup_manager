import flet as ft
import re
import pandas as pd
import json  # Import json to read the config file

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
        
        # Function to read and display the config file
        def read_config():
            try:
                with open('config.json', 'r') as file:
                    config = json.load(file)
                    return ft.Text(f"Config: {json.dumps(config, indent=2)}")
            except Exception as e:
                return ft.Text(f"Error reading config file: {str(e)}")
        
        # First Row: Config Section
        config_section = ft.Container(
            content=read_config(),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            width=500
        )
        
        # Second Row: Placeholder for other content
        second_row = ft.Container(
            content=ft.Text("Second Row Content"),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            width=500
        )
        
        # Third Row: Placeholder for other content
        third_row = ft.Container(
            content=ft.Text("Third Row Content"),
            padding=10,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            width=500
        )
        
        return ft.Column(
            [
                ft.Text("Second Page", size=20, weight="bold"),
                config_section,
                second_row,
                third_row,
                ft.ElevatedButton(text="Go Back to First Page", bgcolor="red", on_click=on_go_back_click),
            ],
            alignment="center",
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