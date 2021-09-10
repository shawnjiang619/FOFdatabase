# encoding: utf-8
# 此程序将formatted文件夹中格式正确的基金净值文件处理并上传至sql数据库中
# 处理后的文件将被放置在processed文件夹中

import os
import numpy as np
import pandas as pd
from datetime import date
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.sql import exists
from ormModels import *
import shutil
import math
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime as dt


#directory = '/Users/jw/txfof/fof/formatted/'
directory = 'C:/Users/zhangguanglei/fof/formatted/'


# 接受到一个file，提取该file指定基金数据件并上传至sql数据库中
# file需要符合基金净值数据模板
def handle_file(file):
    print("handling: ", file)
    # 打开指定的excel
    file_path = directory + file
    print(file_path)
    data_frame = pd.read_excel(file_path)

    # 提取基金相关信息,处理数据格式
    fund_name = data_frame.iloc[0, 3].encode('utf-8')
    fund_type = data_frame.iloc[0, 4].astype(int).item()
    fund_advisor = str(data_frame.iloc[0, 5]).encode('utf-8')
    company_name = data_frame.iloc[0, 6].encode('utf-8')
    fund_size = data_frame.iloc[0, 7].item()
    if math.isnan(fund_size):
        fund_size = sqlalchemy.sql.null()
    update_date = date.today()
    # 提取基金净值序列
    fund_nv = data_frame[['date', 'nv', 'anv']]

    # 初始化数据库连接:
    engine = create_engine('mysql+mysqlconnector://jtx:Happy@2021@localhost:3306/fof')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()

    # 初始化company_info.id
    comp_id = 0
    # 通过公司名判断该公司是否存在数据库
    if not session.query(exists().where(CompanyInfo.name == company_name)).scalar():
        # 如果该公司不存在表中，插入一条

        # 创建新company对象:
        new_company = CompanyInfo(name=company_name, fund_num=1, fund_size=fund_size)
        # 添加到session:
        session.add(new_company)
        print("added new company", company_name)
    elif not session.query(exists().where(FundInfo.name == fund_name)).scalar():
        # 该公司已存在表中，基金不存在表中，仅更新基金数(fund_num)
        print("company already exists", company_name)
        _ = session.query(CompanyInfo).filter(CompanyInfo.name == company_name)\
            .update({CompanyInfo.fund_num: CompanyInfo.fund_num + 1}, synchronize_session=False)
        print("updated company_info.fund_num: ", company_name)

    # 拿到company_info.id用作fund_info的foreign key
    temp_company = session.query(CompanyInfo).filter(CompanyInfo.name == company_name).one()
    comp_id = temp_company.id

    # 初始化fund_id
    fund_id = 0
    # 检查该基金是否已存在
    if not session.query(exists().where(FundInfo.name == fund_name)).scalar():
        # 插入一条到基金基本信息表
        new_fund = FundInfo(name=fund_name, company_id=comp_id, type=fund_type, advisor=fund_advisor, update_date=update_date)
        # 添加到session:
        session.add(new_fund)
        print("added new fund_info", fund_name)
        session.flush()
        # 拿到fund_info.id
        fund_id = new_fund.id
        # 插入一条到基金指标表
        new_fund_indicators = FundIndicator(fund_id=fund_id, trade_date=update_date)
        # 添加到session:
        session.add(new_fund_indicators)
        print("added new fund_indicators", fund_name)
    else:
        # 拿到fund_info.id用作fund_nv的foreign key
        temp_fund = session.query(FundInfo).filter(FundInfo.name == fund_name).one()
        fund_id = temp_fund.id

    # 插入基金净值信息
    for i in range(len(fund_nv.index)):
        trade_d = fund_nv.loc[i].at["date"]
        nv = fund_nv.loc[i].at["nv"]
        a_nv = fund_nv.loc[i].at["anv"]
        if math.isnan(a_nv):
            a_nv = sqlalchemy.sql.null()
        if math.isnan(nv):
            nv = sqlalchemy.sql.null()
        if not session.query(exists().where(FundNv.fund_id == fund_id).where(FundNv.trade_date == trade_d)).scalar():
            new_fund_nv = FundNv(fund_id=fund_id, trade_date=trade_d, net_value=nv, accumulated_net_value=a_nv, update_date=update_date)
            session.add(new_fund_nv)
            # print("added a nv query")

    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()
    print("finished processing, disconnecting sql")

def handle_file_job():
    # 查看formatted文件夹里是否有新的未处理文件
    if len(os.listdir(directory)) != 0:
        # 有未处理文件
        print("[formatted] directory is not empty")
        # 遍历未处理文件
        for filename in os.listdir(directory):
            if os.path.splitext(filename)[-1] == ".xls" or os.path.splitext(filename)[-1] == ".xlsx":
                # 处理文件导入sql数据库
                handle_file(filename)

                # 把处理过的文件移到processed文件夹中
                original = 'C:/Users/zhangguanglei/fof/formatted/' + filename
                target = 'C:/Users/zhangguanglei/fof/processed/' + filename
                shutil.move(original, target)


    else:
        # 无未处理文件，结束程序
        print("[formatted] directory is empty, exiting program")

def cron_job():
    try:
        handle_file_job()
    except Exception as e:
        print('Error occurred ' + str(e))
        logging.error('Error occurred ' + str(e) + "    " + str(dt.now()), exc_info=True)

if __name__ == '__main__':
    logging.basicConfig(filename='handle_app.log', level=logging.INFO)
    sched = BlockingScheduler()
    # 创建邮箱附件下载任务，每周一至周五的晚上8：00自动执行
    sched.add_job(cron_job, 'cron', day_of_week='mon-fri', hour=20, minute=00)
    sched.start()

