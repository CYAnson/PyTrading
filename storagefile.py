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

"""--------------------------------------------------------------------------------------------------------------------"""

''' def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,averageCost: float,unrealizedPNL: float, realizedPNL: float, accountName: str):
     """print(datetime.fromtimestamp(int(datetime.now().timestamp())), 'UpdatePortfolio.', 'Symbol:', contract.symbol,
           'SecType:', contract.secType, 'Exchange:', contract.exchange, 'Position:', position, 'MarketPrice:',
           marketPrice, 'MarketValue:', marketValue, 'AverageCost:', averageCost, 'UnrealizedPNL:', unrealizedPNL,
           'RealizedPNL:', realizedPNL, 'AccountName:', accountName)"""
     return

 def orderStatus(self, orderId: int, status:str, filled: float, remaining: float, avgFillPrice: float, permId: int,
                 parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
     super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
     openOrder = "OrderStatus. Id:", orderId, "Status:", status, "Filled Order:", filled, "Remaining:", remaining, "AvgFillPrice:", avgFillPrice
     print(openOrder)
     self.tgBot.sendSignal(openOrder)'''


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

    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        if contract.symbol == "HSI":
            self.hsi_position = position
            #print(self.hsi_position)

    def positionEnd(self):
        super().positionEnd()
        #print("PositionEnd")


    def realtimeBar(self, reqId, time:int, open_: float, high: float, low: float, close: float,volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        print("RealTimeBar. TickerId:", reqId, (time, -1, open_, high, low, close, volume, wap, count))
        self.entryprice = round(int(open_))

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