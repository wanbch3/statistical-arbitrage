#!/usr/bin/env python
#  -*- coding: utf-8 -*-

__author__ = 'hsp'

from vnpy_ctastrategy.backtesting import BacktestingEngine
from datetime import datetime

from vnpy.trader.constant import Interval

from vnpy_ctastrategy.strategies.trend_long_turtle_strategy import TrendTurtleStrategy
from vnpy_ctastrategy.strategies.trend_long_sma_strategy import TrendSMAStrategy

from vnpy_ctastrategy.strategies.a_kk_simu_strategy import KKSimuStrategy
from vnpy_ctastrategy.strategies.a_kk_manew_simu_strategy import KKMANewSimuStrategy
from vnpy_ctastrategy.strategies.new_kingkeltner_strategy import NewKKStrategy

STRATEGY_NAME = "中低频策略"
account_money = 100_000

# start_time = datetime(2015, 1, 1),
# end_time = datetime.now(),


def run_backtesting(strategy_class, setting, vt_symbol, interval, rate, slippage, size, pricetick, capital):
    engine = BacktestingEngine()
    start_time = datetime(2021, 12, 31)
    end_time = datetime(2022, 6, 1)
    # end_time = datetime.now()
    engine.set_parameters(
        vt_symbol=vt_symbol,
        interval=interval,
        start=start_time,
        end=end_time,
        rate=rate,
        slippage=slippage,
        size=size,
        pricetick=pricetick,
        capital=capital
    )

    engine.add_strategy(strategy_class, setting)
    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    return df


def show_portfolio(df):
    engine = BacktestingEngine()
    engine.calculate_statistics(df)
    engine.show_chart(df)


def calculate_pnl(df):
    engine = BacktestingEngine()
    statistics = engine.calculate_statistics(df)
    return statistics


if __name__ == '__main__':

    print(f"{STRATEGY_NAME}开始回测！")

    """ 趋势跟随短中线策略之一 """

    setting = {"sma_n": 40, "atr_n": 40, "kk_dev": 1.6, "trailing_percent": 1.4, "cci_window": 10, "fixed_size": 1, "ma_day": 0, "ma_hour": 1}
    df31 = run_backtesting(
        strategy_class=KKMANewSimuStrategy,
        setting=setting,
        vt_symbol="AL8888.SHFE",
        interval=Interval.FIVE,
        rate=0.6/10000,
        slippage=5,
        size=5,
        pricetick=5,
        capital=account_money,
    )

    setting = {"sma_n": 40, "atr_n": 40, "kk_dev": 1.6, "trailing_percent": 1.4, "cci_window": 10, "fixed_size": 1, "ma_day": 0, "ma_hour": 1}
    df32 = run_backtesting(
        strategy_class=KKMANewSimuStrategy,
        setting=setting,
        vt_symbol="P8888.DCE",
        interval=Interval.FIVE,
        rate=1/10000,
        slippage=2,
        size=10,
        pricetick=2,
        capital=account_money,
    )

    setting = {"sma_n": 40, "atr_n": 40, "kk_dev": 1.6, "trailing_percent": 1.4, "cci_window": 10, "fixed_size": 1,
               "ma_day": 0, "ma_hour": 1}
    # setting = {"sma_n": 40, "atr_n": 40, "kk_dev": 1.6, "trailing_percent": 1.4, "cci_window": 10, "fixed_size": 2}
    df33 = run_backtesting(
        strategy_class=KKMANewSimuStrategy,
        setting=setting,
        vt_symbol="RB8888.SHFE",
        interval=Interval.FIVE,
        rate=1/10000,
        slippage=1,
        size=10,
        pricetick=1,
        capital=account_money,
    )

    setting = {"sma_n": 40, "atr_n": 40, "kk_dev": 1.6, "trailing_percent": 1.6, "cci_window": 10, "fixed_size": 1, "ma_day": 0, "ma_hour": 1}
    df34 = run_backtesting(
        strategy_class=KKMANewSimuStrategy,
        setting=setting,
        vt_symbol="SA8888.CZCE",
        interval=Interval.FIVE,
        rate=1/10000,
        slippage=1,
        size=20,
        pricetick=1,
        capital=account_money,
    )

    setting = {"sma_n": 40, "atr_n": 40, "kk_dev": 1.6, "trailing_percent": 1.4, "cci_window": 10, "fixed_size": 2,
               "ma_day": 0, "ma_hour": 1}
    # setting = {"sma_n": 40, "atr_n": 40, "kk_dev": 1.6, "trailing_percent": 1.4, "cci_window": 10, "fixed_size": 2}
    df35 = run_backtesting(
        strategy_class=KKMANewSimuStrategy,
        setting=setting,
        vt_symbol="C8888.DCE",
        interval=Interval.FIVE,
        rate=1/10000,
        slippage=1,
        size=10,
        pricetick=1,
        capital=account_money,
    )

    setting = {"sma_n": 40, "atr_n": 40, "kk_dev": 1.2, "trailing_percent": 1.4, "stop": 0, "atr_ratio": 1000, "cci_window": 10, "fixed_size": 1}
    df36 = run_backtesting(
        strategy_class=NewKKStrategy,
        setting=setting,
        vt_symbol="AP8888.CZCE",
        interval=Interval.FIVE,
        rate=1/10000,
        slippage=1,
        size=10,
        pricetick=1,
        capital=account_money,
    )

    ##################

    dfp = df31 + df32 + df33 + df34 + df35 + df36
    dfp = df31 + df32 + df33 + df35 + df36
    dfp = dfp.dropna()
    show_portfolio(dfp)

    statisticsAll = calculate_pnl(dfp)

    print(f"total_returnAll = {statisticsAll['total_return']}, capital={statisticsAll['capital']}, end_balance={statisticsAll['end_balance']}")

    print(f"Test End！")
