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

def calculate_strike_percent(percent, current_prices):
    strike_percent = {}
    for key, value in current_prices.items():
        strike_percent[key] = math.floor(value * percent)
    return strike_percent

strike_3_percent = calculate_strike_percent(0.97, current_prices)
print(strike_3_percent)

strike_5_percent = calculate_strike_percent(.95, current_prices)
print(strike_5_percent)

strike_9_percent = calculate_strike_percent(.91, current_prices)
print(strike_9_percent)


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
    for strike_percent in [current_prices, strike_3_percent, strike_5_percent, strike_9_percent]:
        weekly_prices = []
        week_index = 0
        strike = strike_percent[ticker]
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
                max_weekly_gains.append({'Ticker': ticker, 'Week': week_index, 'Price': last_price, "Price / Week": round(last_price / week_index,3), "strike":strike, "Max Weekly Gain": round(last_max_weekly_gain,3), "Maintainace margin": maintainanance_margin_dict[ticker]})

        df_weekly_prices = pd.DataFrame(weekly_prices)

df_max_weekly_gains = pd.DataFrame(max_weekly_gains)
print(df_max_weekly_gains)
df_max_weekly_gains.to_csv(sys.stdout, index=False)