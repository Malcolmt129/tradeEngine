from threading import Thread, Event
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class IBAPI(EWrapper, EClient):

    def __init__(self):

        EWrapper.__init__(self)
        EClient.__init__(self, self)

        self.data = []
        self.connected_flag = False
        self.done = False
        self.api_thread = None
        self.nextOrderID = None
        self.nextReqID = 1
        self.net_liquidation = None
        self._net_liq_event = Event()
        self.portfolio: list[dict] = []
        self._portfolio_event = Event()
        

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
   
    
    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
        if key == "NetLiquidation":
            self.net_liquidation = float(val)
            self._net_liq_event.set()

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

    def accountDownloadEnd(self, accountName: str):
        self._portfolio_event.set()

    def getPortfolio(self, timeout: float = 5.0) -> list[dict]:
        self._portfolio_event.wait(timeout=timeout)
        return self.portfolio

    def getNetLiquidation(self, timeout: float = 5.0) -> float | None:
        self._net_liq_event.wait(timeout=timeout)
        return self.net_liquidation
