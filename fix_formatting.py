#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from app import get_sheets_service, SPREADSHEET_ID

load_dotenv()

def fix_formatting():
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()

        # Get the current sheet to find how many rows exist
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A:A'
        ).execute()

        values = result.get('values', [])
        total_rows = len(values)

        print(f"Found {total_rows} rows in the spreadsheet")

        # Format request: Bold header row, normal text for all other rows
        formatting_request = {
            "requests": [
                # First, make header row bold
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": 0,
                            "endRowIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat.textFormat.bold"
                    }
                },
                # Then, make all other rows not bold
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": 1,
                            "endRowIndex": total_rows if total_rows > 1 else 2
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "bold": False
                                }
                            }
                        },
                        "fields": "userEnteredFormat.textFormat.bold"
                    }
                }
            ]
        }

        sheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=formatting_request
        ).execute()

        print("✓ Formatting fixed - only header row is bold now")
        return True
    except Exception as e:
        print(f"Error fixing formatting: {e}")
        return False

if __name__ == "__main__":
    fix_formatting()