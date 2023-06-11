from ib_insync import *
import pandas as pd
import datetime
import sys
import math

maintainanance_margin_dict = {
    "TQQQ": 1700,
    "PLTR": 300,
    "SOXL": 1400,
    "EEM": 880,
    "IWM": 3700,
    "ARKK": 800,
}

# rounded up to the nearest dollar, unless really close to current value
current_prices = {
    "TQQQ": 37,
    "PLTR": 15,
    "SOXL": 23,
    "EEM": 40,
    "IWM": 185,
    "ARKK": 43,
}

strike_3_percent = {
    "TQQQ":  math.floor(current_prices["TQQQ"] * 0.97),
    "PLTR":  math.floor(current_prices["PLTR"] * 0.97),
    "SOXL":  math.floor(current_prices["SOXL"] * 0.97),
    "EEM":  math.floor(current_prices["EEM"] * 0.97),
    "IWM":  math.floor(current_prices["IWM"] * 0.97),
    "ARKK":  math.floor(current_prices["ARKK"] * 0.97),
}

strike_5_percent = {
    "TQQQ":  math.floor(current_prices["TQQQ"] * 0.95),
    "PLTR":  math.floor(current_prices["PLTR"] * 0.95),
    "SOXL":  math.floor(current_prices["SOXL"] * 0.95),
    "EEM":  math.floor(current_prices["EEM"] * 0.95),
    "IWM":  math.floor(current_prices["IWM"] * 0.95),
    "ARKK":  math.floor(current_prices["ARKK"] * 0.95),
}

strike_9_percent = {
    "TQQQ":  math.floor(current_prices["TQQQ"] * 0.91),
    "PLTR":  math.floor(current_prices["PLTR"] * 0.91),
    "SOXL":  math.floor(current_prices["SOXL"] * 0.91),
    "EEM":  math.floor(current_prices["EEM"] * 0.91),
    "IWM":  math.floor(current_prices["IWM"] * 0.91),
    "ARKK":  math.floor(current_prices["ARKK"] * 0.91),
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
start_date = datetime.datetime.now().date()

while start_date.weekday() != 4:  # 4 corresponds to Friday
    start_date += datetime.timedelta(days=1)

comission = 0.015
max_weekly_gains = []

for ticker in maintainanance_margin_dict.keys():
    weekly_prices = []
    week_index = 0
    strike = current_prices[ticker]
    for week_number in range(9):
        date = start_date + datetime.timedelta(days=week_number*7)
        week_index += 1
        contract = Option(ticker, date.strftime('%Y%m%d'), strike, 'P', 'SMART')

        maintainanance_margin = maintainanance_margin_dict[ticker]
        max_orders = math.floor(excess_liquidity/maintainanance_margin)

        bars = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='1 D',
            barSizeSetting='1 hour', whatToShow='BID', useRTH=True)

        if bars is not None and len(bars):
            df = util.df(bars)
            last_price = df['close'].iloc[-1]
            last_max_weekly_gain = max_orders * (last_price - comission) / week_index * 100
            weekly_prices.append({'Week': week_index, 'Price': last_price})
            max_weekly_gains.append({'Ticker': ticker, 'Week': week_index, 'Price': last_price, "Price / Week": round(last_price / week_index,3), "Max Weekly Gain": round(last_max_weekly_gain,3)})

    df_weekly_prices = pd.DataFrame(weekly_prices)
    print(df_weekly_prices)

df_max_weekly_gains = pd.DataFrame(max_weekly_gains)
print(df_max_weekly_gains)
df_max_weekly_gains.to_csv(sys.stdout, index=False)