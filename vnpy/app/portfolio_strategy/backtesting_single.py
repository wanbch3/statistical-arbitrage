from random import randint
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List, Set, Tuple
from functools import lru_cache
from copy import copy
import traceback

import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot
from plotly.subplots import make_subplots

import numpy as np
from pandas import DataFrame

from vnpy.trader.constant import Direction, Offset, Interval, Status
from vnpy.trader.database import database_manager
from vnpy.trader.object import OrderData, TradeData, BarData
from vnpy.trader.utility import round_to, extract_vt_symbol



from .template import StrategyTemplate

INTERVAL_DELTA_MAP = {
    Interval.MINUTE: timedelta(minutes=1),
    Interval.HOUR: timedelta(hours=1),
    Interval.DAILY: timedelta(days=1),
}


class BacktestingEngine_Single:
    """"""

    gateway_name = "BACKTESTING"

    def __init__(self):
        """"""
        self.vt_symbols: List[str] = []
        self.start: datetime = None
        self.end: datetime = None

        self.main_contracts: List[str] = []
        self.second_contracts: List[str] = []
        self.date_seperate: List[str] = []

        self.rates = 0
        self.slippages = 0
        self.sizes = 1
        self.priceticks = 0

        self.capital: float = 1_000_000
        self.risk_free: float = 0

        self.strategy: StrategyTemplate = None
        self.bars: Dict[str, BarData] = {}
        self.datetime: datetime = None

        self.interval: Interval = None
        self.days: int = 0
        self.history_data: Dict[Tuple, BarData] = {}
        self.dts: Set[datetime] = set()

        self.limit_order_count = 0
        self.limit_orders = {}
        self.active_limit_orders = {}

        self.trade_count = 0
        self.trades = {}

        self.logs = []

        self.daily_results = {}
        self.daily_df = None

        self.spreads= []##
        self.boll_up=[]
        self.boll_mid=[]
        self.boll_down=[]
        self.dts_temp=[]
        self.long_position_point=[]
        self.short_position_point=[]
        self.close_long_position_point=[]
        self.close_short_position_point=[]

        self.main_contract_temp=''



    def clear_data(self) -> None:
        """
        Clear all data of last backtesting.
        """
        self.strategy = None
        self.bars = {}
        self.datetime = None

        self.limit_order_count = 0
        self.limit_orders.clear()
        self.active_limit_orders.clear()

        self.trade_count = 0
        self.trades.clear()

        self.logs.clear()
        self.daily_results.clear()
        self.daily_df = None

        self.spreads= []##
        self.boll_up=[]
        self.boll_mid=[]
        self.boll_down=[]
        self.dts_temp=[]

    def set_parameters(
            self,
            # vt_symbols: List[str],
            main_contracts,
            second_contracts,
            date_seperate,
            interval: Interval,
            start: datetime,
            rates: float = 0,
            slippages: float = 0,
            sizes: float = 0,
            priceticks: float = 0,
            capital: int = 0,
            end: datetime = None,
            risk_free: float = 0
    ) -> None:
        """"""
        # self.vt_symbols = vt_symbols
        self.interval = interval

        self.rates = rates
        self.slippages = slippages
        self.sizes = sizes
        self.priceticks = priceticks

        self.start = start
        self.end = end
        self.capital = capital
        self.risk_free = risk_free

        self.main_contracts=main_contracts
        self.second_contracts=second_contracts
        self.date_seperate=date_seperate

        self.main_contract_temp=main_contracts[0]

    def add_strategy(self, strategy_class: type, setting: dict) -> None:
        """"""
        self.strategy = strategy_class(
            self, strategy_class.__name__, copy(self.vt_symbols), setting
        )

    def load_data(self) -> None:
        """"""
        self.output("开始加载历史数据")

        if not self.end:
            self.end = datetime.now()

        if self.start >= self.end:
            self.output("起始日期必须小于结束日期")
            return

        # Clear previously loaded history data
        self.history_data.clear()
        self.dts.clear()

        # Load 30 days of data each time and allow for progress update
        progress_delta = timedelta(days=30)
        total_delta = self.end - self.start
        interval_delta = INTERVAL_DELTA_MAP[self.interval]

        for vt_symbol in self.vt_symbols:
            start = self.start
            end = self.start + progress_delta
            progress = 0

            data_count = 0
            while start < self.end:
                end = min(end, self.end)  # Make sure end time stays within set range

                data = load_bar_data(
                    vt_symbol,
                    self.interval,
                    start,
                    end
                )

                for bar in data:
                    self.dts.add(bar.datetime)
                    self.history_data[(bar.datetime, vt_symbol)] = bar
                    data_count += 1

                progress += progress_delta / total_delta
                progress = min(progress, 1)
                progress_bar = "#" * int(progress * 10)
                self.output(f"{vt_symbol}加载进度：{progress_bar} [{progress:.0%}]")

                start = end + interval_delta
                end += (progress_delta + interval_delta)

            self.output(f"{vt_symbol}历史数据加载完成，数据量：{data_count}")

        self.output("所有历史数据加载完成")

    def get_main_contract_by_date(self, date):
        # self.main_contracts[sum(list(map(lambda x: x <= date, self.date_seperate))) - 1]
        return self.main_contracts[sum(list(map(lambda x: x <= date.replace(tzinfo=None), self.date_seperate))) - 1]

    def get_second_contract_by_date(self, date):
        return self.second_contracts[sum(list(map(lambda x: x <= date.replace(tzinfo=None), self.date_seperate))) - 1]


    def load_data_by_contract(self,start_date,end_date,symbol_1,symbol_2) -> None:
        """"""
        self.output("开始按主力合约加载历史数据")

        if not end_date:
            end_date = datetime.now()

        if start_date >= end_date:
            self.output("起始日期必须小于结束日期")
            return

        # # Clear previously loaded history data
        # self.history_data.clear()
        # self.dts.clear()

        # Load 30 days of data each time and allow for progress update
        progress_delta = timedelta(days=30)
        total_delta = end_date - start_date
        interval_delta = INTERVAL_DELTA_MAP[self.interval]

        vt_symbols=[symbol_1,symbol_2]
        for vt_symbol in vt_symbols:
            start = start_date
            end = start_date + progress_delta
            progress = 0

            data_count = 0
            while start < end_date:
                end = min(end, end_date)  # Make sure end time stays within set range

                data = load_bar_data(
                    vt_symbol,
                    self.interval,
                    start,
                    end
                )

                for bar in data:
                    self.dts.add(bar.datetime)
                    self.history_data[(bar.datetime, vt_symbol)] = bar
                    data_count += 1

                progress += progress_delta / total_delta
                progress = min(progress, 1)
                progress_bar = "#" * int(progress * 10)
                self.output(f"{vt_symbol}加载进度：{progress_bar} [{progress:.0%}]")

                start = end + interval_delta
                end += (progress_delta + interval_delta)

            self.output(f"{vt_symbol}历史数据加载完成，数据量：{data_count}")

        self.output("所有历史数据加载完成")

    def run_backtesting(self) -> None:
        """"""
        self.strategy.on_init()

        # Generate sorted datetime list
        dts = list(self.dts)
        dts.sort()

        # Use the first [days] of history data for initializing strategy
        day_count = 0
        ix = 0

        for ix, dt in enumerate(dts):
            if self.datetime and dt.day != self.datetime.day:
                day_count += 1
                if day_count >= self.days:
                    break

            try:
                self.new_bars(dt)
            except Exception:
                self.output("触发异常，回测终止")
                self.output(traceback.format_exc())
                return

        self.strategy.inited = True
        self.output("策略初始化完成")

        self.strategy.on_start()
        self.strategy.trading = True
        self.output("开始回放历史数据")

        # Use the rest of history data for running backtesting
        for dt in dts[ix:]:
            try:
                self.new_bars(dt)
            except Exception:
                self.output("触发异常，回测终止")
                self.output(traceback.format_exc())
                return

        self.output("历史数据回放结束")

    def calculate_result(self) -> None:
        """"""
        self.output("开始计算逐日盯市盈亏")

        if not self.trades:
            self.output("成交记录为空，无法计算")
            return

        # Add trade data into daily reuslt.
        for trade in self.trades.values():
            d = trade.datetime.date()
            daily_result = self.daily_results[d]
            daily_result.add_trade(trade)

        # Calculate daily result by iteration.
        pre_closes = {}
        start_poses = {}

        for daily_result in self.daily_results.values():
            daily_result.calculate_pnl(
                pre_closes,
                start_poses,
                self.sizes,
                self.rates,
                self.slippages,
            )

            pre_closes = daily_result.close_prices
            start_poses = daily_result.end_poses

        # Generate dataframe
        results = defaultdict(list)

        for daily_result in self.daily_results.values():
            fields = [
                "date", "trade_count", "turnover",
                "commission", "slippage", "trading_pnl",
                "holding_pnl", "total_pnl", "net_pnl"
            ]
            for key in fields:
                value = getattr(daily_result, key)
                results[key].append(value)

        self.daily_df = DataFrame.from_dict(results).set_index("date")

        self.output("逐日盯市盈亏计算完成")
        return self.daily_df

    def calculate_statistics(self, df: DataFrame = None, output=True) -> None:
        """"""
        self.output("开始计算策略统计指标")

        # Check DataFrame input exterior
        if df is None:
            df = self.daily_df
            if df is None:
                # Set all statistics to 0 if no trade.
                start_date = ""
                end_date = ""
                total_days = 0
                profit_days = 0
                loss_days = 0
                percentage_profitable = 0  ##
                end_balance = 0
                max_drawdown = 0
                max_ddpercent = 0
                max_drawdown_duration = 0
                total_net_pnl = 0
                daily_net_pnl = 0
                total_commission = 0
                daily_commission = 0
                total_slippage = 0
                daily_slippage = 0
                total_turnover = 0
                daily_turnover = 0
                total_trade_count = 0
                daily_trade_count = 0
                average_trade_cycle = 0  ##
                total_return = 0
                annual_return = 0
                daily_return = 0
                return_std = 0
                sharpe_ratio = 0
                return_drawdown_ratio = 0
            else:
                # Calculate balance related time series data
                df["balance"] = df["net_pnl"].cumsum() + self.capital
                df["return"] = np.log(df["balance"] / df["balance"].shift(1)).fillna(0)  # 对数收益率
                df["highlevel"] = (
                    df["balance"].rolling(
                        min_periods=1, window=len(df), center=False).max()
                )
                df["drawdown"] = df["balance"] - df["highlevel"]
                df["ddpercent"] = df["drawdown"] / df["highlevel"] * 100

                # Calculate statistics value
                start_date = df.index[0]
                end_date = df.index[-1]

                total_days = len(df)
                profit_days = len(df[df["net_pnl"] > 0])
                loss_days = len(df[df["net_pnl"] < 0])
                percentage_profitable = profit_days / (profit_days+loss_days) * 100  ##

                end_balance = df["balance"].iloc[-1]
                max_drawdown = df["drawdown"].min()
                max_ddpercent = df["ddpercent"].min()
                max_drawdown_end = df["drawdown"].idxmin()

                if isinstance(max_drawdown_end, date):
                    max_drawdown_start = df["balance"][:max_drawdown_end].idxmax()
                    max_drawdown_duration = (max_drawdown_end - max_drawdown_start).days
                else:
                    max_drawdown_duration = 0

                total_net_pnl = df["net_pnl"].sum()
                daily_net_pnl = total_net_pnl / total_days

                total_commission = df["commission"].sum()
                daily_commission = total_commission / total_days

                total_slippage = df["slippage"].sum()
                daily_slippage = total_slippage / total_days

                total_turnover = df["turnover"].sum()
                daily_turnover = total_turnover / total_days

                total_trade_count = df["trade_count"].sum()
                daily_trade_count = total_trade_count / total_days
                average_trade_cycle = 1 / daily_trade_count  ##

                total_return = (end_balance / self.capital - 1) * 100
                annual_return = total_return / total_days * 240
                daily_return = df["return"].mean() * 100
                return_std = df["return"].std() * 100

                if return_std:
                    daily_risk_free = self.risk_free / np.sqrt(240)
                    sharpe_ratio = (daily_return - daily_risk_free) / return_std * np.sqrt(240)
                else:
                    sharpe_ratio = 0

                return_drawdown_ratio = -total_net_pnl / max_drawdown

            statistics = {
                "start_date": start_date,
                "end_date": end_date,
                "total_days": total_days,
                "profit_days": profit_days,
                "loss_days": loss_days,
                "percentage_profitable": percentage_profitable,  ##
                "capital": self.capital,
                "end_balance": end_balance,
                "max_drawdown": max_drawdown,
                "max_ddpercent": max_ddpercent,
                "max_drawdown_duration": max_drawdown_duration,
                "total_net_pnl": total_net_pnl,
                "daily_net_pnl": daily_net_pnl,
                "total_commission": total_commission,
                "daily_commission": daily_commission,
                "total_slippage": total_slippage,
                "daily_slippage": daily_slippage,
                "total_turnover": total_turnover,
                "daily_turnover": daily_turnover,
                "total_trade_count": total_trade_count,
                "daily_trade_count": daily_trade_count,
                "average_trade_cycle": average_trade_cycle,  ##
                "total_return": total_return,
                "annual_return": annual_return,
                "daily_return": daily_return,
                "return_std": return_std,
                "sharpe_ratio": sharpe_ratio,
                "return_drawdown_ratio": return_drawdown_ratio,
            }

            # Filter potential error infinite value
            for key, value in statistics.items():
                if value in (np.inf, -np.inf):
                    value = 0
                statistics[key] = np.nan_to_num(value)

            self.output("策略统计指标计算完成")
            return statistics, df
        else:
            # Calculate balance related time series data
            Df=df.copy(deep=True)
            Df["balance"] = Df["net_pnl"].cumsum() + self.capital
            Df["return"] = np.log(Df["balance"] / Df["balance"].shift(1)).fillna(0)  # 对数收益率
            Df["highlevel"] = (
                Df["balance"].rolling(
                    min_periods=1, window=len(Df), center=False).max()
            )
            Df["drawdown"] = Df["balance"] - Df["highlevel"]
            Df["ddpercent"] = Df["drawdown"] / Df["highlevel"] * 100

            # Calculate statistics value
            start_date = Df.index[0]
            end_date = Df.index[-1]

            total_days = len(Df)
            profit_days = len(Df[Df["net_pnl"] > 0])
            loss_days = len(Df[Df["net_pnl"] < 0])
            percentage_profitable = profit_days / (profit_days+loss_days) * 100  ##

            end_balance = Df["balance"].iloc[-1]
            max_drawdown = Df["drawdown"].min()
            max_ddpercent = Df["ddpercent"].min()
            max_drawdown_end = Df["drawdown"].idxmin()

            if isinstance(max_drawdown_end, date):
                max_drawdown_start = Df["balance"][:max_drawdown_end].idxmax()
                max_drawdown_duration = (max_drawdown_end - max_drawdown_start).days
            else:
                max_drawdown_duration = 0

            total_net_pnl = Df["net_pnl"].sum()
            daily_net_pnl = total_net_pnl / total_days

            total_commission = Df["commission"].sum()
            daily_commission = total_commission / total_days

            total_slippage = Df["slippage"].sum()
            daily_slippage = total_slippage / total_days

            total_turnover = Df["turnover"].sum()
            daily_turnover = total_turnover / total_days

            total_trade_count = Df["trade_count"].sum()
            daily_trade_count = total_trade_count / total_days
            average_trade_cycle = 1 / daily_trade_count  ##

            total_return = (end_balance / self.capital - 1) * 100
            annual_return = total_return / total_days * 240
            daily_return = Df["return"].mean() * 100
            return_std = Df["return"].std() * 100

            if return_std:
                daily_risk_free = self.risk_free / np.sqrt(240)
                sharpe_ratio = (daily_return - daily_risk_free) / return_std * np.sqrt(240)
            else:
                sharpe_ratio = 0

            return_drawdown_ratio = -total_net_pnl / max_drawdown

            statistics = {
                "start_date": start_date,
                "end_date": end_date,
                "total_days": total_days,
                "profit_days": profit_days,
                "loss_days": loss_days,
                "percentage_profitable": percentage_profitable,  ##
                "capital": self.capital,
                "end_balance": end_balance,
                "max_drawdown": max_drawdown,
                "max_ddpercent": max_ddpercent,
                "max_drawdown_duration": max_drawdown_duration,
                "total_net_pnl": total_net_pnl,
                "daily_net_pnl": daily_net_pnl,
                "total_commission": total_commission,
                "daily_commission": daily_commission,
                "total_slippage": total_slippage,
                "daily_slippage": daily_slippage,
                "total_turnover": total_turnover,
                "daily_turnover": daily_turnover,
                "total_trade_count": total_trade_count,
                "daily_trade_count": daily_trade_count,
                "average_trade_cycle": average_trade_cycle,  ##
                "total_return": total_return,
                "annual_return": annual_return,
                "daily_return": daily_return,
                "return_std": return_std,
                "sharpe_ratio": sharpe_ratio,
                "return_drawdown_ratio": return_drawdown_ratio,
            }

            # Filter potential error infinite value
            for key, value in statistics.items():
                if value in (np.inf, -np.inf):
                    value = 0
                statistics[key] = np.nan_to_num(value)

            self.output("策略统计指标计算完成")
            return statistics, Df

    def run_backtesting_by_trans_cycle(self) -> None:
        """"""
        self.strategy.on_init()

        # Generate sorted datetime list
        dts = list(self.dts)
        dts.sort()

        # Use the first [days] of history data for initializing strategy
        day_count = 0
        ix = 0

        for ix, dt in enumerate(dts):
            if self.datetime and dt.day != self.datetime.day:
                day_count += 1
                if day_count >= self.days:
                    break

            try:
                self.new_bars_by_contract(dt)
            except Exception:
                self.output("触发异常，回测终止")
                self.output(traceback.format_exc())
                return

        vt_symbols=self.main_contracts
        vt_symbols.extend(self.second_contracts)
        self.strategy.init_position(vt_symbols)

        self.strategy.inited = True
        self.output("策略初始化完成")

        self.strategy.on_start()
        self.strategy.trading = True
        self.output("开始回放历史数据")

        # Use the rest of history data for running backtesting
        for dt in dts[ix:]:
            try:
                self.new_bars_by_contract(dt)
            except Exception:
                self.output("触发异常，回测终止")
                self.output(traceback.format_exc())
                return

        self.output("历史数据回放结束")



    def show_chart(self, df: DataFrame = None, stat: Dict = None) -> None:
        """"""

        if stat is None:
            stat,_ = self.calculate_statistics()
        # Check DataFrame input exterior
        if df is None:
            df = self.daily_df

        # Check for init DataFrame
        # if df is None:
        #     return

        fig = make_subplots(
            rows=4,
            cols=1,
            subplot_titles=["SR=%.2f      total_return=%.2f%%     annual_return=%.2f%% " % (
                stat['sharpe_ratio'], stat['total_return'], stat['annual_return'])
                , " max_drawdown=%d     max_ddpercent=%.2f%%   max_drawdown_duration=%d" % (
                                stat['max_drawdown'], stat['max_ddpercent'], stat['max_drawdown_duration'])
                , "profit_days=%d      percentage_profitable=%d%%        average_trade_cycle=%.1f" % (
                                stat['profit_days'], stat['percentage_profitable'], stat['average_trade_cycle'])
                , "return_std=%.2f     return_drawdown_ratio=%.2f" % (
                                stat['return_std'], stat['return_drawdown_ratio'])],
            vertical_spacing=0.06
        )

        balance_line = go.Scatter(
            x=df.index,
            y=df["balance"],
            mode="lines",
            name="Balance"
        )
        drawdown_scatter = go.Scatter(
            x=df.index,
            y=df["ddpercent"],
            fillcolor="red",
            fill='tozeroy',
            mode="lines",
            name="Drawdown"
        )
        pnl_bar = go.Bar(y=df["net_pnl"], name="Daily Pnl")
        pnl_histogram = go.Histogram(x=df["net_pnl"], nbinsx=100, name="Days")

        fig.add_trace(balance_line, row=1, col=1)
        fig.add_trace(drawdown_scatter, row=2, col=1)
        fig.add_trace(pnl_bar, row=3, col=1)
        fig.add_trace(pnl_histogram, row=4, col=1)

        fig.update_layout(height=1000, width=1000)
        fig.show()

    def show_spreads(self, df: DataFrame = None):
        if df is None:
            results={"date":self.dts_temp,"spread":self.spreads,"boll_up":self.boll_up,"boll_mid":self.boll_mid,"boll_down":self.boll_down}
            df = DataFrame.from_dict(results).set_index("date")
        else:
            pass
        fig=go.Scatter(x=df.index,y=df['spread'])
        data=[fig]
        iplot(data)

    def show_trading_sketch(self, df: DataFrame = None)-> None:##
        """
        wbc
        :param df:
        :return:
        """
        if df is None:
            results={"date":self.dts_temp,"spread":self.spreads,"boll_up":self.boll_up,"boll_mid":self.boll_mid,"boll_down":self.boll_down,"long_position_point":self.long_position_point,"short_position_point":self.short_position_point,"close_long_position_point":self.close_long_position_point,"close_short_position_point":self.close_short_position_point}
            df = DataFrame.from_dict(results).set_index("date")
        else:
            pass
        # results={"date":self.dts_temp,"spread":self.spreads,"boll_up":self.boll_up,"boll_mid":self.boll_mid,"boll_down":self.boll_down}
        # df=DataFrame.from_dict(results).set_index("date")
        # df=self.spread_df
        #df_2=self.daily_df
        fig=go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['boll_up'],
            mode='lines',
            line_color='lightyellow',
            name='short signal'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['boll_down'],
            mode='lines',
            fill='tonexty',
            line_color='lightyellow',
            name='long signal'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['boll_mid'],
            mode='lines',
            line_color='red',
            name='prediction'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['spread'],
            mode='lines',
            line_color='blue',
            name='spread'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['long_position_point'],
            mode='markers',
            line_color='maroon',
            # size="pop",
            name='long_position'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['short_position_point'],
            mode='markers',
            line_color='olive',
            # size="pop",
            name='short_position'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['close_long_position_point'],
            mode='markers',
            line_color='maroon',
            # size="pop",
            name='close_long_position'
        ))
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['close_short_position_point'],
            mode='markers',
            line_color='olive',
            # size="pop",
            name='close_short_position'
        ))
        fig.show()

    def write_report(self, filename, setting, stat: Dict = None) -> None:
        """wbc"""

        if stat is None:
            stat = self.calculate_statistics()
        temp = filename + '#' + str(randint(10000, 99999)) + '.txt'
        f = open(temp, "w")
        f.write('Strategy parameters:\n')
        for key, val in setting.items():
            f.write(key + '   :   ' + str(val) + '\n')

        f.write('\nBack test statistics:\n')
        for key, val in stat.items():
            f.write(key + '   :   ' + str(val) + '\n')
        f.close()

    def update_daily_close(self, bars: Dict[str, BarData], dt: datetime) -> None:
        """"""
        d = dt.date()

        close_prices = {}
        for bar in bars.values():
            close_prices[bar.vt_symbol] = bar.close_price

        daily_result = self.daily_results.get(d, None)

        if daily_result:
            daily_result.update_close_prices(close_prices)
        else:
            self.daily_results[d] = PortfolioDailyResult(d, close_prices)

    def new_bars(self, dt: datetime) -> None:
        """"""
        self.datetime = dt


        bars: Dict[str, BarData] = {}
        for vt_symbol in self.vt_symbols:
            bar = self.history_data.get((dt, vt_symbol), None)

            # If bar data of vt_symbol at dt exists
            if bar:
                # Update bar data for crossing order
                self.bars[vt_symbol] = bar

                # Put bar into dict for strategy.on_bars update
                bars[vt_symbol] = bar
            # Otherwise, use previous close to backfill
            elif vt_symbol in self.bars:
                old_bar = self.bars[vt_symbol]

                bar = BarData(
                    symbol=old_bar.symbol,
                    exchange=old_bar.exchange,
                    datetime=dt,
                    open_price=old_bar.close_price,
                    high_price=old_bar.close_price,
                    low_price=old_bar.close_price,
                    close_price=old_bar.close_price,
                    gateway_name=old_bar.gateway_name
                )
                self.bars[vt_symbol] = bar

        self.cross_limit_order()
        # self.strategy.on_bars(bars)

        results=self.strategy.on_bars(bars,True)

        # print(dt.replace(tzinfo=None),self.end)
        if dt.replace(tzinfo=None)==self.end:
            # print('合约换期，进行平仓交易')
            # self.output("合约换期，进行平仓交易")
            self.strategy.close_position(bars)

        if results is None:
            pass
        else:
            self.spreads.append(results[0])
            self.boll_up.append(results[1])
            self.boll_mid.append(results[2])
            self.boll_down.append(results[3])
            self.dts_temp.append(dt)

        if self.strategy.inited:
            self.update_daily_close(self.bars, dt)


    def new_bars_by_contract(self, dt: datetime) -> None:
        # self.output('NEW BARS BY CONTRACT')
        """"""
        self.datetime = dt


        main_contract=self.get_main_contract_by_date(dt)
        second_contract=self.get_second_contract_by_date(dt)
        vt_symbols=[main_contract,second_contract]

        bars: Dict[str, BarData] = {}
        for vt_symbol in vt_symbols:
            bar = self.history_data.get((dt, vt_symbol), None)

            # If bar data of vt_symbol at dt exists
            if bar:
                # Update bar data for crossing order
                self.bars[vt_symbol] = bar

                # Put bar into dict for strategy.on_bars update
                bars[vt_symbol] = bar
            # Otherwise, use previous close to backfill
            elif vt_symbol in self.bars:
                old_bar = self.bars[vt_symbol]

                bar = BarData(
                    symbol=old_bar.symbol,
                    exchange=old_bar.exchange,
                    datetime=dt,
                    open_price=old_bar.close_price,
                    high_price=old_bar.close_price,
                    low_price=old_bar.close_price,
                    close_price=old_bar.close_price,
                    gateway_name=old_bar.gateway_name
                )
                self.bars[vt_symbol] = bar

        self.cross_limit_order()
        # self.strategy.on_bars(bars)

        results=self.strategy.on_bars_by_contract(bars,main_contract,second_contract,True)

        if main_contract!= self.main_contract_temp:
            self.main_contract_temp=main_contract
            # self.output("合约换期，进行平仓交易")
            print( main_contract, "-->", second_contract)
            self.strategy.close_position_by_contract(main_contract,second_contract,bars)

        if results is None:
            pass
        else:
            self.spreads.append(results[0])
            self.boll_up.append(results[1])
            self.boll_mid.append(results[2])
            self.boll_down.append(results[3])
            self.long_position_point.append(results[4])
            self.short_position_point.append(results[5])
            self.close_long_position_point.append(results[6])
            self.close_short_position_point.append(results[7])
            self.dts_temp.append(dt)

        if self.strategy.inited:
            self.update_daily_close(self.bars, dt)

    def update_sketch_data(self):
        result={'spread':self.spreads,'boll_up':self.boll_up,'boll_mid':self.boll_mid,'boll_down':self.boll_down,'date':self.dts_temp}
        df=DataFrame(result)
        df=df.set_index("date")
        return df

    def cross_limit_order(self) -> None:
        """
        Cross limit order with last bar/tick data.
        """
        for order in list(self.active_limit_orders.values()):
            bar = self.bars[order.vt_symbol]

            long_cross_price = bar.low_price
            short_cross_price = bar.high_price
            long_best_price = bar.open_price
            short_best_price = bar.open_price

            # Push order update with status "not traded" (pending).
            if order.status == Status.SUBMITTING:
                order.status = Status.NOTTRADED
                self.strategy.update_order(order)

            # Check whether limit orders can be filled.
            long_cross = (
                    order.direction == Direction.LONG
                    and order.price >= long_cross_price
                    and long_cross_price > 0
            )

            short_cross = (
                    order.direction == Direction.SHORT
                    and order.price <= short_cross_price
                    and short_cross_price > 0
            )

            if not long_cross and not short_cross:
                continue

            # Push order update with status "all traded" (filled).
            order.traded = order.volume
            order.status = Status.ALLTRADED
            self.strategy.update_order(order)

            self.active_limit_orders.pop(order.vt_orderid)

            # Push trade update
            self.trade_count += 1

            if long_cross:
                trade_price = min(order.price, long_best_price)
            else:
                trade_price = max(order.price, short_best_price)

            trade = TradeData(
                symbol=order.symbol,
                exchange=order.exchange,
                orderid=order.orderid,
                tradeid=str(self.trade_count),
                direction=order.direction,
                offset=order.offset,
                price=trade_price,
                volume=order.volume,
                datetime=self.datetime,
                gateway_name=self.gateway_name,
            )

            self.strategy.update_trade(trade)
            self.trades[trade.vt_tradeid] = trade

    def load_bars(
            self,
            strategy: StrategyTemplate,
            days: int,
            interval: Interval
    ) -> None:
        """"""
        self.days = days

    def send_order(
            self,
            strategy: StrategyTemplate,
            vt_symbol: str,
            direction: Direction,
            offset: Offset,
            price: float,
            volume: float,
            lock: bool,
            net: bool
    ) -> List[str]:
        """"""
        price = round_to(price, self.priceticks)
        symbol, exchange = extract_vt_symbol(vt_symbol)

        self.limit_order_count += 1

        order = OrderData(
            symbol=symbol,
            exchange=exchange,
            orderid=str(self.limit_order_count),
            direction=direction,
            offset=offset,
            price=price,
            volume=volume,
            status=Status.SUBMITTING,
            datetime=self.datetime,
            gateway_name=self.gateway_name,
        )

        self.active_limit_orders[order.vt_orderid] = order
        self.limit_orders[order.vt_orderid] = order

        return [order.vt_orderid]

    def cancel_order(self, strategy: StrategyTemplate, vt_orderid: str) -> None:
        """
        Cancel order by vt_orderid.
        """
        if vt_orderid not in self.active_limit_orders:
            return
        order = self.active_limit_orders.pop(vt_orderid)

        order.status = Status.CANCELLED
        self.strategy.update_order(order)

    def write_log(self, msg: str, strategy: StrategyTemplate = None) -> None:
        """
        Write log message.
        """
        msg = f"{self.datetime}\t{msg}"
        self.logs.append(msg)

    def send_email(self, msg: str, strategy: StrategyTemplate = None) -> None:
        """
        Send email to default receiver.
        """
        pass

    def sync_strategy_data(self, strategy: StrategyTemplate) -> None:
        """
        Sync strategy data into json file.
        """
        pass

    def put_strategy_event(self, strategy: StrategyTemplate) -> None:
        """
        Put an event to update strategy status.
        """
        pass

    def output(self, msg) -> None:
        """
        Output message of backtesting engine.
        """
        print(f"{datetime.now()}\t{msg}")

    def get_all_trades(self) -> List[TradeData]:
        """
        Return all trade data of current backtesting result.
        """
        return list(self.trades.values())

    def get_all_orders(self) -> List[OrderData]:
        """
        Return all limit order data of current backtesting result.
        """
        return list(self.limit_orders.values())

    def get_all_daily_results(self) -> List["PortfolioDailyResult"]:
        """
        Return all daily result data.
        """
        return list(self.daily_results.values())


