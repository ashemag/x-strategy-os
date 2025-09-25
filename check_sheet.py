#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from app import get_sheets_service, SPREADSHEET_ID

load_dotenv()

def check_sheet():
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()

        # Get spreadsheet metadata
        metadata = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = metadata.get('sheets', [])

        print("Sheet information:")
        for s in sheets:
            properties = s.get('properties', {})
            print(f"  Title: {properties.get('title')}")
            print(f"  Sheet ID: {properties.get('sheetId')}")
            print(f"  Grid Properties: {properties.get('gridProperties')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sheet()