from fastapi import FastAPI
from dotenv import load_dotenv
import os
import databento as db
import sqlite3

app = FastAPI()

#getdata

#connect to databroker
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "bento.env"), verbose=True)

databentokey = os.getenv("DATABENTO_KEY")
client = db.Historical(databentokey)

databaseName = os.getenv("DATABASE_TEST")
#connect to database

#This error is ok
databaseConn = sqlite3.connect(databaseName)


messageBus = []

"""
Lets try to balance the fidelity portfolio. As of now there isno way to connect to the brokerage and actually make trades.
But what can happen is that we use statistical research to seewhich products are correlated and what we could do to bala


"""
    





def getHistoricalData():
    #What to query
    dbentoDataset = "GLBX.MDP3"
    schema = "ohlcv-1d"
    stypeIn = "continuous"
    contract = "ES.c.0"
    startDate = "2025-01-01"

    #When I start to use time, It's going to have to be in the
    # following forms:
    # yyyy-mm-dd
    #or ^ the THH:MM:SS.NNNNNNNN S and N are optional


    #This confirms that the current query items are correct.
    timeSeriesDataCost = client.metadata.get_cost(
            dataset=dbentoDataset,
            symbols=contract,
            stype_in=stypeIn,
            schema=schema,
            start=startDate,
            )



def goingLive():
    client = db.Live(key=databentokey)

    client.subscribe(
            dataset="GLBX.MDP3",
            schema="trades",
            stype_in="parent",
            symbols="ES.FUT"
            ) 


