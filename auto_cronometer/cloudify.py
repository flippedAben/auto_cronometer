import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import auto_cronometer.grocery_list as grocery_list

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SHEET_ID = os.environ.get('google_sheets_api_sheet_id')


def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.environ.get('google_sheets_api_token_pickle_path')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_path = os.environ.get('google_sheets_api_client_id_path')
            flow = InstalledAppFlow.from_client_secrets_file(
                client_path,
                SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
    return service


def get_metadata(sheet):
    """
    Retrieve meta data on the groceries.
    """
    sheet_name = 'Metadata'

    result = sheet.values().get(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A:C',
    ).execute()

    values = result['values']
    metadata = {}
    for i, row in enumerate(values[1:], start=2):
        item = row[0]
        order = row[1]
        # Omitted value implies the item is not in stock
        in_stock = False
        if len(row) == 3:
            in_stock = bool(row[2])
        metadata[item] = [f'={sheet_name}!B{i}', float(order), in_stock]
    return metadata


def update_groceries(sheet, metadata):
    """
    Put grocery list data on the cloud.
    """
    print('Updating grocery sheet...')
    sheet_name = 'List'

    # Clear the existing grocery list
    sheet.values().clear(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A:D',
        body={}
    ).execute()

    # Read the local grocery list from ingredients.csv files
    # Ignore the header
    data = grocery_list.get_grocery_list()[1:]

    # Ignore items that are "in stock" (i.e. we already have enough)
    out_of_stock_data = []
    for row in data:
        item = row[0]
        if item in metadata:
            if not metadata[item][2]:
                out_of_stock_data.append(row)
        else:
            print(f'Not in the Metadata sheet: {item}')

    # Apply an ordering if it exists
    for row in out_of_stock_data:
        item = row[0]
        if item in metadata:
            row.append(metadata[item][1])

    # Sort by order
    out_of_stock_data.sort(key=lambda x: x[3])
    body = {
        'values': out_of_stock_data
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
                        'endIndex': len(out_of_stock_data[0])
                    }
                }
            }
        ]
    }
    sheet.batchUpdate(
        spreadsheetId=SHEET_ID,
        body=body
    ).execute()


def upload_grocery_list():
    sheet = get_service().spreadsheets()
    metadata = get_metadata(sheet)
    update_groceries(sheet, metadata)
