#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from app import get_sheets_service, SPREADSHEET_ID
from datetime import datetime

load_dotenv()

def resort_sheet():
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()

        # Get all data
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A:S'
        ).execute()

        values = result.get('values', [])

        if len(values) <= 1:
            print("No data to sort")
            return

        # Separate header and data
        header = values[0]
        data = values[1:]

        print(f"Found {len(data)} data rows to sort")

        # Sort data by date (column 0) and time (column 1) in descending order
        # Parse the date and time for proper sorting
        def parse_datetime(row):
            try:
                if len(row) >= 2:
                    date_str = row[0]
                    time_str = row[1].replace(' ET', '')  # Remove ET suffix
                    datetime_str = f"{date_str} {time_str}"
                    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                return datetime.min
            except:
                return datetime.min

        data.sort(key=parse_datetime, reverse=True)

        # Clear the sheet
        sheet.values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A:S'
        ).execute()

        # Write back header and sorted data
        all_values = [header] + data

        body = {
            'values': all_values
        }

        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A:S',
            valueInputOption='RAW',
            body=body
        ).execute()

        # Format header as bold
        formatting_request = {
            "requests": [
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
                }
            ]
        }

        sheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=formatting_request
        ).execute()

        print("✓ Sheet resorted in descending order (newest tweets first)")
        return True

    except Exception as e:
        print(f"Error resorting sheet: {e}")
        return False

if __name__ == "__main__":
    resort_sheet()