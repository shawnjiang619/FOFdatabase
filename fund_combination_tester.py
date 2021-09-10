from jqdatasdk import *
auth('18510437635','Happy123!')
import xlsxwriter
import pandas as pd
import xlwt
from indicator_calculator import *
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from ormModels import *
import xlrd
from xlutils.copy import copy

div = [[0.3,0.7],[0.4,0.6],[0.5,0.5],[0.6,0.4], [0.7,0.3]]

# key: fund_info.id - value: combo percentage
combo_map = {1: 0.5, 2: 0.5}
#combo_map = {1: 1}

downloaded_directory = 'C:/Users/zhangguanglei/fof/downloaded/'
formatted_directory= 'C:/Users/zhangguanglei/fof/formatted/'

file_name = '潼骁产品净值数据_20210721.xlsx'

# 从本地excel文件中读取nv
def test_from_excel(file_name):
    file_path = downloaded_directory + file_name
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'yyyy/mm/dd'
    # f = pd.ExcelFile(file_path)
    # rb = xlrd.open_workbook(file_path)
    # wb = copy(rb)
    # w_sheet = wb.get_sheet(0)

    df_qth = pd.read_excel(file_path, sheet_name='中信期货-潼骁全天候1号')
    df_txzs = pd.read_excel(file_path, sheet_name='潼骁致晟1号')
    df_xzc = pd.read_excel(file_path, sheet_name='潼骁新资产')
    df_cz = pd.read_excel(file_path, sheet_name='5return')
    print(df_cz.to_string())
    # 转换日期格式
    df_qth['净值日期'] = pd.to_datetime(df_qth['净值日期'], format='%Y%m%d')
    df_txzs['净值日期'] = pd.to_datetime(df_txzs['净值日期'], format='%Y%m%d')
    df_xzc['净值日期'] = pd.to_datetime(df_xzc['净值日期'], format='%Y%m%d')
    df_cz['净值日期'] = pd.to_datetime(df_cz['净值日期'], format='%Y%m%d')
    # 设日期为index
    df_qth.index = df_qth['净值日期']
    df_txzs.index = df_txzs['净值日期']
    df_xzc.index = df_xzc['净值日期']
    df_cz.index = df_cz['净值日期']
    # 使用交易日历reindex
    calender = get_trade_days(start_date="2020-03-05", end_date="2021-7-19", count=None)
    df_qth = df_qth.reindex(calender, method='ffill')
    df_txzs = df_txzs.reindex(calender, method='ffill')
    df_xzc = df_xzc.reindex(calender, method='ffill')
    df_cz = df_cz.reindex(calender, method='ffill')
    # 整合至一个dataframe
    df_nv = pd.DataFrame()
    df_nv['净值日期'] = df_qth['净值日期']
    df_nv['全天候净值'] = df_qth['累计净值']
    df_nv['致晟净值'] = df_txzs['累计净值']
    df_nv['新资产净值'] = df_xzc['累计净值']
    df_nv['纯债净值'] = df_cz['累计净值']
    df_nv.index = df_nv['净值日期']

    print(df_nv.to_string())

    # 计算基金的return
    for k in range(len(df_nv.index) - 1):
        tx_1 = df_nv.iloc[k].at['致晟净值']
        tx_2 = df_nv.iloc[k + 1].at['致晟净值']
        qth_1 = df_nv.iloc[k].at['全天候净值']
        qth_2 = df_nv.iloc[k + 1].at['全天候净值']
        xzc_1 = df_nv.iloc[k].at['新资产净值']
        xzc_2 = df_nv.iloc[k + 1].at['新资产净值']
        cz_1 = df_nv.iloc[k].at['纯债净值']
        cz_2 = df_nv.iloc[k + 1].at['纯债净值']
        tx_rt = tx_2 / tx_1 - 1
        qth_rt = qth_2 / qth_1 - 1
        xzc_rt = xzc_2 / xzc_1 - 1
        cz_rt = cz_2 / cz_1 - 1
        date = df_nv.iloc[k + 1].at['净值日期']
        df_nv.at[date, 'tx_rt'] = tx_rt
        df_nv.at[date, 'qth_rt'] = qth_rt
        df_nv.at[date, 'xzc_rt'] = xzc_rt
        df_nv.at[date, 'cz_rt'] = cz_rt

    df_nv.at["2020-03-05", 'tx_rt'] = 0
    df_nv.at["2020-03-05", 'qth_rt'] = 0
    df_nv.at["2020-03-05", 'xzc_rt'] = 0
    df_nv.at["2020-03-05", 'cz_rt'] = 0

    print(df_nv.to_string())

    # 计算组合nv
    i = 0
    while i < len(div):
        # df_nv["_".join([str(x) for x in div[i]]) + '_rt_p_1'] = div[i][0] * df_nv['tx_rt'] + div[i][1]* df_nv['qth_rt'] + 1
        df_nv["_".join([str(x) for x in div[i]]) + '_rt_p_1'] = 0.25 * df_nv['tx_rt'] + 0.25 * df_nv['qth_rt'] + 0.25 * \
                                                                df_nv['xzc_rt'] + 0.25 * df_nv['cz_rt'] + 1
        df_nv["_".join([str(x) for x in div[i]]) + '_nv'] = df_nv[
            "_".join([str(x) for x in div[i]]) + '_rt_p_1'].cumprod()

        i += 1

    column_names = ["sd", "aagr", "sharpe", "mdd", "calmar", "semi_std"]
    df_indicators = pd.DataFrame(columns=column_names)

    # 计算指标
    for column in df_nv:
        if 'nv' in column:
            temp = pd.DataFrame()
            temp[column] = df_nv[column]
            temp_new = temp.rename(columns={column: 'net_value'})
            print(temp_new.to_string())
            sd = calc_std(temp_new)
            aagr = calc_aagr(temp_new)
            sharpe_ratio = calc_sharpe(aagr, sd)
            mdd = calc_max_drawdown(temp_new)
            calmar_ratio = calc_calmar(aagr, mdd)
            semi_std = calc_semi_std(temp_new)

            df_indicators.loc[column] = [sd, aagr, sharpe_ratio, mdd, calmar_ratio, semi_std]
    print(df_indicators.to_string())

    writer = pd.ExcelWriter(downloaded_directory + 'combo_nv_indicators.xlsx', engine='xlsxwriter')
    df_indicators.to_excel(writer, sheet_name='indicators')
    df_nv.to_excel(writer, sheet_name='nv')
    writer.save()
    # wb.save(file_path)"""

