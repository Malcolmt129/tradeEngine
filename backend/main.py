from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from . import historydb
from .ibconnect import IBAPI

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ib_api
    historydb.init_db()
    ib_api = IBAPI()
    yield
    ib_api.disconnect()


app = FastAPI(lifespan=lifespan)


# FastAPI automatically reads a JSON payload from request body and converts it to
# specified pydantic model. So I need to define them for the post requests.
class OrderEntry(BaseModel):
    ticker: str
    exchange: str
    secType: str
    quantity: int
    price: float
    action: str
    orderType: str
    contractExpiry: str


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


@app.get("/api/historical")
def getHistoricalData(
    ticker: str,
    exchange: str,
    secType: str,
    startDate: str,
    endDate: str,
    barSize: str = "1 day",
    whatToShow: str = "TRADES",
    useRTH: bool = True,
    contractExpiry: str = "",
):

    endDateTime, duration = historydb.daterange_to_ib_params(startDate, endDate)
    print(duration)
    try:
        bars = ib_api.getHistoricalData(
            ticker=ticker,
            exchange=exchange,
            secType=secType,
            endDateTime=endDateTime,
            duration=duration,
            barSize=barSize,
            whatToShow=whatToShow,
            useRTH=useRTH,
            contractExpiry=contractExpiry,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"res": bars, "source": "ib"}


@app.post("/api/order")
def placeManualOrder(order: OrderEntry):
    try:
        result = ib_api.submitOrder(
            ticker=order.ticker,
            exchange=order.exchange,
            secType=order.secType,
            action=order.action,
            orderType=order.orderType,
            quantity=order.quantity,
            price=order.price,
            contractExpiry=order.contractExpiry,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if result["status"] == "Error":
        raise HTTPException(status_code=400, detail=result)

    return result
