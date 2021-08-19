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
import pytz

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

class actionOrder(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        self.signal =False # For placing Order
        self.entrtprice = 0
        self.hsi_position = 0
        self.signal, self.action, self.qty, self.orderType = getstrategy(2, "MKT")
        self.symbol, self.secType, self.currency, self. exchange, self.lastTradeDateOrContractMonth = gettradeproduct("HSI", "FUT", "HKD", "HKFE", "20210830")

        self.tgBot = telegramBot()

    def error(self,reqId,errorCode,errorString):
        print(datetime.fromtimestamp(int(datetime.now().timestamp())),'Error: ',reqId,' ',errorCode,' ',errorString)
        return

    def nextValidId(self, orderId):
        self.nextOrderId = orderId
        return


    def realtimeBar(self, reqId, time:int, open_: float, high: float, low: float, close: float,volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        print("RealTimeBar. TickerId:", reqId, (time, -1, open_, high, low, close, volume, wap, count))
        self.entryprice = round(int(open_))

        if self.signal != False and self.hsi_position == 0:
            self.actionOrder()
            entry_message = ("Oredr: " + str(self.action) + " At " + str(self.entryprice))
            self.tgBot.sendSignal(entry_message)   # telegramBot send notification
            print(entry_message)
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

    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()
        return


class coverOrder(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        self.entrtprice = 0
        self.hsi_position = 0
        self.signal, self.action, self.qty, self.orderType = getstrategy(2, "MKT")
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
            print(self.hsi_position)

    def positionEnd(self):
        super().positionEnd()
        # print("PositionEnd")

    def realtimeBar(self, reqId, time:int, open_: float, high: float, low: float, close: float,volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        print("RealTimeBar. TickerId:", reqId, (time, -1, open_, high, low, close, volume, wap, count))
        self.coverprice = round(int(close))
        print(self.signal, self.hsi_position)

        if self.signal != False and self.hsi_position != 0:
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

    def coverOrder(self):
        contract = Contract()
        contract.symbol = self.symbol
        contract.secType = self.secType
        contract.currency = self.currency
        contract.exchange = self.exchange
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

    def stop(self):
        self.reqAccountUpdates(False, "")
        self.done = True
        self.disconnect()
        return


#----------------------------------------------------------------------------------------------------------------------#

def ib_main_action():
    app = actionOrder()
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

    app.reqRealTimeBars(1, contract, 1, "MIDPOINT", False, [])
    app.reqPositions()

    """app.reqMktData(1, contract, "", False, False, [])
    app.reqAllOpenOrders()"""
    Timer(3, app.stop).start()
    app.run()


def ib_main_cover():
    app = coverOrder()
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

    app.reqRealTimeBars(1, contract, 1, "MIDPOINT", False, [])
    app.reqPositions()

    """app.reqMktData(1, contract, "", False, False, [])
    app.reqAllOpenOrders()"""
    Timer(3, app.stop).start()
    app.run()

if __name__=="__main__":
    local_tz = pytz.timezone("Asia/Hong_Kong")
    while True:
        live_hour = datetime.now(local_tz).hour
        live_mins = datetime.now(local_tz).minute
        live_second = datetime.now(local_tz).second
        time.sleep(1)
        try:
            if live_hour == 22 and live_mins == 3 and live_second == 0:
                ib_main_action()
            elif live_hour == 22 and live_mins == 5 and live_second == 0:
                ib_main_cover()
            else:
                print("Nothing Happen")
                print(live_second)
                pass
        except EOFError as e:
            print(datetime.fromtimestamp(int(datetime.now().timestamp())), 'main() error due to :', type(e), e)