from ibapi.client import EClient
from ibapi.common import RealTimeBar
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
from ibapi.order import Order
from myutils import *
import time


class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.started = False
        self.nextValidOrderId = None
        self.series_slow = []
        self.ma_slow = 0
        self.ibcontract = None
        self.all_positions = pd.DataFrame([], columns=['Account', 'Symbol', 'Quantity', 'Average Cost', 'Sec Type'])

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)
    # ! [nextvalidid]

        self.ibcontract = Contract()
        self.ibcontract.secType = "FUT"
        self.ibcontract.lastTradeDateOrContractMonth = 202004
        self.ibcontract.currency = "USD"
        self.ibcontract.symbol = "GC"
        self.ibcontract.exchange = "NYMEX"

        # we can start now
        self.start()

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    def tickPrice(self, reqId, tickType, price: float,
                  attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        print("TickPrice. TickerId:", reqId, "tickType:", tickType,
              "Price:", price, "CanAutoExecute:", attrib.canAutoExecute,
              "PastLimit:", attrib.pastLimit, end=' ')
    # ! [tickprice]

    # ! [ticksize]
    def tickSize(self, reqId, tickType, size: int):
        super().tickSize(reqId, tickType, size)
        print("TickSize. TickerId:", reqId, "TickType:", tickType, "Size:", size)
    # ! [ticksize]

    # ! [realtimebar]
    def realtimeBar(self, reqId, time:int, open_: float, high: float, low: float, close: float,
                        volume: int, wap: float, count: int):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        print("hit")
        print("RealTimeBar. TickerId:", reqId, RealTimeBar(time, -1, open_, high, low, close, volume, wap, count))

        if len(self.series_slow) < 5:
            self.series_slow.append(close)
        else:
            self.series_slow.pop(0)
            self.series_slow.append(close)
            self.ma_slow = sum(self.series_slow)/5

            if close > self.ma_slow:
                print("place order")
                o = mkt_order("BUY", 1)
                self.placeOrder(self.nextOrderId(), self.ibcontract, o)
            else:
                print("skip")

        print("moving average: ", str(self.ma_slow))
        print(self.series_slow)

    # ! [realtimebar]

    def realTimeBarsOperations_req(self):
        # Requesting real time bars
        # ! [reqrealtimebars]

        self.reqRealTimeBars(3001, self.ibcontract, 5, "MIDPOINT", False, [])
        # ! [reqrealtimebars]

    def position(self, account: str, contract: Contract, position: float,
                 avgCost: float):
        super().position(account, contract, position, avgCost)
        index = str(account) + str(contract.symbol)
        self.all_positions.loc[index] = account, contract.symbol, position, avgCost, contract.secType
        print("Position.", "Account:", account, "Symbol:", contract.symbol, "SecType:",
              contract.secType, "Currency:", contract.currency,
              "Position:", position, "Avg cost:", avgCost)

    def positionEnd(self):
        super().positionEnd()
        print("PositionEnd")

    def start(self):
        if self.started:
            return

        self.started = True

        ibcontract = Contract()
        ibcontract.secType = "FUT"
        ibcontract.lastTradeDateOrContractMonth = 202004
        ibcontract.currency = "USD"
        ibcontract.symbol = "GC"
        ibcontract.exchange = "NYMEX"

        self.reqPositions()
        print("request done")
        print(self.all_positions)
#        self.realTimeBarsOperations_req()
#        self.reqMarketDataType(1)
#        self.reqMktData(1, ibcontract, "", False, False, [])


def main():
    app = TestApp()
    app.connect("127.0.0.1", 7497, 0)


#    app.reqMarketDataType(4)
#    app.reqMktData(1, contr, "", False, False, [])
#    app.reqRealTimeBars(3001, contr, 5, "MIDPOINT", False, [])

    app.run()

if __name__ == '__main__':
    main()
