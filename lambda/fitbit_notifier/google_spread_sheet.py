from secret_manager import SecretManager
from oauth2client.service_account import ServiceAccountCredentials
import json
import gspread

class Google_SpreadSheet:

    def __init__(self, secret_name):
        self.secret_name = secret_name
        self.gspread = self.__get_spreadsheetClient()

    # spreadsheetClientを取得
    def __get_spreadsheetClient(self):
        secret = SecretManager(self.secret_name).get()
        cred = ServiceAccountCredentials.from_json_keyfile_dict(secret, scopes=gspread.auth.DEFAULT_SCOPES)
        gc = gspread.authorize(cred)
        return gc
    
    # spreadsheetの最終行のセルを取得
    def get_last_rows(self, spreadsheet_name, worksheet_name):
        sheets = self.gspread.open(spreadsheet_name)
        sheet = sheets.worksheet(worksheet_name)
        last_row_number = len(list(filter(None, sheet.col_values(1))))
        return sheet.row_values(last_row_number)
