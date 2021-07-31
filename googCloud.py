import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import  ServiceAccountCredentials
from datetime import datetime, timedelta
import time

class googCloud():

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(r'E:\Github\PyTrading\PyTrading/resounding-net-291613-c7c0f14f4421.json',scope)
    goog_credentials = gspread.authorize(credentials)

    def get_goog_SheetValue(self, goog_spread, goog_slide):
        gc = self.goog_credentials
        sh = gc.open(goog_spread)
        ws = sh.worksheet(goog_slide)
        cell_value = ws.acell('B2').value
        print(cell_value)
        return cell_value



if __name__ == "__main__":
    gc = googCloud()
    gc.get_goog_SheetValue("程式交易紀錄", "Home")