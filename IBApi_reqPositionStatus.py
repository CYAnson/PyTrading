from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
from threading import Timer

import pandas as pd
import time


class IBapi(EWrapper, EClient):


    def __init__(self):
        EClient.__init__(self, self)

        self.all_positions = pd.DataFrame([], columns=['Account', 'ConID', 'Symbol', 'Sec Type', 'Exchange', 'Currency','Quantity', 'Average Cost'])

    def error(self, reqId, errorCode, errorString):
        print('Error: ', reqId, ' ', errorCode, ' ', errorString)

    def position(self, account, contract, pos, avgCost):
        index = str(account) + str(contract.symbol)
        self.all_positions.loc[index] = account, contract.conId, contract.symbol, contract.secType, contract.exchange, contract.currency, pos, avgCost

    def positionEnd(self):
        self.disconnect()

    def pnlSingle(self, reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value):
        print(dailyPnL, unrealizedPnL, realizedPnL, value)


def main():

    app = IBapi()
    app.nextOrderId = 0
    app.connect('127.0.0.1', 7497, 0)
    app.reqPositions()
    current_positions = app.all_positions

    app.run()
    print(current_positions.to_string())



