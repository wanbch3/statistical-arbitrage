#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'hsp'

import re
from typing import Dict, List


def get_comm_index_vt_name():
    name = "ALL8888.SHFE"
    return name


def get_comm_index_name():
    name = "ALL8888"
    return name


def get_comm_index_exchange():
    exchange = "SHFE"
    return exchange


def get_max_open_interest(bars):
    bar_max = {'symbol': '', 'open_interest': 0, 'volume': 0}
    for bar in bars:
        if bar['volume'] > bar_max['volume']:
            bar_max = bar

    return bar_max


def get_symbol_kinds(symbols: List[str]):
    """
    从合约列表中获取合约的品种和品种列表
    """
    kinds: Dict[str, List[str]] = {}
    for symbol in symbols:
        vt_symbol = symbol
        kind = left_alphas(vt_symbol)
        if kind not in kinds:
            kinds[kind] = [vt_symbol]
        else:
            if vt_symbol not in kinds[kind]:
                kinds[kind].append(vt_symbol)

    return kinds


def left_alphas(instr: str):
    """
    得到字符串左边的字符部分
    """
    ret_str = ''
    for s in instr:
        if s.isalpha():
            ret_str += s
        else:
            break
    return ret_str


def get_comm_index_symbols() -> List[str]:

    ci_symbols: List[str] = ["PB8888.SHFE", "PG8888.DCE", "FG8888.CZCE", "RM8888.CZCE", "LU8888.INE", "L8888.DCE",
                             "Y8888.DCE", "A8888.DCE", "NR8888.INE", "RU8888.SHFE", "M8888.DCE", "P8888.DCE",
                             "PP8888.DCE", "SR8888.CZCE", "AP8888.CZCE", "SM8888.CZCE", "SF8888.CZCE", "UR8888.CZCE",
                             "JD8888.DCE", "OI8888.CZCE", "CF8888.CZCE", "FU8888.SHFE", "TA8888.CZCE", "SC8888.INE",
                             "PF8888.CZCE", "MA8888.CZCE", "AL8888.SHFE", "C8888.DCE", "SA8888.CZCE", "NI8888.SHFE",
                             "EG8888.DCE", "SP8888.SHFE", "V8888.DCE", "SS8888.SHFE", "CS8888.DCE", "EB8888.DCE",
                             "RB8888.SHFE", "BU8888.SHFE", "HC8888.SHFE", "ZC8888.CZCE", "ZN8888.SHFE", "CU8888.SHFE",
                             "I8888.DCE", "SN8888.SHFE", "J8888.DCE", "JM8888.DCE"]

    return ci_symbols


