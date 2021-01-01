import csv
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import grocery_list
import secrets

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SHEET_ID = secrets.sheet_id


def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_id.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service


def get_ordering(sheet):
    """
    Retrieve the order in which we should buy items.
    """
    sheet_name = 'Order'

    result = sheet.values().get(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A:B',
    ).execute()

    values = result['values']
    ordering = {}
    for i, (item, _) in enumerate(values, start=1):
        ordering[item] = f'={sheet_name}!B{i}'
    return ordering


def update_groceries(sheet, ordering):
    """
    Put grocery list data on the cloud.
    """
    sheet_name = 'List'

    # Clear the existing grocery list
    sheet.values().clear(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A:D',
        body={}
    ).execute()

    # Read the local grocery list from ingredients.csv (recently scraped)
    data = grocery_list.get_grocery_list()
    # Apply an ordering if it exists
    for row in data:
        item = row[0]
        if item in ordering:
            row.append(ordering[item])
    body = {
        'values': data
    }
    sheet.values().update(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A1',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    # Auto resize the columns for easier reading
    body = {
        'requests': [
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': len(data[0])
                    }
                }
            }
        ]
    }
    sheet.batchUpdate(
        spreadsheetId=SHEET_ID,
        body=body
    ).execute()


def main():
    sheet = get_service().spreadsheets()
    ordering = get_ordering(sheet)
    update_groceries(sheet, ordering)


if __name__ == '__main__':
    main()