class ContractDailyResult:
    """"""

    def __init__(self, result_date: date, close_price: float):
        """"""
        self.date: date = result_date
        self.close_price: float = close_price
        self.pre_close: float = 0

        self.trades: List[TradeData] = []
        self.trade_count: int = 0

        self.start_pos: float = 0
        self.end_pos: float = 0

        self.turnover: float = 0
        self.commission: float = 0
        self.slippage: float = 0

        self.trading_pnl: float = 0
        self.holding_pnl: float = 0
        self.total_pnl: float = 0
        self.net_pnl: float = 0

    def add_trade(self, trade: TradeData) -> None:
        """"""
        self.trades.append(trade)

    def calculate_pnl(
            self,
            pre_close: float,
            start_pos: float,
            size: int,
            rate: float,
            slippage: float
    ) -> None:
        """"""
        # If no pre_close provided on the first day,
        # use value 1 to avoid zero division error
        if pre_close:
            self.pre_close = pre_close
        else:
            self.pre_close = 1

        # Holding pnl is the pnl from holding position at day start
        self.start_pos = start_pos
        self.end_pos = start_pos

        self.holding_pnl = self.start_pos * (self.close_price - self.pre_close) * size

        # Trading pnl is the pnl from new trade during the day
        self.trade_count = len(self.trades)

        for trade in self.trades:
            if trade.direction == Direction.LONG:
                pos_change = trade.volume
            else:
                pos_change = -trade.volume

            self.end_pos += pos_change

            turnover = trade.volume * size * trade.price

            self.trading_pnl += pos_change * (self.close_price - trade.price) * size
            self.slippage += trade.volume * size * slippage
            self.turnover += turnover
            self.commission += turnover * rate

        # Net pnl takes account of commission and slippage cost
        self.total_pnl = self.trading_pnl + self.holding_pnl
        self.net_pnl = self.total_pnl - self.commission - self.slippage

    def update_close_price(self, close_price: float) -> None:
        """"""
        self.close_price = close_price