# 从fof数据库中提取nv
def test_from_db(combo_name, combo_map):
    # 初始化数据库连接:
    engine = create_engine('mysql+mysqlconnector://jtx:Happy@2021@localhost:3306/fof')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()
    df_dict={}
    start_date_list = []
    curr_date_list = []

    # get nv
    for key in combo_map:
        fund_nvs = session.query(FundNv).filter(FundNv.fund_id == key).order_by(FundNv.trade_date.asc()).all()
        # 转化成dataframe
        temp_df = pd.DataFrame([nv.__dict__ for nv in fund_nvs])
        df_dict[key] = temp_df
        start_date_list.append(temp_df.iloc[0].at["trade_date"])
        curr_date_list.append(temp_df.iloc[len(temp_df.index) - 1].at["trade_date"])
    start_date = np.max(start_date_list)
    curr_date = np.min(curr_date_list)

    # reindex
    for key in df_dict:
        # 用交易日期当index
        df_dict[key].index = df_dict[key]['trade_date']
        # 拿到交易日历
        calender = get_trade_days(start_date=start_date, end_date=curr_date, count=None)
        # 用交易日历reindex
        nv_df = df_dict[key].reindex(calender, method='ffill')
        nv_df['trade_date'] = nv_df.index
        df_dict[key] = nv_df
        # print(nv_df.to_string())

    # 计算每个基金的return
    for key in df_dict:
        for k in range(len(df_dict[key].index) - 1):
            col = get_col_name(df_dict[key])
            rt_1 = df_dict[key].iloc[k].at[col]
            rt_2 = df_dict[key].iloc[k + 1].at[col]
            rt_pc = rt_2 / rt_1 - 1
            date = df_dict[key].iloc[k + 1].at['trade_date']
            df_dict[key].at[date, 'rt'] = rt_pc

        df_dict[key].at[start_date, 'rt'] = 0
        #print(df_dict[key].to_string())

    # create combo nv_df
    combo_nv = pd.DataFrame(index = df_dict[list(df_dict.keys())[0]]['trade_date'], columns = ['rt_p_1', 'net_value'])
    for index in df_dict[list(df_dict.keys())[0]].index:
        rt_p_1 = 1
        for key in df_dict:
            col = get_col_name(df_dict[key])
            rt_p_1 += df_dict[key].loc[index].at['rt'] * combo_map[key]
        combo_nv.at[index, 'rt_p_1'] = rt_p_1

    # calculate  combo_nv
    combo_nv['net_value'] = combo_nv['rt_p_1'].cumprod()

    column_names = ["sd", "aagr", "sharpe", "mdd", "calmar", "semi_std"]
    df_indicators = pd.DataFrame(columns=column_names)

    # calculate indicators
    sd = calc_std(combo_nv)
    aagr = calc_aagr(combo_nv)
    sharpe_ratio = calc_sharpe(aagr, sd)
    mdd = calc_max_drawdown(combo_nv)
    calmar_ratio = calc_calmar(aagr, mdd)
    semi_std = calc_semi_std(combo_nv)

    df_indicators.loc[combo_name] = [sd, aagr, sharpe_ratio, mdd, calmar_ratio, semi_std]
    print(df_indicators.to_string())


if __name__ == '__main__':
    #test_from_excel(file_name)
    test_from_db("测试", combo_map)
