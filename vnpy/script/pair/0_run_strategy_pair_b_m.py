#!/usr/bin/env python
#  -*- coding: utf-8 -*-

__author__ = 'hsp'

from datetime import datetime
from importlib import reload
from vnpy.trader.constant import Interval
from vnpy.trader.hqyu import get_back_test_rates, get_back_test_slippages, get_back_test_sizes, get_back_test_priceticks

import vnpy.app.portfolio_strategy
reload(vnpy.app.portfolio_strategy)

from vnpy.app.portfolio_strategy import BacktestingEngine
import vnpy.app.portfolio_strategy.strategies.pair_trading_strategy as stg
reload(stg)
from  vnpy.app.portfolio_strategy.strategies.pair_trading_strategy import PairTradingStrategy

if __name__ == '__main__':
    print("强弱套利策略开始回测！")
    engine = BacktestingEngine()
        
    # 豆二 <-> 豆粕【盈利】
    engine.set_parameters(
        vt_symbols=["B8888.DCE", "M8888.DCE"],
        interval=Interval.MINUTE,#interval=Interval.FIVE
        start=datetime(2015, 1, 1),
        # end=datetime(2021, 1, 12),
        end=datetime.now(),

        rates=get_back_test_rates(),
        slippages={"B8888.DCE": 0, "M8888.DCE": 0},
        sizes=get_back_test_sizes(),
        priceticks=get_back_test_priceticks(),

        capital=1_000_000,
    )

    setting = {
        "leg1_price_add": 1,
        "leg2_price_add": 1,
        "boll_window": 40,
        "boll_dev": 2,
        "leg1_fixed_size": 1,
        "leg2_fixed_size": 1,
        "leg1_ratio": 1,
        "leg2_ratio": 1,
    }

    engine.add_strategy(PairTradingStrategy, setting)

    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()

    print("强弱套利策略回测结束！")
