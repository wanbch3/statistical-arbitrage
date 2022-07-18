#!/usr/bin/env python
#  -*- coding: utf-8 -*-

__author__ = 'wbc'

from datetime import datetime
import os
import re
import pandas as pd
from jqdatasdk import *

def get_dominant_future_list(future_type,start_date,end_date):
    '''
    提取主力合约以及他们对应的时间段（使用了jqdata的api）
    '''
    dominant_f=get_dominant_future(future_type,start_date,end_date)
    temp=0
    date_seperate=[start_date]
    dominant_future_list=[]
    str_to_date=lambda x: datetime.strptime(x,'%Y-%m-%d')
    for i in dominant_f:
        if not temp:
    #         print(i)
            temp=i
            dominant_future_list.append(i)
        else:
            if temp!=i:
    #             print(temp,i)
                date_temp=str_to_date(dominant_f[dominant_f==temp].index[-1])
                date_seperate.append(date_temp)
                dominant_future_list.append(i)
    #             print(dominant_f[dominant_f==temp].index[-1])
            temp=i
    date_seperate.append(end_date)
    return dominant_future_list,date_seperate

def get_second_dominant_future_list(future_type,dominant_future_list,date_seperate):
    '''
    根据主力合约提取每个主力合约在它们的对应时间段内的次主力合约（使用了jqdata的api）
    '''
    second_dominant_future_list=[]

    for i in range(len(date_seperate)-1):
        set_temp_1=set(get_future_contracts(future_type, date_seperate[i]))
        set_temp_2=set(get_future_contracts(future_type, date_seperate[i+1]))
        futures_list=list(set_temp_1.union(set_temp_2))
        futures_list=[future for future in futures_list if future>dominant_future_list[i]]
#         print('主力：',dominant_future_list[i])
#         print(futures_list)
    #     futures_list=list(map(lambda x: datetime.strptime(x,'%Y-%m-%d'),futures_list))
        df_c=get_bars(futures_list, count=50, unit='1d',
             fields=['date','open','high','low','close','volume'],
             include_now=False, end_dt=date_seperate[i+1], fq_ref_date=None,df=True)
        df_c=df_c.reset_index()
        df_c=df_c.rename(columns={'level_0':'futures'})
        second_dominant_future_temp=df_c.groupby(by='futures')['volume'].mean().sort_values(ascending = False).index[0]
        print('起始日期：',date_seperate[i],'结束日期：',date_seperate[i+1])
#         print(df_c.groupby(by='futures')['volume'].sum())
#         print(df_c.groupby(by='futures')['volume'].count())
        print(df_c.groupby(by='futures')['volume'].mean().sort_values(ascending = False))
        print('主力：',dominant_future_list[i],'  次主力：',second_dominant_future_temp)
#         print(futures_list)
        second_dominant_future_list.append(second_dominant_future_temp)
    return second_dominant_future_list

def calculate_spreads(df_future_1,df_future_2):
    '''
    输入两个期货k线数据，计算它们在相同时间段内的价差
    '''
    df_future_1=df_future_1.sort_values(by='date')
    df_future_2=df_future_2.sort_values(by='date')
    df_future_1=df_future_1.set_index('date')
    df_future_2=df_future_2.set_index('date')
#     df_spreads=pd.concat([df_future_1['trade_time'],df_future_1['close']-df_future_2['close']],axis=1)
    df_spreads=df_future_1.close-df_future_2.close
    df_spreads=df_spreads.to_frame().rename(columns={'close':'spreads'})
    df_spreads=df_spreads.dropna()
    return df_spreads

def calculate_spreads_between_dominant_and_second(dominant_futures_list,second_dominant_futures_list,date_seperate):
    '''
    输入主力与次主力合约与时间列表，返回价差
    '''
    df_spreads=pd.DataFrame()
    bars_num=pd.Series(date_seperate).diff(periods=1).max().days*555
    for i in range(len(date_seperate)-1):
        future_1=dominant_futures_list[i]
        future_2=second_dominant_futures_list[i]
        df_future_1=get_bars(future_1,count=bars_num,unit='1m',
                             fields=['date','open','high','low','close','volume'],
                             include_now=False, end_dt=date_seperate[i+1], fq_ref_date=None,df=True)
#         print(date_seperate[i])
        df_future_1=df_future_1.reset_index()
        df_future_1=df_future_1[(df_future_1.date>str(date_seperate[i]))]
        df_future_2=get_bars(future_2,count=bars_num,unit='1m',
                             fields=['date','open','high','low','close','volume'],
                             include_now=False, end_dt=date_seperate[i+1], fq_ref_date=None,df=True)
        df_future_2=df_future_2.reset_index()
        df_future_2=df_future_2[(df_future_2.date>str(date_seperate[i]))]
        df_spreads_temp=calculate_spreads(df_future_1,df_future_2)
        df_spreads=pd.concat([df_spreads_temp,df_spreads])
    df_spreads=df_spreads.sort_index()
    return df_spreads

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