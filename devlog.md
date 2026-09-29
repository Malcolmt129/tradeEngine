


I need to have a way to format time and check the time format.

Something else that I need to consider is setting the timezone to use in the 
TWS API, for all requests... I think:

https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-date-formatting/operator-time-zone


========= Resolved

There is a way to access the earliest data point. I need to take advantage of that:

https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/finding-the-earliest-available-data-point/requesting-the-earliest-data-point

========== Resolved

My historical-date-formatting isnt working as intended. Im a couple days short of where I should be on the day count.
This could mean that the duration string only counts trading days. Just keep this in mind.

============== Unresolved
Lets start with the idea of getting data by the type of contract. It seems like for futures I have to do something different
compared to stocks. So what is a good way of splitting this up. We dont need the best way off rip:

- I could have a route for each type... I dont like this. 
- I could have a struct and if certain parts of the struct are there, say like a contract expiry, that means its a future
so I should do such and such to get the data. I think I like this one.

How the algorithm will go:

1) Get all the front months for the time period. Most of them will be expired, so I need to request contract details.

============= Unresolved
