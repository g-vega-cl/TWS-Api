from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

# TICKER - year, month, day - strike - P or C - exchange
contract = Option('TQQQ', '20230602', 30, 'P', 'SMART')

# Fetching historical bid prices
bars = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='1 D',
    barSizeSetting='1 hour', whatToShow='BID', useRTH=True)

# convert to pandas dataframe:
df = util.df(bars)
print(df)