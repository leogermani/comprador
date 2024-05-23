# app/spreadsheet.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import Config
import os

class Spreadsheet:
    def __init__(self):

        credentials_path = os.path.dirname(__file__) + '/service-account.json'

        # Set up Google Sheets API credentials
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, scope)
        client = gspread.authorize(creds)

        # Open the Google Spreadsheet
        sheet = client.open_by_key( Config.SHEETS_SPREADSHEET_ID )
        self.products_sheet = sheet.worksheet( Config.PRODUCTS_SHEET_NAME )

    def get_products(self):
        products = self.products_sheet.col_values(2)
        return products[2:]

