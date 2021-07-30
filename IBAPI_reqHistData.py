from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

import threading
import time


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def historicalData(self, reqId, bar):
        print(f'Time: {bar.date} Close: {bar.close}')


def main():
    app = IBapi()
    app.connect('127.0.0.1', 7497, 0)

    # Create contract object
    HSI_contract = Contract()
    HSI_contract.symbol = 'HSI'
    HSI_contract.secType = 'FUT'
    HSI_contract.exchange = 'HKFE'
    HSI_contract.currency = 'HKD'
    HSI_contract.lastTradeDateOrContractMonth = "202007"
    HSI_contract.multiplier = "50"

    # Request historical candles
    app.reqMarketDataType(2)
    app.reqHistoricalData(1, HSI_contract, '', '2 Y', '1 day', 'MIDPOINT', 0, 1, False, [])
    time.sleep(10)
    app.run()
    app.disconnect()

