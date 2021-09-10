# 用于更新邮箱收到的每周/日群发净值信息(只适用于初始录入完成的基金的日常更新)
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from datetime import datetime as dt
import os
import pandas as pd
from datetime import date
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
import shutil
from sqlalchemy.sql import exists
from ormModels import *
from nv_file_templete import *
import sqlalchemy

downloaded_directory = 'C:/Users/zhangguanglei/fof/downloaded/'


def handle_file(filename, templete):
    # 打开指定的excel
    file_path = downloaded_directory + filename
    print(file_path)
    f = pd.ExcelFile(file_path)

    # 初始化数据库连接:
    engine = create_engine('mysql+mysqlconnector://jtx:Happy@2021@localhost:3306/fof')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()
    k = 0
    for i in f.sheet_names:
        print("new loop")
        print(templete['fund_id'])
        print('doing...', templete['fund_id'][k])
        print('k is ', k)

        fund_id = templete['fund_id'][k]


        if fund_id < 0: # 无效sheet，跳过
            k+=1
            if k >= len(templete['fund_id']):
                break
            else:
                continue
        df = pd.read_excel(file_path, sheet_name=i, header=templete['header'])
        # 提取基金净值序列
        date_col = templete['date']
        nv_col = templete['nv']
        anv_col = templete['anv']
        nv_df = df[[date_col, nv_col, anv_col]].copy()
        if not isinstance(df.loc[0].at[date_col], pd._libs.tslibs.timestamps.Timestamp):
            if not isinstance(df.loc[0].at[date_col], str):
                df[date_col] = df[date_col].astype(str)
            nv_df.loc[:, date_col] = pd.to_datetime(df[date_col])
        #print(nv_df.to_string())
        fund_nvs = session.query(FundNv).filter(FundNv.fund_id == fund_id).order_by(FundNv.trade_date.desc()).first()
        last_update_date = pd.Timestamp(fund_nvs.trade_date)

        rslt_df = nv_df[nv_df[date_col] > last_update_date]

        update_date = date.today()
        print(rslt_df.to_string())
        for index in rslt_df.index:

            trade_date = rslt_df.loc[index].at[date_col]

            if nv_col is not '':
                nv = rslt_df.loc[index].at[nv_col]
            else:
                nv = sqlalchemy.sql.null()
            if anv_col is not '':
                anv = rslt_df.loc[index].at[anv_col]
            else:
                anv = sqlalchemy.sql.null()

            if not session.query(
                    exists().where(FundNv.fund_id == fund_id).where(FundNv.trade_date == trade_date)).scalar():
                new_fund_nv = FundNv(fund_id=fund_id, trade_date=trade_date, net_value=nv, accumulated_net_value=anv,
                                     update_date=update_date)
                session.add(new_fund_nv)
                print("added a new nv id:", fund_id)
        k+=1


    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()

def update_nv_job(templete):
    if len(os.listdir(downloaded_directory)) != 0:
        # 遍历未处理文件
        for filename in os.listdir(downloaded_directory):
            if templete['file_name'] in filename:
                handle_file(filename, templete)

                # 把处理过的文件移到archieve文件夹中
                original = 'C:/Users/zhangguanglei/fof/downloaded/' + filename
                target = 'C:/Users/zhangguanglei/fof/archive/' + filename
                shutil.move(original, target)

def cron_job(templete):
    try:
        update_nv_job(templete)
    except Exception as e:
        print('Error occurred ' + str(e))
        logging.error('Error occurred ' + str(e) + "    " + str(dt.now()), exc_info=True)


if __name__ == '__main__':
    logging.basicConfig(filename='index_app.log', level=logging.INFO)
    # update_nv_job(templete_rongxi)
    # update_nv_job(templete_tongxiao)
    # update_nv_job(templete_zhiyuan)
    #update_nv_job(templete_tianyan)
    sched = BlockingScheduler()
    # 创建基金净值导入任务，每周一至周五的下午7：00自动执行
    sched.add_job(lambda: cron_job(templete_rongxi), 'cron', day_of_week='mon-fri', hour=19, minute=30)
    sched.add_job(lambda: cron_job(templete_tongxiao), 'cron', day_of_week='mon-fri', hour=19, minute=31)
    sched.add_job(lambda: cron_job(templete_zhiyuan), 'cron', day_of_week='fri', hour=19, minute=32)
    sched.add_job(lambda: cron_job(templete_tianyan), 'cron', day_of_week='fri', hour=19, minute=33)
    sched.start()
