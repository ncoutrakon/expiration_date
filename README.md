# expiration_date
For a predefined set of assets and expiration months, the logic will return the exact calendar date on which the contract expires and trading ceases.

**Contracts.csv** is a list of trading contracts of the format "XXX11", where "XXX" is a three-letter abbreviation for the month and "11" are the last two digits of the year.

**Holidays.csv** is a table of holidays observed for each asset ID.

**Rules.csv** is a table of the parameters for each asset id. It contains the rules for determining how each asset will expire.


All assets are grouped into one of three categories based on how the expire: fixed, relative, or biz. They all take similar parameters but vary slightly.



###Fixed
#####References a specific calendar date.
*num_day* is a specific calendar day. (i.e. the 25th, the last day, the first day)
*days_before*, how many days before the num_day
*months_before*, if expiration falls in any of previous months, also used for expirations relative to First calendar day
*succeed*, if num_day is a holiday or not a business day, then do we use succeeding or preceding day (True = succeed)

###Relative
#####References an occurrence of a specific day of the calendar month
*day* is a weekday
*num_day* is which instance of the calendar day in the month (i.e. the 3rd Wednesday)
see above for rest of parameters

###Biz
#####References a specific business day of the calendar month
*num_day* is which business day of calendar we reference (10th business day of month)
see above for rest of parameters
