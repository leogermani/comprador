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
        self.sheet = client.open_by_key( Config.SHEETS_SPREADSHEET_ID )

        # memoization
        self.suppliers = None
        self.products = None
        self.items_suppliers = None

    def get_products(self):
        if self.products:
            return self.products
        products_sheet = self.sheet.worksheet( Config.PRODUCTS_SHEET_NAME )
        products = products_sheet.col_values(2)
        self.products = products[2:]
        return products[2:]

    def get_suppliers(self):
        if self.suppliers:
            return self.suppliers

        print("fetching suppliers")
        suppliers_sheet = self.sheet.worksheet( Config.SUPPLIERS_SHEET_NAME )
        suppliers = suppliers_sheet.get_all_values()
        first = True
        suppliers_dict = {}
        for supplier in suppliers:
            if first:
                first = False
                continue

            item = {}
            item['name'] = supplier[0]
            item['CNPJ'] = supplier[1]
            item['contato'] = supplier[3]
            item['phone'] = supplier[4]
            item['items'] = []

            suppliers_dict[supplier[1]] = item

        self.suppliers = suppliers_dict
        return suppliers_dict

    def get_items_suppliers(self):
        if self.items_suppliers:
            return self.items_suppliers

        products_sheet = self.sheet.worksheet( Config.PRODUCTS_SHEET_NAME )
        products = products_sheet.get_all_values()
        first = True
        second = True
        items_suppliers = {}
        suppliers_indexes = {}
        for product in products:
            if first:
                first = False
                continue

            if second:
                for i in range(2, len(product)):
                    suppliers_indexes[i] = product[i]
                second = False
                continue

            items = []

            for i in range(2, len(product)):
                if product[i] == 'x':
                    supplier = suppliers_indexes[i]
                    items.append(supplier)


            items_suppliers[product[1]] = items

        self.items_suppliers = items_suppliers
        return items_suppliers

    def get_suppliers_for_item(self, item):
        items_suppliers = self.get_items_suppliers()
        cnpjs = items_suppliers[item]
        suppliers = self.get_suppliers()
        return [suppliers[cnpj] for cnpj in cnpjs]

