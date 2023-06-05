from ib_insync import *
import pandas as pd
import datetime
import sys
import math


maintainanance_margin_dict = {
    "TQQQ": 1700,
    "PLTR": 300,
    "SOXL": 1400,
    "EEM": 880
}

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

# Get available liquidity
account_values = ib.accountValues()
excess_liquidity = 0

for i in range(len(account_values)):
    if account_values[i].tag == 'ExcessLiquidity':
        excess_liquidity = float(account_values[i].value)
print(f'Available liquidity: {excess_liquidity}')

# Specify the initial date
# Get today's date
start_date = datetime.datetime.now().date()

# Find the last Friday before the specified date
while start_date.weekday() != 4:  # 4 corresponds to Friday
    start_date += datetime.timedelta(days=1)

# Initialize an empty list to store week/price pairs
weekly_prices = []
max_weekly_gains = []
week_index = 0
# Retrieve prices for 7 days from the initial date
strike = 37
comission = 0.015

ticker = 'TQQQ'
for week_number in range(9):
    date = start_date + datetime.timedelta(days=week_number*7)
    week_index += 1
    # TICKER - year, month, day - strike - P or C - exchange
    contract = Option(ticker, date.strftime('%Y%m%d'), strike, 'P', 'SMART')

    maintainanance_margin = maintainanance_margin_dict[ticker]
    max_orders = math.floor(excess_liquidity/maintainanance_margin)

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

        last_max_weekly_gain = max_orders * (last_price - comission) / week_index * 100
        # Append week/price pair to the list
        weekly_prices.append({'Week': week_index, 'Price': last_price, "Price / Week": round(last_price / week_index,3)})
        max_weekly_gains.append({'Week': week_index, 'Price': last_price, "Price / Week": round(last_price / week_index,3), "Max Weekly Gain": round(last_max_weekly_gain,3)})

# Create a DataFrame from the list
df_weekly_prices = pd.DataFrame(weekly_prices)
df_max_weekly_gains = pd.DataFrame(max_weekly_gains)

# Print the dataframe
print(df_max_weekly_gains)
print(df_weekly_prices)
df_weekly_prices.to_csv(sys.stdout, index=False)