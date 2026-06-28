import pandas as pd



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
