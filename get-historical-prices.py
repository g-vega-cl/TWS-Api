from ib_insync import *
import pandas as pd
import datetime
import sys
import math

# NEED TO CONFIGURE WITH UBUNTU, BUT YOU CAN RUN WITH WINDOWS BASH

# stocks
stocks = {
    "TQQQ": {
        "current_price": 42,
        "maintainanance_margin": 1700,
        "short": False,
    },
    "SQQQ": {
        "current_price": 20,
        "maintainanance_margin": 1250,
        "short": True,
    },
    "SPXL": {
        "current_price": 80,
        "maintainanance_margin": 5000,
        "short": False,
    },
    "SPXU": {
        "current_price": 12,
        "maintainanance_margin": 750,
        "short": True,
    },
    "SDOW": {
        "current_price": 27,
        "maintainanance_margin": 1700,
        "short": True,
    },
    "SRTY": {
        "current_price": 52,
        "maintainanance_margin": 3000,
        "short": True,
    },
    "LNG": {
        "current_price": 167,
        "maintainanance_margin": 3800,
        "short": False,
    }
}

# Get current prices out of the stocks object
current_prices = {}
for key in stocks.keys():
    current_prices[key] = stocks[key]["current_price"]




def calculate_strike_percent(percent, stocks):
    strike_percent = {}
    for key in stocks.keys():
        value = stocks[key]["current_price"]
        strike_percent[key] = math.floor(value * percent)
    return strike_percent

strike_3_percent = calculate_strike_percent(0.97, stocks)

strike_5_percent = calculate_strike_percent(.95, stocks)

strike_9_percent = calculate_strike_percent(.91, stocks)

strike_neg_9_percent = calculate_strike_percent(1.09, stocks)

strike_neg_5_percent = calculate_strike_percent(1.05, stocks)

strike_neg_3_percent = calculate_strike_percent(1.03, stocks)


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


for ticker in stocks.keys():
    if(stocks[ticker]["short"]):
        for strike_percent in [current_prices, strike_neg_3_percent, strike_neg_5_percent, strike_neg_9_percent]:
            weekly_prices = []
            week_index = 0
            strike = strike_percent[ticker]
            for week_number in range(9):
                date = start_date + datetime.timedelta(days=week_number*7)
                week_index += 1
                contract = Option(ticker, date.strftime('%Y%m%d'), strike, 'C', 'SMART')

                maintainanance_margin = stocks[ticker]["maintainanance_margin"]
                max_orders = math.floor(excess_liquidity/maintainanance_margin)

                bars = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='1 D',
                    barSizeSetting='1 hour', whatToShow='BID', useRTH=True)

                if bars is not None and len(bars):
                    df = util.df(bars)
                    last_price = df['close'].iloc[-1]
                    last_max_weekly_gain = max_orders * (last_price - comission) / week_index * 100
                    weekly_prices.append({'Week': week_index, 'Price': last_price})
                    max_weekly_gains.append({'Ticker': ticker, 'Week': week_index, 'Price': last_price, "Price / Week": round(last_price / week_index,3), "current_price":strike, "Max Weekly Gain": round(last_max_weekly_gain,3), "Maintainace margin": maintainanance_margin})

            # df_weekly_prices = pd.DataFrame(weekly_prices)
    else:
        for strike_percent in [current_prices, strike_3_percent, strike_5_percent, strike_9_percent]:
            weekly_prices = []
            week_index = 0
            strike = strike_percent[ticker]
            for week_number in range(9):
                date = start_date + datetime.timedelta(days=week_number*7)
                week_index += 1
                contract = Option(ticker, date.strftime('%Y%m%d'), strike, 'P', 'SMART')

                maintainanance_margin = stocks[ticker]["maintainanance_margin"]
                max_orders = math.floor(excess_liquidity/maintainanance_margin)

                bars = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='1 D',
                    barSizeSetting='1 hour', whatToShow='BID', useRTH=True)

                if bars is not None and len(bars):
                    df = util.df(bars)
                    last_price = df['close'].iloc[-1]
                    last_max_weekly_gain = max_orders * (last_price - comission) / week_index * 100
                    weekly_prices.append({'Week': week_index, 'Price': last_price})
                    max_weekly_gains.append({'Ticker': ticker, 'Week': week_index, 'Price': last_price, "Price / Week": round(last_price / week_index,3), "current_price":strike, "Max Weekly Gain": round(last_max_weekly_gain,3), "Maintainace margin": maintainanance_margin})

            # df_weekly_prices = pd.DataFrame(weekly_prices)

df_max_weekly_gains = pd.DataFrame(max_weekly_gains)
print(df_max_weekly_gains)
df_max_weekly_gains.to_csv(sys.stdout, index=False)