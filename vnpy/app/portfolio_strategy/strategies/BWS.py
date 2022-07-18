from typing import List, Dict
from datetime import datetime

from scipy.stats import norm

import numpy as np

from vnpy.app.portfolio_strategy import StrategyTemplate, StrategyEngine
from vnpy.trader.utility import BarGenerator
from vnpy.trader.object import TickData, BarData, TradeData
from vnpy.trader.constant import Interval, Direction, Offset


class bwsArbitrageStrategy(StrategyTemplate):
    """"""

    author = "wbc"

    price_add = 5
    boll_window = 20
    entry_level_percentage = 0.15
    prior_mean = 0
    prior_variance = 1
    known_variance = 1
    # boll_dev = 2
    fixed_size = 1
    leg1_fixed_size = 1
    leg2_fixed_size = 1
    leg1_ratio = 1
    leg2_ratio = 1

    leg1_symbol = ""
    leg2_symbol = ""
    current_spread = 0.0
    posterior_mean = 0.0
    posterior_variance = 0.0
    # boll_mid = 0.0
    boll_down = 0.0
    boll_up = 0.0

    parameters = [
        "price_add",
        "boll_window",
        "entry_level_percentage",
        "use_percentage",
        "entry_level",
        "prior_mean",
        "prior_variance",
        "known_variance",
        "fixed_size",
        "leg1_fixed_size",
        "leg2_fixed_size",
        "leg1_ratio",
        "leg2_ratio",
    ]
    variables = [
        "leg1_symbol",
        "leg2_symbol",
        "current_spread",
        "posterior_mean",
        "posterior_variance",
        "boll_mid",
        "boll_down",
        "boll_up",
        "long_position_point",
        "short_position_point",
        "close_long_position_point",
        "close_short_position_point"
    ]

    def __init__(
            self,
            strategy_engine: StrategyEngine,
            strategy_name: str,
            vt_symbols: List[str],
            setting: dict
    ):
        """"""
        super().__init__(strategy_engine, strategy_name, vt_symbols, setting)

        self.bgs: Dict[str, BarGenerator] = {}
        self.targets: Dict[str, int] = {}
        self.last_tick_time: datetime = None

        self.spread_count: int = 0
        self.spread_data: np.array = np.zeros(100)

        # Obtain contract info
        self.leg1_symbol, self.leg2_symbol = vt_symbols

        def on_bar(bar: BarData):
            """"""
            pass

        for vt_symbol in self.vt_symbols:
            self.targets[vt_symbol] = 0
            self.bgs[vt_symbol] = BarGenerator(on_bar)

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("策略初始化")

        self.load_bars(1)

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        if (
                self.last_tick_time
                and self.last_tick_time.minute != tick.datetime.minute
        ):
            bars = {}
            for vt_symbol, bg in self.bgs.items():
                bars[vt_symbol] = bg.generate()
            self.on_bars(bars)

        bg: BarGenerator = self.bgs[tick.vt_symbol]
        bg.update_tick(tick)

        self.last_tick_time = tick.datetime

    def on_bars(self, bars: Dict[str, BarData],bool = False):
        """"""
        self.cancel_all()

        # Return if one leg data is missing
        if self.leg1_symbol not in bars or self.leg2_symbol not in bars:
            return

        # Calculate current spread
        leg1_bar = bars[self.leg1_symbol]
        leg2_bar = bars[self.leg2_symbol]

        # # Filter time only run every 5 minutes
        # if (leg1_bar.datetime.minute + 1) % 5:
        #    return

        self.current_spread = (
                leg1_bar.close_price * self.leg1_ratio - leg2_bar.close_price * self.leg2_ratio
        )

        # Update to spread array
        self.spread_data[:-1] = self.spread_data[1:]
        self.spread_data[-1] = self.current_spread

        self.spread_count += 1
        if self.spread_count <= self.boll_window:
            return

        # Calculate boll value
        buf: np.array = self.spread_data[-self.boll_window:]

        # std = buf.std()
        # self.boll_mid = buf.mean()
        # self.boll_up = self.boll_mid + self.boll_dev * std
        # self.boll_down = self.boll_mid - self.boll_dev * std

        # self.prior_mean = buf.mean()
        # self.prior_variance = buf.std() ** 2

        sig_square_n = self.known_variance / self.boll_window

        self.boll_mid = buf.mean()
        # self.boll_mid = self.posterior_mean
        A = 1 / sig_square_n + 1 / self.prior_variance
        B = buf.mean() / sig_square_n + self.prior_mean / self.prior_variance
        self.posterior_mean = B / A
        self.posterior_variance = (1 / A) ** (0.5)


        self.boll_mid=self.posterior_mean


        if self.use_percentage is True:
            self.boll_down = norm.ppf(self.entry_level_percentage, loc=self.posterior_mean,
                                      scale=self.posterior_variance)
            self.boll_up = norm.ppf(1 - self.entry_level_percentage, loc=self.posterior_mean,
                                    scale=self.posterior_variance)
        else:
            self.boll_up = self.posterior_mean + self.entry_level
            self.boll_down = self.posterior_mean - self.entry_level

        # Calculate new target position
        leg1_pos = self.get_pos(self.leg1_symbol)
        # print('AAA')

        self.long_position_point=None
        self.short_position_point =None
        self.close_short_position_point =None
        self.close_long_position_point =None

        if not leg1_pos:
            if self.current_spread >= self.boll_up:
                print("价差:", self.current_spread, ">=上界:", self.boll_up)
                self.short_position_point=self.boll_up
                self.targets[self.leg1_symbol] = -self.leg1_fixed_size
                self.targets[self.leg2_symbol] = self.leg2_fixed_size
            elif self.current_spread <= self.boll_down:
                print("价差:", self.current_spread, "<=下界:", self.boll_down)
                self.long_position_point = self.boll_down
                self.targets[self.leg1_symbol] = self.leg1_fixed_size
                self.targets[self.leg2_symbol] = -self.leg2_fixed_size
        elif leg1_pos > 0:
            if self.current_spread >= self.boll_mid:
                print("价差:", self.current_spread, ">=均线:", self.boll_mid)
                self.close_long_position_point=self.boll_mid
                self.targets[self.leg1_symbol] = 0
                self.targets[self.leg2_symbol] = 0
        else:
            if self.current_spread <= self.boll_mid:
                print("价差:", self.current_spread, "<=均线:", self.boll_mid)
                self.close_short_position_point = self.boll_mid
                self.targets[self.leg1_symbol] = 0
                self.targets[self.leg2_symbol] = 0

        # Execute orders
        for vt_symbol in self.vt_symbols:
            target_pos = self.targets[vt_symbol]
            current_pos = self.get_pos(vt_symbol)

            pos_diff = target_pos - current_pos
            # print("abs(pos_diff):     ",abs(pos_diff))
            volume = abs(pos_diff)
            bar = bars[vt_symbol]

            if pos_diff > 0:
                price = bar.close_price + self.price_add

                if current_pos < 0:
                    self.cover(vt_symbol, price, volume)
                else:
                    self.buy(vt_symbol, price, volume)
            elif pos_diff < 0:
                price = bar.close_price - self.price_add

                if current_pos > 0:
                    self.sell(vt_symbol, price, volume)
                else:
                    self.short(vt_symbol, price, volume)

        self.put_event()
        # print('AAA')


        if bool is True:
            if self.current_spread is None:
                return None
            # print(current_spread ,boll_up ,boll_mid ,boll_down)
            else :
                results=[self.current_spread ,self.boll_up ,self.boll_mid ,self.boll_down,self.long_position_point,self.short_position_point,self.close_long_position_point,self.close_short_position_point]
                return results
                # return self.current_spread ,self.boll_up ,self.boll_mid ,self.boll_down
            # return result
        else:
            # print('AUUUUUUUH')
            return

    def update_trade(self, trade: TradeData) -> None:
        """
        Callback of new trade data update.
        """

        """
         Callback of new trade data update.
        """
        if trade.direction == Direction.LONG:
            self.pos[trade.vt_symbol] += trade.volume
        else:
            self.pos[trade.vt_symbol] -= trade.volume

        # vt_symbol = vt_symbol_to_index_symbol(trade.vt_symbol)

        # if trade.direction == Direction.LONG:
        #    self.pos[vt_symbol] += trade.volume
        # else:
        #    self.pos[vt_symbol] -= trade.volume

        # pos = self.get_pos(trade.vt_symbol)
        # msg = f"【交易完成】指数合约：{trade.vt_symbol}，交易合约：{trade.vt_symbol}，price={trade.price}, volume={trade.volume}, pos={pos}"
        msg = f"【交易完成】指数合约：{trade.vt_symbol}，交易合约：{trade.vt_symbol}，price={trade.price}, volume={trade.volume},offset={trade.offset},direction={trade.direction},datetime={trade.datetime}"
        print(msg)
        # self.write_log2file(msg)
