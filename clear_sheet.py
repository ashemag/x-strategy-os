#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from app import get_sheets_service, SPREADSHEET_ID

load_dotenv()

def clear_sheet():
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()

        # Clear the entire sheet
        sheet.values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range='posts'
        ).execute()

        print("✓ Spreadsheet cleared successfully")
        return True
    except Exception as e:
        print(f"Error clearing spreadsheet: {e}")
        return False

if __name__ == "__main__":
    clear_sheet()