def get_symbol_fixed_size(vt_symbol) -> float:

    price = 1
    fixed_size = 1
    if vt_symbol == "PB8888.SHFE":
        price = 13500
        fixed_size = 6
    if vt_symbol == "PG8888.DCE":
        price = 16500
        fixed_size = 5
    if vt_symbol == "FG8888.CZCE":
        price = 10300
        fixed_size = 8
    if vt_symbol == "RM8888.CZCE":
        price = 4300
        fixed_size = 19
    if vt_symbol == "LU8888.INE":
        price = 5505
        fixed_size = 14
    if vt_symbol == "L8888.DCE":
        price = 6170
        fixed_size = 13

    if vt_symbol == "Y8888.DCE":
        price = 13500
        fixed_size = 6
    if vt_symbol == "A8888.DCE":
        price = 10000
        fixed_size = 8
    if vt_symbol == "NR8888.INE":
        price = 18300
        fixed_size = 4
    if vt_symbol == "RU8888.SHFE":
        price = 22600
        fixed_size = 4
    if vt_symbol == "M8888.DCE":
        price = 5500
        fixed_size = 14
    if vt_symbol == "P8888.DCE":
        price = 13500
        fixed_size = 6

    if vt_symbol == "PP8888.DCE":
        price = 6400
        fixed_size = 12
    if vt_symbol == "SR8888.CZCE":
        price = 7200
        fixed_size = 11
    if vt_symbol == "AP8888.CZCE":
        price = 8500
        fixed_size = 9
    if vt_symbol == "SM8888.CZCE":
        price = 5800
        fixed_size = 14
    if vt_symbol == "SF8888.CZCE":
        price = 6500
        fixed_size = 12
    if vt_symbol == "UR8888.CZCE":
        price = 7710
        fixed_size = 10

    if vt_symbol == "JD8888.DCE":
        price = 6950
        fixed_size = 11
    if vt_symbol == "OI8888.CZCE":
        price = 14800
        fixed_size = 5
    if vt_symbol == "CF8888.CZCE":
        price = 13700
        fixed_size = 6
    if vt_symbol == "FU8888.SHFE":
        price = 4700
        fixed_size = 17
    if vt_symbol == "TA8888.CZCE":
        price = 3310
        fixed_size = 24
    if vt_symbol == "SC8888.INE":
        price = 80000
        fixed_size = 1

    if vt_symbol == "PF8888.CZCE":
        price = 4700
        fixed_size = 17
    if vt_symbol == "MA8888.CZCE":
        price = 4000
        fixed_size = 20
    if vt_symbol == "AL8888.SHFE":
        price = 16000
        fixed_size = 5
    if vt_symbol == "C8888.DCE":
        price = 4000
        fixed_size = 20
    if vt_symbol == "SA8888.CZCE":
        price = 6800
        fixed_size = 12
    if vt_symbol == "NI8888.SHFE":
        price = 25000
        fixed_size = 3

    if vt_symbol == "EG8888.DCE":
        price = 8850
        fixed_size = 9
    if vt_symbol == "SP8888.SHFE":
        price = 9500
        fixed_size = 8
    if vt_symbol == "V8888.DCE":
        price = 6900
        fixed_size = 12
    if vt_symbol == "SS8888.SHFE":
        price = 15500
        fixed_size = 5
    if vt_symbol == "CS8888.DCE":
        price = 4000
        fixed_size = 20
    if vt_symbol == "EB8888.DCE":
        price = 7900
        fixed_size = 10

    if vt_symbol == "RB8888.SHFE":
        price = 8900
        fixed_size = 9
    if vt_symbol == "BU8888.SHFE":
        price = 5500
        fixed_size = 15
    if vt_symbol == "HC8888.SHFE":
        price = 9600
        fixed_size = 8
    if vt_symbol == "ZC8888.CZCE":
        price = 15700
        fixed_size = 5
    if vt_symbol == "ZN8888.SHFE":
        price = 20000
        fixed_size = 4
    if vt_symbol == "CU8888.SHFE":
        price = 61700
        fixed_size = 1

    if vt_symbol == "I8888.DCE":
        price = 22140
        fixed_size = 4
    if vt_symbol == "SN8888.SHFE":
        price = 40000
        fixed_size = 2
    if vt_symbol == "J8888.DCE":
        price = 45000
        fixed_size = 2
    if vt_symbol == "JM8888.DCE":
        price = 20000
        fixed_size = 4

    return fixed_size


def get_back_test_rates():
    rates = {
        "AG8888.SHFE": 0 / 10000,
        "AL8888.SHFE": 0 / 10000,
        "AU8888.SHFE": 0 / 10000,
        "BU8888.SHFE": 0 / 10000,
        "CU8888.SHFE": 0 / 10000,
        "FU8888.SHFE": 0 / 10000,
        "HC8888.SHFE": 0 / 10000,
        "ZN8888.SHFE": 0 / 10000,
        "SP8888.SHFE": 0 / 10000,
        "SN8888.SHFE": 0 / 10000,
        "RU8888.SHFE": 0 / 10000,
        "RB8888.SHFE": 0 / 10000,
        "PB8888.SHFE": 0 / 10000,
        "NI8888.SHFE": 0 / 10000,
        "SS8888.SHFE": 0 / 10000,

        "A8888.DCE": 0 / 10000,
        "B8888.DCE": 0 / 10000,
        "C8888.DCE": 2 / 10000,
        "CS8888.DCE": 2 / 10000,
        "EB8888.DCE": 0 / 10000,
        "EG8888.DCE": 0 / 10000,
        "I8888.DCE": 0 / 10000,
        "J8888.DCE": 0 / 10000,
        "JD8888.DCE": 0 / 10000,
        "JM8888.DCE": 0 / 10000,
        "L8888.DCE": 0 / 10000,
        "M8888.DCE": 0 / 10000,
        "Y8888.DCE": 0 / 10000,
        "V8888.DCE": 0 / 10000,
        "PP8888.DCE": 0 / 10000,
        "PG8888.DCE": 0 / 10000,
        "P8888.DCE": 0 / 10000,
        "LH8888.DCE": 0 / 10000,

        "CF8888.CZCE": 0 / 10000,
        "AP8888.CZCE": 0 / 10000,
        "SA8888.CZCE": 0 / 10000,
        "CY8888.CZCE": 0 / 10000,
        "FG8888.CZCE": 0 / 10000,
        "ZC8888.CZCE": 0 / 10000,
        "UR8888.CZCE": 0 / 10000,
        "TA8888.CZCE": 0 / 10000,
        "SR8888.CZCE": 0 / 10000,
        "SM8888.CZCE": 0 / 10000,
        "SF8888.CZCE": 0 / 10000,
        "RM8888.CZCE": 0 / 10000,
        "OI8888.CZCE": 0 / 10000,
        "MA8888.CZCE": 0 / 10000,
        "PF8888.CZCE": 0 / 10000,

        "IC8888.CFFEX": 0 / 10000,
        "IF8888.CFFEX": 0 / 10000,
        "IH8888.CFFEX": 0 / 10000,
        "TS8888.CFFEX": 0 / 10000,
        "TF8888.CFFEX": 0 / 10000,
        "T8888.CFFEX": 0 / 10000,
        "SC8888.INE": 0 / 10000,
        "LU8888.INE": 0 / 10000,
        "NR8888.INE": 0 / 10000,
        "ALL8888.SHFE": 0 / 10000,
    }

    return rates


