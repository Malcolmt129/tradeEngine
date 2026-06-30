from fastapi import FastAPI

from ibconnect import IBAPI

app = FastAPI()


#Create an object to interactive with IB TWS API
ib_api = IBAPI()

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
