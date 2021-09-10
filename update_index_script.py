# 每日更新指数净值
from jqdatasdk import *
auth('18510437635','Happy123!')
#auth('18600070100','Happy123!')
import datetime
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.sql import exists
from ormModels import *
import logging
from datetime import timedelta
from datetime import datetime as dt
from apscheduler.schedulers.blocking import BlockingScheduler

indexs = {
               '000300.XSHG': '沪深300',
               '000905.XSHG': '中证500',
               '000001.XSHG': '上证指数',
               '000016.XSHG': '上证50',
               '399006.XSHE': '创业板指',
               '399106.XSHE':'深证综指',
               '000012.XSHG': '国债指数',
               '000022.XSHG': '上证公司债指数',
               'T8888.CCFX': '10年期国债合约',
               'TF8888.CCFX': '5年期国债合约',
               'RB8888.XSGE': '螺纹钢指数',
               'M8888.XDCE': '豆粕指数',
               'CL': 'NYMEX原油',
               'GC': 'COMEX黄金',
               'AHD': 'LME铝3个月'
          }
# '000013.XSHG': '上证企业债指数'

# 请求数据天数
num_days = 5

def update_index_job():

    # 初始化数据库连接:
    engine = create_engine('mysql+mysqlconnector://jtx:Happy@2021@localhost:3306/fof')
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()

    ct = datetime.datetime.now()
    date = (ct - timedelta(num_days))
    print(ct, date)
    for key in indexs.keys():
        print("importing ", key)
        try:
            if len(key) > 5:
                df_price = get_price(key, start_date=date, end_date=ct, frequency='1d')
                print('got price')
            else:
                df_price = finance.run_query(
                    query(finance.FUT_GLOBAL_DAILY).filter(finance.FUT_GLOBAL_DAILY.code == key, finance.FUT_GLOBAL_DAILY.day > date))
        except Exception as e:
            logging.error('Error occurred ' + str(e), exc_info=True)

        print(df_price.to_string())
        #return None
        index_name = indexs[key]

        # 拿到index_info.id用作index_nv的foreign key
        temp_index = session.query(IndexInfo).filter(IndexInfo.name == index_name).one()
        index_id = temp_index.id

        # 插入指数净值信息
        for index in df_price.index:
            # account for two df structure
            if 'day' in df_price.columns: # 外盘期货
                trade_d = df_price.loc[index].at["day"]
            else: # 内盘指数
                trade_d = index
            nv = df_price.loc[index].at["close"]

            if not session.query(
                    exists().where(IndexNv.index_id == index_id).where(IndexNv.trade_date == trade_d)).scalar():
                new_index_nv = IndexNv(index_id=index_id, trade_date=trade_d, net_value=nv, update_date=ct)
                session.add(new_index_nv)
                # print("added a nv query")
        print("finished importing ", key)

    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()
    print("finished importing ", dt.now())

def cron_job():
    try:
        update_index_job()
    except Exception as e:
        print('Error occurred ' + str(e))
        logging.error('Error occurred ' + str(e) + "    " + str(dt.now()), exc_info=True)


if __name__ == '__main__':
    logging.basicConfig(filename='index_app.log', level=logging.INFO)
    sched = BlockingScheduler()
    # 创建指数净值导入任务，每周一至周五的下午5：00自动执行
    sched.add_job(cron_job, 'cron', day_of_week='mon-fri', hour=17, minute=00)
    sched.start()
