from fastapi import FastAPI
from pydantic import BaseModel

from .ibconnect import IBAPI

app = FastAPI()


#Create an object to interactive with IB TWS API
ib_api = IBAPI()



#FastAPI automatically reads a JSON payload from request body and converts it to
#specified pydantic model. So I need to define them for the post requests.
class OrderEntry(BaseModel):
    ticker: str
    exchange: str
    secType: str
    price: float
    action: str
    orderType: str 

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/status")
def getConnectionStatus():
    return {"res": ib_api.connected_flag}



@app.get("/api/account/value")
def getAccountValue():
    return {"res": ib_api.getNetLiquidation()}


@app.get("/api/account/portfolio")
def getPortfolio():
    return {"res": ib_api.getPortfolio()}


@app.post("/api/order")
def createOrder(order: OrderEntry):
    pass