class PortfolioDailyResult:
    """"""

    def __init__(self, result_date: date, close_prices: Dict[str, float]):
        """"""
        self.date: date = result_date
        self.close_prices: Dict[str, float] = close_prices
        self.pre_closes: Dict[str, float] = {}
        self.start_poses: Dict[str, float] = {}
        self.end_poses: Dict[str, float] = {}

        self.contract_results: Dict[str, ContractDailyResult] = {}

        for vt_symbol, close_price in close_prices.items():
            self.contract_results[vt_symbol] = ContractDailyResult(result_date, close_price)

        self.trade_count: int = 0
        self.turnover: float = 0
        self.commission: float = 0
        self.slippage: float = 0
        self.trading_pnl: float = 0
        self.holding_pnl: float = 0
        self.total_pnl: float = 0
        self.net_pnl: float = 0

    def add_trade(self, trade: TradeData) -> None:
        """"""
        contract_result = self.contract_results[trade.vt_symbol]
        contract_result.add_trade(trade)

    def calculate_pnl(
            self,
            pre_closes: Dict[str, float],
            start_poses: Dict[str, float],
            sizes:  float,
            rates: float,
            slippages: float,
    ) -> None:
        """"""
        self.pre_closes = pre_closes

        for vt_symbol, contract_result in self.contract_results.items():
            contract_result.calculate_pnl(
                pre_closes.get(vt_symbol, 0),
                start_poses.get(vt_symbol, 0),
                sizes,
                rates,
                slippages
            )

            self.trade_count += contract_result.trade_count
            self.turnover += contract_result.turnover
            self.commission += contract_result.commission
            self.slippage += contract_result.slippage
            self.trading_pnl += contract_result.trading_pnl
            self.holding_pnl += contract_result.holding_pnl
            self.total_pnl += contract_result.total_pnl
            self.net_pnl += contract_result.net_pnl

            self.end_poses[vt_symbol] = contract_result.end_pos

    def update_close_prices(self, close_prices: Dict[str, float]) -> None:
        """"""
        self.close_prices = close_prices

        for vt_symbol, close_price in close_prices.items():
            contract_result = self.contract_results.get(vt_symbol, None)
            if contract_result:
                contract_result.update_close_price(close_price)


@lru_cache(maxsize=999)
def load_bar_data(
        vt_symbol: str,
        interval: Interval,
        start: datetime,
        end: datetime
):
    """"""
    symbol, exchange = extract_vt_symbol(vt_symbol)

    return database_manager.load_bar_data(
        symbol, exchange, interval, start, end
    )
