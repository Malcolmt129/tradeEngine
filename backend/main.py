from dotenv import load_dotenv
import os
import databento as db
import pandas as pd
import numpy as np

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

#connect to databroker
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "bento.env"), verbose=True)

databentokey = os.getenv("DATABENTO_KEY")
client = db.Historical(databentokey)


data = db.DBNStore.from_file("../../../research/GLBX-20260613-H7HPD8PCNX/glbx-mdp3-20100606-20250924.ohlcv-1d.dbn.zst")

symbols = ["ES", "NQ"]
dataDf = data.to_df()

es_data = dataDf[dataDf['symbol'].str.match(r'^ES[A-Z]\d+$')]
nq_data = dataDf[dataDf['symbol'].str.match(r'^NQ[A-Z]\d+$')]

# Reset index so ts_event is a column we can groupby cleanly
es_data = es_data.reset_index()
nq_data = nq_data.reset_index()

# Pick highest volume row per date, this has been confirmed to get me what I'm
# looking for. All of the days only have one entry for the front month and it 
# rolls over to the next contract. It isn't back adjusted but it doesn't have
# to be right now. 
es_front = get_front_month(es_data) 
nq_front = get_front_month(nq_data) 

es_returns = es_front['close'].pct_change().dropna()
nq_returns = nq_front['close'].pct_change().dropna()

#This error is fine
correlation = es_returns.corr(nq_returns)
print(f"ES vs NQ return correlation: {correlation:.4f}")


