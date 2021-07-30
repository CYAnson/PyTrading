from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
import pandas as pd
import time


class IBapi(EWrapper, EClient):


    def __init__(self):
        EClient.__init__(self, self)
        self.all_positions = pd.DataFrame([], columns=['contract.conId', 'contract.symbol', 'position',
                                                       'averageCost', 'marketPrice', 'marketValue', 'unrealizedPNL', 'realizedPNL'])

    #iswrapper
    def updateAccountValue(self, key:str, val:str, currency:str,accountName:str):
        pass
    #iswrapper
    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,averageCost: float, unrealizedPNL: float, realizedPNL:float, accountName:str):
        super().updatePortfolio(contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName)
        #print(contract.conId, contract.symbol, position, averageCost, marketPrice, marketValue, unrealizedPNL, realizedPNL)
        index = str(contract.conId)
        print(index)
        self.all_positions.loc[index] = contract.conId, contract.symbol, position, averageCost, marketPrice, marketValue, unrealizedPNL, realizedPNL

    #iswrapper
    def updateAccountTime(self, timeStamp:str):
        pass
    #iswrapper
    def accountDownloadEnd(self, accountName:str):
        self.disconnect()

def main():

    app = IBapi()
    app.connect('127.0.0.1', 7497, 0)

    #isECclient
    app.reqAccountUpdates(True, "XXXXXXXX")
    current_positions = app.all_positions
    app.run()
    print(current_positions.to_string())


if __name__ == "__main__":
    main()

