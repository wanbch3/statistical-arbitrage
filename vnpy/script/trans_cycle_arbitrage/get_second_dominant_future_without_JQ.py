#!/usr/bin/env python
#  -*- coding: utf-8 -*-

__author__ = 'wbc'

from datetime import datetime
import os
import re
import pandas as pd


def get_second_dominant_future_without_jq(df, future_type, start_date, end_date):
    """
    根据本地数据获取主力合约与次主力合约列表
    :param df: 本地输入的主力合约列表，即每日日期及其主力合约
    :param future_type: 期货类型，例如'AL'
    :param start_date: 起始日期
    :param end_date: 结束日期
    :return: 返回主力合约列表，次主力合约列表，对应时间段（长度n+1）
    """
    # str_to_date = lambda x: datetime.strptime(x, '%Y-%m-%d')
    temp = df.future[0]
    futures_list = []
    date_list = []
    dominant_futures_list = []
    second_dominant_futures_list = []
    futures_list.append(temp)
    date_list.append(str_to_date(df.date[0]))
    date_seperate = [start_date]
    for future, date in zip(df.future, df.date):
        if temp != future:
            futures_list.append(future)
            date_list.append(str_to_date(date))
            temp = future
    date_list.append(end_date)

    for i in range(len(futures_list)):
        future = futures_list[i]
        if (date_list[i + 1] > start_date) & (date_list[i] < end_date):
            dominant_futures_list.append(future)
            try:
                second_dominant_futures_list.append(futures_list[i + 1])
            except(IndexError):
                pattern = re.compile(future_type + '\\d+')
                dirs = os.listdir('D:\\furdata\\furdata')
                pkl_file_list = [fut.rstrip('_1m.pkl') for fut in dirs if
                                 (fut > future) & (re.match(pattern, fut, flags=0) != None)]
                pkl_file_list.sort(key=lambda x: get_bars_by_pickle_file('D:\\furdata\\furdata', jq_to_pkl(x), date,
                                                                         end_date).vol.mean(), reverse=True)
                second_dominant_futures_list.append(pkl_to_jq(pkl_file_list[0]))
            if date_list[i + 1] > start_date:
                date_seperate.append(date_list[i + 1])
            elif date_list[i] < end_date:
                date_seperate.append(date_list[i])
    return dominant_futures_list, second_dominant_futures_list, date_seperate


def calculate_spreads(df_future_1, df_future_2):
    """
    输入两个期货k线数据，计算它们在相同时间段内的价差
    """
    df_future_1 = df_future_1.sort_values(by='trade_time')
    df_future_2 = df_future_2.sort_values(by='trade_time')
    df_future_1 = df_future_1.set_index('trade_time')
    df_future_2 = df_future_2.set_index('trade_time')
    #     df_spreads=pd.concat([df_future_1['trade_time'],df_future_1['close']-df_future_2['close']],axis=1)
    df_spreads = df_future_1.close - df_future_2.close
    df_spreads = df_spreads.to_frame().rename(columns={'close': 'spreads'})
    df_spreads = df_spreads.dropna()
    return df_spreads


def calculate_spreads_between_dominant_and_second(dominant_futures_list, second_dominant_futures_list, date_seperate):
    df_spreads = pd.DataFrame()
    for i in range(len(date_seperate) - 1):
        future_1 = dominant_futures_list[i]
        future_2 = second_dominant_futures_list[i]
        df_future_1 = get_bars_by_pickle_file('D:\\furdata\\furdata', jq_to_pkl(future_1), date_seperate[i],
                                              date_seperate[i + 1])
        df_future_2 = get_bars_by_pickle_file('D:\\furdata\\furdata', jq_to_pkl(future_2), date_seperate[i],
                                              date_seperate[i + 1])
        df_spreads_temp = calculate_spreads(df_future_1, df_future_2)
        df_spreads = pd.concat([df_spreads_temp, df_spreads])
    df_spreads = df_spreads.sort_index()
    return df_spreads


def pkl_to_jq(pkl_future):
    """
    将pkl的命名格式转化为jqdata文件的命名格式
    """
    if 'SHF' in pkl_future:
        jq_future = pkl_future.replace('SHF', 'XSGE')
    elif 'DCE' in pkl_future:
        jq_future = pkl_future.replace('DCE', 'XDCE')
    else:
        jq_future = pkl_future.replace('ZCE', 'XZCE')
    return jq_future


def jq_to_pkl(jq_future):
    """
    将jqdata的命名格式转化为pkl文件的命名格式
    """
    if 'SGE' in jq_future:
        pkl_future = jq_future.replace('XSGE', 'SHF')
    elif 'XDCE' in jq_future:
        pkl_future = jq_future.replace('XDCE', 'DCE')
    else:
        pkl_future = jq_future.replace('XZCE', 'ZCE')
    return pkl_future

def jq_to_vnpy(jq_future):
    """
    将jqdata的命名格式转化为vnpy文件的命名格式
    """
    if 'SGE' in jq_future:
        pkl_future = jq_future.replace('XSGE', 'SHFE')
    elif 'XDCE' in jq_future:
        pkl_future = jq_future.replace('XDCE', 'DCE')
    else:
        pkl_future = jq_future.replace('XZCE', 'CZCE')
    return pkl_future


def get_bars_by_pickle_file(abs_path, future, start_date, end_date):
    """
    从pkl文件提取k线数据
    """
    df_future = pd.read_pickle(abs_path + '\\' + future + '_1m.pkl')
    df_future = df_future[(df_future.trade_time < str(end_date)) & (df_future.trade_time > str(start_date))]
    return df_future


def str_to_date(string):
    return datetime.strptime(string, '%Y-%m-%d')
