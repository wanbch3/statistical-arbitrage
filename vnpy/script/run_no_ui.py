#!/usr/bin/env python
#  -*- coding: utf-8 -*-

__author__ = 'hsp'

import multiprocessing
import re
import sys

from copy import copy
from enum import Enum
from time import sleep
from datetime import datetime, time
from logging import INFO

from vnpy.app.portfolio_strategy import PortfolioStrategyApp
from vnpy.trader.constant import Exchange
from vnpy.trader.object import BarData, TickData
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine
from vnpy.trader.utility import load_json, extract_vt_symbol
from vnpy.event import EventEngine

from vnpy.gateway.ctp import CtpGateway

from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from vnpy.app.data_recorder.engine import RecorderEngine

running = True

EXCHANGE_LIST = [
    Exchange.SHFE,
    Exchange.DCE,
    Exchange.CZCE,
    Exchange.CFFEX,
    Exchange.INE,
]

SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
#SETTINGS["log.console"] = True
SETTINGS["log.console"] = False

CTP_SETTING = load_json("connect_ctp.json")

def is_futures(vt_symbol: str) -> bool:
    """
    是否是期货
    """
    return bool(re.match(r"^[a-zA-Z]{1,3}\d{2,4}.[A-Z]+$", vt_symbol))

class RecordMode(Enum):
    BAR = "bar"
    TICK = "tick"

class WholeMarketRecorder(RecorderEngine):
    def __init__(self, main_engine, event_engine, record_modes=[RecordMode.BAR]):
        super().__init__(main_engine, event_engine)
        self.record_modes = record_modes

        # 非交易时间
        self.drop_start = time(3, 15)
        self.drop_end = time(8, 45)

        # 大连、上海、郑州交易所，小节休息
        self.rest_start = time(10, 15)
        self.rest_end = time(10, 30)

    def is_trading(self, vt_symbol, current_time) -> bool:
        """
        交易时间，过滤校验Tick
        """
        symbol, exchange = extract_vt_symbol(vt_symbol)

        if current_time >= self.drop_start and current_time < self.drop_end:
            return False

        if exchange in [Exchange.DCE, Exchange.SHFE, Exchange.CZCE]:
            if current_time >= self.rest_start and current_time < self.rest_end:
                return False

        return True

    def load_setting(self):
        pass

    def record_tick(self, tick: TickData):
        """
        抛弃非交易时间校验数据
        """
        tick_time = tick.datetime.time()
        if not self.is_trading(tick.vt_symbol, tick_time):
            return
        task = ("tick", copy(tick))
        self.queue.put(task)

    def record_bar(self, bar: BarData):
        """
        抛弃非交易时间校验数据
        """
        bar_time = bar.datetime.time()
        if not self.is_trading(bar.vt_symbol, bar_time):
            return
        task = ("bar", copy(bar))
        self.queue.put(task)

    def process_contract_event(self, event):
        """"""
        contract = event.data
        vt_symbol = contract.vt_symbol
        # 不录制期权
        if is_futures(vt_symbol):
            if RecordMode.BAR in self.record_modes:
                self.add_bar_recording(vt_symbol)
            if RecordMode.TICK in self.record_modes:
                self.add_tick_recording(vt_symbol)
            self.subscribe(contract)

def check_trading_period():
    """"""
    # Chinese futures market trading period (day/night)
    MORNING_START = time(8, 45)
    MORNING_END = time(12, 0)

    AFTERNOON_START = time(12, 45)
    AFTERNOON_END = time(15, 35)

    NIGHT_START = time(20, 45)
    NIGHT_END = time(3, 5)

    current_time = datetime.now().time()
    trading = False
    if ((current_time >= MORNING_START and current_time <= MORNING_END)
        or (current_time >= AFTERNOON_START and current_time <= AFTERNOON_END)
        or (current_time >= NIGHT_START)
        or (current_time <= NIGHT_END)):
        trading = True

    return True

def run_child_trade():
    """
    Running in the child process.
    """

    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(CtpGateway)
    #cta_engine = main_engine.add_app(CtaStrategyApp)
    portfolio_engine = main_engine.add_app(PortfolioStrategyApp)
    print("主引擎创建成功")

    log_engine = main_engine.get_engine("log")
    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    print("注册日志事件监听")

    main_engine.connect(CTP_SETTING, "CTP")
    print("连接CTP接口")

    whole_market_recorder = WholeMarketRecorder(main_engine, event_engine)

    #sleep(10)

    #cta_engine.init_engine()
    #main_engine.write_log("CTA策略初始化完成")

    #cta_engine.init_all_strategies()
    #sleep(60)   # Leave enough time to complete strategy initialization
    #main_engine.write_log("CTA策略全部初始化")

    #cta_engine.start_all_strategies()
    #main_engine.write_log("CTA策略全部启动")

    sleep(20)

    portfolio_engine.init_engine()
    print("CTA组合策略初始化完成")

    portfolio_engine.init_all_strategies()
    sleep(20)   # Leave enough time to complete strategy initialization
    print("CTA组合策略全部初始化")

    portfolio_engine.start_all_strategies()
    print("CTA组合策略全部启动")

    sleep(10)  # Leave enough time to complete strategy initialization

    global running
    while running:
        sleep(10)

        trading = check_trading_period()
        if not trading:
            print("关闭子进程")
            main_engine.close()
            sys.exit(0)


def run_parent():
    """
    Running in the parent process.
    """

    child_process = None
    global running
    while running:
        trading = check_trading_period()

        # Start child process in trading period
        if trading and child_process is None:
            print("启动子进程")
            child_process = multiprocessing.Process(target=run_child_trade)
            child_process.start()
            print("子进程启动成功")

        # 非记录时间则退出子进程
        if not trading and child_process is not None:
            if not child_process.is_alive():
                child_process = None
                print("子进程关闭成功")

        sleep(5)

def start_running():

    print("启动CTA策略监听进程")

    global running
    running = True

def stop_running():

    print("停止CTA策略监听进程")

    global running
    running = False

if __name__ == "__main__":

    start_running()

    try:
        run_parent()
    except KeyboardInterrupt:
        # print("\nApplication exit!")
        stop_running()

