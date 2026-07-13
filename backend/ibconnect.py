from threading import Thread, Event
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

class IBAPI(EWrapper, EClient):

    def __init__(self):

        EWrapper.__init__(self)
        EClient.__init__(self, self)

        self.data = []
        self.connected_flag = False
        self.done = False
        self.api_thread = None
        self.nextOrderId = None
        self.nextReqID = 1
        self.net_liquidation = None
        self._net_liq_event = Event()
        self.portfolio: list[dict] = []
        self._portfolio_event = Event()

        self._order_events: dict[int, Event] = {}
        self._order_results: dict[int, dict] = {}
        
        self.timeout: float = 5.0  

        self.connectApi()

    def connectApi(self):

        try:
            if not self.connected_flag:
                self.connect("127.0.0.1", 7497, clientId=1)
                self.api_thread = Thread(target=self.run_loop, daemon=True)
                self.api_thread.start()
                
        except Exception as e:
            print(f"[Error] Connection Failed: {e}")
    

    def nextValidId(self, orderId):
        """Called when connection is fully established"""
        self.nextOrderId = orderId
        self.connected_flag = True
        print(f"[IB] Next valid order ID: {orderId}")
        print("[Connected] IBKR API connection established.")
                # Request account updates now that connection is ready
        self.reqAccountUpdates(True, "")

    def run_loop(self):
        self.run()

    def error(self, reqId, errorCode, errorString):
        print(f"[Error] reqId={reqId} code={errorCode} msg={errorString}")
        if reqId in self._order_events:
            self._order_results[reqId] = {
                "orderId": reqId,
                "status": "Error",
                "errorCode": errorCode,
                "errorMessage": errorString,
            }
            self._order_events[reqId].set()
    

    # API function
    def orderStatus(self, orderId, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str, mktCapPrice: float):
        if orderId in self._order_events:
            self._order_results[orderId] = {
                "orderId": orderId,
                "status": status,
                "filled": filled,
                "remaining": remaining,
                "avgFillPrice": avgFillPrice,
            }
            self._order_events[orderId].set()

        
    
    # API function
    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        if key == "NetLiquidation":
            self.net_liquidation = float(val)
            self._net_liq_event.set()
    
    
    #API function
    def updatePortfolio(self, contract: Contract, position: float, 
                        marketPrice: float, marketValue: float, 
                        averageCost: float, unrealizedPNL: float,
                        realizedPNL: float, accountName: str):

        self.portfolio = [p for p in self.portfolio if p["symbol"] != contract.symbol]
        self.portfolio.append({
            "symbol": contract.symbol,
            "secType": contract.secType,
            "position": position,
            "marketPrice": marketPrice,
            "marketValue": marketValue,
            "averageCost": averageCost,
            "unrealizedPNL": unrealizedPNL,
            "realizedPNL": realizedPNL,
            "accountName": accountName,
        })
    
    #API function
    def accountDownloadEnd(self, accountName: str):
        self._portfolio_event.set()
    
    #API function
    def getPortfolio(self) -> list[dict]:
        self._portfolio_event.wait(timeout=self.timeout)
        return self.portfolio
    
    #API function
    def getNetLiquidation(self) -> float | None:
        self._net_liq_event.wait(timeout=self.timeout)
        return self.net_liquidation

    

    def submitOrder(self, ticker: str, exchange: str, secType:str,
                    action: str, orderType: str, quantity: int,
                    price: float, contractExpiry: str = "") -> dict:


        if self.nextOrderId is None:
            raise RuntimeError("Cannot submit order: nextOrderId is not set(IB is not connected)")

        orderId = self.nextOrderId
        self.nextOrderId += 1

        contract = Contract()
        contract.symbol = ticker
        contract.secType = secType
        contract.exchange = exchange
        contract.currency = "USD"

        if contract.secType == "FUT":
            contract.lastTradeDateOrContractMonth = contractExpiry

        print(contract)
        order = Order()
        order.action = action.upper()
        order.orderType = orderType.upper()
        order.totalQuantity = quantity
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        order.tif = "DAY"

        if order.orderType == "LMT":
            order.lmtPrice = price
            

        event = Event()
        self._order_events[orderId] = event

        self.placeOrder(orderId, contract, order)

        print(f"[Order Submitted]{order.action} {order.totalQuantity} {contract.symbol} {order.orderType}")

        event.wait(timeout=self.timeout)
        self._order_events.pop(orderId, None)
        result = self._order_results.pop(orderId, None)

        if result is None:
            result = {"orderId": orderId, "status": "Unknown"}

        return result
 
