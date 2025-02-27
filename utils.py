import re
import pandas as pd
from datetime import datetime, timedelta

def extract_sheet_id(url):
    print("Extracting Sheet ID from URL...")
    pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, url)
    if match:
        print(f"Sheet ID extracted: {match.group(1)}")
        return match.group(1)
    else:
        print("Invalid Google Sheet URL.")
        return None

def read_google_sheet(url, sheet_name="lite"):
    print("Reading Google Sheet data...")
    sheet_id = extract_sheet_id(url)
    if not sheet_id:
        return "Invalid Google Sheet URL. Please check the URL and try again."
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        print(f"Fetching data from URL: {csv_url}")
        df = pd.read_csv(csv_url)
        print("Data loaded successfully!")
        return df
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return f"Error: {str(e)}"

def excel_to_datetime(excel_serial):
    """Convert Excel serial number to datetime string."""
    epoch = datetime(1899, 12, 30)
    delta = timedelta(days=int(excel_serial), seconds=int((excel_serial % 1) * 86400))
    return (epoch + delta).strftime("%Y-%m-%d %H:%M:%S")

def datetime_to_excel(dt_str):
    """Convert datetime string to Excel serial number."""
    epoch = datetime(1899, 12, 30)
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        delta = dt - epoch
        return delta.days + (delta.seconds / 86400.0)
    except ValueError:
        print(f"Invalid datetime format: {dt_str}")
        return 0