import csv
import pickle
import os.path
import secrets
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SHEET_ID = secrets.sheet_id
SHEET_NAME = 'List'


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


def main():
    # Call the Sheets API
    sheet = get_service().spreadsheets()

    # Put local grocery_list data on the cloud

    ## Clear the existing grocery list
    sheet.values().clear(
        spreadsheetId=SHEET_ID,
        range=f'{SHEET_NAME}!A:D',
        body={}
    ).execute()

    ## Read the local grocery_list (recently scraped)
    data = []
    with open('data/grocery_list.csv', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)

    body = {
        'values': data
    }
    sheet.values().update(
        spreadsheetId=SHEET_ID,
        range=f'{SHEET_NAME}!A1',
        valueInputOption='USER_ENTERED',
        body=body).execute()

    ## Auto resize the columns for easier reading
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
        body=body).execute()

if __name__ == '__main__':
    main()
