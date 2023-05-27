from ib_insync import *
import pandas as pd
import datetime

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

# Specify the initial date
# Get today's date
start_date = datetime.datetime.now().date()

# Find the last Friday before the specified date
while start_date.weekday() != 4:  # 4 corresponds to Friday
    start_date += datetime.timedelta(days=1)

# Initialize an empty list to store week/price pairs
weekly_prices = []
week_index = 1
# Retrieve prices for 7 days from the initial date
for i in range(7):
    date = start_date + datetime.timedelta(days=i*7)

    # TICKER - year, month, day - strike - P or C - exchange
    contract = Option('TQQQ', date.strftime('%Y%m%d'), 30, 'P', 'SMART')

    # Fetch historical bid prices
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='1 D',
        barSizeSetting='1 hour', whatToShow='BID', useRTH=True)

    # Check if bars is None or empty
    if bars is not None and len(bars):
        # Convert to pandas dataframe:
        df = util.df(bars)
        
        # Get the last price for the day
        last_price = df['close'].iloc[-1]

        # Append week/price pair to the list
        weekly_prices.append({'Week': week_index, 'Price': last_price, "Price / Week": round(last_price / week_index,3)})
        week_index += 1
# Create a DataFrame from the list
df_weekly_prices = pd.DataFrame(weekly_prices)

# Print the dataframe
print(df_weekly_prices)