# encoding: utf-8
# 基金指标计算util

import statistics as st
import numpy as np
import pandas as pd
import math
import datetime
from jqdatasdk import *
auth('18510437635','Happy123!')

# 无风险收益率constant
#annual_risk_free_rate = 0.03
#weekly_risk_free_rate = math.pow((1+annual_risk_free_rate), (1/52)) - 1
#daily_risk_free_rate = math.pow((1+annual_risk_free_rate), (1/365)) - 1

annual_risk_free_rate = 0
weekly_risk_free_rate = 0
daily_risk_free_rate = 0

# 交易天数
num_trading_days = 252

def get_col_name(nv_df):
    if nv_df.iloc[len(nv_df.index) - 1].at["net_value"] is not None \
            and not np.isnan(nv_df.iloc[len(nv_df.index) - 1].at["net_value"]) and not np.isnan(
        nv_df.iloc[0].at["net_value"]):
            return 'net_value'
    else:
        return 'accumulated_net_value'

# 计算基金的年化收益
def calc_aagr(nv_df):
    # 默认最后一行为最新净值
    # 默认（nv exists or anv exists）
    col = get_col_name(nv_df)

    curr_nv = nv_df.iloc[len(nv_df.index) - 1].at[col]

    # 默认传进来的df根据交易日历reindex过
    num_days = len(nv_df.index)

    aagr = math.pow(curr_nv,(num_trading_days/num_days))-1

    print("calculated day aagr:         ", aagr)

    return float(aagr)


# 通过年化与最大回撤计算calmar比率
def calc_calmar(aagr, mdd):
    if mdd == 0:
        # 代表正无穷
        print("calculated calmar:       ", 0x3f3f3f3f)
        return 0x3f3f3f3f
    calmar = aagr / abs(mdd)
    print("calculated calmar:       ", calmar)
    return float(calmar)


# 计算最大回撤
def calc_max_drawdown(nv_df):
    col = get_col_name(nv_df)
    temp_df = nv_df
    # 加一列目前最大值
    temp_df["max_til_here"] = temp_df[col].expanding().max()
    # 加一列当前最大回撤
    temp_df["drawdown_here"] = (temp_df["max_til_here"] - temp_df[col]) / temp_df["max_til_here"]
    # 找出当前最大回撤的max
    mdd = temp_df["drawdown_here"].max()
    print("calculated mdd：         ", mdd)
    return float(mdd)


# 计算夏普比率
def calc_sharpe(aagr, sd):
    sharpe_ratio = (aagr - annual_risk_free_rate) / sd
    print("calculated sharpe:       ", sharpe_ratio)
    return float(sharpe_ratio)


# 计算年化波动率
def calc_std(nv_df):
    rt_list = []

    col = get_col_name(nv_df)
    for i in range (len(nv_df.index) - 1):

        nv1 = nv_df.iloc[i].at[col]
        nv2 = nv_df.iloc[i + 1].at[col]
        if not nv1 == 0:
            rt = (nv2-nv1)/nv1
        else:
            rt = 0
        rt_list.append(rt)

    std = st.pstdev(rt_list)

    # 转化为年波动率
    std = std * math.sqrt(num_trading_days)

    print("calculated sd:          ", std)
    return float(std)


# 计算半方差
def calc_semi_std(nv_df):

    rt_list = []
    col = get_col_name(nv_df)
    for i in range(len(nv_df.index) - 1):

        nv1 = nv_df.iloc[i].at[col]
        nv2 = nv_df.iloc[i + 1].at[col]
        if not nv1 == 0:
            rt = (nv2-nv1)/nv1
        else:
            rt = 0
        rt_list.append(rt)


    # 计算平均数
    mean = sum(rt_list) / len(rt_list)

    # 过滤出小于等于平均数的值
    low = [e for e in rt_list if e <= mean]

    # 计算semi-var
    semi_var = np.sum((low-mean) ** 2) / len(low)
    semi_sd = math.sqrt(semi_var)

    # 转化为年化半方差/波动率
    semi_sd = semi_sd * math.sqrt(num_trading_days)

    print("calculated semi_std:     ", semi_sd)
    return float(semi_sd)


# 计算两个基金的协方差
def calc_co_var(nv1, nv2):
    col1 = get_col_name(nv1)
    col2 = get_col_name(nv2)
    co_var = nv1[col1].cov(nv2[col2])
    print("calculated co_var:   ", co_var)
    return co_var


# 计算两个基金的相关性
def calc_correlation(nv1, nv2):
    col1 = get_col_name(nv1)
    col2 = get_col_name(nv2)
    corr = nv1[col1].corr(nv2[col2])
    print("calculated corr:   ", corr)
    return corr


# 计算两个基金的下行相关性
def calc_downside_correlation(nv1, nv2):
    print("calculated downside corr")