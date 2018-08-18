import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
START_MONEY = 10000000
class Context:
    def __init__(self, date_index):
        self.money = pd.Series(0., index = date_index)
        self.equity = pd.Series(0., index = date_index)

    def set_equity(self, date, yesterday_money):
        self.money[date] = yesterday_money
        self.equity[date] = yesterday_money

    def buy_sell(self, buy_price, sell_price, buy_money, buy_date):
        self.money[buy_date] = self.money[buy_date] - buy_money
        amount = buy_money/buy_price
        sell_money = amount * sell_price
        return sell_money

    def get_cagr(self):
        total_ret = (self.equity[-1] / self.equity[0])
        total_day = (self.equity.index.values[-1] - self.equity.index.values[0]) / (np.timedelta64(1, 'D'))
        total_year = float(total_day) / 365
        return round((total_ret ** (1 / total_year)) - 1, 2)

    def get_mdd(self):
        dds = [0]
        max_equity = self.equity.iloc[0]
        for i in range(len(self.equity)):
            if max_equity < self.equity[i]:
                max_equity = self.equity[i]
            dd = -(max_equity - self.equity[i]) / max_equity
            dds.append(dd)
        return round(min(dds), 2)

def process():
    df = pd.read_csv('KosdaqLevLogday_from20180102.csv', parse_dates=['logDate'])
    date_index = df['logDate'].unique()
    df['T_priceOpen'] = df['priceOpen'].shift(-1)
    context = Context(date_index)
    yesterday_money = START_MONEY
    for day in date_index:
        context.set_equity(day, yesterday_money)
        today_stock_list = df.where(df.logDate == day).dropna(axis=0, how='all')
        delta_money = 0
        for i, r in today_stock_list.iterrows():
            delta_money = delta_money + context.buy_sell(
                buy_price=r['priceClose'], sell_price=r['T_priceOpen'],
                buy_money=context.equity[day], buy_date=day
            )
        yesterday_money = delta_money + context.money[day]
    print('CAGR: {}%, MDD: {}%'.format(context.get_cagr()*100, context.get_mdd()*100))
    ax.plot(date_index, context.equity)
    plt.annotate('CAGR: {}%, MDD: {}%'.format(context.get_cagr()*100, context.get_mdd()*100),
                 xy=(0.05, 0.95), xycoords='axes fraction')

def plot_equity():
    fig.autofmt_xdate()
    plt.legend(['equity curve'], loc='best')
    plt.title('KOSDAQ 150 LEV Simple Overnight')
    plt.show()

process()
plot_equity()



