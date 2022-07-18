#!/usr/bin/env python
#  -*- coding: utf-8 -*-

__author__ = 'wbc'
from datetime import datetime
from importlib import reload
from vnpy.trader.constant import Interval
from vnpy.trader.hqyu import get_back_test_rates, get_back_test_slippages, get_back_test_sizes, get_back_test_priceticks

import vnpy.app.portfolio_strategy

reload(vnpy.app.portfolio_strategy)

from vnpy.app.portfolio_strategy import BacktestingEngine
import vnpy.app.portfolio_strategy.strategies.pair_trading_strategy as stg

reload(stg)
from vnpy.app.portfolio_strategy.strategies.pair_trading_strategy import PairTradingStrategy

if __name__ == '__main__':
    print("强弱套利策略开始回测！")
    engine = BacktestingEngine()

    # 玉米加权合约 <-> 玉米淀粉加权合约
    engine.set_parameters(
        vt_symbols=["C8888.DCE", "CS8888.DCE"],
        # interval=Interval.MINUTE,  # interval=Interval.FIVE
        interval=Interval.DAILY,
        start=datetime(2015, 1, 1),
        # start=datetime(2018, 1, 1),
        # end=datetime(2021, 1, 12),
        end=datetime.now(),

        rates=get_back_test_rates(),
        slippages={"C8888.DCE": 0, "CS8888.DCE": 0},
        sizes=get_back_test_sizes(),
        priceticks=get_back_test_priceticks(),

        capital=1_000_000,
    )

    setting = {
        "leg1_price_add": 1,
        "leg2_price_add": 1,
        # "boll_window": 14400*3,
        "boll_window":150,
        "boll_dev": 1,
        "leg1_fixed_size": 1,
        "leg2_fixed_size": 1,
        "leg1_ratio": 1,
        "leg2_ratio": 1,
    }


    engine.add_strategy(PairTradingStrategy, setting)

    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    
    # engine.calculate_statistics()
    engine.show_chart()
    engine.show_trading_sketch()
    # engine.write_report('PairTradingStrategy_c_cs',setting)

    print("强弱套利策略回测结束！")
