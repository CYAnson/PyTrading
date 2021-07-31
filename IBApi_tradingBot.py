import os
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.ticktype import TickTypeEnum
from threading import Timer
import pandas as pd
import threading
import time
from datetime import datetime
from telegramBot import telegramBot

def getstrategy(qty, orderType):

    #signal_indicator = int(os.environ.get('signal'))

    #signal_indicator = int(-1)

    signal_indicator = 1

    if signal_indicator == 1:
        signal = True
        action = "BUY"
    elif signal_indicator == -1:
        signal = True
        action = "SELL"
    else:
        signal = False
        action = ""

    signal = signal
    action = action

    #signal = True
    #action = "Buy"
    qty = qty
    ordertype = orderType
    return signal, action, qty, ordertype

def gettradeproduct(symbol, secType, currency, exchange, lastTradeDateOrContractMonth):
    return symbol, secType, currency, exchange, lastTradeDateOrContractMonth

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []  # Historical

        self.signal =False # For placing Order
        self.entrtprice = 0
        self.hsi_position = 0
        self.signal, self.action, self.qty, self.orderType = getstrategy(1, "MKT")
        self.symbol, self.secType, self.currency, self. exchange, self.lastTradeDateOrContractMonth = gettradeproduct("HSI", "FUT", "HKD", "HKFE", "20210830")

        self.tgBot = telegramBot()

    def error(self,reqId,errorCode,errorString):
        print(datetime.fromtimestamp(int(datetime.now().timestamp())),'Error: ',reqId,' ',errorCode,' ',errorString)
        return

    def nextValidId(self, orderId):
        self.nextOrderId = orderId
        return

    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        if contract.symbol == "HSI":
            self.hsi_position = position
            #print(self.hsi_position)

    def positionEnd(self):
        super().positionEnd()
        #print("PositionEnd")

    """def tickPrice(self, reqId, tickType, price, attrib):
        #if TickTypeEnum.to_str(tickType) == "CLOSE": # eg: tickType = 1 (1=bid, 2=ask, 4=last, 6=high, 7=low, 9=close)
        #print('Tick Price.Ticker Id:', reqId, 'tickType:', TickTypeEnum.to_str(tickType), 'Price:', price)

        if TickTypeEnum.to_str(tickType) == "ASK" and int(price) != 0:
            self.askprice = int(price)

        if TickTypeEnum.to_str(tickType) == "BID" and int(price) != 0:
            self.bidprice = int(price)

        if self.signal != False and self.hsi_position == 0:
            self.actionOrder()
            print("Oredr: " + str(self.action) + " At " + str(self.entryprice))
        elif self.signal != False and self.hsi_position != 0:
            if self.hsi_position > 0:
                self.coverOrder()
                print("Cover: " + str(self.action) + " At " + str(self.entryprice))
            else:
                self.coverOrder()
                print("Cover: " + str(self.action) + " At " + str(self.entryprice))
        else:
            print("No Signal Generated")
            pass
        return"""

    def realtimeBar(self, reqId, time:int, open_: float, high: float, low: float, close: float,volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        print("RealTimeBar. TickerId:", reqId, (time, -1, open_, high, low, close, volume, wap, count))
        print("MIDPOINT price: " + str(close))
        self.entryprice = round(int(open_))
        self.coverprice = round(int(close))

        if self.signal != False and self.hsi_position == 0:
            self.actionOrder()
            entry_message = ("Oredr: " + str(self.action) + " At " + str(self.entryprice))
            self.tgBot.sendSignal(entry_message)   # telegramBot send notification
            print(entry_message)
        elif self.signal != False and self.hsi_position != 0:
            if self.hsi_position > 0:
                self.coverOrder()
                cover_message1 = ("Cover: " + str(self.action) + " At " + str(self.coverprice))
                self.tgBot.sendSignal(cover_message1)   # telegramBot send notification
                print(cover_message1)
            else:
                self.coverOrder()
                cover_message2 = ("Cover: " + str(self.action) + " At " + str(self.coverprice))
                self.tgBot.sendSignal(cover_message2)   # telegramBot send notification
                print(cover_message2)
        else:
            print("No Signal Generated")
            pass
        return

    def actionOrder(self):
        contract = Contract()
        contract.symbol = self.symbol
        contract.secType = self.secType
        contract.currency = self.currency
        contract.exchange = self. exchange
        contract.lastTradeDateOrContractMonth = self.lastTradeDateOrContractMonth

        order = Order()
        order.signal = self.signal
        order.action = self.action
        order.totalQuantity = self.qty
        order.lmtPrice = self.entryprice
        order.orderType = self.orderType
        order.OutsideRth = True
        self.placeOrder(self.nextOrderId, contract, order)
        # Update Portfolio
        self.reqAccountUpdates(True, "")
        return

    def coverOrder(self):
        contract = Contract()
        contract.symbol = self.symbol
        contract.secType = self.secType
        contract.currency = self.currency
        contract.exchange = self. exchange
        contract.lastTradeDateOrContractMonth = self.lastTradeDateOrContractMonth

        cover = Order()
        cover.signal = self.signal
        cover.action = "SELL"
        cover.totalQuantity = self.hsi_position
        cover.lmtPrice = self.coverprice
        cover.orderType = self.orderType
        cover.OutsideRth = True

        if self.hsi_position > 0:
            pass
        else:
            cover.action = "BUY"
            cover.lmtPrice = self.coverprice
            cover.totalQuantity = self.hsi_position * -1

        self.placeOrder(self.nextOrderId, contract, cover)
        # Update Portfolio
        self.reqAccountUpdates(True, "")
        print(self.hsi_position)
        return

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,averageCost: float,unrealizedPNL: float, realizedPNL: float, accountName: str):
        """print(datetime.fromtimestamp(int(datetime.now().timestamp())), 'UpdatePortfolio.', 'Symbol:', contract.symbol,
              'SecType:', contract.secType, 'Exchange:', contract.exchange, 'Position:', position, 'MarketPrice:',
              marketPrice, 'MarketValue:', marketValue, 'AverageCost:', averageCost, 'UnrealizedPNL:', unrealizedPNL,
              'RealizedPNL:', realizedPNL, 'AccountName:', accountName)"""
        return


    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()
        return

#----------------------------------------------------------------------------------------------------------------------#

def ib_main():
    app = TestApp()
    app.nextOrderId = 0
    app.connect('127.0.0.1', 7496, 0)

    symbol, secType, currency, exchange, lastTradeDateOrContractMonth = gettradeproduct("HSI", "FUT", "HKD", "HKFE", "20210830")

    contract = Contract()
    contract.symbol = symbol
    contract.secType = secType
    contract.currency = currency
    contract.exchange = exchange
    contract.lastTradeDateOrContractMonth = lastTradeDateOrContractMonth

    # Call stop() after 3 seconds to disconnect the program

    app.reqMktData(1, contract, "", False, False, [])
    app.reqRealTimeBars(1, contract, 1, "MIDPOINT", False, [])
    app.reqPositions()
    Timer(3, app.stop).start()
    app.run()

if __name__=="__main__":
    while True:
        try:
            ib_main()
        except EOFError as e:
            print(datetime.fromtimestamp(int(datetime.now().timestamp())), 'main() error due to :', type(e), e)
        time.sleep(10)