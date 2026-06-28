from dotenv import load_dotenv
import os
import time
import databento as db
import pandas as pd
import numpy as np
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Thread

def get_front_month(data: pd.DataFrame) -> pd.DataFrame:
    #Because the raw data will have multiple entries per day with different 
    #front months. So you group them by the day.
    groups = data.groupby('ts_event')
    
    #Look at only the volume column
    volume_per_group = groups['volume']
    
    #Get the indices of the max volume of that day
    idx_of_max_volume = volume_per_group.idxmax()

    #Use the indices to select one row for that date, because thats the front
    # month contract.
    frontMonth = data.loc[idx_of_max_volume]
    

    #Set the date as the index again, like it was
    frontMonth = frontMonth.set_index('ts_event')

    return frontMonth


"""
Find the correlation between two instruments returns.
"""
def find_rolling_correlation(data: pd.DataFrame, first: str, second: str) -> pd.Series:
    # This is going to be used to strip the rows that are aggregates.
    firstMatchStr = f'^{first}[A-Z]\\d+$'
    secondMatchStr = f'^{second}[A-Z]\\d+$'
    
    #Get the data
    firstData = data[data['symbol'].str.match(firstMatchStr)]
    secondData = data[data['symbol'].str.match(secondMatchStr)]

    # Need to reset the index because you just took it away
    firstData = firstData.reset_index()
    secondData = secondData.reset_index()
    
    # If I don't do this I get 3 entries for each day, because there are
    # 3 contracts of the same symbol that may be available for that day.
    # So get the front month contract's entry, as that has the most volume.
    firstFront = get_front_month(firstData)
    secondFront = get_front_month(secondData)
    
    firstReturns = firstFront['close'].pct_change().dropna()
    secondReturns = secondFront['close'].pct_change().dropna()
    
    #This error is fine
    rollingCorr = firstReturns.rolling(30).corr(secondReturns)
    
    """
    TODO: Figure out why Im getting this warning. But the error is ok.
    The function still works.
    """
    return rollingCorr
    
class IBData(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.done = False


    def historicalData(self, reqId: int, bar):
        self.data.append([bar.date, bar.open, bar.open, bar.high, bar.low, bar.close,
                          bar.volume])
    

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        self.done = True


def run_loop(app):
    app.run()

#connect to databroker
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "bento.env"), verbose=True)

databentokey = os.getenv("DATABENTO_KEY")
client = db.Historical(databentokey)


data = db.DBNStore.from_file("../../../research/GLBX-20260613-H7HPD8PCNX/glbx-mdp3-20100606-20250924.ohlcv-1d.dbn.zst")

symbols = ["ES", "NQ"]
running = True
dataDf = data.to_df()



# Set up IB API Client
app = IBData()
app.connect("127.0.0.1", 7496, clientId=1)
api_thread = Thread(target=run_loop, args=(app,), daemon=True)
api_thread.start()

time.sleep(1)

# Define DBMF contract
contract = Contract()
contract.symbol = "DBMF"
contract.secType = "STK"
contract.exchange = "ARCA"
contract.currency = "USD"

# Request daily historical data from 2019-01-01 to now
end_date = ""
duration_str = "5 Y"    # Get up to 5 years of data
bar_size = "1 day"

app.reqHistoricalData(
    reqId=1,
    contract=contract,
    endDateTime=end_date,
    durationStr=duration_str,
    barSizeSetting=bar_size,
    whatToShow="TRADES",
    useRTH=1,
    formatDate=1,
    keepUpToDate=False,
    chartOptions=[]
)

timeout = 20   # seconds

t0 = time.time()
while not app.done and (time.time() - t0) < timeout:
    time.sleep(0.2)