def get_back_test_slippages():
    slippages = {
        "AG8888.SHFE": 1,
        "AL8888.SHFE": 5,
        "AU8888.SHFE": 0.02,
        "BU8888.SHFE": 2,
        "CU8888.SHFE": 10,
        "FU8888.SHFE": 1,
        "HC8888.SHFE": 1,
        "ZN8888.SHFE": 5,
        "SP8888.SHFE": 2,
        "SN8888.SHFE": 10,
        "RU8888.SHFE": 5,
        "RB8888.SHFE": 1,
        "PB8888.SHFE": 5,
        "NI8888.SHFE": 10,
        "SS8888.SHFE": 5,

        "A8888.DCE": 1,
        "B8888.DCE": 1,
        "C8888.DCE": 1,
        "CS8888.DCE": 1,
        "EB8888.DCE": 1,
        "EG8888.DCE": 1,
        "I8888.DCE": 0.5,
        "J8888.DCE": 0.5,
        "JD8888.DCE": 1,
        "JM8888.DCE": 0.5,
        "L8888.DCE": 5,
        "M8888.DCE": 1,
        "Y8888.DCE": 2,
        "V8888.DCE": 5,
        "PP8888.DCE": 1,
        "PG8888.DCE": 1,
        "P8888.DCE": 2,
        "LH8888.DCE": 5,

        "CF8888.CZCE": 5,
        "AP8888.CZCE": 1,
        "SA8888.CZCE": 1,
        "CY8888.CZCE": 5,
        "FG8888.CZCE": 1,
        "ZC8888.CZCE": 0.2,
        "UR8888.CZCE": 1,
        "TA8888.CZCE": 2,
        "SR8888.CZCE": 1,
        "SM8888.CZCE": 2,
        "SF8888.CZCE": 2,
        "RM8888.CZCE": 1,
        "OI8888.CZCE": 1,
        "MA8888.CZCE": 1,
        "PF8888.CZCE": 2,

        "IC8888.CFFEX": 0.2,
        "IF8888.CFFEX": 0.2,
        "IH8888.CFFEX": 0.2,
        "TS8888.CFFEX": 0.005,
        "TF8888.CFFEX": 0.005,
        "T8888.CFFEX": 0.005,
        "SC8888.INE": 0.1,
        "LU8888.INE": 1,
        "NR8888.INE": 5,
        "ALL8888.SHFE": 1
    }

    return slippages


