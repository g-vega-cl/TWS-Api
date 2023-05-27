from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

year = "2023"
month = "6".zfill(2)
day = "2".zfill(2)

date = year + month + day

# TICKER - year, month, day - strike - P or C - exchange
contract = Option('TQQQ', date, 30, 'P', 'SMART')

# Fetching historical bid prices
bars = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='1 D',
    barSizeSetting='1 hour', whatToShow='BID', useRTH=True)

# convert to pandas dataframe:
df = util.df(bars)
print(df)