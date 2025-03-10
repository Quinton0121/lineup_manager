import flet as ft
from pages import first_page, second_page

def main(page: ft.Page):
    print("Initializing Flet app...")
    page.title = "Google Sheet Reader"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # UI components
    url_input = ft.TextField(
        label="Google Sheet URL",
        width=500,
        hint_text="Paste your Google Sheet URL here",
        value="https://docs.google.com/spreadsheets/d/1Lg-SDFWTgYmEZRKJQdHaDJ6r4PNDFFSy/edit?gid=335596611#gid=335596611"
    )
    result_text = ft.Text()
    submit_button = ft.ElevatedButton(text="Submit", bgcolor="red")
    next_page_button = ft.ElevatedButton(text="Go to Next Page", bgcolor="red", visible=False)
    data_list_view = ft.ListView(expand=True, spacing=10, padding=20)
    
    fetched_data = None  # Global storage for fetched data

    def on_submit_click(e):
        nonlocal fetched_data
        from utils import read_google_sheet
        print("Submit button clicked...")
        url = url_input.value
        if not url:
            print("URL is empty.")
            result_text.value = "Please enter a Google Sheet URL."
            page.update()
            return

        print(f"URL entered: {url}")
        data = read_google_sheet(url)
        if isinstance(data, str):
            print(f"Error: {data}")
            result_text.value = data
            data_list_view.controls.clear()
            next_page_button.visible = False
        else:
            print("Data loaded successfully. Updating UI...")
            fetched_data = data
            result_text.value = "Data loaded successfully!"
            data_list_view.controls.clear()
            for index, row in data.iterrows():
                row_text = ", ".join([str(item) for item in row])
                data_list_view.controls.append(ft.Text(row_text))
            next_page_button.visible = True
        page.update()

    def on_next_page_click(e):
        print("Navigating to second page...")
        page.clean()
        page.add(second_page(page, fetched_data, url_input, result_text, submit_button, next_page_button, data_list_view))
        page.update()

    submit_button.on_click = on_submit_click
    next_page_button.on_click = on_next_page_click

    print("Adding first page to the app...")
    page.add(first_page(page, url_input, result_text, submit_button, next_page_button, data_list_view))

if __name__ == "__main__":
    print("Starting Flet app...")
    ft.app(target=main)