def get_back_test_sizes():
    sizes = {
        "AG8888.SHFE": 15,
        "AL8888.SHFE": 5,
        "AU8888.SHFE": 1000,
        "BU8888.SHFE": 10,
        "CU8888.SHFE": 5,
        "FU8888.SHFE": 10,
        "HC8888.SHFE": 10,
        "ZN8888.SHFE": 5,
        "SP8888.SHFE": 10,
        "SN8888.SHFE": 1,
        "RU8888.SHFE": 10,
        "RB8888.SHFE": 10,
        "PB8888.SHFE": 5,
        "NI8888.SHFE": 1,
        "SS8888.SHFE": 5,

        "A8888.DCE": 10,
        "B8888.DCE": 10,
        "C8888.DCE": 10,
        "CS8888.DCE": 10,
        "EB8888.DCE": 10,
        "EG8888.DCE": 10,
        "I8888.DCE": 100,
        "J8888.DCE": 100,
        "JD8888.DCE": 10,
        "JM8888.DCE": 60,
        "L8888.DCE": 5,
        "M8888.DCE": 10,
        "Y8888.DCE": 10,
        "V8888.DCE": 5,
        "PP8888.DCE": 10,
        "PG8888.DCE": 20,
        "P8888.DCE": 10,
        "LH8888.DCE": 16,

        "AP8888.CZCE": 10,
        "CF8888.CZCE": 5,
        "SA8888.CZCE": 5,
        "CY8888.CZCE": 5,
        "FG8888.CZCE": 20,
        "ZC8888.CZCE": 100,
        "UR8888.CZCE": 20,
        "TA8888.CZCE": 5,
        "SR8888.CZCE": 10,
        "SM8888.CZCE": 5,
        "SF8888.CZCE": 5,
        "RM8888.CZCE": 10,
        "OI8888.CZCE": 10,
        "MA8888.CZCE": 10,
        "PF8888.CZCE": 5,

        "IC8888.CFFEX": 200,
        "IF8888.CFFEX": 300,
        "IH8888.CFFEX": 300,
        "TS8888.CFFEX": 20000,
        "TF8888.CFFEX": 10000,
        "T8888.CFFEX": 10000,
        "SC8888.INE": 1000,
        "LU8888.INE": 10,
        "NR8888.INE": 10,
        "ALL8888.SHFE": 10
    }

    return sizes


def get_back_test_priceticks():
    priceticks = {
        "AG8888.SHFE": 1,
        "AL8888.SHFE": 5,
        "AU8888.SHFE": 0.02,
        "BU8888.SHFE": 2,
        "CU8888.SHFE": 10,
        "FU8888.SHFE": 1,
        "HC8888.SHFE": 1,
        "ZN8888.SHFE": 5,
        "SP8888.SHFE": 2,
        "SN8888.SHFE": 10,
        "RU8888.SHFE": 5,
        "RB8888.SHFE": 1,
        "PB8888.SHFE": 5,
        "NI8888.SHFE": 10,
        "SS8888.SHFE": 5,

        "A8888.DCE": 1,
        "B8888.DCE": 1,
        "C8888.DCE": 1,
        "CS8888.DCE": 1,
        "EB8888.DCE": 1,
        "EG8888.DCE": 1,
        "I8888.DCE": 0.5,
        "J8888.DCE": 0.5,
        "JD8888.DCE": 1,
        "JM8888.DCE": 0.5,
        "L8888.DCE": 5,
        "M8888.DCE": 1,
        "Y8888.DCE": 2,
        "V8888.DCE": 5,
        "PP8888.DCE": 1,
        "PG8888.DCE": 1,
        "P8888.DCE": 2,
        "LH8888.DCE": 5,

        "CF8888.CZCE": 5,
        "AP8888.CZCE": 1,
        "SA8888.CZCE": 1,
        "CY8888.CZCE": 5,
        "FG8888.CZCE": 1,
        "ZC8888.CZCE": 0.2,
        "UR8888.CZCE": 1,
        "TA8888.CZCE": 2,
        "SR8888.CZCE": 1,
        "SM8888.CZCE": 2,
        "SF8888.CZCE": 2,
        "RM8888.CZCE": 1,
        "OI8888.CZCE": 1,
        "MA8888.CZCE": 1,
        "PF8888.CZCE": 2,

        "IC8888.CFFEX": 0.2,
        "IF8888.CFFEX": 0.2,
        "IH8888.CFFEX": 0.2,
        "TS8888.CFFEX": 0.005,
        "TF8888.CFFEX": 0.005,
        "T8888.CFFEX": 0.005,
        "SC8888.INE": 0.1,
        "LU8888.INE": 1,
        "NR8888.INE": 5,
        "ALL8888.SHFE": 1
    }

    return priceticks


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
^	       匹配字符串的开头
[...]	   用来表示一组字符,单独列出：[amk] 匹配 'a'，'m'或'k'
re{ n, m}  匹配 n 到 m 次由前面的正则表达式定义的片段，贪婪方式
\d	       匹配任意数字，等价于 [0-9].
re+	       匹配1个或多个的表达式。
$	       匹配字符串的末尾。
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# return bool(re.match(r"^[a-zA-Z]{1,3}\d{2,4}.[A-Z]+$", vt_symbol))

