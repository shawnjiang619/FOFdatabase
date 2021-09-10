# encoding: utf-8
# 计算基金指标脚本，每日执行一遍

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime as dt
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ormModels import *
from indicator_calculator import *
import logging
from datetime import date
from jqdatasdk import *
auth('18510437635','Happy123!')
#auth('18600070100','Happy123!')

def clean_df(temp_df):
    initial_date = temp_df.iloc[0].at["trade_date"]
    curr_date = temp_df.iloc[len(temp_df.index) - 1].at["trade_date"]

    # 用交易日期当index
    temp_df.index = temp_df['trade_date']

    # 拿到交易日历
    calender = get_trade_days(start_date=initial_date, end_date=curr_date, count=None)
    # 用交易日历reindex
    nv_df = temp_df.reindex(calender, method='ffill')
    nv_df['trade_date'] = nv_df.index
    #print(nv_df.to_string())
    return nv_df



def calc_indicators(nv_df_list):

    fund_indicators_list = []
    # 遍历每个dataframe，计算指标
    for nv_df in nv_df_list:
        # print(nv_df.loc[0].at["fund_id"])
        # print(nv_df.to_string())
        #跳过数据为空的element
        if nv_df is None or len(nv_df) == 0:
            continue

        # 计算衍生指标
        sd = calc_std(nv_df)
        aagr = calc_aagr(nv_df)
        sharpe_ratio = calc_sharpe(aagr, sd)
        mdd = calc_max_drawdown(nv_df)
        calmar_ratio = calc_calmar(aagr, mdd)
        semi_sd = calc_semi_std(nv_df)

        # 组装orm object，放入list中return
        fund_indicators = FundIndicator(fund_id=nv_df.iloc[0].at["fund_id"], trade_date=date.today(), AAGR=aagr,
                                        max_drawdown=mdd, calmar_ratio=calmar_ratio, sharpe_ratio=sharpe_ratio,
                                        sd=sd, semi_dev=semi_sd)
        fund_indicators_list.append(fund_indicators)
        print("finished ........", nv_df.iloc[0].at["fund_id"])
    return fund_indicators_list


# 基金指标计算任务
def indicators_job():
    # 首先从数据库提取每只基金净值数据

    # 初始化数据库连接:
    engine = create_engine('mysql+mysqlconnector://jtx:Happy@2021@localhost:3306/fof')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()
    # 拿到所有的基金信息
    funds = session.query(FundInfo).all()
    #funds = session.query(FundInfo).filter(FundInfo.id == 761)

    nv_df_list = []
    # 遍历每只基金，提取净值信息计算指标
    for fund in funds:
        print(fund.name)
        # 找出所有该基金的净值信息,按交易时间从开始到现在排序
        fund_nvs = session.query(FundNv).filter(FundNv.fund_id == fund.id).order_by(FundNv.trade_date.asc()).all()
        # 转化成dataframe
        temp_df = pd.DataFrame([nv.__dict__ for nv in fund_nvs])
        nv_df = clean_df(temp_df)
        print(temp_df.to_string())
        nv_df_list.append(nv_df)

    # print(nv_df_list)

    # 计算基金各项指标，并更新数据库
    fund_indicators_list = calc_indicators(nv_df_list)
    print(len(fund_indicators_list))

    # 更新list中的每个indicators
    for indicators in fund_indicators_list:
        print("inside loop")
        print(indicators.fund_id, " ", indicators.AAGR)
        session.query(FundIndicator).filter(FundIndicator.fund_id == int(indicators.fund_id)).update({
                     'trade_date': indicators.trade_date, 'AAGR': indicators.AAGR,
                     'max_drawdown': indicators.max_drawdown,
                     'calmar_ratio': indicators.calmar_ratio, 'sharpe_ratio': indicators.sharpe_ratio,
                     'var': indicators.var, 'sd': indicators.sd, 'semi_var': indicators.semi_var,
                     'semi_dev': indicators.semi_dev})
        print("updated :", indicators.id,indicators.fund_id)


    # 提交即保存到数据库:
    session.commit()

    # 关闭session:
    session.close()

    print("finished calculating ", dt.now())

def cron_job():
    try:
        indicators_job()
    except Exception as e:
        print('Error occurred ' + str(e))
        logging.error('Error occurred ' + str(e) + "    " + str(dt.now()), exc_info=True)

if __name__ == '__main__':
    logging.basicConfig(filename='cal_app.log', level=logging.INFO)
    sched = BlockingScheduler()
    # 创建基金指标计算任务，每周一至周五的下午5：30自动执行
    sched.add_job(cron_job, 'cron', day_of_week='mon-fri', hour=17, minute=30)
    sched.start()
    #indicators_job()
