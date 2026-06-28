from fastapi import FastAPI

app = FastAPI()


#Create an object to interactive with IB TWS API


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/api/tws/status")
def getConnectionStatus():
    return {"res": True}
