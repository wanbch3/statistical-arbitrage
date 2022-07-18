#!/usr/bin/env python
#  -*- coding: utf-8 -*-

__author__ = 'wbc'

from datetime import datetime
from datetime import timedelta
import pandas as pd
from importlib import reload
from vnpy.trader.constant import Interval
from vnpy.trader.hqyu import get_back_test_rates, get_back_test_slippages, get_back_test_sizes, get_back_test_priceticks

import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot
from plotly.subplots import make_subplots

from jqdatasdk import *
auth('18702013837','&UJM,ki8')
from vnpy.script.trans_cycle_arbitrage.get_second_dominant_future import get_second_dominant_future_list,get_dominant_future_list,jq_to_vnpy

# from vnpy.script.trans_cycle_arbitrage.get_second_dominant_future_without_JQ import \
#     get_second_dominant_future_without_jq, get_bars_by_pickle_file, pkl_to_jq, str_to_date, jq_to_pkl, jq_to_vnpy

import vnpy.app.portfolio_strategy

reload(vnpy.app.portfolio_strategy)

from vnpy.app.portfolio_strategy.backtesting_single import BacktestingEngine_Single
# from vnpy.app.portfolio_strategy import BacktestingEngine_Single
import vnpy.app.portfolio_strategy.strategies.pair_trading_strategy as stg

reload(stg)
from vnpy.app.portfolio_strategy.strategies.pair_trading_for_transCycle import PairTradingStrategyForTransCycle

if __name__ == '__main__':
    print("跨期套利策略开始回测！")
    end_date = datetime.now() - timedelta(days=31 * 10)
    start_date = end_date - timedelta(days=31 * 5)

    # end_date=datetime.now()
    # start_date=datetime(2021,1,1)

    dominant_future_list, date_seperate = get_dominant_future_list('PB', start_date, end_date)
    second_dominant_future_list = get_second_dominant_future_list('PB', dominant_future_list, date_seperate)

    dominant_future_list = list(map(lambda x:jq_to_vnpy(x.replace('PB', 'pb')),dominant_future_list))
    second_dominant_future_list = list(map(lambda x: jq_to_vnpy(x.replace('PB', 'pb')), second_dominant_future_list))


    setting = {
        "leg1_price_add": 0,
        "leg2_price_add": 0,
        # "boll_window": 555*40,
        "boll_window": 15000,
        "boll_dev": 4,
        "leg1_fixed_size": 1,
        "leg2_fixed_size": 1,
        "leg1_ratio": 1,
        "leg2_ratio": 1,

    }

    capital_temp = 1_000_000
    df_daily_pnl_and_stat = pd.DataFrame()
    df_sketch = pd.DataFrame()

    engine = BacktestingEngine_Single()
    engine.set_parameters(
        # vt_symbols=[dominant_future, second_dominant_future],
        main_contracts=dominant_future_list,
        second_contracts=second_dominant_future_list,
        date_seperate=date_seperate,
        interval=Interval.MINUTE,  # interval=Interval.FIVE
        # interval=Interval.DAILY,
        start=start_date,
        end=end_date,


        rates=0.3/10000,#手续费
        slippages=1,#滑点
        sizes=5,#
        priceticks=5,#价差

        capital=capital_temp,
    )

    for i in range(len(dominant_future_list)):

        dominant_future=dominant_future_list[i]
        second_dominant_future=second_dominant_future_list[i]
        start_date_temp = date_seperate[i]
        end_date_temp = date_seperate[i + 1]

        engine.load_data_by_contract(start_date_temp,end_date_temp,dominant_future,second_dominant_future)

        print('------------------------------')


    engine.add_strategy(PairTradingStrategyForTransCycle, setting)
    engine.run_backtesting_by_trans_cycle()
    engine.calculate_result()
    # engine.show_spreads()
    engine.show_chart()
    engine.show_trading_sketch()









    print("跨期套利策略回测结束！")